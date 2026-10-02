import os
import time
import json
import requests
import shutil
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
load_dotenv(ENV_PATH)
KEYS = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_TEXT")]
KEYS = [k for k in KEYS if k]
current_key_idx = 0

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

def init_gemini():
    genai.configure(api_key=KEYS[current_key_idx])

def rotate_api_key():
    global current_key_idx
    if current_key_idx < len(KEYS) - 1:
        current_key_idx += 1
        print(f"🔄 Rotando a llave Gemini #{current_key_idx + 1}")
        init_gemini()
        return True
    return False

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

    # Usar el modelo standard para visión (en código antiguo usamos gemini-1.5-flash)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        return json.loads(response.text)
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
            print("⚠️ Cuota de API agotada.")
            return "QUOTA_EXCEEDED"
        print(f"⚠️ Gemini Error: {e}")
        return None

def catalogador_loop():
    print("🛸 Iniciando Fase B: Catalogador de Inbox...")
    
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, "r") as f:
                catalogo = json.load(f)
        except:
            catalogo = {}
    else:
        catalogo = {}

    inbox_files = [f for f in os.listdir(INBOX_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not inbox_files:
        print("📭 Inbox vacío. Nada que catalogar.")
        return

    print(f"📦 Encontrados {len(inbox_files)} archivos en Inbox. Procesando...")
    
    for filename in inbox_files:
        inbox_path = os.path.join(INBOX_DIR, filename)
        dest_path = os.path.join(ASSETS_DIR, filename)
        
        print(f"  Analizando: {filename}...")
        
        metadata = analyze_image_with_gemini(inbox_path)
        
        if metadata == "QUOTA_EXCEEDED":
            if rotate_api_key():
                print("Reintentando con nueva llave...")
                metadata = analyze_image_with_gemini(inbox_path)
                if metadata == "QUOTA_EXCEEDED":
                    send_telegram_alert("Todas las cuotas de Gemini están agotadas. El catalogador se pondrá a dormir hasta mañana.")
                    return # Cortamos la ejecución por hoy
            else:
                send_telegram_alert("Cuota de Gemini agotada y no hay más llaves de repuesto. Durmiendo...")
                return

        if metadata and isinstance(metadata, dict):
            # Guardamos la metadata
            catalogo[filename] = metadata
            with open(CATALOG_PATH, "w") as f:
                json.dump(catalogo, f, indent=4)
            # Movemos físicamente
            shutil.move(inbox_path, dest_path)
            print(f"  ✅ Catalogado y movido.")
        else:
            print(f"  ⚠️ No se pudo procesar. Se saltará.")
            
        time.sleep(SLEEP_BETWEEN_CALLS)

def master_loop():
    print("🌌 NODRIZA AUTÓNOMA INICIADA 🌌")
    if not KEYS:
        print("❌ No se encontraron API keys en .env")
        return
    init_gemini()
    
    while True:
        # 1. Comprobación de salud (Espacio en disco)
        current_size = get_vault_size()
        print(f"\n📊 Estado de Bóveda: {current_size / (1024**3):.2f} GB / {MAX_VAULT_SIZE_GB} GB")
        
        if current_size >= MAX_GB_BYTES:
            print("🛑 LÍMITE DE 50GB ALCANZADO. Scraper deshabilitado.")
            send_telegram_alert(f"Límite de bóveda de {MAX_VAULT_SIZE_GB}GB alcanzado. Deteniendo recolección.")
            # Aunque no pueda scrapear, puede que haya cosas en el Inbox, intentamos catalogar
            catalogador_loop()
            print("💤 Durmiendo 1 hora...")
            time.sleep(3600)
            continue
            
        # 2. Fase A: Recolección (Scraper)
        # TODO: Implementar lógica de lectura de transit_palettes.json e invocación segura
        # del scraper aquí para descargar lentamente hacia INBOX_DIR.
        
        # 3. Fase B: Catalogación de Inbox
        catalogador_loop()
        
        print("💤 Ciclo completado. Durmiendo 5 minutos...")
        time.sleep(300)

if __name__ == "__main__":
    try:
        master_loop()
    except KeyboardInterrupt:
        print("\nNodriza Autónoma apagada.")
