import os
import time
import json
import requests
import shutil
import subprocess
from dotenv import load_dotenv

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 1. Rutas
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault"
INBOX_DIR = os.path.join(VAULT_DIR, "Descargas_Crudas")
ASSETS_DIR = os.path.join(VAULT_DIR, "Assets_Reusables")
CATALOG_PATH = os.path.join(VAULT_DIR, "catalogo_nodriza.json")
PALETTES_PATH = os.path.join(PROJECT_ROOT, "content_factory", "transit_palettes.json")

# 2. Límites
MAX_VAULT_SIZE_GB = 50
MAX_GB_BYTES = MAX_VAULT_SIZE_GB * 1024 * 1024 * 1024
SLEEP_BETWEEN_CALLS = 6  # ~10 por minuto max.

# 3. Inicializar entorno
import sys
sys.path.insert(0, PROJECT_ROOT)
from v2 import cuota

load_dotenv(ENV_PATH)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚨 *Nodriza Autónoma:*\n{message}", "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def init_gemini(key):
    genai.configure(api_key=key)

def get_vault_size():
    total_size = 0
    for dirpath, _, filenames in os.walk(VAULT_DIR):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def analyze_image_with_gemini(filepath):
    import PIL.Image
    try:
        img = PIL.Image.open(filepath)
        img.thumbnail((512, 512)) # Reducir para la API
    except Exception as e:
        print(f"❌ Error abriendo imagen {filepath}: {e}")
        return None

    elegida = cuota.elegir_key()
    if not elegida:
        return "QUOTA_EXCEEDED"
    nombre_key, key = elegida
    init_gemini(key)
    cuota.esperar_ritmo()

    # Usar el modelo standard para visión (en código antiguo usamos gemini-1.5-flash)
    model = genai.GenerativeModel('gemini-3.6-flash')
    
    prompt = """Analiza esta imagen para uso en un video astrológico esotérico/psicológico.
Responde ÚNICAMENTE en JSON válido con este formato exacto:
{
  "etiquetas_visuales": ["lista", "de", "palabras", "clave"],
  "emociones": ["lista", "de", "emociones", "que", "transmite"],
  "colores_predominantes": ["color1", "color2"],
  "es_apropiado_para_astrologia": true
}"""
    try:
        response = model.generate_content(
            [prompt, img],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            generation_config={"response_mime_type": "application/json"}
        )
        cuota.registrar_uso(nombre_key)
        return json.loads(response.text)
    except Exception as e:
        tipo = cuota.registrar_error(nombre_key, e)
        if tipo != "otro":
            print(f"⏸️ {nombre_key} en pausa ({tipo}).")
            return "RETRY_OTHER_KEY"
        print(f"⚠️ Gemini Error: {e}")
        return None

def catalogador_loop():
    print("🛸 Iniciando Fase B: Catalogador de Inbox...")
    
    # Leer contexto para saber la semana actual
    try:
        with open(os.path.join(PROJECT_ROOT, 'contexto_astrologico.json'), 'r') as f:
            adn = json.load(f)
            semana = adn['produccion']['semana_prefijo']
    except:
        semana = 'General'
        
    current_inbox = os.path.join(INBOX_DIR, semana)
    os.makedirs(current_inbox, exist_ok=True)
    
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, 'r') as f:
                catalogo = json.load(f)
        except:
            catalogo = {}
    else:
        catalogo = {}

    inbox_files = [f for f in os.listdir(current_inbox) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4'))]
    inbox_files = inbox_files[:5] # MAX 5 por ciclo (60 por hora) para no quemar la cuota diaria
    if not inbox_files:
        print("📭 Inbox vacío. Nada que catalogar.")
        return

    print(f"📦 Encontrados {len(inbox_files)} archivos en Inbox. Procesando...")
    
    for filename in inbox_files:
        inbox_path = os.path.join(current_inbox, filename)
        
        is_video = filename.lower().endswith('.mp4')
        subfolder = "Videos" if is_video else "Imagenes"
        final_dest_dir = os.path.join(ASSETS_DIR, subfolder, semana)
        os.makedirs(final_dest_dir, exist_ok=True)
        dest_path = os.path.join(final_dest_dir, filename)
        
        print(f"  Analizando: {filename}...")
        
        if filename.lower().endswith('.mp4'):
            import re
            palabras = [w.lower() for w in re.split(r'[/_.-]', filename) if len(w) > 3 and w.lower() not in ["abstract", "video", "mp4", "pexels", "pixabay", "assets"]]
            metadata = {
                "etiquetas_visuales": palabras + ["video", "animacion"],
                "emociones": palabras + ["movimiento", "fluidez", "misterio"],
                "colores_predominantes": ["variado"],
                "es_apropiado_para_astrologia": True,
                "formato": "mp4"
            }
        else:
            metadata = analyze_image_with_gemini(inbox_path)
        
        if metadata == 'RETRY_OTHER_KEY':
            metadata = analyze_image_with_gemini(inbox_path)  # 1 reintento con otra key
            if metadata == 'RETRY_OTHER_KEY':
                metadata = None
        if metadata == 'QUOTA_EXCEEDED':
            if cuota.alerta_pendiente():
                send_telegram_alert('Todas las cuotas de Gemini están agotadas. Duermo hasta que se renueven (≈4 a.m. Argentina). Aviso una sola vez por día.')
            return

        if metadata and isinstance(metadata, dict):
            catalogo[filename] = metadata
            with open(CATALOG_PATH, 'w') as f:
                json.dump(catalogo, f, indent=4)
            shutil.move(inbox_path, dest_path)
            print(f"  ✅ Catalogado y movido.")
        else:
            print(f"  ⚠️ No se pudo procesar. Se saltará.")
            
        time.sleep(SLEEP_BETWEEN_CALLS)

def purge_if_needed():
    current_size = get_vault_size()
    print(f"\n📊 Estado de Bóveda: {current_size / (1024**3):.2f} GB / {MAX_VAULT_SIZE_GB} GB")
    
    if current_size > MAX_GB_BYTES:
        print("⚠️ LÍMITE DE 50GB SUPERADO. Moviendo archivos antiguos a /Revision_Manual...")
        REVISION_DIR = os.path.join(VAULT_DIR, "Revision_Manual")
        os.makedirs(REVISION_DIR, exist_ok=True)
        TARGET_FREE_BYTES = 2 * 1024 * 1024 * 1024 # Liberar 2GB
        
        all_files = []
        for dirpath, _, filenames in os.walk(ASSETS_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    all_files.append((fp, os.path.getmtime(fp), os.path.getsize(fp)))
        
        all_files.sort(key=lambda x: x[1]) # Más viejos primero
        
        freed_bytes = 0
        for fp, mtime, size in all_files:
            if freed_bytes >= TARGET_FREE_BYTES:
                break
                
            dest = os.path.join(REVISION_DIR, os.path.basename(fp))
            if os.path.exists(dest):
                dest = os.path.join(REVISION_DIR, f"{int(time.time())}_{os.path.basename(fp)}")
            
            try:
                shutil.move(fp, dest)
                freed_bytes += size
                print(f"  -> Movido: {os.path.basename(fp)} ({(size/1024/1024):.2f} MB)")
            except Exception as e:
                print(f"  ❌ Error moviendo {os.path.basename(fp)}: {e}")
                
        print(f"✅ Purga completada. Se movieron {(freed_bytes / 1024 / 1024):.2f} MB a Revision_Manual.")
        send_telegram_alert(f"Purga de bóveda completada. Se liberaron {(freed_bytes/1024/1024/1024):.2f} GB.")
    else:
        print("✅ Espacio dentro de los límites saludables.")

def master_loop():
    print("🌌 NODRIZA AUTÓNOMA INICIADA 🌌")
    if not cuota.keys_produccion():
        print("❌ No se encontraron API keys en .env")
        return
    print(cuota.resumen())
    
    last_scrape_time = 0
    scrape_interval = 3600  # 1 hora en segundos
    
    while True:
        # 1. Comprobación de salud (Espacio en disco y purga de assets viejos)
        purge_if_needed()
            
        # 2. Fase A: Recolección (Scraper y Arte Sintético)
        now = time.time()
        if now - last_scrape_time >= scrape_interval:
            print("🚀 Iniciando Fase A: Recolección y Generación de Arte (cada 1 hora)...")
            script_dir = os.path.join(PROJECT_ROOT, "v2", "celula_0")
            
            try:
                # 2.1 Descarga desde Internet (Pexels) - Muy conservador (max 5 y 3) para no quemar API
                subprocess.run(["python3", os.path.join(script_dir, "recolector_visual.py"), "--opcion", "1", "--max", "5"])
                subprocess.run(["python3", os.path.join(script_dir, "recolector_visual.py"), "--opcion", "2", "--max", "3"])
                subprocess.run(["python3", os.path.join(script_dir, "recolector_visual.py"), "--opcion", "5", "--max", "3"])
                
                # 2.2 Creación de Arte IA (Pollinations)
                subprocess.run(["python3", os.path.join(script_dir, "generador_arte_ia.py")])
                
                last_scrape_time = time.time()
                print("✅ Fase A completada.")
            except Exception as e:
                print(f"❌ Error ejecutando subprocesos en Fase A: {e}")
        else:
            wait_min = (scrape_interval - (now - last_scrape_time)) / 60
            print(f"⏳ Fase A en reposo. Próxima recolección en {wait_min:.1f} minutos.")
        
        # 3. Fase B: Catalogación de Inbox (solo si hay alguna key disponible)
        if cuota.todas_agotadas():
            espera = min(cuota.segundos_hasta_proxima_key(), 3600)
            print(f"💤 Todas las keys en descanso. Duermo {espera // 60} min sin hacer ninguna llamada.")
            print(cuota.resumen())
            time.sleep(max(espera, 300))
            continue
        catalogador_loop()
        
        print("💤 Ciclo de Nodriza completado. Durmiendo 5 minutos...")
        time.sleep(300)

if __name__ == "__main__":
    try:
        master_loop()
    except KeyboardInterrupt:
        print("\nNodriza Autónoma apagada.")
