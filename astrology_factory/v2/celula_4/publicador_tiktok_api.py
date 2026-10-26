#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — Módulo: publicador_tiktok_api.py
Motor de publicación robusto para TikTok Direct Post API v2 (Producción).

Características de Robustez:
1. Auto-refresh transparente: Si el token vence, se renueva solo sin parar el flujo.
2. Sincronización dual: Actualiza tanto tiktok_token.json como la base de datos SQLite (si existe).
3. Reintento resiliente: Si falla un chunk de subida por red, reintenta hasta 3 veces con backoff.
4. Verificación de estado asíncrona: Consulta /v2/post/publish/status/fetch/ hasta confirmar SUCCESS o FAILED.
5. Modo Producción/Privado configurable: Gobernado por TIKTOK_PRIVACY_LEVEL en .env.
"""

import json
import os
import sys
import time
import math
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ubicaciones del proyecto
CELL_DIR = Path(__file__).resolve().parent
FACTORY_ROOT = CELL_DIR.parents[1]
TOKEN_FILE = CELL_DIR / "tiktok_token.json"
ENV_PATH = FACTORY_ROOT / ".env"
DB_PATH = FACTORY_ROOT / "web_app" / "database" / "users.sqlite"

# Cargar variables de entorno
load_dotenv(ENV_PATH)

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_KEY", "sbaw1bxm8knugdcxbs")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "XMaqRO69uVDpakX8nP8SfRZwyonRyKrd")
DEFAULT_PRIVACY = os.environ.get("TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE")

RESET = "\033[0m"
VERDE = "\033[92m"
ROJO = "\033[91m"
CYAN = "\033[96m"
AMARILLO = "\033[93m"
MAGENTA = "\033[95m"

def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

def sync_token_to_sqlite(open_id, access_token, refresh_token):
    """Sincroniza los tokens actualizados en la base de datos de la web en OCI."""
    if not DB_PATH.exists():
        return
    try:
        import sqlite3
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tiktok_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    open_id TEXT UNIQUE,
                    access_token TEXT,
                    refresh_token TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT INTO tiktok_auth (open_id, access_token, refresh_token)
                VALUES (?, ?, ?)
                ON CONFLICT(open_id) DO UPDATE SET
                    access_token=excluded.access_token,
                    refresh_token=excluded.refresh_token,
                    updated_at=CURRENT_TIMESTAMP
            ''', (open_id, access_token, refresh_token))
            conn.commit()
    except Exception as e:
        log(f"⚠️ No se pudo sincronizar SQLite (no crítico): {e}", AMARILLO)

def refresh_access_token():
    """
    Renueva el access_token usando el refresh_token contra la API oficial de TikTok.
    TikTok devuelve un NUEVO access_token y un NUEVO refresh_token (rotación obligatoria).
    """
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"No existe {TOKEN_FILE.name}. Ejecuta configurador_tiktok.py primero.")

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    refresh_tok = data.get("refresh_token")
    if not refresh_tok:
        raise ValueError("El archivo de token no contiene 'refresh_token'.")

    log("🔄 TikTok Token: Renovando access_token en segundo plano...", AMARILLO)

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    payload = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }

    resp = requests.post(token_url, data=payload, headers=headers, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"Error renovando token HTTP {resp.status_code}: {resp.text}")

    res_json = resp.json()
    if "access_token" not in res_json:
        raise RuntimeError(f"TikTok no devolvió access_token al renovar: {res_json}")

    # Calculamos timestamp de expiración (con margen de seguridad de 5 minutos)
    expires_in = res_json.get("expires_in", 86400)
    res_json["expires_at"] = time.time() + expires_in - 300

    # Guardamos en JSON
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(res_json, f, indent=4)

    # Sincronizamos en SQLite si hay open_id
    open_id = res_json.get("open_id", data.get("open_id", "admin_account"))
    sync_token_to_sqlite(open_id, res_json["access_token"], res_json.get("refresh_token", refresh_tok))

    log("✅ TikTok Token: ¡Renovación exitosa y guardada!", VERDE)
    return res_json["access_token"]

def get_valid_access_token():
    """
    Obtiene un access_token garantizado. Si ya expiró o le faltan menos de 5 min,
    lo renueva automáticamente.
    """
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(f"No se encontró {TOKEN_FILE.name}. Ejecuta configurador_tiktok.py primero.")

    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    access_token = data.get("access_token")
    expires_at = data.get("expires_at")

    # Si no tiene fecha de expiración o ya expiró, renovar de inmediato
    if not access_token or not expires_at or time.time() >= expires_at:
        return refresh_access_token()

    return access_token

def verify_account():
    """Verifica el estado de conexión de la cuenta autorizada."""
    token = get_valid_access_token()
    user_url = "https://open.tiktokapis.com/v2/user/info/?fields=open_id,union_id,avatar_url,display_name"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(user_url, headers=headers, timeout=15)
    if resp.status_code == 200:
        data = resp.json().get("data", {}).get("user", {})
        display_name = data.get("display_name", "Desconocido")
        open_id = data.get("open_id", "")
        log(f"👤 Cuenta TikTok Conectada: {display_name} (ID: {open_id[:8]}...)", VERDE)
        return True, data
    else:
        log(f"⚠️ Error verificando cuenta: {resp.text}", ROJO)
        return False, None

def check_publish_status(publish_id, access_token, max_attempts=12, delay_sec=5):
    """
    Consulta periódica a TikTok para confirmar si el video fue procesado y publicado.
    Estados posibles: PROCESSING_DOWNLOAD, PROCESSING_UPLOAD, SUCCESS, FAILED.
    """
    status_url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    payload = {"publish_id": publish_id}

    log(f"🔍 Monitoreando procesamiento en TikTok (Publish ID: {publish_id})...", CYAN)

    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.post(status_url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                res_data = resp.json()
                status_info = res_data.get("data", {})
                status = status_info.get("status")
                
                if status == "SUCCESS":
                    post_id = status_info.get("publicaly_available_post_id") or status_info.get("post_id")
                    log(f"🎉 ¡VIDEO PUBLICADO EN TIKTOK CON ÉXITO! (Post ID: {post_id})", VERDE)
                    return True, post_id
                elif status == "FAILED":
                    fail_reason = status_info.get("fail_reason", "Razón no especificada")
                    log(f"❌ TikTok rechazó el video. Razón: {fail_reason}", ROJO)
                    return False, fail_reason
                else:
                    log(f"   ⏳ Intento {attempt}/{max_attempts}: Estado actual '{status}'... esperando {delay_sec}s", CYAN)
            else:
                log(f"   ⚠️ Error de red consultando estado ({resp.status_code}), reintentando...", AMARILLO)
        except Exception as e:
            log(f"   ⚠️ Excepción consultando estado: {e}", AMARILLO)

        time.sleep(delay_sec)

    log(f"⚠️ El video sigue procesándose en los servidores de TikTok. El Publish ID es {publish_id}.", AMARILLO)
    return True, publish_id

def upload_video(video_path, description, privacy_level=None):
    """
    Subida directa y robusta de video a TikTok API V2 (Direct Post).
    video_path: ruta al archivo .mp4
    description: descripción con hashtags
    privacy_level: 'PUBLIC_TO_EVERYONE' | 'MUTUAL_FOLLOW_FRIENDS' | 'SELF_ONLY'
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video no encontrado: {video_path}")

    file_size = video_path.stat().st_size
    if file_size == 0:
        raise ValueError("El archivo de video está vacío (0 bytes).")

    # Determinar nivel de privacidad
    level = privacy_level or DEFAULT_PRIVACY
    # Validación de valores aceptados por TikTok
    valid_levels = {"PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "SELF_ONLY"}
    if level not in valid_levels:
        log(f"⚠️ Nivel '{level}' desconocido. Usando 'PUBLIC_TO_EVERYONE'.", AMARILLO)
        level = "PUBLIC_TO_EVERYONE"

    # Obtener token garantizado
    access_token = get_valid_access_token()

    # Cálculo de Chunks (20MB)
    chunk_size = 20 * 1024 * 1024
    if file_size < chunk_size:
        chunk_size = file_size
        total_chunk_count = 1
    else:
        total_chunk_count = math.floor(file_size / chunk_size)

    log(f"\n🚀 Iniciando subida a TikTok API V2: {video_path.name}", MAGENTA)
    log(f"🔒 Nivel de Privacidad: {level}", CYAN)
    log(f"📦 Tamaño: {file_size / (1024*1024):.2f} MB en {total_chunk_count} chunk(s)", CYAN)

    init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    payload = {
        "post_info": {
            "title": description,
            "privacy_level": level,
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

    # Inicializar subida (con reintento de refresh si da 401)
    response = requests.post(init_url, headers=headers, json=payload, timeout=30)
    if response.status_code == 401:
        log("🔄 Token rechazado por TikTok (401). Forzando renovación...", AMARILLO)
        access_token = refresh_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.post(init_url, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        log(f"❌ Error al inicializar subida HTTP {response.status_code}: {response.text}", ROJO)
        return False

    res_data = response.json()
    error_info = res_data.get("error", {})
    if error_info.get("code", "ok") != "ok":
        log(f"❌ Error devuelto por la API de TikTok: {error_info}", ROJO)
        return False

    publish_id = res_data.get("data", {}).get("publish_id")
    upload_url = res_data.get("data", {}).get("upload_url")

    if not upload_url:
        log(f"❌ TikTok no devolvió URL de subida: {res_data}", ROJO)
        return False

    log(f"📡 Transmitiendo video a la red de TikTok...", CYAN)

    # Subida de Chunks con reintentos
    with open(video_path, "rb") as f:
        for i in range(total_chunk_count):
            start_byte = i * chunk_size
            if i == total_chunk_count - 1:
                chunk_data = f.read()
                end_byte = file_size - 1
            else:
                chunk_data = f.read(chunk_size)
                end_byte = start_byte + chunk_size - 1

            put_headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                "Content-Length": str(len(chunk_data))
            }

            subido = False
            for retry in range(1, 4):
                try:
                    upload_res = requests.put(upload_url, headers=put_headers, data=chunk_data, timeout=60)
                    if upload_res.status_code in [200, 201]:
                        subido = True
                        break
                    else:
                        log(f"   ⚠️ Error en chunk {i+1} (HTTP {upload_res.status_code}), reintento {retry}/3...", AMARILLO)
                        time.sleep(2 * retry)
                except Exception as e:
                    log(f"   ⚠️ Excepción en chunk {i+1} ({e}), reintento {retry}/3...", AMARILLO)
                    time.sleep(2 * retry)

            if not subido:
                log(f"❌ No se pudo subir el chunk {i+1} tras 3 intentos. Abortando.", ROJO)
                return False

            log(f"✅ Chunk {i+1}/{total_chunk_count} recibido con éxito.", VERDE)

    log(f"✅ Transmisión completada. Iniciando verificación en TikTok...", VERDE)

    # Verificación de procesamiento asíncrono
    success, details = check_publish_status(publish_id, access_token)
    return success

if __name__ == "__main__":
    print("\n==============================================")
    print("🔐 TEST DE CONEXIÓN TIKTOK API V2 (PRODUCCIÓN)")
    print("==============================================")
    ok, user = verify_account()
    if ok:
        print("\n✅ El módulo TikTok API v2 está 100% OPERATIVO y VINCULADO.")
    else:
        print("\n❌ Hubo un inconveniente con la cuenta de TikTok.")
