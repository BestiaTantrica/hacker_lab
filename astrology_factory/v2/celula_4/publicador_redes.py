#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — Script 4.2: publicador_redes.py
Reemplaza al mock anterior. Sube el video y la metadata a YouTube.
SEGURIDAD: Forza privacyStatus="private".
"""

import json
import os
import sys
from pathlib import Path
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

try:
    from publicador_tiktok_api import upload_video as upload_video_tiktok
except ImportError:
    upload_video_tiktok = None

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

EVENTO_ID = ADN["produccion"]["evento_id"]
METADATA_DIR = Path(ADN["assets"]["boveda_base"]) / "Metadata_Redes"
VIDEOS_FINALES = Path(ADN["assets"]["paths"]["videos_finales"])

TOKEN_FILE = Path(__file__).parent / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; MAGENTA = "\033[95m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")

def get_youtube_client():
    if not TOKEN_FILE.exists():
        log("❌ No se encontró token.json. Ejecuta primero configurador_oauth.py", ROJO)
        sys.exit(1)
        
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        else:
            log("❌ El token es inválido o ha expirado. Ejecuta configurador_oauth.py nuevamente.", ROJO)
            sys.exit(1)
        
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def main():
    log("\n📢 CÉLULA 4.2 — Publicador YouTube (Modo Seguro)", MAGENTA)
    
    SEMANA = ADN["produccion"].get("semana_prefijo", "")
    video_dir = VIDEOS_FINALES / SEMANA if SEMANA else VIDEOS_FINALES
    video_path = video_dir / f"FINAL_{EVENTO_ID}.mp4"
    if not video_path.exists():
        # Tratar de buscar sin "FINAL_" porque el mock buscaba evento_id_FINAL.mp4
        alt_path = video_dir / f"{EVENTO_ID}_FINAL.mp4"
        if alt_path.exists():
            video_path = alt_path
        else:
            # Quizas MASTER_?
            alt_path2 = video_dir / f"MASTER_{EVENTO_ID}.mp4"
            if alt_path2.exists():
                 video_path = alt_path2
            else:
                 log(f"❌ Video final no encontrado para el evento {EVENTO_ID} en {video_dir}", ROJO)
                 sys.exit(1)
        
    metadata_path = METADATA_DIR / f"{EVENTO_ID}_metadata.json"
    if not metadata_path.exists():
        log(f"❌ Metadata no encontrada en: {metadata_path}", ROJO)
        sys.exit(1)
        
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    youtube = get_youtube_client()
    
    titulo = metadata.get('titulo_youtube', 'Tránsito Astrológico')
    descripcion = metadata.get('descripcion', '')
    
    # Agregar hashtags a la descripcion
    hashtags = " ".join(metadata.get('tags_cortos', []))
    if hashtags:
        descripcion += f"\n\n{hashtags}"
        
    tags = metadata.get('tags_largos', [])
    if len(tags) > 15:
        tags = tags[:15] # API Limit safety
        
    body = {
        "snippet": {
            "title": titulo,
            "description": descripcion,
            "tags": tags,
            "categoryId": "22" # People & Blogs
        },
        "status": {
            "privacyStatus": "private", # <--- SEGURIDAD ABSOLUTA
            "selfDeclaredMadeForKids": False
        }
    }
    
    log(f"🎬 Subiendo: {video_path.name}", CYAN)
    log("🔒 ESTADO: Privado", CYAN)
    
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    try:
        response = request.execute()
        log(f"✅ ¡Video subido a YouTube con éxito!", VERDE)
        log(f"🔗 ID del video: {response.get('id')}", VERDE)
        log(f"👁️ Podés verlo en: https://studio.youtube.com/video/{response.get('id')}/edit", CYAN)
    except googleapiclient.errors.HttpError as e:
        log(f"❌ Error de la API de YouTube: {e}", ROJO)

    # ==========================================
    # Lógica para TikTok (API Oficial V2 + Fallback)
    # ==========================================
    log("\n📢 CÉLULA 4.3 — Publicador TikTok", MAGENTA)
    
    subido_tiktok = False
    token_path = Path(__file__).parent / "tiktok_token.json"
    if token_path.exists() and upload_video_tiktok:
        log("🔑 Intentando subida por API Oficial (Sandbox)...", CYAN)
        try:
            tiktok_desc = f"{titulo}\n\n{hashtags}"
            subido_tiktok = upload_video_tiktok(str(video_path), description=tiktok_desc)
            if subido_tiktok:
                log(f"✅ ¡Video subido a TikTok con éxito (Vía API Oficial)!", VERDE)
            else:
                log(f"⚠️ Falló la subida por API. La app puede estar en Sandbox y requerir cuenta privada.", AMARILLO)
        except Exception as e:
            log(f"❌ Error al subir por API TikTok: {e}", ROJO)
    
    # Fallback a Automatización Web si la API falla o no está configurada
    if not subido_tiktok:
        log("\n🔄 Intentando subida por Automatización Web (Fallback)...", AMARILLO)
        cookies_path = Path(__file__).parent / "cookies.txt"
        if cookies_path.exists():
            try:
                from tiktok_uploader.upload import upload_video as upload_video_web
                log("🍪 Archivo cookies.txt encontrado. Iniciando subida con tiktok-uploader...", CYAN)
                tiktok_desc = f"{titulo}\n\n{hashtags}"
                upload_video_web(str(video_path), description=tiktok_desc, cookies=str(cookies_path), headless=True)
                log(f"✅ ¡Video subido a TikTok con éxito (Vía Web Automation)!", VERDE)
            except ImportError:
                log("❌ La librería tiktok-uploader no está instalada para usar el fallback.", ROJO)
            except Exception as e:
                log(f"❌ Error al subir a TikTok por Web: {e}", ROJO)
        else:
            log("⚠️ No se encontró cookies.txt. No se pudo usar el Fallback de Web Automation.", ROJO)

if __name__ == "__main__":
    main()
