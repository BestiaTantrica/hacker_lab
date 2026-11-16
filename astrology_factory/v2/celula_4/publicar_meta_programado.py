#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import requests
from datetime import datetime

LOG_FILE = "/home/ubuntu/astrology_web/web_app/logs/meta_programado.log"

def log(msg):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    txt = f"[{now}] {msg}"
    print(txt)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(txt + "\n")

PAGE_ACCESS_TOKEN = "EAANZBBguuIgYBS7WKZAeHjW56RlMJPfcBtZAfHTozGStJFZAPBGavZCgeFVs11dFZBnuNOxKR5hlKSdfGWVyLuUey8gR7EdHvcRAMIwYoGYScPIZCf6bDyAkcmpYXyZAAsHqrtx2OLT7MnOCqAZAQbQwaQlmXvwSTL7XZBLWEg1jsyOaZCwNArs766w9hGMCzXiIkyovYA9"
IG_USER_ID = "17841475641030103"
PAGE_ID = "719363844595258"

VIDEO_URL = "https://portaltarotmistico.com/static/reels/FINAL_2026-11-07_Luna_Conjuncion_Venus_Libra.mp4"
TITLE = "7 de Noviembre | Luna conjunción Venus en Libra: El pacto soberano ⚖️✨🕊️"
CAPTION = """7 de Noviembre | Luna conjunción Venus en Libra: El pacto soberano ⚖️✨🕊️

Ayer el frío de Saturno te puso a prueba... hoy el aire se afloja ⚖️✨

Al mediodía la Luna se abraza con Venus en Libra: el deseo y la emoción vuelven a entenderse. Se arma un pacto entre iguales que no te pide agachar la cabeza 🕊️

A la tarde llega el fuego: Marte y Júpiter en Leo te sostienen desde el sextil con dignidad 🦁🔥

Contá en qué signo tenés a Venus... y descubrí en el link de mi perfil qué casa te enciende este aspecto 👇

#astrologia #lunaenlibra #venus #marte #jupiter #transitosastrologicos #autoconocimiento #desarrollopersonal #horoscopo #fyp"""

def publicar_instagram():
    log("📸 Iniciando publicación en Instagram Reels...")
    create_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "REELS",
        "video_url": VIDEO_URL,
        "caption": CAPTION,
        "share_to_feed": True,
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        r = requests.post(create_url, data=payload).json()
        if "id" not in r:
            log(f"❌ Error al crear contenedor de Instagram: {r}")
            return None
        
        container_id = r["id"]
        log(f"⏳ Contenedor creado ({container_id}). Esperando procesamiento...")
        
        status_url = f"https://graph.facebook.com/v21.0/{container_id}?fields=status_code,status&access_token={PAGE_ACCESS_TOKEN}"
        for _ in range(30):
            time.sleep(5)
            st = requests.get(status_url).json()
            code = st.get("status_code")
            log(f"   Estado Instagram: {code}")
            if code == "FINISHED":
                break
            elif code in ["ERROR", "EXPIRED"]:
                log(f"❌ Error procesando en Instagram: {st}")
                return None
        else:
            log("❌ Timeout procesando en Instagram")
            return None

        pub_url = f"https://graph.facebook.com/v21.0/{IG_USER_ID}/media_publish"
        pr = requests.post(pub_url, data={"creation_id": container_id, "access_token": PAGE_ACCESS_TOKEN}).json()
        if "id" not in pr:
            log(f"❌ Error publicando Reel en Instagram: {pr}")
            return None

        media_id = pr["id"]
        log(f"✅ ¡Reel publicado en Instagram! https://www.instagram.com/p/{media_id}/")
        return media_id
    except Exception as e:
        log(f"❌ Excepción en Instagram: {e}")
        return None

def publicar_facebook():
    log("📘 Iniciando publicación en Facebook Videos...")
    fb_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/videos"
    payload = {
        "file_url": VIDEO_URL,
        "title": TITLE,
        "description": CAPTION,
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        r = requests.post(fb_url, data=payload).json()
        if "id" not in r:
            log(f"❌ Error publicando en Facebook: {r}")
            return None
        video_id = r["id"]
        log(f"✅ ¡Video publicado en Facebook! https://www.facebook.com/watch/?v={video_id}")
        return video_id
    except Exception as e:
        log(f"❌ Excepción en Facebook: {e}")
        return None

def limpiar_cron_y_archivo():
    log("🧹 Limpiando crontab y archivo estático temporal...")
    try:
        os.system("rm -f /home/ubuntu/astrology_web/web_app/static/reels/FINAL_2026-11-07_Luna_Conjuncion_Venus_Libra.mp4")
        os.system("crontab -l | grep -v 'publicar_meta_programado.py' | crontab -")
        log("✅ Limpieza completada.")
    except Exception as e:
        log(f"⚠️ Aviso en limpieza: {e}")

if __name__ == "__main__":
    log("=== INICIO DE DISPARO PROGRAMADO META ===")
    ig = publicar_instagram()
    fb = publicar_facebook()
    log(f"Resultado final: IG={ig}, FB={fb}")
    if ig or fb:
        limpiar_cron_y_archivo()
    log("=== FIN DE DISPARO PROGRAMADO META ===")

