#!/usr/bin/env python3
"""
portal_noticias/reportero_ejecutivo.py — Agente Analista B2B (Powered by Claude)
Este script extrae la información cruda y se la pasa a Claude (vía OpenRouter)
para redactar un Reporte Ejecutivo certero y sin alucinaciones.
"""

import os
import json
import urllib.request
from datetime import datetime
from portal_noticias.rss_collector import collect_all_data
from portal_noticias.trend_engine import calculate_opinion_thermometer

# Leemos la API Key desde el archivo entorno.env
from dotenv import load_dotenv
load_dotenv("/home/LAB/espejo_oci1/config/entorno.env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def llamar_a_groq(prompt: str) -> str:
    """Envía el prompt a Llama 3 mediante la API de Groq."""
    if not GROQ_API_KEY:
        return "[ERROR] No se encontró GROQ_API_KEY en las variables de entorno."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Sos un Analista Jefe de Inteligencia de Fuentes Abiertas (OSINT) y Riesgo Político/Económico en Argentina. Tu trabajo es leer titulares en vivo y extraer 3 insights ejecutivos precisos, sin alucinar, sin inventar datos y yendo al hueso. Formato: Viñetas cortas."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result['choices'][0]['message']['content']
    except Exception as e:
        return f"[ERROR API Groq] {str(e)}"

def generar_reporte_ejecutivo():
    print("🤖 Claude Analista B2B: Analizando datos crudos de las últimas 24h...")
    raw_data = collect_all_data()
    items = raw_data.get("live_feed_items", [])
    
    if not items:
        print("⚠️ No hay datos crudos para analizar. Saliendo.")
        return
        
    thermometer = calculate_opinion_thermometer(items)
    
    print(f"📡 Enviando {len(items)} documentos crudos a Claude para síntesis...")
    
    # Preparar el corpus para Claude
    corpus = "\n".join([f"- [{i['source']}] {i['title']}: {i['snippet']}" for i in items])
    
    instruccion = f"""
Basado estrictamente en los siguientes titulares reales recopilados hoy, generá una 'SÍNTESIS EJECUTIVA (Top 3 Insights para toma de decisiones)' y una breve 'ALERTA TEMPRANA' si detectás algún conflicto, paro o problema emergente. 
No inventes absolutamente nada que no esté en el texto provisto.

TITULARES RECOPILADOS:
{corpus}
"""

    if GROQ_API_KEY:
        sintesis_ia = llamar_a_groq(instruccion)
    else:
        sintesis_ia = "⚠️ SIMULACRO POR FALTA DE API KEY: \n1. [POLÍTICA] El nivel de apoyo se mantiene fuerte en el núcleo duro...\n(Configurar GROQ_API_KEY para habilitar la síntesis real)."
    
    reporte_generado = f"""
=========================================================
📈 REPORTE EJECUTIVO B2B - INTELIGENCIA DE REDES
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}
=========================================================

📊 TERMÓMETRO SOCIAL (RUMBO ECONÓMICO)
🟢 Apoyo/Alineado:   {thermometer['acuerdo_rumbo']}%
🟡 Cautela/Espera:   {thermometer['cautela']}%
🔴 Desacuerdo:       {thermometer['desacuerdo']}%

🧠 SÍNTESIS DE LA IA (Generada Automáticamente):
{sintesis_ia}

=========================================================
Este reporte fue generado de forma automatizada por el Motor de 
Inteligencia Social. Confidencial - Uso Interno del Cliente.
"""
    
    reporte_path = os.path.join(os.path.dirname(__file__), "ultimo_reporte_b2b.txt")
    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write(reporte_generado)
        
    print(f"✅ Reporte generado exitosamente en {reporte_path}")
    print("\nPrevisualización del Entregable:\n")
    print(reporte_generado)

if __name__ == "__main__":
    generar_reporte_ejecutivo()
