#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 CÉLULA MADRE 4 — Script 4.4: publicador_meta.py
Publicador automático para Instagram Reels y Facebook Reels vía Meta Graph API v21.0.
- Cuenta de Instagram: @portaltarotmistico
- Página de Facebook: portaltarotmistico
- Servidor OCI para hosting temporal del video: portaltarotmistico.com
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

CONFIG_PATH = Path(__file__).parent / "meta_tokens.json"
REGISTRO_PATH = FACTORY_ROOT / "produccion" / "registro_publicaciones.json"

OCI_IP = "143.47.115.34"
OCI_USER = "ubuntu"
SSH_KEY = Path("/home/LAB/llave_oci")
REMOTE_STATIC_REELS = "/home/ubuntu/astrology_web/web_app/static/reels"
PUBLIC_BASE_URL = "https://portaltarotmistico.com/static/reels"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; MAGENTA = "\033[95m"; AMARILLO = "\033[93m"
def log(msg, color=RESET): print(f"{color}{msg}{RESET}")

def cargar_config():
    if not CONFIG_PATH.exists():
        log("❌ No se encontró meta_tokens.json en celula_4", ROJO)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def subir_video_a_oci_temporal(local_video_path: Path) -> str:
    """Copia el video a la carpeta estática de OCI para que Meta lo pueda descargar."""
    log(f"📦 Subiendo video temporal a OCI (portaltarotmistico.com)...", CYAN)
    video_name = local_video_path.name
    
    # Asegurar carpeta remota
    cmd_mkdir = f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {OCI_USER}@{OCI_IP} 'mkdir -p {REMOTE_STATIC_REELS}'"
    subprocess.run(cmd_mkdir, shell=True, check=True)
    
    # Rsync video
    cmd_rsync = f"rsync -avz -e 'ssh -i {SSH_KEY} -o StrictHostKeyChecking=no' {local_video_path} {OCI_USER}@{OCI_IP}:{REMOTE_STATIC_REELS}/{video_name}"
    subprocess.run(cmd_rsync, shell=True, check=True)
    
    public_url = f"{PUBLIC_BASE_URL}/{video_name}"
    log(f"🌐 URL pública lista para Meta: {public_url}", VERDE)
    return public_url

def limpiar_video_oci_temporal(video_name: str):
    """Elimina el video temporal de OCI una vez publicado."""
    try:
        cmd_rm = f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no {OCI_USER}@{OCI_IP} 'rm -f {REMOTE_STATIC_REELS}/{video_name}'"
        subprocess.run(cmd_rm, shell=True, check=True)
        log(f"🧹 Video temporal limpiado de OCI ({video_name})", CYAN)
    except Exception as e:
        log(f"⚠️ Aviso al limpiar video temporal: {e}", AMARILLO)

def publicar_instagram_reel(cfg: dict, video_url: str, caption: str) -> str:
    """Publica un Reel en Instagram Business Account."""
    ig_id = cfg["instagram_business_account_id"]
    token = cfg["page_access_token"]
    
    log(f"\n📸 Publicando Reel en Instagram (@{cfg.get('instagram_username', 'portaltarotmistico')})...", MAGENTA)
    
    # 1. Crear contenedor de Reel
    create_url = f"https://graph.facebook.com/v21.0/{ig_id}/media"
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": True,
        "access_token": token
    }
    
    r = requests.post(create_url, data=payload)
    res = r.json()
    if "id" not in res:
        log(f"❌ Error al crear contenedor de Instagram: {res}", ROJO)
        return None
        
    container_id = res["id"]
    log(f"⏳ Contenedor creado (ID: {container_id}). Esperando que Meta procese el video...", CYAN)
    
    # 2. Polling del estado de procesamiento
    status_url = f"https://graph.facebook.com/v21.0/{container_id}?fields=status_code,status&access_token={token}"
    for attempt in range(30):
        time.sleep(5)
        st_res = requests.get(status_url).json()
        code = st_res.get("status_code")
        log(f"   Estado de procesamiento: {code} ({st_res.get('status', '')})", CYAN)
        if code == "FINISHED":
            break
        elif code in ["ERROR", "EXPIRED"]:
            log(f"❌ Error durante el procesamiento de video en Instagram: {st_res}", ROJO)
            return None
    else:
        log("❌ Timeout esperando procesamiento del video en Instagram.", ROJO)
        return None
        
    # 3. Publicar contenedor
    publish_url = f"https://graph.facebook.com/v21.0/{ig_id}/media_publish"
    pub_payload = {
        "creation_id": container_id,
        "access_token": token
    }
    pr = requests.post(publish_url, data=pub_payload)
    pub_res = pr.json()
    if "id" not in pub_res:
        log(f"❌ Error al publicar contenedor en Instagram: {pub_res}", ROJO)
        return None
        
    ig_media_id = pub_res["id"]
    log(f"✅ ¡Reel publicado en Instagram con éxito! (Media ID: {ig_media_id})", VERDE)
    return ig_media_id

def publicar_facebook_reel(cfg: dict, video_url: str, title: str, description: str) -> str:
    """Publica un Reel o Video en la Fan Page de Facebook."""
    page_id = cfg["page_id"]
    token = cfg["page_access_token"]
    
    log(f"\n📘 Publicando en Facebook Page ({cfg.get('page_name', 'portaltarotmistico')})...", MAGENTA)
    
    fb_url = f"https://graph.facebook.com/v21.0/{page_id}/videos"
    payload = {
        "file_url": video_url,
        "title": title,
        "description": description,
        "access_token": token
    }
    r = requests.post(fb_url, data=payload)
    res = r.json()
    if "id" not in res:
        log(f"❌ Error al publicar en Facebook: {res}", ROJO)
        return None
        
    fb_video_id = res["id"]
    log(f"✅ ¡Video publicado en Facebook con éxito! (Video ID: {fb_video_id})", VERDE)
    return fb_video_id

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publicador Automático de Instagram y Facebook Reels")
    parser.add_argument("--evento", help="ID del evento a publicar (ej: 2026-11-05_Luna_Ingresa_Libra)")
    parser.add_argument("--solo_instagram", action="store_true", help="Publicar solo en Instagram")
    parser.add_argument("--solo_facebook", action="store_true", help="Publicar solo en Facebook")
    args = parser.parse_args()
    
    cfg = cargar_config()
    evento_id = args.evento or ADN["produccion"]["evento_id"]
    log(f"\n🚀 PUBLICADOR META (Instagram Reels + Facebook Reels): {evento_id}", MAGENTA)
    
    # Buscar video local
    semana = ADN["produccion"].get("semana_prefijo", "Nov_W1")
    video_path = Path(ADN["assets"]["paths"]["videos_finales"]) / semana / f"FINAL_{evento_id}.mp4"
    if not video_path.exists():
        video_path = FACTORY_ROOT / "produccion" / "semana_02nov_08nov" / f"FINAL_{evento_id}.mp4"
    if not video_path.exists():
        log(f"❌ No se encontró el video final para {evento_id}", ROJO)
        sys.exit(1)
        
    # Buscar metadata
    meta_path = Path(ADN["assets"]["boveda_base"]) / "Metadata_Redes" / f"{evento_id}_metadata.json"
    if not meta_path.exists():
        meta_path = FACTORY_ROOT / "produccion" / "semana_02nov_08nov" / f"{evento_id}_metadata.json"
    if not meta_path.exists():
        log(f"❌ No se encontró la metadata para {evento_id}", ROJO)
        sys.exit(1)
        
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    titulo = meta_data.get("titulo_youtube", "Tránsito Astrológico")
    descripcion = meta_data.get("descripcion", "")
    
    # Subir video temporalmente a OCI
    public_url = subir_video_a_oci_temporal(video_path)
    
    ig_id = None
    fb_id = None
    
    try:
        # Publicar en Instagram
        if not args.solo_facebook:
            caption_ig = f"{titulo}\n\n{descripcion}"
            ig_id = publicar_instagram_reel(cfg, public_url, caption_ig)
            
        # Publicar en Facebook
        if not args.solo_instagram:
            fb_id = publicar_facebook_reel(cfg, public_url, titulo, descripcion)
            
        # Actualizar registro maestro si corresponde
        if REGISTRO_PATH.exists() and (ig_id or fb_id):
            with open(REGISTRO_PATH, "r", encoding="utf-8") as rf:
                reg = json.load(rf)
            for f_k, item in reg.get("publicaciones", {}).items():
                if item.get("evento_id") == evento_id:
                    if ig_id:
                        item["instagram_media_id"] = ig_id
                        item["instagram_url"] = f"https://www.instagram.com/p/{ig_id}/"
                        item["estado_instagram"] = "PUBLICADO"
                    if fb_id:
                        item["facebook_video_id"] = fb_id
                        item["facebook_url"] = f"https://www.facebook.com/watch/?v={fb_id}"
                        item["estado_facebook"] = "PUBLICADO"
                    break
            with open(REGISTRO_PATH, "w", encoding="utf-8") as rf:
                json.dump(reg, rf, indent=2, ensure_ascii=False)
            log("📋 Registro maestro actualizado con Instagram y Facebook.", VERDE)
            
    finally:
        # Limpiar video temporal de OCI
        limpiar_video_oci_temporal(video_path.name)
        
    log("\n🎉 ¡PROCESO DE META FINALIZADO CON ÉXITO!", VERDE)

if __name__ == "__main__":
    main()

