"""
auto_image_finder.py — v4
──────────────────────────
Cascada de fuentes por escena del storyboard:
  1. Pexels Videos (portrait) → clips reales con movimiento natural
  2. Pexels Photos  (portrait) → fotos estáticas de alta calidad
  3. Wikimedia Commons         → fotos educativas libres
  4. produccion/fondos_fallback/ → emergencia local

Sistema de selección: descarga N_CANDIDATOS por escena, puntúa por
contraste / brillo / color (imagen) o frame del medio (video),
conserva solo el ganador.

Nomenclatura de salida:
  XX_bg.mp4  → video clip descargado
  XX_bg.jpg  → imagen estática descargada
"""

import os
import subprocess
import glob
import urllib.request
import urllib.parse
import json
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

HEADERS = {"User-Agent": "AstrologyFactory/1.0 (local automation pipeline)"}
N_CANDIDATOS = 8

ASSET_VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault"
os.makedirs(ASSET_VAULT_DIR, exist_ok=True)

_STOPWORDS = {
    "aesthetic", "vertical", "dark", "subtle", "elegant", "high",
    "resolution", "deep", "mystic", "atmospheric", "moody", "cinematic",
    "wallpaper", "background", "texture", "abstract", "beautiful", "stunning",
}


# ─────────────────────────────────────────────────────────────────────────────
# Scoring
# ─────────────────────────────────────────────────────────────────────────────

def _score_imagen(img_path: str) -> float:
    try:
        img  = Image.open(img_path).convert("RGB")
        arr  = np.array(img, dtype=np.float32)
        h, w = arr.shape[:2]

        luma       = 0.299*arr[:,:,0] + 0.587*arr[:,:,1] + 0.114*arr[:,:,2]
        contraste  = np.std(luma) / 128.0
        orient     = 1.0 if h >= w else 0.4
        brillo     = np.mean(luma) / 255.0
        brillo_s   = 1.0 - abs(brillo - 0.42) * 2
        r, g, b    = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        color_s    = min((np.std(r-g) + np.std(g-b) + np.std(r-b)) / 3 / 25.0, 1.0)

        return float((contraste * 0.40 + brillo_s * 0.30 + color_s * 0.20) * orient)
    except Exception:
        return 0.0


def _score_video(video_path: str) -> float:
    """Puntúa un video extrayendo el frame del segundo 1."""
    tmp = video_path + "_frame.jpg"
    try:
        r = subprocess.run(
            ["ffmpeg", "-y", "-ss", "1", "-i", video_path,
             "-frames:v", "1", "-update", "1", tmp],
            capture_output=True, stdin=subprocess.DEVNULL
        )
        if r.returncode != 0 or not os.path.exists(tmp):
            return 0.0
        score = _score_imagen(tmp)
        # Penalización a videos para favorecer imágenes (a petición del Arquitecto)
        return score * 0.85
    except Exception:
        return 0.0
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except: pass


def _elegir_mejores(candidatos: list[str], k: int = 4) -> list[str]:
    if not candidatos:
        return []

    scores = []
    for p in candidatos:
        s = _score_video(p) if p.endswith(".mp4") else _score_imagen(p)
        scores.append((p, s))
    scores.sort(key=lambda x: x[1], reverse=True)

    mejores = [p for p, _ in scores[:k]]
    
    for i, (p, s) in enumerate(scores):
        if i < k:
            print(f"      🎯 Ganadora {i+1}: {os.path.basename(p)} (score={s:.3f})")
        else:
            print(f"         Descartada: {os.path.basename(p)} (score={s:.3f})")
            try: os.remove(p)
            except: pass

    return mejores


# ─────────────────────────────────────────────────────────────────────────────
# Helpers FFmpeg
# ─────────────────────────────────────────────────────────────────────────────

def _recortar_a_vertical(src: str, dst: str) -> bool:
    tmp = src + ".tmp.jpg"
    try:
        cmd = [
            "ffmpeg", "-y", "-i", src,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-frames:v", "1", "-update", "1", tmp
        ]
        r = subprocess.run(cmd, capture_output=True, stdin=subprocess.DEVNULL)
        if r.returncode == 0 and os.path.exists(tmp):
            os.replace(tmp, dst)
            return True
    except Exception:
        pass
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except: pass
    return False


# ─────────────────────────────────────────────────────────────────────────────
# Fuente 0: Pixabay Illustrations (portrait preferred)
# ─────────────────────────────────────────────────────────────────────────────

def _buscar_pixabay_ilustracion(query: str, output_dir: str, idx: int,
                                 n: int = N_CANDIDATOS) -> list[str]:
    api_key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not api_key:
        return []

    # Quitar etiquetas del query
    q_limpio = query.replace("[illustration]", "").replace("[video]", "").strip()
    encoded = urllib.parse.quote(q_limpio)
    
    url = (f"https://pixabay.com/api/?key={api_key}&q={encoded}"
           f"&image_type=illustration&orientation=vertical&per_page={n*2}")
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            
        hits = data.get("hits", [])
        candidatos = []
        import random
        top = hits[:20]
        if len(top) > n: top = random.sample(top, n)
        for i, hit in enumerate(top):
            foto_url = hit.get("largeImageURL")
            if not foto_url: continue
            
            cand_raw   = os.path.join(output_dir, f"{idx:02d}_pc{i}.jpg")
            cand_final = os.path.join(output_dir, f"{idx:02d}_pcv{i}.jpg")
            
            try:
                req2 = urllib.request.Request(foto_url, headers=HEADERS)
                with urllib.request.urlopen(req2, timeout=15) as r, \
                     open(cand_raw, "wb") as f:
                    f.write(r.read())
                
                if _recortar_a_vertical(cand_raw, cand_final):
                    os.remove(cand_raw)
                    candidatos.append(cand_final)
                else:
                    try: os.remove(cand_raw)
                    except: pass
            except Exception:
                pass
        return candidatos

    except Exception as e:
        print(f"      ⚠️  Pixabay API: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Fuente 1: Pexels Videos (portrait)
# ─────────────────────────────────────────────────────────────────────────────

def _buscar_pexels_video(query: str, output_dir: str, idx: int,
                          n: int = N_CANDIDATOS) -> list[str]:
    """
    Busca clips de video portrait en Pexels.
    Retorna lista de paths .mp4 descargados listos para scoring.
    """
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    if not api_key:
        return []

    encoded = urllib.parse.quote(query)
    url = (f"https://api.pexels.com/videos/search"
           f"?query={encoded}&orientation=portrait&per_page={n*2}&size=medium")

    try:
        req = urllib.request.Request(url, headers={**HEADERS, "Authorization": api_key})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        videos = data.get("videos", [])
        if not videos:
            return []

        candidatos = []
        import random
        top = videos[:20]
        if len(top) > n: top = random.sample(top, n)
        for i, video in enumerate(top):
            files = video.get("video_files", [])
            # Preferir archivos portrait (h > w), entre 480p y 1440p
            portrait = [f for f in files
                        if f.get("height", 0) > f.get("width", 0)
                        and 480 <= f.get("height", 0) <= 1440]
            if not portrait:
                portrait = [f for f in files
                            if f.get("height", 0) > f.get("width", 0)]
            if not portrait:
                continue

            best = sorted(portrait, key=lambda x: x.get("height", 0))[-1]
            video_url = best["link"]
            cand_path = os.path.join(output_dir, f"{idx:02d}_vc{i}.mp4")

            try:
                req2 = urllib.request.Request(video_url, headers=HEADERS)
                with urllib.request.urlopen(req2, timeout=45) as r, \
                     open(cand_path, "wb") as f_out:
                    f_out.write(r.read())
                if os.path.getsize(cand_path) > 10_000:
                    candidatos.append(cand_path)
                else:
                    os.remove(cand_path)
            except Exception as e:
                print(f"      ⚠️  Video DL error: {e}")

        return candidatos

    except Exception as e:
        print(f"      ⚠️  Pexels Video API: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Fuente 2: Pexels Photos (portrait)
# ─────────────────────────────────────────────────────────────────────────────

def _buscar_pexels_foto(query: str, output_dir: str, idx: int,
                         n: int = N_CANDIDATOS) -> list[str]:
    api_key = os.getenv("PEXELS_API_KEY", "").strip()
    if not api_key:
        return []

    encoded = urllib.parse.quote(query)
    url = (f"https://api.pexels.com/v1/search"
           f"?query={encoded}&orientation=portrait&per_page={n}&size=large")
    try:
        req = urllib.request.Request(url, headers={**HEADERS, "Authorization": api_key})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())

        fotos = data.get("photos", [])
        candidatos = []
        import random
        top = fotos[:20]
        if len(top) > n: top = random.sample(top, n)
        for i, foto in enumerate(top):
            foto_url   = foto["src"]["large2x"]
            cand_raw   = os.path.join(output_dir, f"{idx:02d}_fc{i}.jpg")
            cand_final = os.path.join(output_dir, f"{idx:02d}_fcv{i}.jpg")
            try:
                req2 = urllib.request.Request(foto_url, headers=HEADERS)
                with urllib.request.urlopen(req2, timeout=15) as r, \
                     open(cand_raw, "wb") as f:
                    f.write(r.read())
                if _recortar_a_vertical(cand_raw, cand_final):
                    os.remove(cand_raw)
                    candidatos.append(cand_final)
                else:
                    try: os.remove(cand_raw)
                    except: pass
            except Exception:
                pass
        return candidatos

    except Exception as e:
        print(f"      ⚠️  Pexels Photo API: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Fuente 3: Wikimedia Commons
# ─────────────────────────────────────────────────────────────────────────────

def _simplificar_queries(query: str) -> list[str]:
    palabras = query.split()
    core = [p for p in palabras if p.lower() not in _STOPWORDS]
    candidatos = [query]
    if core != palabras:
        candidatos.append(" ".join(core))
    if len(core) >= 3:
        candidatos.append(" ".join(core[:2]))
    if len(core) >= 2:
        candidatos.append(core[0])
    vistos, result = set(), []
    for c in candidatos:
        if c not in vistos:
            vistos.add(c)
            result.append(c)
    return result


def _buscar_wikimedia(query: str, output_dir: str, idx: int,
                       n: int = N_CANDIDATOS) -> list[str]:
    candidatos = []
    for q in _simplificar_queries(query):
        if len(candidatos) >= n:
            break
        if q != query:
            print(f"      🔁 Wikimedia: '{q}'")
        encoded = urllib.parse.quote(q)
        api_url = (
            "https://commons.wikimedia.org/w/api.php"
            f"?action=query&list=search&srsearch={encoded}&srnamespace=6"
            f"&srlimit={n*3}&srinfo=&srprop=&format=json"
        )
        try:
            req = urllib.request.Request(api_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
            for item in data.get("query", {}).get("search", []):
                if len(candidatos) >= n:
                    break
                titulo = item["title"]
                ext = titulo.lower().split(".")[-1] if "." in titulo else ""
                if ext not in {"jpg", "jpeg", "png"}:
                    continue
                nombre = urllib.parse.quote(
                    titulo.replace("File:", "").replace(" ", "_"))
                thumb_url = (
                    f"https://commons.wikimedia.org/wiki/Special:FilePath/"
                    f"{nombre}?width=1080"
                )
                i = len(candidatos)
                cand_raw   = os.path.join(output_dir, f"{idx:02d}_wc{i}.jpg")
                cand_final = os.path.join(output_dir, f"{idx:02d}_wcv{i}.jpg")
                try:
                    req2 = urllib.request.Request(thumb_url, headers=HEADERS)
                    with urllib.request.urlopen(req2, timeout=15) as r, \
                         open(cand_raw, "wb") as f:
                        f.write(r.read())
                    if _recortar_a_vertical(cand_raw, cand_final):
                        os.remove(cand_raw)
                        candidatos.append(cand_final)
                    else:
                        try: os.remove(cand_raw)
                        except: pass
                except Exception:
                    continue
        except Exception as e:
            print(f"      ⚠️  Wikimedia: {e}")

    return candidatos


# ─────────────────────────────────────────────────────────────────────────────
# Fuente 4: Fallback local
# ─────────────────────────────────────────────────────────────────────────────

def _usar_fallback_local(output_path: str, fallback_dir: str) -> bool:
    fondos = (glob.glob(os.path.join(fallback_dir, "*.jpg")) +
              glob.glob(os.path.join(fallback_dir, "*.png")))
    if not fondos:
        return False
    return _recortar_a_vertical(sorted(fondos)[-1], output_path)


# ─────────────────────────────────────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────────────────────────────────────

def get_automated_background(evento_name: str, output_dir: str) -> bool:
    """
    Lee storyboard.txt y descarga el mejor asset (video o imagen) por escena.
    Cascada: Pexels Videos → Pexels Photos → Wikimedia → local.
    Salida: {idx:02d}_bg.mp4 (video) o {idx:02d}_bg.jpg (imagen).
    """
    storyboard_path = os.path.join(output_dir, "storyboard.txt")

    if not os.path.exists(storyboard_path):
        print("⚠️  Sin storyboard.txt — usando queries genéricas.")
        with open(storyboard_path, "w", encoding="utf-8") as f:
            f.write("person alone window autumn\n"
                    "emotional burden solitude man\n"
                    "scales harmony golden light\n"
                    "dark sky stars venus\n"
                    "mirror truth reflection\n"
                    "shadow silhouette duality\n"
                    "woman meditation peace\n"
                    "cosmos stars night connection\n")

    with open(storyboard_path, "r", encoding="utf-8") as f:
        lineas = [l.strip() for l in f if l.strip()]

    if not lineas:
        return False

    base_dir     = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    fallback_dir = os.path.join(base_dir, "produccion", "fondos_fallback")
    os.makedirs(fallback_dir, exist_ok=True)

    tiene_pexels = bool(os.getenv("PEXELS_API_KEY", "").strip())
    print(f"🔍 {len(lineas)} escenas | Videos+Fotos Pexels → Wikimedia → local | "
          f"{N_CANDIDATOS} candidatos/escena")

    assets_finales = []

    for idx, raw_query in enumerate(lineas):
        print(f"\n   🎬 Escena {idx+1}/{len(lineas)}: '{raw_query}'")

        is_video = "[video]" in raw_query.lower()
        is_illustration = "[illustration]" in raw_query.lower()
        query = raw_query.replace("[video]", "").replace("[illustration]", "").strip()

        # Limpiar assets anteriores de este índice
        for old in glob.glob(os.path.join(output_dir, f"{idx:02d}_bg.*")):
            try: os.unlink(old)
            except: pass

        final_mp4 = os.path.join(output_dir, f"{idx:02d}_bg.mp4")
        final_jpg = os.path.join(output_dir, f"{idx:02d}_bg.jpg")

        # --- REVISIÓN EN BÓVEDA ---
        safe_query = "".join(c if c.isalnum() else "_" for c in query.lower()).strip("_")
        safe_query = "_".join(filter(None, safe_query.split("_")))
        vault_mp4 = os.path.join(ASSET_VAULT_DIR, f"{safe_query}.mp4")
        vault_jpg = os.path.join(ASSET_VAULT_DIR, f"{safe_query}.jpg")

        if os.path.exists(vault_mp4):
            print(f"      🔒 Recuperado de Bóveda (Offline): {safe_query}.mp4")
            os.symlink(vault_mp4, final_mp4)
            assets_finales.append(final_mp4)
            continue
        elif os.path.exists(vault_jpg):
            print(f"      🔒 Recuperado de Bóveda (Offline): {safe_query}.jpg")
            os.symlink(vault_jpg, final_jpg)
            assets_finales.append(final_jpg)
            continue

        candidatos = []

        assets_dir = os.path.join(output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # 0. Pixabay Illustrations
        if not is_video:
            pix = _buscar_pixabay_ilustracion(query, assets_dir, idx, N_CANDIDATOS)
            if pix:
                print(f"      🎨 Pixabay Ilustración: {len(pix)} imagen(es)")
            candidatos += pix

        # 1. Pexels Videos
        if (not is_illustration or not candidatos) and tiene_pexels:
            vids = _buscar_pexels_video(query, assets_dir, idx, N_CANDIDATOS)
            if vids:
                print(f"      📹 Pexels Video: {len(vids)} clip(s)")
            candidatos += vids

        # 2. Pexels Photos (si faltan candidatos)
        if len(candidatos) < 2 and tiene_pexels and not is_video:
            fotos = _buscar_pexels_foto(query, assets_dir, idx,
                                         N_CANDIDATOS - len(candidatos))
            if fotos:
                print(f"      📷 Pexels Foto: {len(fotos)} imagen(es)")
            candidatos += fotos

        # 3. Wikimedia
        if not candidatos:
            wc = _buscar_wikimedia(query, assets_dir, idx, N_CANDIDATOS)
            if wc:
                print(f"      🌐 Wikimedia: {len(wc)} imagen(es)")
            candidatos += wc

        # 4. Fallback local
        if not candidatos:
            print(f"      ⚠️  Sin resultados online. Fallback local...")
            if _usar_fallback_local(final_jpg, fallback_dir):
                print(f"      ✅ Fallback → {final_jpg}")
                assets_finales.append(final_jpg)
            else:
                print(f"      ❌ Sin asset para escena {idx+1}.")
            continue

        # Seleccionar las mejores (k=4 a petición del Arquitecto, priorizando imágenes para aliviar FFmpeg pero manteniendo la edición sugestiva)
        mejores = _elegir_mejores(candidatos, k=4)
        if not mejores:
            continue

        import uuid
        for sub_idx, mejor in enumerate(mejores):
            uid = uuid.uuid4().hex[:6]
            es_mp4 = mejor.endswith(".mp4")
            ext = ".mp4" if es_mp4 else ".jpg"
            final_path = os.path.join(assets_dir, f"{idx:02d}_{sub_idx}_bg{ext}")
            nuevo_nombre = f"{safe_query}_{uid}{ext}"
            vault_nuevo = os.path.join(ASSET_VAULT_DIR, nuevo_nombre)
            
            os.replace(mejor, vault_nuevo)
            try:
                os.symlink(vault_nuevo, final_path)
            except: pass
            print(f"      ✅ Asset {sub_idx+1} guardado en Bóveda → {nuevo_nombre}")
            assets_finales.append(final_path)

    if not assets_finales:
        print("\n❌ Sin assets para ninguna escena.")
        return False

    print(f"\n✅ {len(assets_finales)}/{len(lineas)} assets listos.")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        get_automated_background(sys.argv[1], sys.argv[2])
