#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validador_headers.py — Analizador de cabeceras de seguridad HTTP y estado de red.
Recibe una lista de objetivos o un archivo y comprueba de forma segura el
estado de conexión y la presencia de cabeceras de seguridad esenciales.

Uso:
    python3 validador_headers.py --target example.com
    python3 validador_headers.py --file objetivos.txt
"""

import sys
import argparse
import urllib.request
import urllib.error
import ssl
import json
from datetime import datetime, timezone

# Cabeceras de seguridad a auditar y su nivel de importancia
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "desc": "HSTS - Fuerza conexiones seguras HTTPS",
        "required": True
    },
    "Content-Security-Policy": {
        "desc": "CSP - Previene inyección de scripts (XSS/Clickjacking)",
        "required": True
    },
    "X-Frame-Options": {
        "desc": "Previene Clickjacking",
        "required": True
    },
    "X-Content-Type-Options": {
        "desc": "Previene MIME-sniffing",
        "required": True
    },
    "Referrer-Policy": {
        "desc": "Controla qué información de referencia se envía",
        "required": False
    },
    "Permissions-Policy": {
        "desc": "Restringe APIs del navegador permitidas",
        "required": False
    },
    "Access-Control-Allow-Origin": {
        "desc": "CORS - Permisos de compartición de recursos",
        "required": False
    }
}

def analizar_url(url, user_agent=None, custom_headers=None, ignore_ssl=False):
    """
    Realiza una petición HTTP/S a la URL y analiza sus cabeceras.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        # Por defecto asumir https
        url = "https://" + url

    headers = {
        "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Security-Header-Validator/1.0"
    }
    if custom_headers:
        headers.update(custom_headers)

    ctx = ssl.create_default_context()
    if ignore_ssl:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers=headers, method="GET")
    
    resultado = {
        "url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": None,
        "error": None,
        "headers_found": {},
        "missing_headers": [],
        "security_score": 0
    }

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            resultado["status"] = response.status
            resp_headers = response.info()
            
            # Normalizar cabeceras a minúsculas
            headers_dict = {k.lower(): v for k, v in resp_headers.items()}
            analizar_cabeceras(headers_dict, resultado)
            
    except urllib.error.HTTPError as e:
        resultado["status"] = e.code
        # La petición devolvió un código de error (e.g. 403, 404, 500) pero sigue teniendo cabeceras
        headers_dict = {k.lower(): v for k, v in e.headers.items()}
        analizar_cabeceras(headers_dict, resultado)
    except urllib.error.URLError as e:
        resultado["error"] = f"Error de red/conexión: {e.reason}"
    except Exception as e:
        resultado["error"] = f"Error inesperado: {str(e)}"
        
    return resultado

def analizar_cabeceras(headers_dict, resultado):
    """Auxiliar para verificar la presencia de cabeceras de seguridad."""
    presentes = {}
    faltantes = []
    
    for h_name, info in SECURITY_HEADERS.items():
        h_lower = h_name.lower()
        if h_lower in headers_dict:
            presentes[h_name] = headers_dict[h_lower]
        else:
            faltantes.append(h_name)
            
    resultado["headers_found"] = presentes
    resultado["missing_headers"] = faltantes
    
    # Calcular puntuación básica (100% si tiene todas las requeridas configuradas)
    req_headers = [h for h, info in SECURITY_HEADERS.items() if info["required"]]
    req_configuradas = sum(1 for h in req_headers if h in presentes)
    resultado["security_score"] = int((req_configuradas / len(req_headers)) * 100) if req_headers else 100

def main():
    parser = argparse.ArgumentParser(description="Verifica cabeceras de seguridad HTTP y estados de conexión.")
    parser.add_argument("--target", help="Dominio o URL a analizar (ej. example.com)")
    parser.add_argument("--file", help="Archivo de texto con un dominio por línea")
    parser.add_argument("--header", action="append", help="Cabecera personalizada (ej. 'X-HackerOne-Research: usuario')")
    parser.add_argument("--ignore-ssl", action="store_true", help="Ignorar errores de certificados SSL")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON puro")
    
    args = parser.parse_args()
    
    custom_headers = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                k, v = h.split(":", 1)
                custom_headers[k.strip()] = v.strip()
                
    targets = []
    if args.target:
        targets.append(args.target)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    line_clean = line.strip()
                    if line_clean and not line_clean.startswith("#"):
                        targets.append(line_clean)
        except Exception as e:
            print(f"Error al leer el archivo {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    resultados = []
    for t in targets:
        if not args.json:
            print(f"[*] Analizando {t}...")
        res = analizar_url(t, custom_headers=custom_headers, ignore_ssl=args.ignore_ssl)
        resultados.append(res)
        
        if not args.json:
            if res["error"]:
                print(f"  [-] Error: {res['error']}")
            else:
                print(f"  [+] Código de estado: {res['status']}")
                print(f"  [+] Puntuación de seguridad: {res['security_score']}%")
                if res["missing_headers"]:
                    print(f"  [-] Cabeceras faltantes: {', '.join(res['missing_headers'])}")
                else:
                    print("  [+] Todas las cabeceras de seguridad requeridas están configuradas.")
            print("-" * 50)
            
    if args.json:
        print(json.dumps(resultados, indent=2))

if __name__ == "__main__":
    main()
