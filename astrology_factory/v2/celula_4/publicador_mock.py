#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — Script 4.2: publicador_mock.py
Empaqueta el video final y la metadata en una carpeta de publicación lista para subir.
En el futuro, esto se conectará a las APIs de YouTube Data V3 y TikTok.
"""

import json
import os
import sys
import shutil
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID = ADN["produccion"]["evento_id"]
METADATA_DIR = Path(ADN["assets"]["boveda_base"]) / "Metadata_Redes"
VIDEOS_FINALES = Path(ADN["assets"]["paths"]["videos_finales"])
LISTOS_PARA_SUBIR = Path(ADN["assets"]["boveda_base"]) / "Listos_Para_Subir"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; MAGENTA = "\033[95m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def main():
    log("\n📢 CÉLULA 4.2 — Empaquetador / Publicador Mock", MAGENTA)
    
    video_path = VIDEOS_FINALES / f"{EVENTO_ID}_FINAL.mp4"
    metadata_path = METADATA_DIR / f"{EVENTO_ID}_metadata.json"
    
    if not video_path.exists():
        log(f"❌ Video final no encontrado en: {video_path}", ROJO)
        log("Espera a que termine la Célula 3 (Ensamblador Final).", ROJO)
        sys.exit(1)
        
    if not metadata_path.exists():
        log(f"❌ Metadata no encontrada en: {metadata_path}", ROJO)
        log("Ejecuta primero el Script 4.1 (generador_metadata.py).", ROJO)
        sys.exit(1)
        
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    # Crear carpeta de entrega
    carpeta_entrega = LISTOS_PARA_SUBIR / EVENTO_ID
    asegurar_dir(carpeta_entrega)
    
    # Mover una copia del video
    video_entrega = carpeta_entrega / video_path.name
    shutil.copy2(video_path, video_entrega)
    
    # Generar el TXT para el Community Manager
    txt_entrega = carpeta_entrega / "Copiar_Y_Pegar_Redes.txt"
    
    contenido_txt = f"""=== METADATA OPTIMIZADA PARA YOUTUBE / TIKTOK ===
VIDEO: {video_entrega.name}

--- TÍTULO ---
{metadata.get('titulo_youtube', '')}

--- DESCRIPCIÓN ---
{metadata.get('descripcion', '')}

--- HASHTAGS (TikTok / Reels) ---
{' '.join(metadata.get('tags_cortos', []))}

--- ETIQUETAS SEO (YouTube Tags) ---
{', '.join(metadata.get('tags_largos', []))}
===================================================
(En futuras iteraciones, este paquete se subirá vía API automáticamente).
"""

    with open(txt_entrega, "w", encoding="utf-8") as f:
        f.write(contenido_txt)
        
    log(f"✅ ¡EMPAQUETADO EXITOSO!", VERDE)
    log(f"Todo listo para publicar en: {carpeta_entrega}", CYAN)
    print(contenido_txt)

if __name__ == "__main__":
    main()
