#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Nodriza VIP (Auditora Automática)
Demonio que corre en segundo plano y lanza los scripts de IA (Imágenes y Videos)
para auditar los archivos desde Assets_Reusables hacia Assets_Auditados.
Respeta los límites de cuota y se ejecuta periódicamente.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# ── Entorno ────────────────────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"

SCRIPT_IMAGENES = FACTORY_ROOT / "v2" / "celula_0" / "auto_clasificador_ia.py"
SCRIPT_VIDEOS = FACTORY_ROOT / "v2" / "celula_0" / "auto_clasificador_ia_videos.py"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 👁️ VIP: {msg}", flush=True)

def cargar_adn():
    try:
        with open(ADN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log(f"Error cargando ADN: {e}")
        return None

def main_loop():
    log("Iniciando Nodriza VIP (Demonio Auditor IA)")
    
    while True:
        adn = cargar_adn()
        if not adn:
            time.sleep(60)
            continue
            
        semana_prefijo = adn.get("produccion", {}).get("semana_prefijo", "General")
        
        # Hardcodear la ruta absoluta para el entorno del usuario
        base_vault = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault")
        dir_reusables = base_vault / "Assets_Reusables"
        dir_auditados = base_vault / "Assets_Auditados"
        
        # 1. Auditar Imágenes
        dir_img = dir_reusables / "Imagenes"
        dir_img_auditados = dir_auditados / "Imagenes"
        os.makedirs(dir_img_auditados, exist_ok=True)
        
        if dir_img.exists():
            log(f"Ejecutando clasificador de Imágenes sobre {dir_img} -> {dir_img_auditados}")
            try:
                subprocess.run(
                    [sys.executable, str(SCRIPT_IMAGENES), "--directorio", str(dir_img), "--salida", str(dir_img_auditados)],
                    check=False
                )
            except Exception as e:
                log(f"Error ejecutando clasificador de imágenes: {e}")
                
        # 2. Auditar Videos
        dir_vid = dir_reusables / "Videos"
        dir_vid_auditados = dir_auditados / "Videos"
        os.makedirs(dir_vid_auditados, exist_ok=True)
        
        if dir_vid.exists():
            log(f"Ejecutando clasificador de Videos sobre {dir_vid} -> {dir_vid_auditados}")
            try:
                subprocess.run(
                    [sys.executable, str(SCRIPT_VIDEOS), "--directorio", str(dir_vid), "--salida", str(dir_vid_auditados)],
                    check=False
                )
            except Exception as e:
                log(f"Error ejecutando clasificador de videos: {e}")
                
        # Dormir 15 minutos (900 segundos) para no saturar
        log("Ciclo completado. Durmiendo 15 minutos...")
        time.sleep(900)

if __name__ == "__main__":
    main_loop()
