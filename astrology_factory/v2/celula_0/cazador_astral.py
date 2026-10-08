#!/usr/bin/env python3
"""
🌔 CÉLULA 0 — Script 0.1: cazador_astral.py
El Recolector Automatizado de Assets Astrológicos.
Este script se conecta a Pexels y Pixabay para buscar y descargar imágenes/videos
respetando una Taxonomía Astrológica estricta (Fuego, Agua, Tierra, Aire).
"""

import os
import json
import time
import requests
import re
from pathlib import Path
from dotenv import load_dotenv

FACTORY_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(FACTORY_ROOT / ".env")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

VAULT_BASE = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados")
REGISTRY_PATH = VAULT_BASE / "registry.json"

# Filtro de Calidad: Términos PROHIBIDOS en la bóveda
EXCLUSION_TERMS = {
    "bear", "oso", "child", "baby", "cute", "kids", "cartoon", "toy",
    "doll", "puppet", "bunny", "rabbit", "unicorn", "fairy", "princess",
    "kawaii", "chibi", "anime", "clipart", "vector", "sticker",
    "family", "home", "mother", "father", "parent", "domestic",
    "kitchen", "living", "bedroom", "house", "garden", "backyard",
    "smile", "happy", "cheerful", "lifestyle", "dog", "cat", "pet",
    "office", "business", "work", "computer"
}

EXCLUSION_QUERY_SUFFIX = " -cartoon -cute -baby"

def load_registry():
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r") as f:
            return set(json.load(f))
    return set()

def save_registry(registry):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(list(registry), f)

def search_pexels_videos(query, per_page=15):
    safe_query = query.strip()
    # Para TikToks/Shorts pedimos orientation=portrait
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(safe_query)}&per_page={per_page}&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json().get("videos", [])
    except Exception as e:
        print(f"⚠️ Pexels error: {e}")
    return []

def search_pixabay_images(query, per_page=15):
    safe_query = query.strip()
    url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={requests.utils.quote(safe_query)}&image_type=photo&orientation=vertical&per_page={per_page}&safesearch=true"
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
    except Exception as e:
        print(f"⚠️ Error descarga: {e}")
    return False

def clean_filename(text):
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()

def cazar_recursos(elemento: str, sujeto: str, query: str, limit_videos: int = 3, limit_images: int = 7):
    """
    Elemento: Fuego, Agua, Tierra, Aire
    Sujeto: Aries, Sol, Marte, etc.
    """
    target_dir = VAULT_BASE / elemento.capitalize() / sujeto.capitalize()
    target_dir.mkdir(parents=True, exist_ok=True)
    
    registry = load_registry()
    downloads_done = 0
    clean_concept = clean_filename(query)

    print(f"\n🏹 CAZADOR ASTRAL 🏹")
    print(f"Buscando: '{query}' -> Guardando en {target_dir.relative_to(VAULT_BASE)}")

    # 1. Bajar Imágenes (Pixabay)
    images = search_pixabay_images(query, per_page=15)
    img_dls = 0
    for img in images:
        if img_dls >= limit_images: break
        i_id = f"pix_i_{img['id']}"
        if i_id in registry: continue
        
        img_tags = img.get("tags", "").lower()
        if any(bad in img_tags for bad in EXCLUSION_TERMS):
            continue
            
        url = img.get("largeImageURL")
        if url:
            dest = target_dir / f"{clean_concept}_{i_id}.jpg"
            print(f"   ↓ [IMG] Descargando {dest.name}...", flush=True)
            if download_file(url, dest):
                downloads_done += 1
                img_dls += 1
                registry.add(i_id)
                save_registry(registry)
                time.sleep(1)

    # 2. Bajar Videos (Pexels)
    videos = search_pexels_videos(query, per_page=15)
    vid_dls = 0
    for v in videos:
        if vid_dls >= limit_videos: break
        v_id = f"pex_v_{v['id']}"
        if v_id in registry: continue
        
        files = v.get("video_files", [])
        # Preferir resoluciones verticales 1080x1920 o cercanas
        hd = [x for x in files if x.get("height", 0) >= 1200]
        if not hd: hd = files
            
        if hd:
            hd = sorted(hd, key=lambda x: x.get("size", 0) or float('inf'))
            url = hd[0]["link"]
            dest = target_dir / f"{clean_concept}_{v_id}.mp4"
            print(f"   ↓ [VID] Descargando {dest.name}...", flush=True)
            if download_file(url, dest):
                downloads_done += 1
                vid_dls += 1
                registry.add(v_id)
                save_registry(registry)
                time.sleep(1)

    print(f"\n🎉 Cacería terminada. {img_dls} imágenes y {vid_dls} videos ingresados a {elemento}/{sujeto}.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Descarga assets astrológicos.")
    parser.add_argument("--elemento", required=True, help="Ej: Fuego, Agua, Tierra, Aire")
    parser.add_argument("--sujeto", required=True, help="Ej: Aries, Sol, Marte, Escorpio")
    parser.add_argument("--query", required=True, help="Ej: 'fire sparks dark', 'ocean waves mystic'")
    parser.add_argument("--videos", type=int, default=3, help="Cantidad de videos a buscar")
    parser.add_argument("--imagenes", type=int, default=7, help="Cantidad de imágenes a buscar")
    args = parser.parse_args()
    
    cazar_recursos(args.elemento, args.sujeto, args.query, args.videos, args.imagenes)
