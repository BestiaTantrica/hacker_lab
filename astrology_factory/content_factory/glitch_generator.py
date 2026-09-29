#!/usr/bin/env python3
import os
import glob
import random
import subprocess
import json

# Directorios de la Bóveda
VAULT_DIR = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables"
GLITCH_DIR = os.path.join(VAULT_DIR, "Glitches_Source")
PALETTES_FILE = os.path.join(os.path.dirname(__file__), "transit_palettes.json")

def load_palettes():
    if not os.path.exists(PALETTES_FILE): return {}
    with open(PALETTES_FILE, "r") as f:
        data = json.load(f)
        return {t["name"]: t.get("palette", {}) for t in data.get("transits", [])}

def get_color_for_transit(transit_name, palettes):
    # Retorna un color hex o nombre ffmpeg-compatible según el tránsito
    palette = palettes.get(transit_name, {})
    color = palette.get("primary", "Red").lower()
    # Map basic colors for ffmpeg
    if "rojo" in color: return "red"
    if "azul" in color: return "blue"
    if "rosa" in color or "carmesí" in color: return "deeppink"
    if "plata" in color or "gris" in color: return "gray"
    if "verde" in color: return "green"
    return "red" # fallback

def generate_glitches(num_to_generate=10):
    os.makedirs(GLITCH_DIR, exist_ok=True)
    assets = glob.glob(os.path.join(VAULT_DIR, "*.*"))
    assets = [f for f in assets if f.endswith(".jpg") or f.endswith(".mp4")]
    
    if not assets:
        print("No hay assets locales para glitchear.")
        return

    palettes = load_palettes()
    
    generated = 0
    while generated < num_to_generate:
        asset = random.choice(assets)
        basename = os.path.basename(asset)
        parts = basename.split("_")
        
        if len(parts) >= 2:
            # Asumimos que los primeros 2/3 son el transito ej: mars_sextile_uranus_...
            # Intentaremos machear el inicio del filename con los transitos conocidos
            transit = "unknown"
            for t in palettes.keys():
                if basename.startswith(t):
                    transit = t
                    break
            
            color = get_color_for_transit(transit, palettes)
            
            out_name = f"glitch_gen_{generated}_{basename}"
            out_name = out_name.replace(".jpg", ".mp4") # Forzamos salida de video corto
            out_path = os.path.join(GLITCH_DIR, out_name)
            
            if os.path.exists(out_path):
                continue
                
            print(f"⚡ Generando glitch ({color}) para {basename}...")
            
            dur = "0.5" # 0.5 segundos de glitch
            
            cmd = ["ffmpeg", "-y"]
            if asset.endswith(".jpg"):
                cmd.extend(["-loop", "1", "-t", dur, "-i", asset])
            else:
                cmd.extend(["-t", dur, "-i", asset])
                
            # Filtro complejo para RGB split agresivo y tint
            fc = (
                f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"colorchannelmixer=rr=2:gg=0:bb=0[r];"
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"colorchannelmixer=rr=0:gg=2:bb=0[g];"
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                f"colorchannelmixer=rr=0:gg=0:bb=2[b];"
                f"[r]crop=1070:1920:10:0,pad=1080:1920:0:0[r_shifted];"
                f"[g]crop=1080:1910:0:10,pad=1080:1920:0:0[g_shifted];"
                f"[r_shifted][g_shifted]blend=all_mode=addition[rg];"
                f"[rg][b]blend=all_mode=addition,format=yuv420p,"
                f"colorlevels=rimin=0.0:gimin=0.0:bimin=0.0:rimax=1.0:gimax=1.0:bimax=1.0,"
                f"noise=alls=100:allf=t+u,"
                f"drawbox=y=ih/2:color={color}@0.3:width=iw:height=ih/4:t=fill"
            )
            
            cmd.extend([
                "-filter_complex", fc,
                "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
                out_path
            ])
            
            r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode == 0:
                generated += 1
                print(f"   ✅ Guardado en {out_name}")
            else:
                print(f"   ❌ Fallo al generar {out_name}")

if __name__ == "__main__":
    print("Iniciando Motor de Glitches Híbrido...")
    generate_glitches(20)
    print("✅ Generación completa.")
