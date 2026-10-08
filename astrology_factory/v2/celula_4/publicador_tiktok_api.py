#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — Módulo: publicador_tiktok_api.py
Se encarga de publicar videos en TikTok utilizando la API oficial V2.
"""

import json
import os
import time
import requests
from pathlib import Path

# Buscamos el token en el mismo directorio
TOKEN_FILE = Path(__file__).parent / "tiktok_token.json"
RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"

def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

def get_access_token():
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("No se encontró tiktok_token.json. Ejecuta configurador_tiktok.py primero.")
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # TODO: Implementar lógica de refresh_token si el access_token expiró.
    return data.get("access_token")

def upload_video(video_path, description):
    """
    Subida directa de video a TikTok API V2
    video_path: ruta absoluta al archivo .mp4
    description: texto descriptivo y hashtags
    """
    access_token = get_access_token()
    if not access_token:
        raise ValueError("El token de acceso está vacío.")
        
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video no encontrado: {video_path}")
        
    file_size = video_path.stat().st_size
    
    import math
    # Chunk size rules: must be between 5MB and 64MB. Final chunk can be up to 128MB.
    # We will use 20MB chunks.
    chunk_size = 20 * 1024 * 1024 
    if file_size < chunk_size:
        chunk_size = file_size
        total_chunk_count = 1
    else:
        # TikTok requires math.floor for total_chunk_count calculation!
        total_chunk_count = math.floor(file_size / chunk_size)
        
    # 1. Inicializar subida
    log(f"🚀 Iniciando subida a TikTok API V2: {video_path.name}", CYAN)
    
    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    payload = {
        "post_info": {
            "title": description,
            "privacy_level": "SELF_ONLY", # Modo Seguro (Privado)
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count
        }
    }
    
    response = requests.post(init_url, headers=headers, json=payload)
    if response.status_code != 200:
        log(f"❌ Error al inicializar subida: {response.text}", ROJO)
        return False
        
    res_data = response.json()
    error_info = res_data.get("error", {})
    if error_info.get("code", "ok") != "ok":
        log(f"❌ Error de API: {error_info}", ROJO)
        return False
        
    publish_id = res_data.get("data", {}).get("publish_id")
    upload_url = res_data.get("data", {}).get("upload_url")
    
    if not upload_url:
        log(f"❌ No se recibió URL de subida: {res_data}", ROJO)
        return False
        
    log(f"📡 Subiendo el video a TikTok en {total_chunk_count} partes...", CYAN)
    
    # 2. Subir el archivo en chunks
    with open(video_path, "rb") as f:
        for i in range(total_chunk_count):
            start_byte = i * chunk_size
            # If it's the last chunk, it reads the remainder of the file
            if i == total_chunk_count - 1:
                chunk_data = f.read() # Reads everything left
                end_byte = file_size - 1
            else:
                chunk_data = f.read(chunk_size)
                end_byte = start_byte + chunk_size - 1
                
            put_headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                "Content-Length": str(len(chunk_data))
            }
            
            upload_res = requests.put(upload_url, headers=put_headers, data=chunk_data)
            
            if upload_res.status_code not in [200, 201]:
                log(f"❌ Error al subir chunk {i+1}: {upload_res.status_code} {upload_res.text}", ROJO)
                return False
                
            log(f"✅ Chunk {i+1}/{total_chunk_count} subido ({start_byte}-{end_byte}).", VERDE)
            
    log(f"✅ ¡Video completamente subido a TikTok (Publish ID: {publish_id})!", VERDE)
    return True

if __name__ == "__main__":
    print("Módulo de la API oficial de TikTok cargado correctamente.")
