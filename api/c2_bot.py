#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
c2_bot.py — Pegaso AI Telegram Bot Interactivo
==============================================
Bot de Telegram bidireccional que integra Groq/Gemini y permite ejecutar
comandos de bash o automatizaciones directamente desde el chat.
Utiliza Long Polling con urllib puro (cero dependencias externas).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import subprocess
import traceback

# Importar cliente LLM y cargador de entorno
from llm_client import completar, _cargar_dotenv

_cargar_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
AUTHORIZED_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

if not TOKEN or not AUTHORIZED_CHAT_ID:
    print("❌ Error: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados.")
    sys.exit(1)

URL_BASE = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    """Envía un mensaje a Telegram."""
    if len(text) > 4096:
        text = text[:4090] + "\n..."
    url = f"{URL_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")


def execute_bash(command):
    """Ejecuta un comando en la terminal local y devuelve la salida."""
    try:
        result = subprocess.run(
            command, shell=True, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60
        )
        return result.stdout if result.stdout else "Comando ejecutado sin salida."
    except subprocess.TimeoutExpired:
        return "⏳ Error: El comando excedió el tiempo máximo de ejecución."
    except Exception as e:
        return f"Error ejecutando comando: {e}"


def handle_message(text, chat_id):
    """Procesa el mensaje recibido."""
    print(f"\n[💬] Recibido de {chat_id}: {text}")
    
    # Comandos fijos (Hardcoded)
    if text.startswith("/ping"):
        send_message(chat_id, "🏓 Pong! Pegaso operativo y a la escucha.")
        return

    if text.startswith("/bash "):
        comando = text.replace("/bash ", "").strip()
        send_message(chat_id, f"⚙️ Ejecutando: `{comando}`")
        salida = execute_bash(comando)
        send_message(chat_id, f"🖥️ **Salida:**\n```bash\n{salida[-4000:]}\n```")
        return

    # Si no es un comando fijo, pasarlo a la IA (Pegaso)
    send_message(chat_id, "🧠 Procesando...")
    
    system_prompt = f"""Eres Pegaso, el asistente IA de Ciberseguridad integrado en Telegram.
El usuario es Tomas244, tu creador. Tu misión es ayudar en tareas de Bug Bounty.
Puedes sugerirle que use el comando /bash <comando> si necesita ejecutar algo en el servidor,
o puedes simplemente responder preguntas y analizar código.
Mensaje del usuario: {text}"""

    try:
        respuesta = completar(system_prompt, max_tokens=1024)
        send_message(chat_id, respuesta)
    except Exception as e:
        err_msg = traceback.format_exc()
        print(f"[!] Error de IA: {err_msg}")
        send_message(chat_id, f"⚠️ Error en la cascada de IA: {e}")


def main():
    print(f"🚀 Iniciando Pegaso Bot...")
    print(f"🔒 Chat ID autorizado: {AUTHORIZED_CHAT_ID}")
    
    offset = 0
    while True:
        try:
            url = f"{URL_BASE}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url, method="GET")
            
            with urllib.request.urlopen(req, timeout=40) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        texto = update["message"]["text"]
                        
                        # Seguridad: solo responder al dueño
                        if chat_id == AUTHORIZED_CHAT_ID:
                            handle_message(texto, chat_id)
                        else:
                            print(f"[!] Acceso denegado al chat_id: {chat_id}")
                            
        except urllib.error.URLError:
            # Errores de red ignorados (timeout de polling)
            pass
        except Exception as e:
            print(f"[!] Error crítico en el loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
