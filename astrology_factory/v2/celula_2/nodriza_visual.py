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
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_TEXT"),
    os.getenv("GEMINI_API_KEY_WEB"),
    os.getenv("GEMINI_API_KEY_WEB_TEXT"),
    "REMOVED_SECRET",
    "REMOVED_SECRET"
]
API_KEYS = [k for k in API_KEYS if k]

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
    # Ahora la Nodriza Visual ya no cataloga en vivo usando Visión.
    # Simplemente lee el catálogo asíncrono y devuelve lo que ya existe.
    cat = cargar_catalogo()
    
    # Inyectamos TODOS los assets físicos al catálogo en memoria
    # Extraemos etiquetas del nombre del archivo (generado por Célula 0)
    for a in assets:
        key = a.name
        if key not in cat:
            # Parse tags from filename e.g. oct_w1_fuego_accion_name.jpg
            tags = key.replace(".mp4", "").replace(".jpg", "").replace(".png", "").split("_")
            cat[key] = {
                "etiquetas_visuales": tags,
                "tags": tags
            }
        
        cat[key]["path_original"] = str(a.resolve())
        cat[key]["path_video_final"] = str(a.resolve())
    
    return cat

# ── D. Scorer Emocional y Semántico ──────────────────────────────────────────

def elegir_mejor_asset_con_gemini(toma_texto: str, rol: str, cat: dict, ultimos_usados: list) -> str:
    # Desactivamos llamadas de Gemini por cada chunk para no quemar las cuotas ("quemar apis").
    # Usaremos el motor semántico local basado en metadatos generados asíncronamente por Célula 0.
    return None

def calcular_score(toma: dict, asset_key: str, meta: dict, ultimos_usados: list[str], ultimo_elemento: str) -> float:
    # 1. Base score
    score = 0.5
    
    # 2. Penalizaciones fuertes
    # Penalizar repeticiones recientes para asegurar variedad ("usa las mismas imagenes una y otra vez")
    if ultimos_usados:
        if asset_key in ultimos_usados[-5:]: 
            score -= 5.0
        elif asset_key in ultimos_usados:
            score -= 1.0
            
    # 3. Emparejamiento por ROL
    rol = toma.get("rol", "").lower()
    tags = " ".join(meta.get("etiquetas_visuales", [])).lower()
    tags += " " + " ".join(meta.get("tags", [])).lower()
    
    # Penalizar duramente imágenes que rompen la estética ("hay imagenes de familia quie no van ni de joda en el estilo")
    for palabra_prohibida in ["familia", "bebe", "family", "baby", "niño", "niña", "hogar", "niños"]:
        if palabra_prohibida in tags:
            score -= 20.0
    
    # Asignaciones forzadas / Bonos altos
    if "cta" in rol:
        # Preferir animaciones de fondo neutras, "fractal", o cosas que sirvan de fondo para texto
        if "fractal" in tags or "abstract" in tags or "fondo" in tags:
            score += 2.0
    
    if "gancho" in rol:
        if "fuego" in tags or "espacio" in tags:
            score += 1.0
            
    # 4. Emparejamiento por Texto
    texto_toma = toma.get("texto", "").lower()
    for palabra in ["fuego", "espacio", "cosmos", "estrella", "luna", "sagitario", "quemar", "emocion", "pecho"]:
        if palabra in texto_toma and palabra in tags:
            score += 1.5
            
    # Preferencia ligera por videos sobre imagenes para mayor dinamismo
    if asset_key.endswith(".mp4"):
        score += 0.2
            
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

def preprocesar_asset_para_montaje(asset_path: Path, duracion: float, chunk_id: str, es_primer_chunk: bool = False, es_ultimo_chunk: bool = False, score: float = 0.5) -> Path:
    import random
    out_path = TEMP_DIR / f"chunk_{chunk_id}.mp4"

    # Opacidad dinámica: espejismo astrológico (0.72 etéreo → 0.88 presente)
    # A mayor afinidad semántica del asset con la toma, más sólido aparece.
    alpha = round(0.72 + 0.16 * max(0.0, min(1.0, score)), 4)
    
    fondo_dir = VAULT_BASE / "Assets_Reusables" / "Fondos_Animados"
    fondo_video = None
    if fondo_dir.exists():
        fondos = list(fondo_dir.glob("*.mp4"))
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
    list_path = TEMP_DIR / f"list_{uuid.uuid4().hex[:6]}.txt"
    with open(list_path, "w") as f:
        for c in chunks:
            f.write(f"file '{c.resolve()}'\n")
            
    out_path = TRANSMUTADOS_DIR / out_name
    cmd = ["ffmpeg", "-y", "-threads", "1", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(out_path)]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"FFmpeg ensamblar_micro_tomas: {res.stderr.decode('utf-8', errors='ignore')}")
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
    
    for toma in tomas:
        duracion_toma = toma["duracion_s"]
        texto = toma.get("texto", "")
        
        # 1. Slicing Semántico
        cortes = calcular_cortes_ritmicos(texto, duracion_toma)
        info(f"Toma {toma['num']} ({duracion_toma}s) dividida en {len(cortes)} cortes: {[round(c,2) for c in cortes]}")
        
        chunks = []
        for i, dur in enumerate(cortes):
            es_primer_corte_absoluto = (toma == tomas[0] and i == 0)
            es_ultimo_corte_absoluto = (toma == tomas[-1] and i == len(cortes) - 1)
            
            mejor_asset_key = None
            score_para_alpha = 0.5  # fallback neutral
            
            # Buscamos de manera más general cualquier video que tenga 'espacio', 'cosmos' o '07_Espacio_Galaxias'
            assets_espacio_video = [k for k, m in cat.items() if k.endswith(".mp4") and ("07_Espacio_Galaxias" in m.get("path_video_final", "") or "espacio" in " ".join(m.get("tags", [])).lower() or "espacio" in " ".join(m.get("etiquetas_visuales", [])).lower() or "cosmos" in " ".join(m.get("etiquetas_visuales", [])).lower())]
            
            if not asset_gancho_path and assets_espacio_video:
                asset_gancho_path = random.choice(assets_espacio_video)
            
            if (es_primer_corte_absoluto or es_ultimo_corte_absoluto) and asset_gancho_path:
                # Forza el prólogo y epílogo cósmico con EL MISMO video para lograr un loop
                mejor_asset_key = asset_gancho_path
                ganador_meta = cat[mejor_asset_key]
                score_para_alpha = 1.0
            else:
                mejor_asset_key = elegir_mejor_asset_con_gemini(texto, toma.get("rol", ""), cat, ultimos_usados)
                mejor_score = 1.0  # Asumimos score perfecto si Gemini lo eligió
                
                # Fallback si Gemini falla o el catálogo es chico
                if not mejor_asset_key:
                    mejor_score = -999.0
                    for key, meta in cat.items():
                        if not meta.get("path_video_final"): continue
                        score = calcular_score(toma, key, meta, ultimos_usados, ultimo_elemento)
                        if score > mejor_score:
                            mejor_score = score
                            mejor_asset_key = key

                if mejor_asset_key:
                    ganador_meta = cat[mejor_asset_key]
                    # Mapear score semántico al rango de opacidad [0, 1]
                    score_para_alpha = max(0.0, min(1.0, mejor_score))

            if mejor_asset_key:
                ultimos_usados.append(mejor_asset_key)
                ultimo_elemento = ganador_meta.get("elemento_visual")
                if "stats_uso" in ganador_meta:
                    ganador_meta["stats_uso"].append(EVENTO_ID)

                # Preprocesar on-demand para este corte
                chunk_id = f"{toma['num']}_{i}_{uuid.uuid4().hex[:4]}"
                p_chunk = preprocesar_asset_para_montaje(
                    Path(ganador_meta["path_video_final"]), dur, chunk_id,
                    es_primer_chunk=es_primer_corte_absoluto,
                    es_ultimo_chunk=es_ultimo_corte_absoluto,
                    score=score_para_alpha
                )
                chunks.append(p_chunk)
            
        if chunks:
            # Ensamblar super-clip
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
