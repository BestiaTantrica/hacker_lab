#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script Auxiliar: generador_arte_ia.py
Genera arte sintético astrológico profundo usando Gemini (para prompts)
y Pollinations.ai (para renderizado de imágenes) sin coste de API.
Guarda los resultados en Descargas_Crudas con prefijo 'arte_propio_'.
"""

import json
import os
import sys
import time
import urllib.parse
import requests
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

try:
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ Faltan dependencias. Ejecuta: pip3 install google-genai requests python-dotenv")
    sys.exit(1)

load_dotenv(FACTORY_ROOT / ".env")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Falta GEMINI_API_KEY en .env")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
try:
    with open(ADN_PATH, encoding="utf-8") as f:
        ADN = json.load(f)
except FileNotFoundError:
    print("❌ No se encontró contexto_astrologico.json")
    sys.exit(1)

VAULT_BASE = Path(ADN["assets"]["boveda_base"])
SEMANA = ADN["produccion"]["semana_prefijo"]
DESC_CRUDAS = VAULT_BASE / "Descargas_Crudas" / SEMANA

DESC_CRUDAS.mkdir(parents=True, exist_ok=True)

def generate_prompts():
    prompt = f"""
You are an expert surrealist AI artist and esoteric astrologer.
Based on the following astrological context, create 3 ultra-detailed, evocative, and highly complex image generation prompts in English.
Do NOT just say "{ADN['produccion']['evento_titulo']}". Describe the energetic tension, sacred geometry, colors, and cymatic resonance of multiple planets involved.
The images will be vertical (9:16 aspect ratio). Make them profound, dark, and beautiful.

ASTROLOGICAL CONTEXT:
Event: {ADN['produccion']['evento_titulo']}
Description: {ADN['transito']['descripcion_breve']}
Primary Archetype: {ADN['arquetipos']['primario']}
Colors: {', '.join(ADN['estetica_visual']['paleta_colores'].values())}
Keywords: {', '.join(ADN['transito']['palabras_clave'])}

Output ONLY a valid JSON array of 3 strings (the prompts), and nothing else.
Example:
[
  "Abstract visualization of Scorpio energy clashing with Taurus, dark red and electric blue, cymatic waves, sacred geometry overlay, surreal cosmic depth, sharp focus, 8k resolution, cinematic lighting",
  "..."
]
"""
    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        prompts = json.loads(text.strip())
        return prompts
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return []

def download_image(prompt, index):
    print(f"🎨 Generando imagen {index+1} en Pollinations...")
    # Añadir tags visuales extra para forzar calidad
    enhanced_prompt = prompt + ", highly detailed, 8k, masterpiece, dark fantasy, esoteric art, vertical"
    safe_prompt = urllib.parse.quote(enhanced_prompt)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1080&height=1920&nologo=true"
    
    try:
        res = requests.get(url, timeout=120)
        if res.status_code == 200:
            timestamp = int(time.time())
            filename = DESC_CRUDAS / f"arte_propio_{timestamp}_{index}.jpg"
            with open(filename, 'wb') as f:
                f.write(res.content)
            print(f"✅ Guardado: {filename.name}")
        else:
            print(f"❌ Error HTTP {res.status_code} en Pollinations")
    except Exception as e:
        print(f"❌ Error de red: {e}")

def main():
    print("🔮 Solicitando prompts astrológicos complejos a Gemini...")
    prompts = generate_prompts()
    if not prompts:
        print("❌ No se pudieron generar los prompts.")
        sys.exit(1)
        
    for i, p in enumerate(prompts):
        print(f"\n=> Prompt {i+1}: {p}")
        download_image(p, i)
        time.sleep(2) # Respetar rate limits de pollinations

    prompts_file = DESC_CRUDAS / "PROMPTS_ARTE.md"
    try:
        with open(prompts_file, 'w', encoding='utf-8') as f:
            f.write("# Prompts de Arte Generados\n\n")
            for i, p in enumerate(prompts):
                f.write(f"## Imagen {i+1}\n```\n{p}\n```\n\n")
        print(f"✅ Prompts guardados en {prompts_file.name} para revisión manual.")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el archivo de prompts: {e}")

if __name__ == "__main__":
    main()
