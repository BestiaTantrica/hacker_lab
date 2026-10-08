#!/usr/bin/env python3
"""
🌓 CÉLULA MADRE 2.0 — LA NODRIZA VISUAL
Reemplaza al asignador_semantico.py
Convierte imágenes estáticas en MP4, deduce el clima emocional de los assets 
con Gemini, y realiza un matching semántico matemático con la toma astrológica.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import random

QUOTA_EXCEEDED = False
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

import google.genai as genai
from google.genai import types

from v2 import db_visual

# ── Director de Arte (semántica local, sin API) ────────────────────────────
from v2.celula_2.director_de_arte import (
    enriquecer_tomas,
    score_semantico,
    opacidad_boost as emocion_opacidad_boost,
)

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY_TEXT")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EVENTO_ID        = ADN["produccion"]["evento_id"]
SEMANA           = ADN["produccion"]["semana_prefijo"]
VAULT_BASE       = Path(ADN["assets"]["boveda_base"])
ASSETS_AUDITADOS = Path(ADN["assets"]["paths"]["assets_auditados"])
TIMELINE_DIR     = Path(ADN["assets"]["paths"]["timeline_huecos"])
TEMP_DIR         = VAULT_BASE / "temp"

# Catálogo central
CATALOG_PATH = ASSETS_AUDITADOS / "vault_catalog.json"
TRANSMUTADOS_DIR = VAULT_BASE / "transmutados"

FORMATOS_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
FORMATOS_IMG   = {".jpg", ".jpeg", ".png"}

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; GRIS = "\033[90m"

def log(msg, color=RESET):  print(f"{color}{msg}{RESET}")
def ok(msg):                log(f"  ✅ {msg}", VERDE)
def err(msg):               log(f"  ❌ {msg}", ROJO)
def info(msg):              log(f"  ℹ️  {msg}", CYAN)
def warn(msg):              log(f"  ⚠️  {msg}", AMARILLO)

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

asegurar_dir(TEMP_DIR)
asegurar_dir(TRANSMUTADOS_DIR)

# ── Clientes Multiplexados (Hydra) ─────────────────────────────────────────
API_KEYS = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and "_WEB" not in k and v]
API_KEYS = list(dict.fromkeys(API_KEYS))  # sin duplicados, conserva orden


gemini_clients = []
for key in API_KEYS:
    try:
        gemini_clients.append(genai.Client(api_key=key))
    except Exception:
        pass

if not gemini_clients:
    err("No se encontraron llaves de API de Gemini válidas en .env")
    sys.exit(1)

import base64
from io import BytesIO
from PIL import Image

def _image_to_base64(img_path: Path) -> str:
    img = Image.open(img_path)
    img.thumbnail((1024, 1024))
    buffered = BytesIO()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# ── Lectura del timeline ─────────────────────────────────────────────────────

def cargar_timeline() -> dict:
    ruta = TIMELINE_DIR / f"{EVENTO_ID}.json"
    if not ruta.exists():
        err(f"Timeline no encontrado: {ruta}")
        sys.exit(1)
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)

# ── A. Inventariador Universal ───────────────────────────────────────────────

def listar_assets(directorio: Path) -> list[Path]:
    if not directorio.exists():
        return []
    assets = []
    for f in directorio.rglob("*"):
        if f.is_file() and (f.suffix.lower() in FORMATOS_VIDEO or f.suffix.lower() in FORMATOS_IMG):
            assets.append(f)
    return sorted(assets)

# ── B. Motor de Transmutación ────────────────────────────────────────────────

def get_transmutado_path(img_path: Path) -> Path:
    return TRANSMUTADOS_DIR / f"{img_path.stem}_transmutado.mp4"

def transmutar_imagen_a_video(img_path: Path, mood_scores: dict) -> Path:
    """Convierte un JPG/PNG en MP4 usando un Ken Burns Effect sutil en FFmpeg."""
    out_path = get_transmutado_path(img_path)
    if out_path.exists():
        return out_path
    
    info(f"Transmutando imagen: {img_path.name}...")
    
    # Decisión de filtro según el mood (muy simplificado para V1)
    # Por defecto hacemos un slow zoom-in
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0010,1.5)':d=10*30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"
    
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
        "-vf", vf,
        "-c:v", "libx264", "-t", "10", "-pix_fmt", "yuv420p",
        "-fpsmax", "30",
        str(out_path)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            ok(f"Transmutación exitosa: {out_path.name}")
            return out_path
        else:
            err(f"Error transmutando {img_path.name}")
            return None
    except Exception as e:
        err(f"Exception transmutando: {e}")
        return None

# ── C. Catalogador Semántico ─────────────────────────────────────────────────

def cargar_catalogo() -> dict:
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_catalogo(catalogo: dict):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=2)

def actualizar_catalogo_dummy(assets: list[Path]) -> dict:
    # La Nodriza Visual ahora lee el catálogo directamente desde SQLite
    # usando las etiquetas extraídas por el auditor_boveda IA.
    cat = cargar_catalogo()
    
    # Obtenemos todos los assets aprobados con sus etiquetas
    assets_db = db_visual.obtener_todos_los_assets_aprobados()
    
    # Indexamos por path_str para búsquedas rápidas
    mapa_db = {Path(r).resolve(): t for r, t in assets_db}
    
    for a in assets:
        key = a.name
        if key not in cat:
            path_absoluto = a.resolve()
            
            # Recuperar etiquetas de SQLite o usar heurística si no existe en DB
            if path_absoluto in mapa_db:
                tags_str = mapa_db[path_absoluto]
                final_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            else:
                path_str = str(path_absoluto).lower()
                import re
                path_words = re.split(r'[/_.-]', path_str)
                valid_words = {w for w in path_words if len(w) > 2 and w not in ["home", "tomas2", "mediacontingencia", "privada", "astrology", "vault", "assets", "auditados", "imagenes", "videos", "mp4", "jpg", "png", "jpeg"]}
                
                # Intentar leer el antiguo .json si existe (retrocompatibilidad)
                json_file = a.parent / (a.stem + ".json")
                semantic_tags = []
                if json_file.exists():
                    try:
                        import json as j
                        with open(json_file, "r") as f:
                            s_meta = j.load(f)
                            if "metaforas" in s_meta:
                                semantic_tags.extend([m.lower() for m in s_meta["metaforas"]])
                            if "mood" in s_meta:
                                semantic_tags.append(s_meta["mood"].lower())
                            if "elemento" in s_meta:
                                semantic_tags.append(s_meta["elemento"].lower())
                    except Exception:
                        pass
                
                final_tags = list(valid_words.union(set(semantic_tags)))
            
            cat[key] = {
                "etiquetas_visuales": final_tags,
                "tags": final_tags,
                "stats_uso": []
            }
        
        cat[key]["path_original"] = str(a.resolve())
        cat[key]["path_video_final"] = str(a.resolve())
    
    return cat

# ── D. Scorer Emocional y Semántico ──────────────────────────────────────────

def elegir_mejor_asset_local(toma: dict, cat: dict, ultimos_usados: list[str], ultimo_elemento: str = None) -> str:
    mejor_score = -9999.0
    mejor_asset_key = None
    for key, meta in cat.items():
        if not meta.get("path_video_final"): continue
        score = calcular_score(toma, key, meta, ultimos_usados, ultimo_elemento)
        if score > mejor_score:
            mejor_score = score
            mejor_asset_key = key
    return mejor_asset_key

from v2.celula_2.prompt_semantico import elegir_mejor_asset_con_gemini

def elegir_mejor_asset_hibrido(toma: dict, cat: dict, ultimos_usados: list, ultimo_elemento: str, gemini_clients: list, evento_id: str) -> str:
    # 1. Ranking local (top 40)
    scores = []
    for key, meta in cat.items():
        if not meta.get("path_video_final"): continue
        s = calcular_score(toma, key, meta, ultimos_usados, ultimo_elemento)
        scores.append((s, key))
    scores.sort(key=lambda x: x[0], reverse=True)
    top_40_keys = [k for s, k in scores[:40]]
    
    if not top_40_keys: return None

    # 2. Filtrar el catálogo para Gemini
    cat_filtrado = {k: cat[k] for k in top_40_keys}
    
    # 3. Llamada a Gemini con cliente rotativo
    if gemini_clients:
        import random
        client_elegido = random.choice(gemini_clients)
        emocion = toma.get('emocion', 'indefinida')
        texto = toma.get('texto_narrador', toma.get('texto', ''))
        rol = toma.get('rol', '')
        
        mejor_key = elegir_mejor_asset_con_gemini(client_elegido, texto, rol, cat_filtrado, ultimos_usados, emocion, evento_id)
        if mejor_key and mejor_key in cat:
            return mejor_key
            
    # Fallback al mejor local
    return top_40_keys[0]

def calcular_score(toma: dict, asset_key: str, meta: dict, ultimos_usados: list[str], ultimo_elemento: str) -> float:
    # 1. Base score
    score = 0.5
    
    # 2. Penalizaciones fuertes
    if ultimos_usados:
        if asset_key in ultimos_usados:
            score -= 100.0  # NUNCA REPETIR IMÁGENES O VIDEOS EN EL MISMO VIDEO
            
    # Penalizar si ya se usó en videos anteriores (para rotación de stock)
    usos_historicos = len(meta.get("stats_uso", []))
    if usos_historicos > 0:
        score -= (usos_historicos * 10.0) # Penalización fuerte por uso histórico
            
    # 3. Emparejamiento por ROL
    rol = toma.get("rol", "").lower()
    tags_list = meta.get("etiquetas_visuales", []) + meta.get("tags", [])
    tags = (" ".join(tags_list) + " " + meta.get("path_original", "")).lower()
    
    # Penalizar a muerte imágenes que rompen la estética
    para_bloquear = ["familia", "bebe", "family", "baby", "niño", "niña", "hogar", "niños", "pareja", "couple", "boda", "wedding", "multitud", "crowd", "niñez", "child", "persona", "hombre", "mujer", "gente", "people", "man", "woman", "person"]
    for palabra_prohibida in para_bloquear:
        if palabra_prohibida in tags:
            score -= 999.0
    
    # 4. Bonus semántico del Director de Arte
    emocion_toma = toma.get("emocion", "aire")
    texto_toma   = toma.get("texto", "")
    score += score_semantico(texto_toma, emocion_toma, tags_list)
    
    # 5. Asignaciones forzadas / bonos altos (se mantienen)
    if "cta" in rol:
        if "fractal" in tags or "abstract" in tags or "fondo" in tags:
            score += 2.0
    
    if "gancho" in rol:
        if "fuego" in tags or "espacio" in tags or "luz" in tags:
            score += 1.0

        # En el gancho preferimos los videos
        if asset_key.endswith(".mp4"):
            score += 0.5
            
    return score

# ── Slicing Semántico y Montaje ──────────────────────────────────────────────

import re
import uuid

def calcular_cortes_ritmicos(texto: str, duracion_total: float) -> list[float]:
    # Retornamos cortes de aproximadamente 2 a 2.5 segundos cada uno
    # para crear un viaje sensorial más dinámico
    num_cortes = max(1, int(duracion_total / 2.0))
    corte_dur = duracion_total / num_cortes
    return [corte_dur] * num_cortes

def preprocesar_asset_para_montaje(asset_path: Path, duracion: float, chunk_id: str, es_primer_chunk: bool = False, es_ultimo_chunk: bool = False, score: float = 0.5, es_iconica: bool = False) -> Path:
    import random
    out_path = TEMP_DIR / f"chunk_{chunk_id}.mp4"

    # Opacidad dinámica: espejismo astrológico (0.72 etéreo → 0.88 presente)
    # A mayor afinidad semántica del asset con la toma, más sólido aparece.
    alpha = round(0.72 + 0.16 * max(0.0, min(1.0, score)), 4)
    
    fondo_dir = VAULT_BASE / "Assets_Auditados" / "Videos"
    fondo_video = None
    if fondo_dir.exists():
        fondos = list(fondo_dir.rglob("*.mp4"))
        if fondos:
            fondo_video = random.choice(fondos)

    is_image = asset_path.suffix.lower() in FORMATOS_IMG

    if fondo_video:
        bg_filter_base = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
        bg_filter = bg_filter_base
        
        if is_image:
            estilo = random.choice(["flotando", "mezclado", "pleno"])
            if estilo == "flotando":
                fg_filter = "scale=864:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black@0"
            elif estilo == "mezclado":
                fg_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            else:  # pleno
                fg_filter = "scale=1020:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black@0"
                
            if es_iconica:
                # Añadimos un leve paneo/zoom (Ken Burns)
                fg_filter += f",zoompan=z='zoom+0.001':d={int(duracion*30)}:s=1080x1920:fps=30"
                
            blend = "overlay=format=auto:shortest=1"
        else:
            # B-Roll: también pasa por el espejismo (alpha dinámico)
            fg_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            blend = "overlay=format=auto:shortest=1"

        if es_ultimo_chunk and not is_image:
            # Cortamos la parte del inicio del asset original y la ponemos en reversa 
            # para que enganche perfecto en un loop si TikTok vuelve a empezar.
            fg_filter += f",trim=0:{duracion},reverse,setpts=PTS-STARTPTS"
            
        fg_alpha = "format=rgba"
        if is_image:
            fade_dur = min(0.5, duracion / 4)
            fade_out_start = max(0.0, duracion - fade_dur)
            fg_alpha += f",fade=t=in:st=0:d={fade_dur}:alpha=1,fade=t=out:st={fade_out_start}:d={fade_dur}:alpha=1"

        # Resonancia Cimática Real (Overlay Fractal)
        # Generar un fractal matemático vibrante de 1080x1920 y mezclarlo suavemente
        filter_complex = (
            f"[0:v] {bg_filter} [bg]; "
            f"[1:v] {fg_filter}, {fg_alpha}, colorchannelmixer=aa={alpha} [fg]; "
            f"sierpinski=s=1080x1920:r=30:seed=1337[fractal];"
            f"[bg][fg] {blend} [base]; "
            f"[base][fractal]blend=all_mode=screen:all_opacity=0.15"
        )
        
        loop_flags = ["-stream_loop", "-1", "-i", str(fondo_video)]
            
        img_flags = ["-loop", "1", "-i", str(asset_path)] if is_image else ["-i", str(asset_path)]
        
        cmd = [
            "ffmpeg", "-y", "-threads", "1"
        ] + loop_flags + img_flags + [
            "-filter_complex", filter_complex, 
            "-c:v", "libx264", "-preset", "ultrafast", "-t", str(duracion), "-pix_fmt", "yuv420p", "-r", "30", str(out_path)
        ]
    else:
        # Fallback normal si no hay fondos animados
        if asset_path.suffix.lower() in FORMATOS_IMG:
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            if es_iconica:
                vf += f",zoompan=z='zoom+0.001':d={int(duracion*30)}:s=1080x1920:fps=30"
            cmd = ["ffmpeg", "-y", "-threads", "1", "-loop", "1", "-i", str(asset_path), "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-t", str(duracion), "-pix_fmt", "yuv420p", "-r", "30", str(out_path)]
        else:
            vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            if es_ultimo_chunk:
                vf += f",trim=0:{duracion},reverse,setpts=PTS-STARTPTS"
            cmd = ["ffmpeg", "-y", "-threads", "1", "-i", str(asset_path), "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-t", str(duracion), "-pix_fmt", "yuv420p", "-r", "30", str(out_path)]
        
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"FFmpeg preprocesar_asset: {res.stderr.decode('utf-8', errors='ignore')}")
    return out_path

def ensamblar_micro_tomas(chunks: list[Path], out_name: str) -> Path:
    out_path = TRANSMUTADOS_DIR / out_name
    if len(chunks) == 1:
        import shutil
        shutil.copy2(chunks[0], out_path)
        return out_path
        
    def get_dur(p: Path) -> float:
        res = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
        return float(res.stdout.strip())
        
    duraciones = [get_dur(c) for c in chunks]
    xfade_dur = 1.5
    
    inputs = []
    for c in chunks:
        inputs.extend(["-i", str(c)])
        
    n = len(chunks)
    partes = []
    # Pad duration logic to preserve exact video length
    for i in range(n):
        pad_t = xfade_dur if i < n - 1 else 0
        pad_prev = xfade_dur if i > 0 else 0
        pad = (pad_t + pad_prev) / 2.0
        f = f"[{i}:v]fps=30,setsar=1,format=yuv420p"
        if pad > 0:
            f += f",tpad=stop_mode=clone:stop_duration={pad + 0.002:.6f}"
        partes.append(f + f"[n{i}]")
        
    label_prev = "n0"
    inicio_narrativo = 0.0
    for i in range(1, n):
        inicio_narrativo += duraciones[i - 1]
        offset = inicio_narrativo - xfade_dur / 2.0
        label_out = f"v{i:02d}"
        partes.append(f"[{label_prev}][n{i}]xfade=transition=fade:duration={xfade_dur}:offset={offset:.6f}[{label_out}]")
        label_prev = label_out
        
    filtro_full = ";".join(partes)
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filtro_full, "-map", f"[{label_prev}]", "-c:v", "libx264", "-preset", "fast", "-crf", "20", str(out_path)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return out_path

# ── Ejecución Principal ──────────────────────────────────────────────────────

def construir_entrada_corte(toma: dict, video_path: str, fuente: str = "nodriza_visual") -> dict:
    p = Path(video_path) if video_path else None
    return {
        "num_toma":          toma["num"],
        "rol":               toma.get("rol", ""),
        "inicio_ms":         toma["inicio_ms"],
        "fin_ms":            toma["fin_ms"],
        "duracion_ms":       toma["duracion_ms"],
        "duracion_s":        toma["duracion_s"],
        "texto":             toma.get("texto", ""),
        "etiqueta_visual":   toma.get("etiqueta_visual"),
        "emocion":           toma.get("emocion", "aire"),
        "transicion_entrada": toma.get("transicion_entrada", "fade"),
        "archivo_video":     str(p.resolve()) if p else None,
        "nombre_video":      p.name if p else None,
        "fuente_asignacion": fuente,
        "requiere_loop":     None,
        "accion_ffmpeg":     None,
    }

def run_nodriza():
    log("\n🧠 NODRIZA VISUAL 2.0 — Asignación Semántica", MAGENTA)
    
    timeline = cargar_timeline()
    tomas = timeline.get("tomas", [])
    
    # ── Director de Arte: enriquecer cada toma con emoción y tags ideales ──
    tomas = enriquecer_tomas(tomas)
    log("🎬 Director de Arte activado: emociones y tags visuales asignados", MAGENTA)
    for t in tomas:
        log(f"   Toma {t['num']} | {t.get('rol','?')} → emoción: {t['emocion']} | transición: {t['transicion_entrada']}", GRIS)
    
    # 1. Inventariador Universal
    assets = listar_assets(ASSETS_AUDITADOS)
    if not assets:
        err(f"No hay assets en {ASSETS_AUDITADOS}")
        sys.exit(1)
        
    info(f"Encontrados {len(assets)} assets físicos en bóveda.")
    
    # 2. Cargar Catálogo estático (solo lo ya auditado asíncronamente)
    cat = actualizar_catalogo_dummy(assets)
    if not cat:
        err("El catálogo está vacío. Debes dejar que Nodriza Autónoma procese los assets primero.")
        sys.exit(1)
    
    # 3. Asignación Scorer
    lista_de_corte = {
        "evento_id": EVENTO_ID,
        "semana": SEMANA,
        "asignaciones": []
    }
    
    ultimos_usados = []
    ultimo_elemento = None
    
    asset_gancho_path = None
    
    for toma_idx, toma in enumerate(tomas):
        duracion_toma = toma["duracion_s"]
        texto = toma.get("texto", "")
        
        es_primera_toma = (toma_idx == 0)
        es_ultima_toma = (toma_idx == len(tomas) - 1)
        
        # --- Elegir el asset principal para la toma completa primero ---
        mejor_asset_key = None
        score_para_alpha = 0.5

        # 1. Fuerza el prólogo cósmico (loop)
        terminos_gancho = ["vórtice", "tunel", "túnel", "viaje", "explosión", "agujero", "estallido"]
        assets_espacio_video = [k for k, m in cat.items() if k.endswith(".mp4") and any(term in " ".join(m.get("tags", []) + m.get("etiquetas_visuales", [])).lower() for term in terminos_gancho)]
        
        if not assets_espacio_video:
            # Fallback a espacio genérico si no hay coincidencias estrictas
            assets_espacio_video = [k for k, m in cat.items() if k.endswith(".mp4") and ("07_Espacio_Galaxias" in m.get("path_video_final", "") or "espacio" in " ".join(m.get("tags", [])).lower() or "espacio" in " ".join(m.get("etiquetas_visuales", [])).lower() or "cosmos" in " ".join(m.get("etiquetas_visuales", [])).lower())]

        if not asset_gancho_path and assets_espacio_video:
            # Ordenamos por cantidad de usos históricos (menor a mayor)
            assets_espacio_video.sort(key=lambda k: len(cat[k].get("stats_uso", [])))
            min_usos = len(cat[assets_espacio_video[0]].get("stats_uso", []))
            candidatos_gancho = [k for k in assets_espacio_video if len(cat[k].get("stats_uso", [])) == min_usos]
            asset_gancho_path = random.choice(candidatos_gancho)

        if (es_primera_toma or es_ultima_toma) and asset_gancho_path:
            mejor_asset_key = asset_gancho_path
            mejor_score = 1.0
        else:
            mejor_asset_key = elegir_mejor_asset_hibrido(toma, cat, ultimos_usados, ultimo_elemento, gemini_clients, EVENTO_ID)
            mejor_score = 1.0 if mejor_asset_key else -999.0

        if mejor_asset_key:
            score_para_alpha = max(0.0, min(1.0, mejor_score))

        chunks = []
        if mejor_asset_key:
            ganador_meta = cat[mejor_asset_key]
            is_video = mejor_asset_key.endswith(".mp4")
            
            # Cortamos dinámicamente TODAS las tomas (incluyendo gancho y CTA) para que las 
            # imágenes se fundan sobre el fondo espacial sin dejar un video monótono de 8s.
            cortes = calcular_cortes_ritmicos(texto, duracion_toma)
                
            assets_para_cortes = []
            
            # Decidimos en qué corte de esta toma meter la elección de Gemini (mejor_asset_key)
            corte_principal_idx = len(cortes) // 2 if len(cortes) > 1 else 0

            for i, c_dur in enumerate(cortes):
                es_primer_corte_absoluto = (es_primera_toma and i == 0)
                es_ultimo_corte_absoluto = (es_ultima_toma and i == len(cortes) - 1)
                
                if es_primer_corte_absoluto or es_ultimo_corte_absoluto:
                    # Obligamos a que el video comience y termine con el mismo espacio (loop)
                    elegido = asset_gancho_path
                elif i == corte_principal_idx and mejor_asset_key:
                    # Honramos la elección de Gemini insertándola en el corte principal de la toma
                    elegido = mejor_asset_key
                else:
                    # En el medio, priorizamos evitar repetición y rotar stock
                    elegido = elegir_mejor_asset_local(toma, cat, ultimos_usados + assets_para_cortes, ultimo_elemento)
                    if not elegido:
                        elegido = mejor_asset_key
                
                assets_para_cortes.append(elegido)

            info(f"Toma {toma['num']} ({duracion_toma}s) -> Dividida en {len(cortes)} cortes.")

            for i, (dur, chunk_asset_key) in enumerate(zip(cortes, assets_para_cortes)):
                chunk_meta = cat[chunk_asset_key]
                ultimos_usados.append(chunk_asset_key)
                ultimo_elemento = chunk_meta.get("elemento_visual")
                if "stats_uso" in chunk_meta:
                    chunk_meta["stats_uso"].append(EVENTO_ID)

                es_primer_corte_absoluto = (es_primera_toma and i == 0)
                es_ultimo_corte_absoluto = (es_ultima_toma and i == len(cortes) - 1)

                chunk_id = f"{toma['num']}_{i}_{uuid.uuid4().hex[:4]}"
                alpha_final = max(0.0, min(1.0, score_para_alpha + emocion_opacidad_boost(toma.get("emocion", "aire"))))
                
                es_iconica = False
                palabras_iconicas = ["tarot", "carta", "simbolo", "dios", "persona", "planeta", "arquetipo", "astrologia", "signo", "constelacion"]
                tags_str = " ".join(chunk_meta.get("etiquetas_visuales", []) + chunk_meta.get("tags", []) + [chunk_meta.get("path_original", "")]).lower()
                if any(p in tags_str for p in palabras_iconicas):
                    es_iconica = True
                
                p_chunk = preprocesar_asset_para_montaje(
                    Path(chunk_meta["path_video_final"]), dur, chunk_id,
                    es_primer_chunk=es_primer_corte_absoluto,
                    es_ultimo_chunk=es_ultimo_corte_absoluto,
                    score=alpha_final,
                    es_iconica=es_iconica
                )
                
                ok(f"Toma {toma['num']} -> Corte {i}: {p_chunk.name}")
                chunks.append(p_chunk)
            
        if chunks:
            montaje_path = ensamblar_micro_tomas(chunks, f"montaje_toma_{toma['num']}_{EVENTO_ID}.mp4")
            ok(f"Toma {toma['num']} -> Montaje dinámico creado: {montaje_path.name}")
            lista_de_corte["asignaciones"].append(construir_entrada_corte(toma, str(montaje_path)))
        else:
            err(f"Toma {toma['num']} no pudo ser asignada.")
            lista_de_corte["asignaciones"].append(construir_entrada_corte(toma, None))
            
    # Guardar catálogo actualizado (por los stats de uso)
    guardar_catalogo(cat)
    
    # Guardar output final
    ruta = TEMP_DIR / f"lista_de_corte_{EVENTO_ID}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(lista_de_corte, f, ensure_ascii=False, indent=2)
    ok(f"Lista de corte guardada: {ruta}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--opcion", type=int, default=1)
    args = parser.parse_args()
    
    if args.opcion == 1:
        run_nodriza()
    else:
        err("Opción no válida para Nodriza Visual.")
