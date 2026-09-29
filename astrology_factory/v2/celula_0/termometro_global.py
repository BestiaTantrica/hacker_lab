import sys
import json
import feedparser
from pathlib import Path
import os
from dotenv import load_dotenv

# Configurar rutas
SCRIPT_DIR = Path(__file__).resolve().parent
FACTORY_ROOT = SCRIPT_DIR.parent.parent
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

VAULT_BASE = Path(ADN["assets"]["boveda_base"])
TEMP_DIR = VAULT_BASE / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = TEMP_DIR / "termometro_actual.json"

# Configurar Gemini
gemini_config = ADN.get("gemini_vision", {})
api_key = os.getenv("GEMINI_API_KEY_TEXT")
if not api_key:
    api_key = os.getenv(gemini_config.get("api_key_env", "GEMINI_API_KEY"))
if not api_key:
    print("❌ Error: GEMINI_API_KEY no encontrada en .env")
    sys.exit(1)

import google.genai as genai
client = genai.Client(api_key=api_key)

# Usamos un modelo rápido para análisis de texto
modelo = "gemini-3.5-flash"

RSS_FEEDS = {
    "Argentina": [
        "https://www.clarin.com/rss/lo-ultimo/",
        "https://www.lanacion.com.ar/arc/outboundfeeds/rss/?outputType=xml"
    ],
    "Global_Latam": [
        "https://feeds.bbci.co.uk/mundo/rss.xml",
        "https://es.reuters.com/rssFeed/topNews"
    ]
}

def obtener_titulares():
    titulares = []
    print("🌍 Recolectando titulares globales y de Argentina...")
    for region, urls in RSS_FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:  # Top 10 por feed
                    titulares.append(f"[{region}] {entry.title}")
            except Exception as e:
                print(f"⚠️ Error leyendo {url}: {e}")
    return titulares

def analizar_zeitgeist(titulares):
    print("🧠 Analizando el Zeitgeist (espíritu de la época) con Gemini...")
    texto_titulares = "\n".join(titulares)
    
    prompt = f"""
Actúa como un sociólogo y analista de tendencias.
Aquí tienes los titulares de noticias más importantes del día en Argentina y el mundo:
{texto_titulares}

Tu tarea es analizar el "humor social" o "clima global" basándote ÚNICAMENTE en estos titulares.
Debes devolver la respuesta en formato JSON estrictamente válido con esta estructura:
{{
  "clima_emocional": "Descripción de 2 oraciones del estado de ánimo general (ej. Incertidumbre económica, agitación política, esperanza, etc.)",
  "temas_dominantes": ["tema1", "tema2", "tema3"],
  "foco_argentina": "Resumen de 1 oración de la situación específica en Argentina.",
  "arquetipo_social": "Un arquetipo junguiano que represente a la humanidad hoy (ej. El Guerrero herido, El Mago buscando respuestas)."
}}
Devuelve SOLO el JSON, sin bloques de código markdown ni texto adicional.
"""
    import time
    for intento in range(3):
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3].strip()
                
            data = json.loads(raw_text)
            return data
        except Exception as e:
            print(f"⚠️ Error en análisis de Gemini (intento {intento+1}): {e}")
            time.sleep(5)
    print("❌ Fallaron todos los intentos con Gemini.")
    return None

if __name__ == "__main__":
    titulares = obtener_titulares()
    if not titulares:
        print("❌ No se pudieron obtener titulares.")
        sys.exit(1)
        
    resultado = analizar_zeitgeist(titulares)
    if resultado:
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        print(f"✅ Termómetro Global actualizado y guardado en {OUT_PATH}")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("❌ Falló la actualización del termómetro.")
        sys.exit(1)
