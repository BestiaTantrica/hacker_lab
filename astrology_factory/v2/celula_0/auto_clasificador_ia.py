#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script Auxiliar: auto_clasificador_ia.py
Recorre una carpeta de assets y usa Gemini Flash para reubicarlos en las 9 categorías.
Diseñado para la capa gratuita (Rate Limit de 10 peticiones por minuto).
"""

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from PIL import Image

# ── Entorno ────────────────────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

try:
    from dotenv import load_dotenv
    from google import genai
except ImportError:
    print("❌ Faltan dependencias. Ejecuta: pip3 install --break-system-packages google-genai pillow python-dotenv")
    sys.exit(1)

load_dotenv(FACTORY_ROOT / ".env")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ No se encontró GEMINI_API_KEY en el archivo .env")
    sys.exit(1)

# Cliente de la nueva SDK oficial
client = genai.Client(api_key=API_KEY)

# ── Categorías ─────────────────────────────────────────────────────────────
ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
try:
    with open(ADN_PATH, encoding="utf-8") as f:
        ADN = json.load(f)
        CATEGORIAS = ADN["assets"]["categorias_auditoria"]
except Exception as e:
    print(f"❌ Error leyendo contexto_astrologico.json: {e}")
    sys.exit(1)

# Construir el prompt del sistema
lista_categorias = "\n".join([f"{k}: {v}" for k, v in CATEGORIAS.items()])
SYSTEM_PROMPT = f"""
Eres un curador de arte abstracto, esotérico y astrológico.
Tu tarea es clasificar la imagen proporcionada en UNA de las siguientes categorías:

{lista_categorias}

REGLAS ESTRICTAS:
1. Responde ÚNICA Y EXCLUSIVAMENTE con un solo número (del 1 al 9).
2. No incluyas texto extra, ni explicaciones, ni símbolos.
"""

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# Lista de modelos a intentar en orden de preferencia
CANDIDATE_MODELS = ['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-flash-latest']

def clasificar_imagen(img_path: Path, max_retries: int = 3) -> str:
    """Envía la imagen a Gemini intentando con modelos en rotación si hay 429/404."""
    img = Image.open(img_path)
    img.thumbnail((1024, 1024)) # Reducir resolución para gastar menos tokens

    for model_name in CANDIDATE_MODELS:
        for intento in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[SYSTEM_PROMPT, img]
                )
                resultado = response.text.strip()
                
                # Validar que sea un número del 1 al 9
                if resultado in CATEGORIAS:
                    return resultado
                else:
                    return "9" # Default a general si falla el formato
                    
            except Exception as e:
                err_str = str(e)
                if "404" in err_str:
                    break # Probar siguiente modelo si este no existe/está descontinuado
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"  ⚠️ Cuota agotada en {model_name} (intento {intento}/{max_retries}). Probando alternativa...")
                    time.sleep(5)
                    break # Saltar de inmediato al siguiente modelo disponible para no perder tiempo
                elif "503" in err_str:
                    print(f"  ⚠️ Alta demanda en {model_name}. Pausa de 10s...")
                    time.sleep(10)
                else:
                    print(f"  ⚠️ Error inesperado con {img_path.name}: {e}")
                    return None
    return None

def main():
    parser = argparse.ArgumentParser(description="Clasificador visual IA con Gemini Flash")
    parser.add_argument("--directorio", type=str, required=True, help="Ruta a la carpeta de assets (ej: Assets_Reusables_Auditados)")
    args = parser.parse_args()
    
    dir_base = Path(args.directorio)
    if not dir_base.exists():
        print(f"❌ El directorio no existe: {dir_base}")
        sys.exit(1)
        
    print(f"\n🔮 AUTO-CLASIFICADOR IA INICIADO")
    print(f"   Directorio: {dir_base}")
    print(f"   Pausa entre imágenes: 8.0 segundos (~7.5 RPM para cuota gratuita sin bloqueos)\n")
    
    registro_path = dir_base / "ia_curated_registry.json"
    
    # Cargar registro
    if registro_path.exists():
        with open(registro_path, "r", encoding="utf-8") as f:
            procesados = set(json.load(f))
    else:
        procesados = set()
        
    # Buscar todas las imágenes recursivamente
    archivos = []
    for ext in ['.jpg', '.jpeg', '.png']:
        archivos.extend(list(dir_base.rglob(f"*{ext}")))
        archivos.extend(list(dir_base.rglob(f"*{ext.upper()}")))
        
    # Filtrar los ya procesados y los que están en la papelera
    archivos = [a for a in archivos if a.is_file() and a.name not in procesados]
    
    print(f"🖼️  Se encontraron {len(archivos)} imágenes pendientes de clasificar.")
    
    if len(archivos) == 0:
        print("✅ No hay imágenes nuevas para procesar.")
        sys.exit(0)
        
    for i, archivo in enumerate(archivos, 1):
        print(f"\n[{i}/{len(archivos)}] Analizando: {archivo.name} ...")
        
        cat_num = clasificar_imagen(archivo)
        
        if cat_num:
            cat_nombre = CATEGORIAS[cat_num]
            
            # Crear la carpeta de destino: /Imagenes/1_Astrologia/
            dir_destino = dir_base / "Imagenes" / cat_nombre
            asegurar_dir(dir_destino)
            
            destino = dir_destino / archivo.name
            
            # Mover el archivo (si el destino es diferente al origen)
            if archivo.resolve() != destino.resolve():
                shutil.move(archivo, destino)
                print(f"  ✅ Movido a → {cat_nombre}")
            else:
                print(f"  ✅ Ya estaba en la carpeta correcta ({cat_nombre})")
                
            # Registrar como procesado
            procesados.add(archivo.name)
            with open(registro_path, "w", encoding="utf-8") as f:
                json.dump(list(procesados), f)
                
        # PAUSA ESTRATÉGICA PARA EVITAR BANEOS DE LA CAPA GRATUITA
        print("  ⏳ Esperando 8 segundos (Rate limit protection)...")
        time.sleep(8.0)

    print("\n🎉 CLASIFICACIÓN COMPLETADA.")

if __name__ == "__main__":
    main()
