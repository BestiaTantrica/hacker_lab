#!/usr/bin/env python3
"""
notificador.py — Módulo de notificaciones Telegram
Lee TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID desde el entorno o .env del directorio.

Uso standalone:
    python3 notificador.py "Mensaje de prueba"
Importado:
    from notificador import send_telegram
    send_telegram("Alerta: nuevo delta detectado")
"""
import os
import sys
import json
import logging
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def _cargar_dotenv():
    """Carga variables de entorno desde múltiples rutas posibles."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(script_dir, ".env"),                                         # Local: mismo dir del script
        os.path.join(script_dir, "..", "config", "entorno.env"),                  # OCI: monitores/../config/
        os.path.expanduser("~/plataforma_operativa/config/entorno.env"),          # OCI: ruta absoluta
    ]
    for ruta in candidatos:
        ruta = os.path.normpath(ruta)
        if not os.path.isfile(ruta):
            continue
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#") or "=" not in linea:
                    continue
                clave, _, valor = linea.partition("=")
                clave = clave.strip()
                valor = valor.strip().strip('"').strip("'")
                if clave and clave not in os.environ:
                    os.environ[clave] = valor
        return  # Con el primer archivo encontrado alcanza


def send_telegram(message: str) -> bool:
    """
    Envía un mensaje al chat de Telegram configurado en las variables de entorno.
    Devuelve True si fue exitoso, False si hubo cualquier error.
    No lanza excepciones (el pipeline no debe romperse por fallos de notificación).
    """
    _cargar_dotenv()

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        logging.error("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el entorno / .env")
        return False

    # Telegram permite máximo 4096 caracteres por mensaje
    if len(message) > 4096:
        message = message[:4093] + "..."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            if result.get("ok"):
                logging.info("✅ Notificación enviada a Telegram (chat_id=%s)", chat_id)
                return True
            logging.error("Telegram respondió ok=false: %s", result)
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logging.error("HTTP %s desde Telegram: %s", e.code, body)
        return False
    except Exception as e:
        logging.error("Fallo enviando a Telegram: %s", e)
        return False


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "🔔 Prueba de sistema: PEGASO operativo."
    ok = send_telegram(msg)
    sys.exit(0 if ok else 1)
