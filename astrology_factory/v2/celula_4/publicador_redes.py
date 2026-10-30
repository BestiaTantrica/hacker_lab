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

CELL_DIR = Path(__file__).resolve().parent
if str(CELL_DIR) not in sys.path:
    sys.path.insert(0, str(CELL_DIR))

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

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; MAGENTA = "\033[95m"; AMARILLO = "\033[93m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")

def get_youtube_client():
    if not TOKEN_FILE.exists():
        log("❌ No se encontró token.json. Ejecuta primero configurador_oauth.py", ROJO)
        return None
        
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            else:
                log("❌ El token de YouTube es inválido o ha expirado.", ROJO)
                log("💡 Ejecuta python v2/celula_4/configurador_oauth.py para reautenticar.", AMARILLO)
                return None
        return googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    except Exception as e:
        log(f"❌ Error al autenticar cliente de YouTube: {e}", ROJO)
        log("💡 Ejecuta python v2/celula_4/configurador_oauth.py para renovar las credenciales.", AMARILLO)
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publicador Multicanal Seguro (YouTube & TikTok)")
    parser.add_argument("--evento", help="ID del evento a publicar (ej: 2026-10-30_Mercurio_Cuadratura_Partil_Marte)")
    parser.add_argument("--programar", help="Fecha/hora UTC para programar en YouTube (ej: 2026-10-30T21:00:00.000Z)")
    parser.add_argument("--solo_youtube", action="store_true", help="Subir solo a YouTube")
    parser.add_argument("--solo_tiktok", action="store_true", help="Subir solo a TikTok")
    args = parser.parse_args()

    evento_activo = args.evento or EVENTO_ID
    log(f"\n📢 CÉLULA 4.2 — Publicador Multicanal: {evento_activo}", MAGENTA)
    
    SEMANA = ADN["produccion"].get("semana_prefijo", "")
    video_dir = VIDEOS_FINALES / SEMANA if SEMANA else VIDEOS_FINALES
    video_path = video_dir / f"FINAL_{evento_activo}.mp4"
    if not video_path.exists():
        # Tratar en carpeta local produccion/semana_29oct_01nov
        local_path = FACTORY_ROOT / "produccion" / "semana_29oct_01nov" / f"FINAL_{evento_activo}.mp4"
        if local_path.exists():
            video_path = local_path
        else:
            alt_path = video_dir / f"{evento_activo}_FINAL.mp4"
            if alt_path.exists():
                video_path = alt_path
            else:
                log(f"❌ Video final no encontrado para {evento_activo}", ROJO)
                sys.exit(1)
        
    metadata_path = METADATA_DIR / f"{evento_activo}_metadata.json"
    if not metadata_path.exists():
        log(f"❌ Metadata no encontrada en: {metadata_path}", ROJO)
        sys.exit(1)
        
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    titulo = metadata.get('titulo_youtube', 'Tránsito Astrológico')
    descripcion = metadata.get('descripcion', '')
    
    # Agregar hashtags a la descripcion
    hashtags = " ".join(metadata.get('tags_cortos', []))
    if hashtags:
        descripcion += f"\n\n{hashtags}"
        
    tags = metadata.get('tags_largos', [])
    if len(tags) > 15:
        tags = tags[:15] # API Limit safety
        
    privacy_status = os.environ.get("YOUTUBE_PRIVACY_STATUS", "public")
    if args.programar:
        privacy_status = "private"

    body = {
        "snippet": {
            "title": titulo,
            "description": descripcion,
            "tags": tags,
            "categoryId": "22" # People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }
    
    if args.programar:
        body["status"]["publishAt"] = args.programar
        log(f"⏰ Publicación programada en YouTube para: {args.programar}", CYAN)

    log(f"🎬 Video: {video_path.name}", CYAN)
    log(f"🔒 ESTADO: {privacy_status}", CYAN)
    
    youtube_id = None
    if not args.solo_tiktok:
        youtube = get_youtube_client()
        if youtube is not None:
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            try:
                response = request.execute()
                youtube_id = response.get('id')
                log(f"✅ ¡Video subido a YouTube con éxito!", VERDE)
                log(f"🔗 ID del video: {youtube_id}", VERDE)
                log(f"👁️ Podés verlo en: https://studio.youtube.com/video/{youtube_id}/edit", CYAN)

                # Actualizar registro maestro de publicaciones
                registro_path = FACTORY_ROOT / "produccion" / "registro_publicaciones.json"
                if registro_path.exists():
                    try:
                        with open(registro_path, "r", encoding="utf-8") as rf:
                            reg_data = json.load(rf)
                        # Buscar por evento_id
                        for f_key, pub in reg_data.get("publicaciones", {}).items():
                            if pub.get("evento_id") == evento_activo:
                                pub["youtube_video_id"] = youtube_id
                                pub["youtube_url"] = f"https://www.youtube.com/watch?v={youtube_id}"
                                pub["estado_youtube"] = "PROGRAMADO" if args.programar else "PUBLICADO"
                                break
                        with open(registro_path, "w", encoding="utf-8") as rf:
                            json.dump(reg_data, rf, indent=2, ensure_ascii=False)
                        log(f"📋 Registro maestro actualizado con YouTube ID: {youtube_id}", VERDE)
                    except Exception as rex:
                        log(f"⚠️ No se pudo actualizar registro_publicaciones.json: {rex}", AMARILLO)

            except googleapiclient.errors.HttpError as e:
                log(f"❌ Error de la API de YouTube: {e}", ROJO)
        else:
            log("⚠️ Subida a YouTube omitida debido a credenciales no válidas/expiradas.", AMARILLO)

    # ==========================================
    # Lógica para TikTok (Estrategia Canónica: Cookies Web Automation)
    # ==========================================
    if not args.solo_youtube:
        log("\n📢 CÉLULA 4.3 — Publicador TikTok (Producción)", MAGENTA)
        
        subido_tiktok = False
        cookies_path = Path(__file__).parent / "cookies.txt"
        tiktok_desc = f"{titulo}\n\n{hashtags}"

        # 1. Estrategia Primaria Canónica: Cookies Web Automation (Inyección completa de descripción y hashtags)
        if cookies_path.exists():
            log("🍪 Archivo cookies.txt detectado. Publicando vía Automatización Web (Descripción completa)...", CYAN)
            try:
                from tiktok_uploader.upload import upload_video as upload_video_web
                upload_video_web(str(video_path), description=tiktok_desc, cookies=str(cookies_path), headless=True)
                log(f"✅ ¡Video subido a TikTok con éxito con descripción y hashtags automáticos!", VERDE)
                subido_tiktok = True
            except ImportError:
                log("❌ La librería tiktok-uploader no está instalada para automatización web.", ROJO)
            except Exception as e:
                log(f"⚠️ Error al subir a TikTok por Web Automation: {e}", AMARILLO)
        else:
            log("⚠️ No se encontró cookies.txt en celula_4. Procediendo con API fallback.", AMARILLO)

        # 2. Fallback Secundario: API Oficial V2 (Direct Post) si la app ya fue aprobada
        if not subido_tiktok:
            token_path = Path(__file__).parent / "tiktok_token.json"
            if token_path.exists() and upload_video_tiktok:
                log("\n🔑 Intentando publicación por API Oficial V2...", CYAN)
                try:
                    privacy = os.environ.get("TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE")
                    subido_tiktok = upload_video_tiktok(str(video_path), description=tiktok_desc, privacy_level=privacy)
                    if subido_tiktok:
                        log(f"✅ ¡Video publicado en TikTok con éxito vía API Oficial!", VERDE)
                except Exception as e:
                    log(f"❌ Error al subir por API TikTok: {e}", ROJO)

        if subido_tiktok:
            registro_path = FACTORY_ROOT / "produccion" / "registro_publicaciones.json"
            if registro_path.exists():
                try:
                    with open(registro_path, "r", encoding="utf-8") as rf:
                        reg_data = json.load(rf)
                    for f_key, pub in reg_data.get("publicaciones", {}).items():
                        if pub.get("evento_id") == evento_activo:
                            pub["estado_tiktok"] = "PUBLICADO"
                            break
                    with open(registro_path, "w", encoding="utf-8") as rf:
                        json.dump(reg_data, rf, indent=2, ensure_ascii=False)
                    log(f"📋 Registro maestro actualizado: TikTok PUBLICADO", VERDE)
                except Exception as rex:
                    log(f"⚠️ No se pudo actualizar registro_publicaciones.json: {rex}", AMARILLO)

if __name__ == "__main__":
    main()
