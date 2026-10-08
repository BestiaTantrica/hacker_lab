#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — configurador_oauth.py
Script interactivo para autenticar tu cuenta de Google localmente y guardar el token.
Esto se corre UNA SOLA VEZ a mano.
"""

import os
import sys
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes requeridos para subir videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SECRETS_FILE = FACTORY_ROOT / "v2" / "celula_4" / "client_secret.json"
TOKEN_FILE = FACTORY_ROOT / "v2" / "celula_4" / "token.json"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")

def main():
    log("\n🔑 CÉLULA 4.x — Configurador OAuth2 de YouTube", CYAN)
    
    if not SECRETS_FILE.exists():
        log(f"❌ No se encontró el archivo client_secret.json en {SECRETS_FILE}", ROJO)
        log("Por favor, créalo descargándolo desde Google Cloud Console (APIs & Services > Credentials).", ROJO)
        sys.exit(1)
        
    creds = None
    
    # Intentar cargar token existente
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            log("ℹ️ Se encontró un token.json existente. Verificando...", CYAN)
        except Exception as e:
            log(f"⚠️ El token existe pero está corrupto o desactualizado: {e}", ROJO)
            
    # Si no hay credenciales o no son válidas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log("🔄 Refrescando token expirado...", CYAN)
            creds.refresh(Request())
        else:
            log("🌐 Abriendo flujo de autenticación en el navegador...", CYAN)
            flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Guardar las credenciales para la próxima
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        log(f"✅ ¡Autenticación exitosa! Token guardado en {TOKEN_FILE}", VERDE)
    else:
        log("✅ ¡El token actual ya es válido y está listo para usarse!", VERDE)
        
if __name__ == "__main__":
    main()
