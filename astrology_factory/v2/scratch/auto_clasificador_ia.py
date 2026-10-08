#!/usr/bin/env python3
"""
🌑 CÉLULA MADRE 0 — Script Auxiliar: auto_clasificador_ia.py
Recorre una carpeta de assets y usa Gemini Flash para reubicarlos en las 9 categorías.
Diseñado para la capa gratuita (Rate Limit de 10 peticiones por minuto).
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path
from PIL import Image

# Permitir abrir imágenes masivas de la NASA (evita DecompressionBombError)
Image.MAX_IMAGE_PIXELS = None

# ── Entorno ────────────────────────────────────────────────────────────────
FACTORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(FACTORY_ROOT))

try:
    from dotenv import load_dotenv
    from google import genai
except ImportError:
    print("❌ Faltan dependencias. Ejecuta: pip3 install --break-system-packages google-genai pillow python-dotenv groq")
    sys.exit(1)

try:
    from groq import Groq
except ImportError:
    print("❌ Faltan dependencias. Ejecuta: pip3 install --break-system-packages groq")
    sys.exit(1)

load_dotenv(FACTORY_ROOT / ".env")

# ── Clientes con frenos (ver v2/cuota.py) ──────────────────────────────────
from v2 import cuota

_clientes_cache = {}
def _cliente(nombre, key):
    if nombre not in _clientes_cache:
        _clientes_cache[nombre] = genai.Client(api_key=key)
    return _clientes_cache[nombre]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

if not cuota.keys_produccion() and not groq_client:
    print("❌ No se encontraron llaves de API válidas en .env (Gemini o Groq)")
    sys.exit(1)

AGOTADO = "AGOTADO"

# ── Categorías ─────────────────────────────────────────────────────────────
ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
try:
    with open(ADN_PATH, encoding="utf-8") as f:
        ADN = json.load(f)
        CATEGORIAS = ADN["assets"]["categorias_auditoria"]
except Exception as e:
    print(f"❌ Error leyendo contexto_astrologico.json: {e}")
    sys.exit(1)

CATEGORIAS["00"] = "Descarte"  # respuesta del modelo cuando la imagen no sirve

# Construir el prompt del sistema
lista_categorias = "\n".join([f"{k}: {v}" for k, v in CATEGORIAS.items()])
SYSTEM_PROMPT = f"""Eres el curador de arte de un canal de astrología esotérica profunda.
Tu tarea es clasificar la imagen en UNA de estas categorías y extraer sus metadatos.

{lista_categorias}

❌ DESCARTE OBLIGATORIO — Si la imagen contiene alguno de estos elementos, responde con "00" en la categoría:
- Personas de cualquier tipo, rostros humanos, manos, cuerpos, figuras humanas reconocibles
- Personas cotidianas: familias, parejas, bebés, niños, adolescentes, multitudes, sonrisas
- Retratos de personas comunes (selfies, fotos de perfil, fotos de stock con personas)
- Escenas domésticas: cocinas, casas, oficinas, parques con gente, ciudades modernas
- Bodas, reuniones, fiestas, eventos sociales
- Imágenes de noticias o documentales con personas identificables

✅ ACEPTAR SIEMPRE — Estas imágenes SIEMPRE pertenecen a alguna categoría:
- Cosmos, galaxias, nebulosas, planetas, lunas (aunque tengan nombres como "baby nebula")  
- Geometría sagrada, mandalas, símbolos esotéricos, runas
- Fuego, agua, tierra, aire como elementos puros o simbólicos
- Naturaleza sin personas: bosques, montañas, océanos, cielos
- Arte digital abstracto, fractales, texturas mágicas
- Figuras arquetípicas (diosas, deidades, figuras mitológicas claramente no reales)
- Sacerdotisas o figuras espirituales en contexto claramente simbólico/artístico

REGLAS ESTRICTAS:
1. Responde ÚNICA Y EXCLUSIVAMENTE con un JSON válido. No incluyas backticks de markdown ni texto extra.
2. El JSON debe tener esta estructura exacta:
{{
  "categoria": "03", // Número de categoría en string (o "00" si se descarta)
  "elemento": "Agua", // "Fuego", "Tierra", "Aire", "Agua" o "Etereo"
  "mood": "Misterio", // 1 o 2 palabras de emoción dominante (ej: "Caos", "Calma", "Tensión", "Renacer")
  "metaforas": ["infinito", "inconsciente", "profundidad", "limpieza"] // 3 a 5 conceptos esotéricos/metafóricos que sugiere la imagen
}}
"""

def asegurar_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

import base64
from io import BytesIO

def _image_to_base64(img: Image.Image) -> str:
    buffered = BytesIO()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def _llamar_gemini(client, img):
    response = client.models.generate_content(
        model='gemini-3.8-flash', # Estable y con 1500 req/día
        contents=[SYSTEM_PROMPT, img]
    )
    return response.text.strip()

def _llamar_groq(img):
    b64_img = _image_to_base64(img)
    response = groq_client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SYSTEM_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                    },
                ],
            }
        ],
        temperature=0.0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

def clasificar_imagen(img_path: Path) -> dict:
    """Clasifica con UNA llamada por intento, eligiendo la key menos usada.
    Devuelve dict con metadata, None (falló, reintentar luego) o AGOTADO."""
    img = Image.open(img_path)
    img.thumbnail((1024, 1024)) # Reducir resolución para ahorrar tokens/transferencia

    for _ in range(4):  # máximo 4 intentos por imagen, siempre con keys distintas/descansadas
        elegida = cuota.elegir_key()
        if not elegida:
            return AGOTADO
        nombre, key = elegida
        cuota.esperar_ritmo()
        try:
            res_text = _llamar_gemini(_cliente(nombre, key), img)
            cuota.registrar_uso(nombre)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', res_text.replace('\n', ' '), re.DOTALL)
            if json_match:
                res_dict = json.loads(json_match.group(0))
                res_dict["categoria"] = str(res_dict.get("categoria", "00")).zfill(2)
                if res_dict["categoria"] in CATEGORIAS or res_dict["categoria"] == "00":
                    return res_dict
            return None  # respuesta rara: no insistir con otra key
        except Exception as e:
            tipo = cuota.registrar_error(nombre, e)
            if tipo == "otro":
                print(f"  ⚠️ Error en {nombre}: {str(e)[:120]}")
                return None
            print(f"  ⏸️ {nombre} en pausa ({tipo}). Probando otra key...")
    return None

def main():
    parser = argparse.ArgumentParser(description="Clasificador visual IA con Gemini Flash")
    parser.add_argument("--directorio", type=str, required=True, help="Carpeta de origen (ej: Descargas_Crudas/Oct_W1)")
    parser.add_argument("--salida", type=str, required=True, help="Carpeta de destino final (ej: Assets_Auditados/Oct_W1)")
    args = parser.parse_args()
    
    dir_base = Path(args.directorio)
    dir_salida = Path(args.salida)
    if not dir_base.exists():
        print(f"❌ El directorio de origen no existe: {dir_base}")
        sys.exit(1)
        
    print(f"\n🔮 AUTO-CLASIFICADOR IA INICIADO")
    print(f"   Origen: {dir_base}")
    print(f"   Destino: {dir_salida}")
    print(f"   Pausa entre imágenes: 8.0 segundos (~7.5 RPM para cuota gratuita sin bloqueos)\n")
    
    # Registro global en la raíz de Assets_Auditados para que no se borre nunca
    vault_root = dir_salida.parent if dir_salida.name == "Imagenes" else dir_salida
    registro_path = vault_root / "ia_curated_registry.json"
    
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
        
    print("🔍 Construyendo base de datos de hashes (MD5) de la bóveda para evitar duplicados...")
    hashes_existentes = set()
    for ext in ['.jpg', '.jpeg', '.png']:
        for img in dir_salida.rglob(f"*{ext}"):
            with open(img, "rb") as f:
                hashes_existentes.add(hashlib.md5(f.read()).hexdigest())
    print(f"  ✅ {len(hashes_existentes)} hashes únicos registrados en la bóveda de salida.")
        
    for i, archivo in enumerate(archivos, 1):
        print(f"\n[{i}/{len(archivos)}] Analizando: {archivo.name} ...")
        
        # 1. Anti-Duplicado (Hash)
        with open(archivo, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        if h in hashes_existentes:
            print("  🗑️  ¡DUPLICADO EXACTO! Eliminando archivo para no contaminar la bóveda.")
            archivo.unlink()
            # Registrar como procesado para no volver a intentar
            procesados.add(archivo.name)
            continue
            
        hashes_existentes.add(h)
        
        # 2. Clasificación IA
        meta = clasificar_imagen(archivo)
        if meta == AGOTADO:
            print("\n🛑 Todas las keys están agotadas por hoy. Corto aquí; lo pendiente se retoma mañana.")
            print(cuota.resumen())
            sys.exit(0)

        if not meta:
            print("  ⚠️ API falló. Archivo salteado, se reintentará en el próximo ciclo.")
            continue
            
        cat_num = meta.get("categoria", "00")

        if cat_num == "00":
            # Descarte explícito por el modelo: mover a Cuarentena
            cuarentena_dir = dir_salida.parent.parent / "Cuarentena_Visual"
            cuarentena_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(archivo, cuarentena_dir / archivo.name)
            procesados.add(archivo.name)
            with open(registro_path, "w", encoding="utf-8") as f:
                json.dump(list(procesados), f)
            print(f"  🚫 Descartada y movida a Cuarentena: {archivo.name}")
            continue

        if cat_num in CATEGORIAS:
            cat_nombre = CATEGORIAS[cat_num]
            
            # Crear la carpeta de destino
            dir_destino = dir_salida / cat_nombre
            asegurar_dir(dir_destino)
            
            destino = dir_destino / archivo.name
            json_destino = dir_destino / (archivo.stem + ".json")
            
            # Mover el archivo (si el destino es diferente al origen)
            if archivo.resolve() != destino.resolve():
                shutil.move(archivo, destino)
                print(f"  ✅ Movido a → {cat_nombre}")
            else:
                print(f"  ✅ Ya estaba en la carpeta correcta ({cat_nombre})")
                
            # Guardar el JSON semántico
            with open(json_destino, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
                
            # Registrar como procesado
            procesados.add(archivo.name)
            with open(registro_path, "w", encoding="utf-8") as f:
                json.dump(list(procesados), f)
                
        # La pausa entre llamadas la maneja cuota.esperar_ritmo()

    print("\n🎉 CLASIFICACIÓN COMPLETADA.")

if __name__ == "__main__":
    main()
