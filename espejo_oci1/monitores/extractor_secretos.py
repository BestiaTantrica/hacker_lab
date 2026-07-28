#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor_secretos.py — El "Motor de Dinero" Automático
=========================================================================
Fase 3 del Roadmap: Extracción MASIVA y sin autenticación de secretos.
Lee los subdominios de OCI-1, extrae todos los archivos .js, y busca
expresiones regulares de tokens (AWS, Stripe, Twilio, Slack) de alto valor.

Regla de oro cumplida: CERO burocracia, CERO logins, CERO Burp.
"""

import json
import re
import requests
import concurrent.futures
import os
from urllib.parse import urljoin

# Configuración
ARCHIVO_OBJETIVOS = "/home/ubuntu/plataforma_operativa/resultados/actual.json"
MAX_WORKERS = 10
TIMEOUT = 5

# Expresiones regulares de tokens de ALTO VALOR (P1/P2 en HackerOne)
REGEX_SECRETOS = {
    "Stripe Standard API Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Stripe Restricted API Key": r"rk_live_[0-9a-zA-Z]{24}",
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "Twilio API Key": r"SK[0-9a-fA-F]{32}",
    "Slack Token": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
    "GitHub Personal Access Token": r"ghp_[0-9a-zA-Z]{36}",
    "Google API Key (Posible)": r"AIza[0-9A-Za-z-_]{35}",
}

def obtener_urls(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Extraer subdominios de la lista plana
            return [f"https://{sub}" for sub in data.get("subdominios", [])][:1000] # Limitamos a 1000 por corrida para no ahogar
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return []

def analizar_js(url_js, url_origen):
    hallazgos = []
    try:
        r = requests.get(url_js, timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            contenido = r.text
            for nombre, patron in REGEX_SECRETOS.items():
                coincidencias = re.findall(patron, contenido)
                for c in coincidencias:
                    # Filtro anti-falsos positivos básicos (por ejemplo AKIA falso)
                    if "AKIAEXAMPLE" in c: continue
                    hallazgos.append({
                        "tipo": nombre,
                        "secreto": c[:5] + "***" + c[-4:], # Ofuscado para logs
                        "origen": url_origen,
                        "archivo_js": url_js
                    })
    except:
        pass
    return hallazgos

def escanear_target(url):
    hallazgos = []
    try:
        # 1. Obtener la página principal
        r = requests.get(url, timeout=TIMEOUT, verify=False)
        if r.status_code != 200:
            return hallazgos
        
        # 2. Extraer todos los <script src="...">
        scripts = re.findall(r'<script[^>]+src=["\'](.*?\.js)["\']', r.text, re.IGNORECASE)
        
        # 3. Formatear URLs relativas a absolutas
        js_urls = [urljoin(url, s) for s in scripts]
        
        # 4. Analizar cada JS
        for js_url in set(js_urls):
            resultados_js = analizar_js(js_url, url)
            if resultados_js:
                hallazgos.extend(resultados_js)
                
    except Exception as e:
        pass
    
    return hallazgos

def main():
    print("============================================================")
    print("🚀 INICIANDO EXTRACTOR DE SECRETOS JS (Zero Auth)")
    print("============================================================")
    
    if not os.path.exists(ARCHIVO_OBJETIVOS):
        # Fallback local para pruebas
        print(f"No se encontró {ARCHIVO_OBJETIVOS}. ¿Estás corriendo esto en OCI-1?")
        return

    urls = obtener_urls(ARCHIVO_OBJETIVOS)
    print(f"Cargados {len(urls)} objetivos para escaneo...")
    
    hallazgos_totales = []
    
    # Procesamiento multihilo masivo
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futuros = {executor.submit(escanear_target, url): url for url in urls}
        
        for i, futuro in enumerate(concurrent.futures.as_completed(futuros), 1):
            url = futuros[futuro]
            if i % 100 == 0:
                print(f"Progreso: {i}/{len(urls)} escaneados...")
                
            try:
                res = futuro.result()
                if res:
                    for h in res:
                        print(f"🚨 [CRITICAL] {h['tipo']} encontrado en {h['origen']}")
                        hallazgos_totales.append(h)
            except:
                pass

    print("============================================================")
    print(f"✅ ESCANEO FINALIZADO. {len(hallazgos_totales)} secretos encontrados.")
    if hallazgos_totales:
        with open("/home/ubuntu/plataforma_operativa/resultados/secretos_js.json", "w") as f:
            json.dump(hallazgos_totales, f, indent=4)
        print("Guardados en resultados/secretos_js.json (Pegaso leerá esto y te alertará)")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings() # Desactivar warnings de SSL
    main()
