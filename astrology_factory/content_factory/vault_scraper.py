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

VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables"
GLITCH_DIR = os.path.join(VAULT_DIR, "Glitches_Source")
REGISTRY_PATH = os.path.join(VAULT_DIR, "registry.json")
PALETTES_PATH = os.path.join(os.path.dirname(__file__), "transit_palettes.json")

os.makedirs(VAULT_DIR, exist_ok=True)
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
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation=landscape"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("videos", [])
    except Exception as e:
        print(f"⚠️ Pexels error: {e}")
    return []

def search_pixabay_images(query, per_page=15):
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query}&image_type=illustration&orientation=horizontal&per_page={per_page}"
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

def load_transit_data(transit_name):
    if not os.path.exists(PALETTES_PATH):
        print(f"❌ No se encontró el archivo de paletas: {PALETTES_PATH}")
        return None
    with open(PALETTES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        for t in data.get("transits", []):
            if t["name"] == transit_name:
                return t
    return None

def scraper_loop(transit_name, max_batch_per_concept=3):
    if not transit_name:
        print("❌ Error: Debes proveer el ID de un tránsito astrológico (ej. 'moon_in_aries').")
        return

    transit_data = load_transit_data(transit_name)
    if not transit_data:
        print(f"❌ Error: El tránsito '{transit_name}' no existe en transit_palettes.json.")
        return

    registry = load_registry()
    clean_transit = clean_filename(transit_name)
    concepts = transit_data.get("emotional_concepts", [])
    
    print(f"👁️ Iniciando Vault Scraper. Tránsito: '{transit_data.get('display_name')}'")
    print(f"   Se buscarán {len(concepts)} conceptos emocionales: {concepts}")
    
    total_downloads = 0

    for concept in concepts:
        print(f"\n🔍 Buscando concepto: '{concept}'")
        clean_concept = clean_filename(concept)
        downloads_done = 0

        # 1. Bajar Imágenes (Prioridad Principal: 70% del batch)
        target_images = 7
        target_videos = 3
        
        images = search_pixabay_images(concept, per_page=15)
        for img in images:
            if downloads_done >= target_images: break
            i_id = f"pix_i_{img['id']}"
            if i_id in registry: continue
            
            url = img.get("largeImageURL")
            if url:
                dest = os.path.join(VAULT_DIR, f"{clean_transit}_{clean_concept}_{i_id}.jpg")
                print(f"   ↓ Descargando foto: {os.path.basename(dest)}...", flush=True)
                if download_file(url, dest):
                    print(f"   ✅ Foto guardada.")
                    downloads_done += 1
                    registry.add(i_id)
                    save_registry(registry)
                    time.sleep(1) # Rate limit protection

        # 2. Bajar Videos (Minoría: 30% del batch)
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
                dest = os.path.join(VAULT_DIR, f"{clean_transit}_{clean_concept}_{v_id}.mp4")
                print(f"   ↓ Descargando video: {os.path.basename(dest)}...", flush=True)
                if download_file(url, dest):
                    print(f"   ✅ Video guardado.")
                    downloads_done += 1
                    registry.add(v_id)
                    save_registry(registry)
                    time.sleep(1) # Rate limit protection

        # 3. Bajar Glitches Específicos para este concepto (Semánticos)
        glitch_queries = [f"{concept} glitch", f"{concept} broken", f"{concept} distorted", f"{concept} interference"]
        glitch_downloads = 0
        for g_query in glitch_queries:
            if glitch_downloads >= 3: break
            g_videos = search_pexels_videos(g_query, per_page=10)
            for v in g_videos:
                if glitch_downloads >= 3: break
                v_id = f"pex_g_{v['id']}"
                if v_id in registry: continue
                
                files = v.get("video_files", [])
                hd = [x for x in files if 1200 <= x.get("width", 0) <= 2000]
                if not hd: hd = [x for x in files if x.get("width", 0) >= 1200]
                if not hd: hd = files
                    
                if hd:
                    hd = sorted(hd, key=lambda x: x.get("size", 0) or float('inf'))
                    url = hd[0]["link"]
                    dest = os.path.join(GLITCH_DIR, f"{clean_transit}_{clean_concept}_{v_id}.mp4")
                    print(f"   ⚡ Descargando Glitch nativo: {os.path.basename(dest)}...", flush=True)
                    if download_file(url, dest):
                        print(f"   ✅ Glitch guardado.")
                        glitch_downloads += 1
                        registry.add(v_id)
                        save_registry(registry)
                        time.sleep(1)

        total_downloads += downloads_done + glitch_downloads
        print(f"   Total descargado para '{concept}': {downloads_done} assets + {glitch_downloads} glitches")
        time.sleep(2) # Pausa entre conceptos

    print(f"\n🎉 Lote finalizado para '{transit_name}'. {total_downloads} nuevos assets ingresados a la Bóveda.")

if __name__ == "__main__":
    import sys
    transit = sys.argv[1] if len(sys.argv) > 1 else None
    batch = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    scraper_loop(transit, batch)
