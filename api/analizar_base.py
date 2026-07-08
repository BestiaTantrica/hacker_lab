#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizar_base.py — Filtra y analiza con IA los 6915 subdominios iniciales
para extraer los objetivos de mayor criticidad de MongoDB y Elastic.
"""

import os
import json
from llm_client import completar

# Ruta del archivo descargado
ACTUAL_FILE = "/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/api/actual.json"
REPORT_FILE = "/home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB/AUDITORIAS/TOP_OBJETIVOS_INICIALES.md"

# Palabras clave de alto interés para auditoría inicial
KEYWORDS = [
    "admin", "api", "dev", "test", "staging", "secret", "vault", 
    "jenkins", "internal", "ci", "auth", "login", "dashboard", 
    "qa", "sandbox", "private", "mktg", "portal", "status"
]

def filtrar_subdominios(dominios_dict):
    filtrados = {}
    total_leidos = 0
    total_filtrados = 0
    
    for target, lista in dominios_dict.items():
        if not isinstance(lista, list):
            continue
        total_leidos += len(lista)
        filtrados[target] = []
        for sub in lista:
            sub_lower = sub.lower()
            # Si contiene alguna palabra clave de interés
            if any(kw in sub_lower for kw in KEYWORDS):
                filtrados[target].append(sub)
                total_filtrados += 1
                
    print(f"📊 Total leídos: {total_leidos} | Filtrados interesantes: {total_filtrados}")
    return filtrados

def analizar_grupo_ia(target, lista):
    if not lista:
        return "No se encontraron subdominios interesantes para este objetivo."
        
    prompt = f"""
Eres un analista de seguridad y experto en Bug Bounty.
A continuación tienes una lista filtrada de subdominios interesantes para el objetivo '{target}'.
Analízalos y selecciona el TOP 10 de mayor prioridad para buscar vulnerabilidades (como IDOR, bypass de autenticación, fugas de información, etc.).

Lista a analizar:
{json.dumps(lista, indent=2)}

Devuelve una tabla Markdown ordenada por prioridad con las siguientes columnas:
| Prioridad | Subdominio | Nivel de Riesgo (Bajo/Medio/Alto/Crítico) | Explicación del riesgo y qué buscar |
"""
    try:
        respuesta = completar(prompt, max_tokens=1500)
        return respuesta.strip()
    except Exception as e:
        return f"Error en el análisis de la IA: {e}"

def main():
    if not os.path.isfile(ACTUAL_FILE):
        print(f"❌ No se encontró el archivo '{ACTUAL_FILE}'. Debes descargarlo primero desde el servidor OCI.")
        return

    print("📖 Cargando base de datos de subdominios...")
    with open(ACTUAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        dominios = data.get("dominios", {})

    print("🧹 Filtrando subdominios por palabras clave críticas...")
    filtrados = filtrar_subdominios(dominios)

    reporte_md = f"""# 🎯 TOP OBJETIVOS INICIALES DE AUDITORÍA (MongoDB & Elastic)
> Generado con IA a partir de los {sum(len(v) for v in dominios.values())} subdominios iniciales descubiertos.

---

"""

    for target, lista in filtrados.items():
        print(f"🧠 Analizando {target} con Groq/Gemini...")
        reporte_md += f"## 💎 Target: {target}\n"
        reporte_md += f"Se pre-filtraron {len(lista)} subdominios sospechosos. A continuación el análisis de prioridad:\n\n"
        reporte_md += analizar_grupo_ia(target, lista)
        reporte_md += "\n\n---\n\n"

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(reporte_md)
        
    print(f"✅ Reporte de objetivos iniciales guardado con éxito en: {REPORT_FILE}")

if __name__ == "__main__":
    main()
