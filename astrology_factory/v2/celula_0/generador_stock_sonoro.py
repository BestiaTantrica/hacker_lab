#!/usr/bin/env python3
"""
CÉLULA 0 — Generador de Stock Sonoro
Extrae recortes aleatorios de 35s-45s de los audios base (YouTube),
añade frecuencias subliminales y filtros, y los guarda en Stock_Sonoro.
"""
import os
import random
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Rutas
FACTORY_ROOT = Path(__file__).resolve().parents[2]
ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault")
AUDIOS_RAW_DIR = VAULT_BASE / "Assets_Auditados" / "Audios"
STOCK_DIR = VAULT_BASE / "Assets_Auditados" / "Stock_Sonoro"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🎵 Sonido: {msg}", flush=True)

def obtener_frecuencia_adn():
    try:
        with open(ADN_PATH, "r", encoding="utf-8") as f:
            adn = json.load(f)
            return adn.get("produccion", {}).get("frecuencia_hz", 528)
    except:
        return 528

def get_duracion_s(filepath: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)]
    try:
        salida = subprocess.check_output(cmd, text=True).strip()
        return float(salida)
    except Exception:
        return 0.0

def generar_stock():
    STOCK_DIR.mkdir(parents=True, exist_ok=True)
    if not AUDIOS_RAW_DIR.exists():
        log(f"No existe el directorio de crudos: {AUDIOS_RAW_DIR}")
        return

    crudos = list(AUDIOS_RAW_DIR.glob("*.mp3")) + list(AUDIOS_RAW_DIR.glob("*.wav"))
    if not crudos:
        log("No hay audios crudos descargados.")
        return

    hz = obtener_frecuencia_adn()
    
    # Asegurar que tengamos al menos 5 pistas de stock en total
    stock_actual = list(STOCK_DIR.glob("*.mp3"))
    if len(stock_actual) >= 10:
        log("Stock de audio suficiente (10 pistas). No se requiere generación.")
        return

    log(f"Iniciando pre-generación de stock (Frecuencia base: {hz}Hz)...")
    
    # Elegimos un archivo crudo al azar para generar un nuevo track
    crudo = random.choice(crudos)
    duracion_total = get_duracion_s(crudo)
    
    if duracion_total < 50:
        log(f"El track {crudo.name} es demasiado corto ({duracion_total}s).")
        return
        
    dur_corte = random.randint(35, 45)
    max_start = duracion_total - dur_corte - 5
    start_s = random.uniform(5, max_start)
    
    out_name = f"stock_{crudo.stem}_{int(start_s)}s_{dur_corte}s.mp3"
    out_path = STOCK_DIR / out_name
    
    if out_path.exists():
        return
        
    log(f"Creando {out_name} desde {start_s:.1f}s (Duración: {dur_corte}s)")
    
    # Filtro híbrido:
    # 1. Corta el pedazo (atrim)
    # 2. Genera las ondas binaurales de la frecuencia
    # 3. Mezcla ambas, aplica reverb, y fade in/out
    filtro = (
        f"[0:a]atrim={start_s}:{start_s+dur_corte},asetpts=PTS-STARTPTS[recorte];"
        f"aevalsrc='0.15*sin(2*PI*{hz}*t) + 0.15*sin(2*PI*{hz+3}*t)':d={dur_corte}[freq];"
        f"[recorte][freq]amix=inputs=2:duration=first[mezcla];"
        f"[mezcla]aecho=0.8:0.9:1000|1500:0.3|0.2,afade=t=in:st=0:d=4,afade=t=out:st={dur_corte-4}:d=4,volume=0.4[out]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(crudo),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", # Placeholder
        "-filter_complex", filtro,
        "-map", "[out]",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        log(f"Track de stock generado: {out_name}")
    except subprocess.CalledProcessError as e:
        log(f"Error generando stock de audio: {e.stderr.decode('utf-8', errors='ignore')}")

if __name__ == "__main__":
    generar_stock()
