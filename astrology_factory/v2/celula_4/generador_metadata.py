#!/usr/bin/env python3
"""
🚀 CÉLULA MADRE 4 — Script 4.1: generador_metadata.py
Lee el timeline_huecos.json (que contiene el guion) y usa GEMINI_API_KEY_TEXT
para generar el título, descripción y hashtags perfectos para redes sociales.
Salida: metadata_redes.json
"""

import json
import os
import sys
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
with open(ADN_PATH, encoding="utf-8") as f:
    ADN = json.load(f)

# Usamos la llave de TEXTO para no chocar con procesamiento de video
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_TEXT")
EVENTO_ID      = ADN["produccion"]["evento_id"]
TIMELINE_DIR   = Path(ADN["assets"]["paths"]["timeline_huecos"])
METADATA_DIR   = Path(ADN["assets"]["boveda_base"]) / "Metadata_Redes"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"; CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def main():
    log("\n📝 CÉLULA 4.1 — Generador de Metadata Social", MAGENTA)
    
    timeline_path = TIMELINE_DIR / f"{EVENTO_ID}.json"
    if not timeline_path.exists():
        log(f"❌ No se encontró el guion en: {timeline_path}", ROJO)
        log("Espera a que termine la Célula 1.", ROJO)
        sys.exit(1)
        
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline = json.load(f)
        
    # Extraer el guion completo
    guion_completo = " ".join([t["texto"] for t in timeline.get("tomas", []) if "texto" in t])
    
    prompt = f"""Eres un estratega de redes sociales (TikTok/YouTube Shorts) experto en astrología mística y oscura.
    
    TEMA DEL VIDEO: {ADN['transito']['planeta']} en {ADN['transito']['signo_destino']}
    ARQUETIPO: {ADN['arquetipos']['primario']}
    
    GUION DEL VIDEO:
    "{guion_completo}"
    
    TAREA:
    Genera la metadata SEO hiper-optimizada y "ganchera" para este video.
    Devuelve ÚNICAMENTE un JSON con esta estructura exacta (sin markdown):
    {{
      "titulo_youtube": "Título corto y magnético (máximo 60 caracteres)",
      "descripcion": "Descripción intrigante de 3 líneas",
      "tags_cortos": ["#Hashtag1", "#Hashtag2", "#Hashtag3"],
      "tags_largos": ["frase clave SEO 1", "frase clave SEO 2"]
    }}
    """
    
    if not GEMINI_API_KEY:
        log("❌ GEMINI_API_KEY_TEXT no está configurada.", ROJO)
        sys.exit(1)
        
    try:
        import google.genai as genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        log("🧠 Consultando a Gemini para redactar metadata...", CYAN)
        response = client.models.generate_content(
            model=ADN.get("gemini_text", {}).get("modelo", "gemini-3.6-flash"),
            contents=prompt
        )
        
        texto_raw = response.text.strip()
        import re
        texto_limpio = re.sub(r'^```(?:json)?\s*', '', texto_raw, flags=re.MULTILINE)
        texto_limpio = re.sub(r'\s*```$', '', texto_limpio, flags=re.MULTILINE).strip()
        
        metadata = json.loads(texto_limpio)
        
        asegurar_dir(METADATA_DIR)
        out_path = METADATA_DIR / f"{EVENTO_ID}_metadata.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        log(f"✅ Metadata generada y guardada en: {out_path}", VERDE)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        
    except Exception as e:
        log(f"❌ Error generando metadata: {e}", ROJO)

if __name__ == "__main__":
    main()
