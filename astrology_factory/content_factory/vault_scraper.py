import os
import json
import time
import requests
import shutil
import re
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Descargas_Crudas"
IMG_DIR = os.path.join(VAULT_DIR, "Imagenes")
VID_DIR = os.path.join(VAULT_DIR, "Videos")
GLITCH_DIR = os.path.join(VAULT_DIR, "Glitches_Source")
REGISTRY_PATH = os.path.join(VAULT_DIR, "scraper_registry.json")

# ── Categorías Esotéricas a Queries en Inglés ───────────────────────────────
# Mapeo de las 18 categorías a términos de búsqueda óptimos para Pexels/Pixabay
CATEGORIAS_QUERIES = {
    "01_Signos_Zodiacales": ["zodiac constellation", "astrology signs", "aries fire sign", "pisces water sign", "aquarius air sign"],
    "02_Planetas": ["planets", "solar system", "moon astrology dark", "mars planet red", "venus mystic glowing"],
    "03_Elementos_Fuego": ["fire element abstract", "flowing fire", "dark flames", "red fiery spark", "intense fire aura"],
    "04_Elementos_Agua": ["water element abstract", "dark ocean waves", "fluid water", "mystic blue water", "deep sea esoteric"],
    "05_Elementos_Tierra": ["earth element abstract", "dark forest", "crystals ground", "solid stone gold", "mystical mountain peak"],
    "06_Elementos_Aire": ["air element abstract", "dark clouds mist", "ethereal smoke", "neon blue mist", "cyber wind flow"],
    "07_Espacio_Galaxias": ["nebula", "deep space galaxy", "cosmos dark", "purple galaxy abstract", "stars ethereal glowing"],
    "08_Tarot_Misticismo": ["tarot cards", "mysticism", "esoteric fortune telling", "mystic truth shadow", "oracle dark magic"],
    "09_Geometria_Sagrada": ["sacred geometry", "fractal esoteric", "mystic symbols", "golden ratio dark", "neon cyber sigil"],
    "10_Naturaleza_Paisajes": ["nature dark landscape", "misty forest", "mystical nature", "stormy night sky", "ethereal mountain"],
    "11_Humanos_Emociones": ["dramatic portrait dark", "human emotion cinematic", "intense shadow face", "dreamy mystical portrait", "angry dramatic lighting"],
    "12_Rituales_Magia": ["magic ritual", "witchcraft", "candle spell dark", "mystic healing light", "shamanic shadow trance"],
    "13_Abstracto_Fluidos": ["abstract fluid dark", "liquid ink flow", "ethereal waves", "neon blue fluid space", "red fire abstract fluid"],
    "14_Glitch_VFX": ["glitch effect dark", "vfx distortion", "cyber signal error", "futuristic speed light", "cybernetic neon distortion"],
    "15_Astrologia_Cartas": ["astrology chart", "natal chart", "horoscope wheel", "astrolabe glowing", "zodiac wheel mystic"],
    "16_Mitologia_Dioses": ["mythological gods", "greek statues dark", "ancient deity", "ares god war", "aphrodite mystical"],
    "17_Objetos_Esotericos": ["esoteric objects", "crystal ball dark", "ancient book magic", "glowing crystal red", "mystic pendulum"],
    "18_General_B_Roll": ["cinematic dark aesthetic", "mystery b-roll", "ethereal background", "dark ambient motion", "esoteric moody light"]
}

# ── Filtro de Calidad: Términos PROHIBIDOS en la bóveda ────────────────────────
EXCLUSION_TERMS = {
    "bear", "oso", "child", "baby", "cute", "kids", "cartoon", "toy",
    "doll", "puppet", "bunny", "rabbit", "unicorn", "fairy", "princess",
    "kawaii", "chibi", "anime", "clipart", "vector", "sticker",
    "family", "home", "mother", "father", "parent", "domestic",
    "kitchen", "living", "bedroom", "house", "garden", "backyard",
    "smile", "happy", "cheerful", "lifestyle"
}
EXCLUSION_QUERY_SUFFIX = (
    " -cartoon -cute -kids -bear -baby -child -vector -clipart"
    " -family -home -domestic -lifestyle -happy"
)

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(VID_DIR, exist_ok=True)
os.makedirs(GLITCH_DIR, exist_ok=True)

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            return set(json.load(f))
    return set()

def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(list(registry), f)

def search_pexels_videos(query, per_page=15):
    safe_query = (query + EXCLUSION_QUERY_SUFFIX).strip()
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(safe_query)}&per_page={per_page}&orientation=landscape"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("videos", [])
    except Exception as e:
        print(f"⚠️ Pexels error: {e}")
    return []

def search_pixabay_images(query, per_page=15):
    # Pixabay tiene un límite estricto de 100 caracteres para el parámetro 'q'.
    # Usamos solo los primeros 2-3 sufijos de exclusión para no romper la API, 
    # y el resto de la exclusión se hace abajo en Python con 'EXCLUSION_TERMS'.
    safe_query = (query + " -cartoon -cute -kids").strip()[:100]
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={requests.utils.quote(safe_query)}&image_type=photo&orientation=horizontal&per_page={per_page}&safesearch=true"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json().get("hits", [])
    except Exception as e:
        print(f"⚠️ Pixabay error: {e}")
    return []

def download_file(url, out_path):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(r.content)
            return True
    except:
        pass
    return False

def clean_filename(text):
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()

def scraper_loop(target_category=None):
    registry = load_registry()
    total_downloads = 0
    
    categories_to_run = {k: v for k, v in CATEGORIAS_QUERIES.items()}
    if target_category:
        if target_category in CATEGORIAS_QUERIES:
            categories_to_run = {target_category: CATEGORIAS_QUERIES[target_category]}
        else:
            print(f"❌ Error: La categoría '{target_category}' no existe. Opciones válidas:")
            for cat in CATEGORIAS_QUERIES.keys():
                print(f"   - {cat}")
            return

    print(f"👁️ Iniciando Vault Scraper Temático.")
    print(f"   Destino: {VAULT_DIR}")
    print(f"   Categorías a procesar: {len(categories_to_run)}\n")

    for cat_name, concepts in categories_to_run.items():
        print(f"\n========================================")
        print(f"📁 CATEGORÍA: {cat_name}")
        print(f"========================================")
        clean_cat = clean_filename(cat_name)
        
        cat_downloads = 0

        for concept in concepts:
            print(f"\n🔍 Buscando concepto (query): '{concept}'")
            clean_concept = clean_filename(concept)
            downloads_done = 0

            # 1. Bajar Imágenes (Pixabay)
            target_images = 7
            target_videos = 3
            
            images = search_pixabay_images(concept, per_page=15)
            for img in images:
                if downloads_done >= target_images: break
                i_id = f"pix_i_{img['id']}"
                if i_id in registry: continue
                
                img_tags = img.get("tags", "").lower()
                if any(bad in img_tags for bad in ["cartoon", "cute", "kids", "child", "baby", "bear", "bunny", "kawaii"]):
                    print(f"   ⏩ Descartado por tags infantiles: {img_tags[:60]}")
                    continue
                
                url = img.get("largeImageURL")
                if url:
                    dest = os.path.join(IMG_DIR, f"{clean_cat}_{clean_concept}_{i_id}.jpg")
                    print(f"   ↓ Descargando foto: {os.path.basename(dest)}...", flush=True)
                    if download_file(url, dest):
                        print(f"   ✅ Foto guardada.")
                        downloads_done += 1
                        registry.add(i_id)
                        save_registry(registry)
                        time.sleep(1)

            # 2. Bajar Videos (Pexels)
            videos = search_pexels_videos(concept, per_page=10)
            for v in videos:
                if downloads_done >= (target_images + target_videos): break
                v_id = f"pex_v_{v['id']}"
                if v_id in registry: continue
                
                files = v.get("video_files", [])
                hd = [x for x in files if 1200 <= x.get("width", 0) <= 2000]
                if not hd: hd = [x for x in files if x.get("width", 0) >= 1200]
                if not hd: hd = files
                    
                if hd:
                    hd = sorted(hd, key=lambda x: x.get("size", 0) or float('inf'))
                    url = hd[0]["link"]
                    dest = os.path.join(VID_DIR, f"{clean_cat}_{clean_concept}_{v_id}.mp4")
                    print(f"   ↓ Descargando video: {os.path.basename(dest)}...", flush=True)
                    if download_file(url, dest):
                        print(f"   ✅ Video guardado.")
                        downloads_done += 1
                        registry.add(v_id)
                        save_registry(registry)
                        time.sleep(1)

            # 3. Bajar Glitches Específicos para este concepto
            glitch_queries = [f"{concept} glitch", f"{concept} broken", f"{concept} distorted"]
            glitch_downloads = 0
            for g_query in glitch_queries:
                if glitch_downloads >= 2: break
                g_videos = search_pexels_videos(g_query, per_page=5)
                for v in g_videos:
                    if glitch_downloads >= 2: break
                    v_id = f"pex_g_{v['id']}"
                    if v_id in registry: continue
                    
                    files = v.get("video_files", [])
                    hd = [x for x in files if 1200 <= x.get("width", 0) <= 2000]
                    if not hd: hd = [x for x in files if x.get("width", 0) >= 1200]
                    if not hd: hd = files
                        
                    if hd:
                        hd = sorted(hd, key=lambda x: x.get("size", 0) or float('inf'))
                        url = hd[0]["link"]
                        dest = os.path.join(GLITCH_DIR, f"{clean_cat}_{clean_concept}_{v_id}.mp4")
                        print(f"   ⚡ Descargando Glitch nativo: {os.path.basename(dest)}...", flush=True)
                        if download_file(url, dest):
                            print(f"   ✅ Glitch guardado.")
                            glitch_downloads += 1
                            registry.add(v_id)
                            save_registry(registry)
                            time.sleep(1)

            cat_downloads += downloads_done + glitch_downloads
            time.sleep(2)

        total_downloads += cat_downloads
        print(f"   > Total descargado para la categoría '{cat_name}': {cat_downloads} assets.")

    print(f"\n🎉 Lote finalizado. {total_downloads} nuevos assets ingresados a Descargas_Crudas.")

if __name__ == "__main__":
    import sys
    cat = sys.argv[1] if len(sys.argv) > 1 else None
    scraper_loop(cat)
