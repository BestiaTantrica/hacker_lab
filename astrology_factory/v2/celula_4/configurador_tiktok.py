#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — Script: configurador_tiktok.py
(Manejo de OAuth para la API Oficial de TikTok - DIRECT POST API)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Credenciales de la App "Astrology Factory" (SANDBOX)
CLIENT_KEY = "sbaw1bxm8knugdcxbs"
CLIENT_SECRET = "XMaqRO69uVDpakX8nP8SfRZwyonRyKrd"
REDIRECT_URI = "https://www.portaltarotmistico.com/oauth/"

TOKEN_FILE = Path(__file__).parent / "tiktok_token.json"
RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; AMARILLO = "\033[93m"

def log(msg, color=RESET):
    print(f"{color}{msg}{RESET}")

def main():
    print("\n==============================================")
    print("🔐 CONFIGURADOR TIKTOK (API OFICIAL)")
    print("==============================================")
    
    # 1. Construir URL de Autorización
    scopes = "video.upload,video.publish"
    # Nota: TikTok pide un 'state' csrf_token, usamos uno estático para simplificar el script CLI
    state = "factory_auth_state"
    
    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/?"
        f"client_key={CLIENT_KEY}&"
        f"response_type=code&"
        f"scope={scopes}&"
        f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
        f"state={state}"
    )
    
    log("⚠️ PASO 1: EN EL PANEL DE TIKTOK", AMARILLO)
    log("Asegurate de haber agregado el producto 'TikTok Login' en el panel.")
    log(f"Adentro de la config de Login, poné este Redirect URI exacto:\n👉 {REDIRECT_URI}\n")
    
    log("🔗 PASO 2: AUTORIZACIÓN", CYAN)
    log("Abrí el siguiente link en tu navegador donde tenés abierta la cuenta @portaltarotmistico:")
    log(f"\n{auth_url}\n")
    
    log("👉 Cuando autorices la app, TikTok te va a redirigir a una página que dice 'No se encontró' o 'Error 404'. ¡Es normal!")
    log("👉 Lo importante es la URL que aparece arriba en el navegador, que va a decir algo como: https://www.portaltarotmistico.com/oauth/?code=XXX&state=...")
    
    redirected_url = input(f"\n{AMARILLO}Pegá acá la URL COMPLETA a la que te redirigió TikTok:{RESET} ").strip()
    
    if not redirected_url:
        log("❌ No ingresaste ninguna URL.", ROJO)
        sys.exit(1)
        
    try:
        parsed_url = urllib.parse.urlparse(redirected_url)
        params = urllib.parse.parse_qs(parsed_url.query)
        code = params.get("code", [None])[0]
        
        if not code:
            log("❌ No se encontró el 'code' en la URL. ¿Seguro que la copiaste entera?", ROJO)
            sys.exit(1)
            
        log(f"\n✅ Código extraído: {code}", VERDE)
        
    except Exception as e:
        log(f"❌ Error parseando la URL: {e}", ROJO)
        sys.exit(1)
        
    # 2. Intercambiar code por access_token
    log("\n⏳ PASO 3: OBTENIENDO TOKEN OFICIAL...", CYAN)
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    
    data = urllib.parse.urlencode({
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }).encode("utf-8")
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }
    
    req = urllib.request.Request(token_url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            
            if "access_token" in res_json:
                with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                    json.dump(res_json, f, indent=4)
                log(f"✅ ¡ÉXITO! Token guardado en {TOKEN_FILE.name}", VERDE)
                log("🚀 Ya podés usar publicador_redes.py para subir a TikTok.", VERDE)
            else:
                log(f"❌ TikTok no devolvió el token. Respuesta: {res_body}", ROJO)
                
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        log(f"❌ Error HTTP {e.code} al pedir el token: {err_body}", ROJO)
    except Exception as e:
        log(f"❌ Error inesperado: {e}", ROJO)

if __name__ == "__main__":
    main()
