#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script Auxiliar: auto_clasificador_groq.py
Alternativa de rescate usando la API de Groq (Llama 3.2 Vision)
Ultra rápida y excelente para cuando los servidores de Google están saturados.
"""

import argparse
import base64
import json
import os
import shutil
import sys
import time
from pathlib import Path
from PIL import Image
import io

# ── Entorno ────────────────────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

try:
    from dotenv import load_dotenv
    from groq import Groq
except ImportError:
    print("❌ Faltan dependencias. Ejecuta: pip3 install --break-system-packages groq pillow python-dotenv")
    sys.exit(1)

load_dotenv(FACTORY_ROOT / ".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ No se encontró GROQ_API_KEY en el archivo .env")
    print("Por favor, abre tu archivo .env y agrega: GROQ_API_KEY=tu_clave_aqui")
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = 'llama-3.2-11b-vision-preview' # Modelo visual súper rápido y gratis de Groq

# ── Categorías ─────────────────────────────────────────────────────────────
ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
try:
    with open(ADN_PATH, encoding="utf-8") as f:
        ADN = json.load(f)
        CATEGORIAS = ADN["assets"]["categorias_auditoria"]
except Exception as e:
    print(f"❌ Error leyendo contexto_astrologico.json: {e}")
    sys.exit(1)

lista_categorias = "\n".join([f"{k}: {v}" for k, v in CATEGORIAS.items()])
SYSTEM_PROMPT = f"""
Eres un curador de arte abstracto, esotérico y astrológico.
Clasifica la imagen en UNA de estas categorías:

{lista_categorias}

REGLAS ESTRICTAS:
1. Responde ÚNICA Y EXCLUSIVAMENTE con el dígito (1 al 9).
2. NUNCA escribas texto adicional, ni descripciones, ni comillas. Solo un número.
"""

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def clasificar_imagen(img_path: Path) -> str:
    """Envía la imagen a Groq y retorna el número de categoría."""
    try:
        # Groq requiere base64 para las imágenes
        img = Image.open(img_path)
        img.thumbnail((512, 512)) # Bajar res para gastar menos tokens y que sea veloz
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=80)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]}
            ],
            temperature=0.1,
            max_completion_tokens=10
        )
        
        resultado = response.choices[0].message.content.strip()
        
        # Validar que sea un número del 1 al 9 (filtrar cualquier ruido adicional)
        for char in resultado:
            if char in CATEGORIAS:
                return char
                
        return "9" # Default
        
    except Exception as e:
        print(f"  ⚠️ Error de API de Groq con {img_path.name}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directorio", type=str, required=True, help="Ruta a la carpeta de assets")
    args = parser.parse_args()
    
    dir_base = Path(args.directorio)
    if not dir_base.exists():
        sys.exit(1)
        
    print(f"\n🔮 AUTO-CLASIFICADOR IA (Motor: GROQ LLaMA 3.2 Vision) INICIADO")
    print(f"   Pausa entre imágenes: 2.0 segundos (Groq es mucho más veloz)\n")
    
    registro_path = dir_base / "ia_curated_registry_groq.json"
    
    if registro_path.exists():
        with open(registro_path, "r", encoding="utf-8") as f: procesados = set(json.load(f))
    else:
        procesados = set()
        
    archivos = []
    for ext in ['.jpg', '.jpeg', '.png']:
        archivos.extend(list(dir_base.rglob(f"*{ext}")))
        archivos.extend(list(dir_base.rglob(f"*{ext.upper()}")))
        
    archivos = [a for a in archivos if a.is_file() and a.name not in procesados]
    print(f"🖼️  Se encontraron {len(archivos)} imágenes pendientes.\n")
    if len(archivos) == 0: sys.exit(0)
        
    for i, archivo in enumerate(archivos, 1):
        print(f"[{i}/{len(archivos)}] Analizando: {archivo.name[:40]} ...")
        cat_num = clasificar_imagen(archivo)
        
        if cat_num:
            cat_nombre = CATEGORIAS[cat_num]
            dir_destino = dir_base / "Imagenes" / cat_nombre
            asegurar_dir(dir_destino)
            destino = dir_destino / archivo.name
            
            if archivo.resolve() != destino.resolve():
                shutil.move(archivo, destino)
                print(f"  ✅ Movido a → {cat_nombre}")
            else:
                print(f"  ✅ Ya estaba en ({cat_nombre})")
                
            procesados.add(archivo.name)
            with open(registro_path, "w", encoding="utf-8") as f:
                json.dump(list(procesados), f)
                
        # Groq permite unas 30 RPM, bajamos a 2 segundos de pausa
        time.sleep(2.0)

if __name__ == "__main__":
    main()
