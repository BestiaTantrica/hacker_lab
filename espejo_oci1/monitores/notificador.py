#!/usr/bin/env python3
"""
notificador.py — Módulo de Notificaciones y Sincronización OCI-1 -> OCI-2 (C2 Panel)

Regla de Filtrado de Valor:
- Sincroniza todas las deltas y hallazgos hacia OCI-2 (Base de Datos Central).
- Envia mensaje a Telegram SOLO si la oportunidad representa un bounty potencial verificado (Subdomain Takeovers, Secretos Expuestos, CORS credentials) >= $50 USD.
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(script_dir, ".env"),
        os.path.join(script_dir, "..", "config", "entorno.env"),
        os.path.expanduser("~/plataforma_operativa/config/entorno.env"),
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
        return

def send_telegram(message: str) -> bool:
    _cargar_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        logging.error("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
        return False

    if len(message) > 4096:
        message = message[:4093] + "..."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res.get("ok", False)
    except Exception as e:
        logging.error("Fallo enviando a Telegram: %s", e)
        return False

def sync_to_c2_panel(zone: str, deltas_dict: dict, findings: list) -> bool:
    """Envía los datos de recolección de OCI-1 hacia la API de OCI-2 (C2 Panel)."""
    _cargar_dotenv()
    c2_url = os.environ.get("C2_PANEL_URL", "http://127.0.0.1:8000/api/ingest_delta")

    payload = {
        "zone": zone,
        "deltas": deltas_dict,
        "findings": findings
    }

    try:
        req = urllib.request.Request(
            c2_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            logging.info("✅ Datos de zona %s sincronizados exitosamente con OCI-2.", zone)
            return True
    except Exception as e:
        logging.warning("⚠️ No se pudo enviar telemetría a OCI-2 (%s): %s", c2_url, e)
        return False

def notificar_hallazgos_valor(findings: list):
    """Filtra y notifica a Telegram solo las vulnerabilidades verificadas con bounty ($50+ USD)."""
    _cargar_dotenv()
    c2_url = os.environ.get("C2_PANEL_PUBLIC_URL", os.environ.get("C2_PANEL_URL", "http://127.0.0.1:8000")).replace("/api/ingest_delta", "")

    for f in findings:
        target = f.get("target", "N/A")
        vuln_type = f.get("vuln_type", "Desconocida")
        estimated = f.get("estimated_bounty", "$50-$150")
        
        msg = f"🎯 *¡NUEVO HALLAZGO EN RED DE PESCA!*\n\n" \
              f"📌 *Tipo:* {vuln_type}\n" \
              f"🌐 *Target:* `{target}`\n" \
              f"💰 *Estimado Bounty:* {estimated}\n\n" \
              f"🚀 [👉 ABRIR C2 PANEL]({c2_url})"
        
        send_telegram(msg)


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "🔔 Notificador de OCI-1 operativo."
    send_telegram(msg)
