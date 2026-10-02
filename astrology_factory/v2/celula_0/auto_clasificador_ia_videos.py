#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script Auxiliar: auto_clasificador_ia_videos.py
Recorre una carpeta de assets de video, extrae un fotograma clave (frame 0) y
usa Gemini Flash para reubicarlos en las 9 categorías (carpeta Videos).
Diseñado para ahorrar cuota y procesar de manera ligera.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import hashlib
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
API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_TEXT"),
    os.getenv("GEMINI_API_KEY_WEB"),
    os.getenv("GEMINI_API_KEY_WEB_TEXT")
]
API_KEYS = [k for k in API_KEYS if k]

# Clientes de la nueva SDK oficial
gemini_clients = [genai.Client(api_key=key) for key in API_KEYS]

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
Tu tarea es clasificar la imagen proporcionada (que es un fotograma de un video) en UNA de las siguientes categorías:

{lista_categorias}

REGLAS ESTRICTAS:
1. Responde ÚNICA Y EXCLUSIVAMENTE con un solo número (del 1 al 9).
2. No incluyas texto extra, ni explicaciones, ni símbolos.
"""

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def extraer_fotograma(video_path: Path, output_image_path: Path) -> bool:
    """Usa ffmpeg para extraer un fotograma clave del video (ej. al 25% o nudo)."""
    cmd = [
        "ffmpeg", "-y", "-v", "quiet",
        "-ss", "00:00:02", # Saltar los primeros 2s para evitar pantallas negras iniciales
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "3",
        str(output_image_path)
    ]
    try:
        subprocess.run(cmd, check=True, timeout=30)
        return True
    except Exception:
        # Fallback a primer fotograma estricto si el video dura < 2s
        cmd_fallback = [
            "ffmpeg", "-y", "-v", "quiet",
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "3",
            str(output_image_path)
        ]
        try:
            subprocess.run(cmd_fallback, check=True, timeout=30)
            return True
        except Exception as e:
            print(f"  ⚠️ Error extrayendo frame de {video_path.name}: {e}")
            return False

# Lista de modelos a intentar en orden de preferencia
CANDIDATE_MODELS = ['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-flash-latest']

def clasificar_imagen(img_path: Path, max_retries: int = 3) -> str:
    """Envía el fotograma a Gemini intentando con modelos en rotación si hay 429/404."""
    img = Image.open(img_path)
    img.thumbnail((1024, 1024)) # Reducir resolución para gastar menos tokens

    for client in gemini_clients:
        for model_name in CANDIDATE_MODELS:
            for intento in range(1, max_retries + 1):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[SYSTEM_PROMPT, img]
                    )
                    resultado = response.text.strip().zfill(2)
                    
                    # Validar que sea un número del 01 al 18
                    if resultado in CATEGORIAS:
                        return resultado
                    else:
                        return "18" # Default a general si falla el formato
                        
                    
            except Exception as e:
                err_str = str(e)
                if "404" in err_str:
                    break
                elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"  ⚠️ Cuota agotada en {model_name} (intento {intento}/{max_retries}). Probando alternativa...")
                    time.sleep(5)
                    break
                elif "503" in err_str:
                    print(f"  ⚠️ Alta demanda en {model_name}. Pausa de 10s...")
                    time.sleep(10)
                else:
                    print(f"  ⚠️ Error de API con {img_path.name}: {e}")
                    return None
    return None

def main():
    parser = argparse.ArgumentParser(description="Clasificador visual IA de VIDEOS con Gemini Flash")
    parser.add_argument("--directorio", type=str, required=True, help="Ruta a la carpeta de assets (ej: Assets_Reusables_Auditados)")
    parser.add_argument("--salida", type=str, required=False, help="Carpeta de destino final (ej: Assets_Auditados/Videos)")
    args = parser.parse_args()
    
    dir_base = Path(args.directorio)
    if not dir_base.exists():
        print(f"❌ El directorio no existe: {dir_base}")
        sys.exit(1)
        
    print(f"\n🔮 AUTO-CLASIFICADOR IA DE VIDEOS INICIADO")
    print(f"   Directorio: {dir_base}")
    print(f"   Pausa entre videos: 8.0 segundos (~7.5 RPM para cuota gratuita)\n")
    
    registro_path = dir_base / "ia_video_registry.json"
    
    # Cargar registro
    if registro_path.exists():
        with open(registro_path, "r", encoding="utf-8") as f:
            procesados = set(json.load(f))
    else:
        procesados = set()
        
    # Buscar todos los videos recursivamente
    archivos = []
    formatos_video = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    for ext in formatos_video:
        archivos.extend(list(dir_base.rglob(f"*{ext}")))
        archivos.extend(list(dir_base.rglob(f"*{ext.upper()}")))
        
    # Filtrar los ya procesados y evitar procesar videos que ya están en Videos/
    archivos = [a for a in archivos if a.is_file() and a.name not in procesados]
    
    print(f"🎬 Se encontraron {len(archivos)} videos pendientes de clasificar.")
    
    if len(archivos) == 0:
        print("✅ No hay videos nuevos para procesar.")
        sys.exit(0)
        
    print("🔍 Construyendo base de datos de hashes (MD5) de la bóveda para evitar duplicados...")
    hashes_existentes = set()
    dir_salida = Path(args.salida) if hasattr(args, "salida") and args.salida else dir_base
    for ext in formatos_video:
        for vid in dir_salida.rglob(f"*{ext}"):
            try:
                with open(vid, "rb") as f:
                    hashes_existentes.add(hashlib.md5(f.read()).hexdigest())
            except Exception:
                pass
    print(f"  ✅ {len(hashes_existentes)} hashes únicos registrados en la bóveda de salida.")
        
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_frame_path = Path(temp_dir) / "frame_temp.jpg"
        
        for i, archivo in enumerate(archivos, 1):
            print(f"\n[{i}/{len(archivos)}] Analizando video: {archivo.name} ...")
            
            # 1. Anti-Duplicado (Hash)
            try:
                with open(archivo, "rb") as f:
                    archivo_hash = hashlib.md5(f.read()).hexdigest()
                    
                if archivo_hash in hashes_existentes:
                    print(f"  🗑️ Clon exacto detectado en bóveda final. Eliminando clon de Reusables...")
                    archivo.unlink()
                    continue
            except Exception as e:
                print(f"  ⚠️ Error leyendo hash: {e}")
            
            # Extraer frame
            if not extraer_fotograma(archivo, temp_frame_path):
                print(f"  ⚠️ Saltando {archivo.name} por fallo de extracción.")
                continue
            
            # Clasificar
            cat_num = clasificar_imagen(temp_frame_path)
            
            if cat_num:
                cat_nombre = CATEGORIAS[cat_num]
                
                # Crear la carpeta de destino: /18_General/
                dir_destino = dir_salida / cat_nombre
                asegurar_dir(dir_destino)
                
                destino = dir_destino / archivo.name
                
                # Mover el archivo de video (si el destino es diferente al origen)
                if archivo.resolve() != destino.resolve():
                    shutil.move(str(archivo), str(destino))
                    print(f"  ✅ Movido a → Videos/{cat_nombre}")
                else:
                    print(f"  ✅ Ya estaba en la carpeta correcta (Videos/{cat_nombre})")
                    
                # Registrar como procesado
                procesados.add(archivo.name)
                with open(registro_path, "w", encoding="utf-8") as f:
                    json.dump(list(procesados), f)
                    
            # PAUSA ESTRATÉGICA PARA EVITAR BANEOS DE LA CAPA GRATUITA
            print("  ⏳ Esperando 8 segundos (Rate limit protection)...")
            time.sleep(8.0)

    print("\n🎉 CLASIFICACIÓN DE VIDEOS COMPLETADA.")

if __name__ == "__main__":
    main()
