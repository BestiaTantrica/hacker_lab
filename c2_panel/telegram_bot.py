#!/usr/bin/env python3
"""
telegram_bot.py — Daemon de Telegram conectado al Cerebro C2 (OCI-2)
===================================================================
1. Botón Persistente Visible "🌐 Abrir C2 Panel Web" (sin teclear comandos).
2. Memoria Unificada Compartida con la Web (chat_history en c2_db.sqlite).
3. Pegaso responde en Telegram con contexto vivo de hallazgos y conversación previa.
"""

import os
import sys
import time
import json
import sqlite3
import urllib.request
import urllib.error
from dotenv import load_dotenv

C2_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(C2_DIR)
sys.path.append(os.path.join(C2_DIR, "..", "espejo_oci1", "api"))

load_dotenv(os.path.join(C2_DIR, "..", "espejo_oci1", "config", "entorno.env"))
load_dotenv(os.path.join(C2_DIR, ".env"))

try:
    from llm_client import completar
except ImportError:
    completar = None

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
C2_PUBLIC_URL = os.environ.get("C2_PANEL_PUBLIC_URL", "http://129.80.73.248:8000")
DB_PATH = os.path.join(C2_DIR, "c2_db.sqlite")

def get_persistent_keyboard():
    """Retorna un comando para eliminar la botonera gigante inferior."""
    return {
        "remove_keyboard": True
    }

def set_telegram_menu_button():
    """Configura el botón de Menú oficial de Telegram (deshabilitado WebApp por requerir HTTPS estricto)."""
    pass

def send_telegram_with_button(chat_id: str, text: str):
    """Envía mensaje a Telegram adjuntando la botonera fija en la barra de entrada."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": get_persistent_keyboard()
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")
        return None

def process_message(user_msg: str) -> str:
    """Procesa el mensaje mediante la IA Pegaso con contexto vivo y memoria compartida."""
    if not os.path.exists(DB_PATH):
        return "⚠️ Base de datos C2 no inicializada."

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Obtener hallazgos recientes
    cursor.execute("SELECT * FROM findings ORDER BY id DESC LIMIT 5")
    recent_findings = [dict(r) for r in cursor.fetchall()]

    # 2. Obtener conversación compartida previa (Web + Telegram)
    cursor.execute("SELECT source, role, message FROM chat_history ORDER BY id DESC LIMIT 6")
    past_chat = list(reversed([dict(r) for r in cursor.fetchall()]))

    # 3. Guardar mensaje de usuario en chat_history
    cursor.execute("INSERT INTO chat_history (source, role, message) VALUES ('telegram', 'user', ?)", (user_msg,))
    conn.commit()
    conn.close()

    context_str = json.dumps(recent_findings, indent=2) if recent_findings else "Sin hallazgos recientes."
    
    past_chat_str = ""
    if past_chat:
        past_chat_str = "\nHISTORIAL DE CONVERSACIÓN RECIENTE (TELEGRAM Y WEB):\n"
        for item in past_chat:
            past_chat_str += f"[{item['source'].upper()}] {item['role']}: {item['message']}\n"

    system_prompt = f"""Eres Pegaso, el copiloto IA del C2 Panel de Bug Bounty.
Tu usuario está hablando contigo a través de Telegram.
Tu URL oficial del C2 Panel Web es: {C2_PUBLIC_URL}

HALLAZGOS VERIFICADOS RECIENTES:
{context_str}
{past_chat_str}

Pregunta del usuario en Telegram: {user_msg}

Responde de forma clara, concisa y profesional en español. Recuerda informarle que tiene disponible el botón directo para ingresar a la web."""

    if completar is None:
        respuesta = f"🤖 Recibido. Puedes acceder a tu panel web directamente aquí: {C2_PUBLIC_URL}"
    else:
        try:
            respuesta = completar(system_prompt, max_tokens=1024)
        except Exception as e:
            respuesta = f"⚠️ Pegaso AI: Ocurrió un error al procesar tu consulta ({e}). Entra a la web: {C2_PUBLIC_URL}"

    # 4. Guardar respuesta del asistente en chat_history
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (source, role, message) VALUES ('telegram', 'assistant', ?)", (respuesta,))
    conn.commit()
    conn.close()

    return respuesta

def send_telegram_with_inline_url(chat_id: str, text: str):
    """Envía un mensaje a Telegram con un Botón Inline con enlace URL directo que abre el navegador."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🚀 HACER CLIC AQUÍ PARA ENTRAR A LA WEB", "url": C2_PUBLIC_URL}]
            ]
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")
        return None

def poll_updates():
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado en entorno.env")
        return

    print("🤖 Servidor de Telegram Bot iniciando con memoria compartida C2...")
    print(f"🔗 URL C2 Web configurada: {C2_PUBLIC_URL}")

    set_telegram_menu_button()

    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "").strip()
                    chat_id = str(msg.get("chat", {}).get("id", ""))

                    if text and chat_id:
                        print(f"📩 Mensaje recibido de Telegram [{chat_id}]: {text}")
                        
                        # Si el usuario presiona el botón o envía comandos de navegación web, NINGUNA IA responde.
                        # Se envía directamente el enlace URL clicable que abre el navegador.
                        if "ABRIR C2 PANEL WEB" in text.upper() or text.lower() in ["/start", "/web", "/panel", "web", "panel"]:
                            send_telegram_with_inline_url(
                                chat_id, 
                                f"🌐 *Acceso Directo a tu C2 Panel Web*\n\nHaz clic en el botón de abajo para abrir el panel en tu navegador:\n{C2_PUBLIC_URL}"
                            )
                        else:
                            # Para cualquier otra conversación, procesa con IA y adjunta el botón de acceso directo
                            respuesta = process_message(text)
                            send_telegram_with_inline_url(chat_id, respuesta)

        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    poll_updates()
