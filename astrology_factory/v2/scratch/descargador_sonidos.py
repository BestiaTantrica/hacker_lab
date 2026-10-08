#!/usr/bin/env python3
import os
import requests
import json
import time
from pathlib import Path

# Destino para los audios crudos que luego consumirá generador_stock_sonoro.py
DEST_DIR = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Audios")

# Lista de items de Internet Archive (Dominio Público / Creative Commons)
IA_ITEMS = {
    "cuenco_tibetano_1": "2CrystalSingingBowlSacralChakraNoteDAmySikarskie",
    "cuenco_tibetano_largo": "tibetan-sounds-bowls-sonidos-relajantes",
    "canto_gregoriano_misa": "GregorianChantMass",
    "canto_veni_creator": "VeniCreatorSpiritus",
    "om_mantra_11min": "om-mantra-meditation-11-minutes",
    "ambient_space_biosphere": "Inner_Place_Biosphere"
}

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def fetch_metadata(identifier: str):
    url = f"https://archive.org/metadata/{identifier}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"❌ Error obteniendo metadata para {identifier}: {e}")
    return None

def download_file(url: str, dest_path: Path):
    try:
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
    except Exception as e:
        print(f"❌ Error descargando archivo: {e}")
    return False

def main():
    print("🚀 Iniciando descarga de stock auditivo original (Internet Archive)...")
    ensure_dir(DEST_DIR)

    for nombre, identifier in IA_ITEMS.items():
        print(f"\n🔍 Buscando {nombre} ({identifier})...")
        meta = fetch_metadata(identifier)
        if not meta or 'files' not in meta:
            print(f"⚠️ No se encontraron archivos para {identifier}")
            continue
        
        # Filtrar solo MP3 u OGG
        archivos_audio = [f for f in meta['files'] if f['name'].endswith(('.mp3', '.ogg', '.m4a', '.wav'))]
        
        if not archivos_audio:
            print(f"⚠️ No se encontraron formatos de audio soportados para {identifier}")
            continue
            
        # Tomar el archivo más pesado (mejor calidad normalmente) o el primero
        archivos_audio.sort(key=lambda x: int(x.get('size', 0)), reverse=True)
        target_file = archivos_audio[0]['name']
        
        ext = target_file.split('.')[-1]
        out_path = DEST_DIR / f"{nombre}_raw.{ext}"
        
        if out_path.exists():
            print(f"✅ {out_path.name} ya existe. Saltando...")
            continue
            
        download_url = f"https://archive.org/download/{identifier}/{target_file}"
        print(f"⬇️ Descargando {target_file}...")
        
        if download_file(download_url, out_path):
            print(f"🎉 Guardado como: {out_path.name}")
        else:
            print("❌ Falló la descarga.")
            
        time.sleep(2) # Pausa amigable para no sobrecargar el servidor
        
    print("\n✅ Proceso completado. Los crudos están listos para ser procesados por la Célula 0.")

if __name__ == "__main__":
    main()
