#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizar_resultados.py — Analiza infraestructura_verificada.json y resume
los objetivos web más atractivos para auditoría manual.
"""

import os
import json

VERIFIED_FILE = "/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/AUDITORIAS/infraestructura_verificada.json"

INTERESTING_WORDS = [
    "jenkins", "kibana", "grafana", "dashboard", "admin", "login", 
    "sso", "auth", "portal", "staging", "dev", "test", "vault", "secret"
]

def main():
    if not os.path.exists(VERIFIED_FILE):
        print(f"[-] No se encontró el archivo: {VERIFIED_FILE}")
        print("    Asegúrate de que el escaneo de infraestructura haya terminado.")
        return

    print("==============================================================")
    print("🔎 ANALIZANDO RESULTADOS DE INFRAESTRUCTURA VERIFICADA")
    print("==============================================================")

    with open(VERIFIED_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[-] Error al decodificar JSON: {e}")
            return

    activos = data.get("activos", [])
    if not activos:
        print("[-] No se encontraron activos en el archivo.")
        return

    # Contadores y agrupaciones
    stats_status = {}
    portales_200 = []
    interesantes = []

    for item in activos:
        subdomain = item.get("subdomain")
        url = item.get("url")
        status = item.get("status")
        title = item.get("title", "")
        cname = item.get("cname", "")

        # Agrupar por status code
        stats_status[status] = stats_status.get(status, 0) + 1

        # Almacenar portales 200
        if status == 200:
            portales_200.append(item)

        # Buscar coincidencia con palabras de interés en subdominio o título
        sub_lower = subdomain.lower()
        title_lower = title.lower()
        if any(w in sub_lower or w in title_lower for w in INTERESTING_WORDS):
            interesantes.append(item)

    # Mostrar estadísticas básicas
    print(f"[+] Total de endpoints web activos analizados: {len(activos)}")
    print("\n📊 Distribución de códigos de estado HTTP:")
    for status, count in sorted(stats_status.items()):
        print(f"   - HTTP {status}: {count} hosts")

    # Mostrar portales 200
    print(f"\n🟢 Portales con HTTP 200 OK directos ({len(portales_200)}):")
    if portales_200:
        for p in portales_200[:30]:  # Mostrar los primeros 30
            print(f"   - URL: {p['url']} | Título: '{p['title']}'")
        if len(portales_200) > 30:
            print(f"     ... y {len(portales_200) - 30} más.")
    else:
        print("   - Ninguno (todos redirigen o devuelven errores).")

    # Mostrar objetivos altamente interesantes
    print(f"\n🎯 Objetivos con palabras clave críticas ({len(interesantes)}):")
    if interesantes:
        for item in interesantes[:30]:  # Mostrar los primeros 30
            print(f"   - URL: {item['url']} | Status: {item['status']} | Título: '{item['title']}' | CNAME: '{item['cname']}'")
        if len(interesantes) > 30:
            print(f"     ... y {len(interesantes) - 30} más.")
    else:
        print("   - Ninguno detectado.")
        
    print("==============================================================")

if __name__ == "__main__":
    main()
