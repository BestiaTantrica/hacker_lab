#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificar_infraestructura.py — ESLABÓN 1: Análisis de Infraestructura Local
Usa dnsx e httpx de forma nativa mediante subprocesos para validar subdominios y
detectar posibles takeovers y puertos HTTP activos.

Uso:
    python3 verificar_infraestructura.py [archivo_subdominios.txt]
"""

import os
import sys
import json
import subprocess
import shutil

# Rutas de herramientas locales
HERRAMIENTAS_BIN = "/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/herramientas/bin"
DNSX_BIN = os.path.join(HERRAMIENTAS_BIN, "dnsx")
HTTPX_BIN = os.path.join(HERRAMIENTAS_BIN, "httpx")

# Si no están en la carpeta local, buscar en el PATH del sistema
if not os.path.exists(DNSX_BIN):
    DNSX_BIN = shutil.which("dnsx") or "dnsx"
if not os.path.exists(HTTPX_BIN):
    HTTPX_BIN = shutil.which("httpx") or "httpx"

# Huellas digitales de servicios comunes para Subdomain Takeover
TAKEOVER_FINGERPRINTS = {
    "github.io": "GitHub Pages",
    "s3.amazonaws.com": "AWS S3 Bucket",
    "s3-website": "AWS S3 Website",
    "cloudfront.net": "AWS CloudFront",
    "herokuapp.com": "Heroku App",
    "wpengine.com": "WPEngine",
    "zendesk.com": "Zendesk",
    "azurewebsites.net": "Azure App Service",
    "trafficmanager.net": "Azure Traffic Manager",
    "fastly.net": "Fastly CDN (Requiere validar body)",
}

def ejecutar_comando_json(cmd):
    """Ejecuta un comando y parsea cada línea de la salida como JSON."""
    resultados = []
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        for linea in proc.stdout:
            linea_clean = linea.strip()
            if not linea_clean:
                continue
            try:
                resultados.append(json.loads(linea_clean))
            except json.JSONDecodeError:
                pass
        proc.wait()
    except Exception as e:
        print(f"[-] Error al ejecutar {' '.join(cmd)}: {e}")
    return resultados

def analizar(archivo_subdominios):
    if not os.path.exists(archivo_subdominios):
        print(f"[-] El archivo '{archivo_subdominios}' no existe.")
        sys.exit(1)

    print("============================================================")
    # 1. Resolución DNS masiva con dnsx
    print(f"[*] Paso 1: Resolviendo CNAMEs con dnsx ({DNSX_BIN})...")
    cmd_dnsx = [DNSX_BIN, "-l", archivo_subdominios, "-cname", "-resp", "-json", "-silent"]
    resultados_dns = ejecutar_comando_json(cmd_dnsx)
    print(f"[+] Se procesaron {len(resultados_dns)} registros DNS.")

    # Mapear CNAMEs por subdominio
    mapa_cnames = {}
    for r in resultados_dns:
        subdominio = r.get("host")
        cnames = r.get("cnames", [])
        if subdominio and cnames:
            mapa_cnames[subdominio] = cnames

    # 2. Verificación HTTP con httpx
    print(f"[*] Paso 2: Escaneando HTTP con httpx ({HTTPX_BIN})...")
    # Pedimos status code, título, CDN, tecnologías y salida en JSON
    cmd_httpx = [HTTPX_BIN, "-l", archivo_subdominios, "-status-code", "-title", "-cdn", "-json", "-silent"]
    resultados_http = ejecutar_comando_json(cmd_httpx)
    print(f"[+] Se encontraron {len(resultados_http)} endpoints HTTP/HTTPS activos.")

    # 3. Analizar candidatos a Takeover y Estructurar reporte
    print("[*] Paso 3: Analizando huellas digitales y correlacionando...")
    candidatos_takeover = []
    hosts_activos = []

    for r in resultados_http:
        subdominio = r.get("input") or r.get("host")
        url = r.get("url")
        status = r.get("status_code")
        title = r.get("title", "")
        cdn = r.get("cdn-name", "")
        
        # Obtener CNAME si existe en nuestro mapa DNS
        cnames = mapa_cnames.get(subdominio, [])
        cname_str = cnames[0] if cnames else ""

        info_host = {
            "subdomain": subdominio,
            "url": url,
            "status": status,
            "title": title,
            "cdn": cdn,
            "cname": cname_str
        }
        hosts_activos.append(info_host)

        # Buscar si el CNAME tiene alguna firma conocida
        cname_sospechoso = False
        proveedor_detectado = None
        for firma, proveedor in TAKEOVER_FINGERPRINTS.items():
            if cname_str and (firma in cname_str.lower()):
                cname_sospechoso = True
                proveedor_detectado = proveedor
                break

        # Reglas especiales de descarte para evitar falsos positivos
        if cname_sospechoso:
            falso_positivo = False
            
            # Caso Fastly/Zendesk: si responde 200 y tiene título real, no es takeover
            if "Fastly" in proveedor_detectado or "Zendesk" in proveedor_detectado:
                if status == 200 and "Not Found" not in title and title != "":
                    falso_positivo = True
            
            if not falso_positivo:
                candidatos_takeover.append({
                    "subdomain": subdominio,
                    "cname": cname_str,
                    "provider": proveedor_detectado,
                    "status_code": status,
                    "title": title,
                    "url": url
                })

    # Guardar resultados
    salida_datos = {
        "resumen": {
            "total_subdominios_analizados": len(resultados_dns),
            "activos_http": len(hosts_activos),
            "candidatos_takeover": len(candidatos_takeover)
        },
        "activos": hosts_activos,
        "takeovers": candidatos_takeover
    }

    ruta_salida = "/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/AUDITORIAS/infraestructura_verificada.json"
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(salida_datos, f, indent=2)

    print("============================================================")
    print("✅ ANÁLISIS COMPLETADO")
    print(f"   - Subdominios activos HTTP/HTTPS : {len(hosts_activos)}")
    print(f"   - Candidatos a Takeover detectados: {len(candidatos_takeover)}")
    print(f"   - Reporte JSON guardado en: {ruta_salida}")
    print("============================================================")

    if candidatos_takeover:
        print("\n🚨 ¡CANDIDATOS A TAKEOVER ENCONTRADOS!")
        for c in candidatos_takeover:
            print(f"  - [{c['provider']}] {c['subdomain']}")
            print(f"    -> CNAME: {c['cname']}")
            print(f"    -> HTTP {c['status_code']} | Título: {c['title']}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 verificar_infraestructura.py [archivo_subdominios.txt]")
        sys.exit(1)
    
    analizar(sys.argv[1])
