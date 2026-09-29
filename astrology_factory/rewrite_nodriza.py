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

# ── Gemini Client ────────────────────────────────────────────────────────────
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    err("No se pudo iniciar Google GenAI.")
    sys.exit(1)

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

def deducir_metadata_con_gemini(asset_path: Path) -> dict:
    """Usa Gemini para extraer 8 dimensiones emocionales a partir del nombre (y opcionalmente la imagen)."""
    info(f"Analizando semánticamente con Gemini: {asset_path.name}")
    
    prompt = f"""
Analiza este archivo de asset visual llamado '{asset_path.name}'.
Evalúa de 0.0 a 1.0 qué tanto transmite estas 8 dimensiones emocionales:
deseo_profundo, misterio, renacimiento, poder, intensidad, serenidad, caos, transformacion.

También predice la afinidad (0.0 a 1.0) con los siguientes roles narrativos de un video corto:
gancho, cta, efecto_cuerpo_emocion, mecanica_astrologica, afrontarlo_constructivamente

Clasifica el elemento visual principal ("elemento_visual") en UNO de estos: Fuego, Agua, Tierra, Aire, Espacio, Abstracto, Geometria.

Responde ESTRICTAMENTE con este formato JSON:
{{
  "elemento_visual": "Espacio",
  "mood_scores": {{
    "deseo_profundo": 0.0,
    "misterio": 0.0,
    "renacimiento": 0.0,
    "poder": 0.0,
    "intensidad": 0.0,
    "serenidad": 0.0,
    "caos": 0.0,
    "transformacion": 0.0
  }},
  "roles_narrativos": {{
    "gancho": 0.0,
    "cta": 0.0,
    "efecto_cuerpo_emocion": 0.0,
    "mecanica_astrologica": 0.0,
    "afrontarlo_constructivamente": 0.0
  }},
  "tags": ["tag1", "tag2"]
}}
Solo el JSON. Nada de bloques de markdown.
"""
    
    import time
    model_list = ['gemini-3.5-flash', 'gemini-3.5-flash-lite', 'gemini-3.1-flash-lite']
    
    for model_name in model_list:
        for i in range(3):
            try:
                if asset_path.suffix.lower() in FORMATOS_IMG:
                    # Subir archivo
                    uploaded = client.files.upload(file=str(asset_path))
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[uploaded, prompt]
                    )
                    client.files.delete(name=uploaded.name)
                else:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    
                raw = response.text.strip()
                if raw.startswith("```json"): raw = raw[7:-3].strip()
                elif raw.startswith("```"): raw = raw[3:-3].strip()
                return json.loads(raw)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    warn(f"Cuota agotada en {model_name}. Intentando alternativa... {e}")
                    time.sleep(5)
                    break # Probar con el siguiente modelo de la lista
                elif "503" in err_str:
                    warn(f"Alta demanda en {model_name}. Pausa de 10s... {e}")
                    time.sleep(10)
                else:
                    warn(f"Reintentando {model_name} ({i+1}/3)... {e}")
                    time.sleep(5)
                    
    err("Gemini falló al catalogar tras probar múltiples modelos. Retornando default.")
    return {"mood_scores": {"intensidad": 0.5}, "roles_narrativos": {}, "tags": []}

def actualizar_catalogo(assets: list[Path]) -> dict:
    cat = cargar_catalogo()
    modificado = False
    
    for a in assets:
        key = a.name
        if key not in cat:
            meta = deducir_metadata_con_gemini(a)
            # Marcar historial
            meta["stats_uso"] = []
            meta["path_original"] = str(a.resolve())
            
            # Ya no transmutamos preventivamente, se hará On-Demand por el Montajista
            meta["path_video_final"] = str(a.resolve())
                
            cat[key] = meta
            modificado = True
            time.sleep(5)  # Respetar 12 RPM de la API de Gemini (60s / 5s = 12)
            
    if modificado:
        guardar_catalogo(cat)
    return cat

# ── D. Scorer Emocional ──────────────────────────────────────────────────────

def calcular_score(toma: dict, asset_key: str, meta: dict, ultimos_usados: list[str], ultimo_elemento: str) -> float:
    score = 0.0
    
    # 1. Match con la emoción dominante del evento (ej: 'deseo_profundo')
    emocion_evento = ADN.get("arquetipos", {}).get("emocion_dominante", "")
    if emocion_evento and emocion_evento in meta.get("mood_scores", {}):
        score += 0.40 * meta["mood_scores"][emocion_evento]
        
    # 2. Match con el rol narrativo (ej: 'gancho')
    rol = toma.get("rol", "")
    if rol and rol in meta.get("roles_narrativos", {}):
        score += 0.30 * meta["roles_narrativos"][rol]
        
    # 3. Penalidad de uso histórico
    veces_usado = len(meta.get("stats_uso", []))
    score -= 0.15 * veces_usado
    
    # 4. Penalidad extrema si es idéntico al anterior
    if ultimos_usados and asset_key in ultimos_usados[-3:]:
        score -= 2.0
        
    # 5. Penalidad Temática / Variedad Visual
    elemento = meta.get("elemento_visual", "")
    if ultimo_elemento and elemento == ultimo_elemento:
        score -= 1.5 # Fuerza cambio de elemento (no más "solo fuego")
        
    return score

# ── Slicing Semántico y Montaje ──────────────────────────────────────────────

import re
import uuid

def calcular_cortes_ritmicos(texto: str, duracion_total: float) -> list[float]:
    patron = r'(,|;|\.|\s+y\s+|\s+mientras\s+|\s+donde\s+|\s+pero\s+)'
    partes_crudas = re.split(patron, texto, flags=re.IGNORECASE)
    
    frases = []
    current_frase = ""
    for p in partes_crudas:
        if re.match(patron, p, flags=re.IGNORECASE):
            current_frase += p
            frases.append(current_frase.strip())
            current_frase = ""
        else:
            current_frase += p
    if current_frase.strip():
        frases.append(current_frase.strip())
        
    frases = [f for f in frases if len(f) > 0]
    if not frases: frases = [texto]
        
    palabras_totales = max(len(texto.split()), 1)
    
    duraciones = []
    for f in frases:
        palabras_frase = max(len(f.split()), 1)
        dur_frase = (palabras_frase / palabras_totales) * duracion_total
        duraciones.append(dur_frase)
        
    cortes_finales = []
    for d in duraciones:
        while d > 2.8: # Nunca un plano mayor a 2.8s
            cortes_finales.append(2.0)
            d -= 2.0
        if d > 0.4:
            cortes_finales.append(d)
        elif cortes_finales:
            cortes_finales[-1] += d
            
    if not cortes_finales: cortes_finales = [duracion_total]
    
    suma = sum(cortes_finales)
    return [c * (duracion_total / suma) for c in cortes_finales]

def preprocesar_asset_para_montaje(asset_path: Path, duracion: float, chunk_id: str, es_primer_chunk: bool = False, es_ultimo_chunk: bool = False) -> Path:
    import random
    out_path = TEMP_DIR / f"chunk_{chunk_id}.mp4"
    
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
                blend = "overlay=format=auto:shortest=1"
            elif estilo == "mezclado":
                fg_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=rgba,colorchannelmixer=aa=0.7"
                blend = "overlay=format=auto:shortest=1"
            else:
                fg_filter = "scale=1020:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black@0"
                blend = "overlay=format=auto:shortest=1"
        else:
            # Es un video (B-Roll). Ocultamos el fondo animado si queremos, o simplemente
            # lo dejamos fullscreen (que tapa el fondo animado por debajo).
            fg_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            blend = "overlay=format=auto:shortest=1"

        if es_ultimo_chunk and not is_image:
            # Cortamos la parte del inicio del asset original y la ponemos en reversa 
            # para que enganche perfecto en un loop si TikTok vuelve a empezar.
            fg_filter += f",trim=0:{duracion},reverse,setpts=PTS-STARTPTS"
            
        fg_alpha = "format=rgba"
        
        filter_complex = f"[0:v] {bg_filter} [bg]; [1:v] {fg_filter}, {fg_alpha} [fg]; [bg][fg] {blend}"
        
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
    
    # 2. Transmutador y Catalogador
    cat = actualizar_catalogo(assets)
    
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
            
            if es_ultimo_corte_absoluto and asset_gancho_path:
                ganador_meta = {"path_video_final": str(asset_gancho_path)}
                mejor_asset_key = asset_gancho_path.name
            else:
                mejor_score = -999.0
                for key, meta in cat.items():
                    if not meta.get("path_video_final"): continue
                    score = calcular_score(toma, key, meta, ultimos_usados, ultimo_elemento)
                    
                    # Si es el primer corte, darle bonificación ENORME a videos B-Roll (explosiones)
                    # para que el gancho sea poderoso
                    if es_primer_corte_absoluto:
                        is_vid = Path(meta["path_video_final"]).suffix.lower() in FORMATOS_VIDEO
                        if is_vid: score += 100.0
                        
                    if score > mejor_score:
                        mejor_score = score
                        mejor_asset_key = key
                        
                if mejor_asset_key:
                    ganador_meta = cat[mejor_asset_key]
                    
            if mejor_asset_key:
                if es_primer_corte_absoluto:
                    asset_gancho_path = Path(ganador_meta["path_video_final"])
                    
                ultimos_usados.append(mejor_asset_key)
                ultimo_elemento = ganador_meta.get("elemento_visual")
                if "stats_uso" in ganador_meta:
                    ganador_meta["stats_uso"].append(EVENTO_ID)
                
                # Preprocesar on-demand para este corte
                chunk_id = f"{toma['num']}_{i}_{uuid.uuid4().hex[:4]}"
                p_chunk = preprocesar_asset_para_montaje(Path(ganador_meta["path_video_final"]), dur, chunk_id, es_primer_chunk=es_primer_corte_absoluto, es_ultimo_chunk=es_ultimo_corte_absoluto)
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
