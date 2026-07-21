#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizador_completo.py — Analiza el 100% de los subdominios interesantes 
de la base de datos inicial de OCI y genera el Mapa de Ataque completo.
"""

import os
import sys
import json
import datetime
from llm_client import completar
from notificador import send_telegram

# Configuración de rutas en el servidor
BASE_DIR = os.path.expanduser("~/plataforma_operativa")
RESULT_DIR = os.path.join(BASE_DIR, "resultados")
ACTUAL_FILE = os.path.join(RESULT_DIR, "actual.json")
MAPA_FILE = os.path.join(RESULT_DIR, "MAPA_DE_ATAQUE.md")

KEYWORDS = [
    "admin", "api", "dev", "test", "staging", "secret", "vault", 
    "jenkins", "internal", "ci", "auth", "login", "dashboard", 
    "qa", "sandbox", "private", "portal", "status", "git"
]

def filtrar_subdominios(dominios_dict):
    filtrados = {}
    for target, lista in dominios_dict.items():
        if not isinstance(lista, list):
            continue
        filtrados[target] = []
        for sub in lista:
            sub_lower = sub.lower()
            if any(kw in sub_lower for kw in KEYWORDS):
                filtrados[target].append(sub)
    return filtrados

def dividir_en_lotes(lista, tamano=20):
    """Divide una lista larga en lotes más pequeños para evitar límites de tokens."""
    for i in range(0, len(lista), tamano):
        yield lista[i:i + tamano]

def analizar_lote(target, lote, numero_lote, total_lotes):
    print(f"🧠 Analizando lote {numero_lote}/{total_lotes} para {target}...")
    prompt = f"""
Eres un analista de seguridad y experto en Bug Bounty.
A continuación tienes un lote de subdominios interesantes para el objetivo '{target}' (Lote {numero_lote}/{total_lotes}).
Analízalos detalladamente y clasifica su prioridad de investigación.

Lote de subdominios:
{json.dumps(lote, indent=2)}

Devuelve una tabla Markdown con el análisis de cada uno de ellos, utilizando el siguiente formato exacto:
| Subdominio | Prioridad (Alta/Media/Baja) | Qué buscar / Vector de ataque recomendado |
"""
    try:
        respuesta = completar(prompt, max_tokens=1500)
        return respuesta.strip()
    except Exception as e:
        return f"Error analizando lote: {e}"

def main():
    print("🤖 Iniciando analizador_completo.py en el servidor...")
    
    if not os.path.isfile(ACTUAL_FILE):
        print(f"❌ No se encontró el archivo de subdominios en: {ACTUAL_FILE}")
        sys.exit(1)

    with open(ACTUAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        dominios = data.get("dominios", {})

    print("🧹 Pre-filtrando subdominios sospechosos...")
    filtrados = filtrar_subdominios(dominios)
    
    total_filtrados = sum(len(v) for v in filtrados.values())
    print(f"🎯 Total de subdominios sospechosos identificados: {total_filtrados}")

    if total_filtrados == 0:
        print("ℹ️ No se encontraron subdominios sospechosos para analizar.")
        sys.exit(0)

    # Cabecera del reporte
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    reporte_md = f"""# 🗺️ MAPA DE ATAQUE COMPLETO — BUG BOUNTY
> Generado de forma automática el {fecha_hoy}
> Total de objetivos analizados: {total_filtrados}

---

"""

    # Procesar cada target por separado
    for target, lista in filtrados.items():
        if not lista:
            continue
            
        reporte_md += f"## 💎 Target: {target} ({len(lista)} objetivos de interés)\n\n"
        
        # Dividir la lista del target en lotes de 20 para no ahogar a la IA
        lotes = list(dividir_en_lotes(lista, tamano=20))
        total_lotes = len(lotes)
        
        for idx, lote in enumerate(lotes, 1):
            resultado_lote = analizar_lote(target, lote, idx, total_lotes)
            reporte_md += resultado_lote + "\n\n"
            
        reporte_md += "\n---\n\n"

    # Guardar el mapa de ataque en el servidor
    try:
        with open(MAPA_FILE, "w", encoding="utf-8") as f:
            f.write(reporte_md)
        print(f"✅ Mapa de ataque completo guardado en: {MAPA_FILE}")
    except Exception as e:
        print(f"❌ Error guardando el archivo de mapa: {e}")
        sys.exit(1)

    # Mandar notificación resumen a Telegram
    mensaje_telegram = f"""*🎯 MAPA DE ATAQUE GENERADO*
El servidor analizó los {total_filtrados} activos sospechosos iniciales (Mongo + Elastic).

El reporte detallado con las tablas de prioridad ha sido guardado en el servidor:
`~/plataforma_operativa/resultados/MAPA_DE_ATAQUE.md`
"""
    send_telegram(mensaje_telegram)
    print("🚀 Alerta enviada a Telegram.")

if __name__ == "__main__":
    main()
