import sys
import os
import glob
import subprocess
import random
sys.path.append(os.path.dirname(__file__))
from glitch_engine import GlitchEngine

VAULT_ASSETS = "/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Reusables"

def process_event(event_name):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prod_dir = os.path.join(base_dir, "produccion", event_name)
    assets_dir = os.path.join(prod_dir, "assets")
    
    if not os.path.exists(prod_dir):
        print(f"Error: No existe {prod_dir}")
        return
        
    engine = GlitchEngine(prod_dir)
    
    # 1. Analizar el aspecto astrológico
    guion_path = os.path.join(prod_dir, "guion.txt")
    aspect = "conjuncion"
    if os.path.exists(guion_path):
        text = open(guion_path, encoding='utf-8').read().lower()
        if "cuadratura" in text: aspect = "cuadratura"
        elif "oposicion" in text or "oposición" in text: aspect = "oposicion"
        elif "conjuncion" in text or "conjunción" in text: aspect = "conjuncion"
        elif "sextil" in text: aspect = "sextil"
        elif "trigono" in text or "trígono" in text: aspect = "trigono"

    # Cargar paletas
    db_path = os.path.join(base_dir, "content_factory", "astrology_palettes.json")
    import json
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            palettes = json.load(f)
    else:
        palettes = {}

    # Lógica del Pulso Geométrico
    if aspect in palettes:
        num_pulses = palettes[aspect].get("num_pulses", 1)
    else:
        num_pulses = 1
    
    print(f"🌟 Analizando {event_name} -> Aspecto: {aspect.upper()} | Pulsos: {num_pulses}")
    
    # 2. Descubrir cuántas escenas hay
    storyboard_path = os.path.join(prod_dir, "storyboard.txt")
    num_scenes = 4 # Default if no storyboard
    if os.path.exists(storyboard_path):
        with open(storyboard_path, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
            if lines: num_scenes = len(lines)
            
    # 3. Distribuir los pulsos
    pulse_indices = []
    if num_pulses == 1:
        pulse_indices = [num_scenes // 2] # Climax
    else:
        step = max(1, num_scenes / num_pulses)
        for i in range(num_pulses):
            idx = int(i * step)
            pulse_indices.append(min(idx, num_scenes - 1))
            
    print(f"📍 Inyectando pulsos en las escenas: {pulse_indices}")
    
    # 4. Generar e inyectar
    broken_assets = glob.glob(os.path.join(VAULT_ASSETS, "*.jpg")) + glob.glob(os.path.join(VAULT_ASSETS, "*.mp4"))
    
    for i, scene_idx in enumerate(pulse_indices):
        if not broken_assets: break
        random.shuffle(broken_assets)
        selected = broken_assets[:5]
        
        # Generar clip stutter único para este pulso
        glitch_seq = engine.generate_stutter_sequence(selected, aspect, i)
        if glitch_seq and os.path.exists(glitch_seq):
            # Inyectarlo como el asset nro 3 de la escena
            target = os.path.join(assets_dir, f"{scene_idx:02d}_3_bg.mp4")
            subprocess.run(["cp", glitch_seq, target])
            print(f"✅ Pulso {i+1} inyectado como {target}")
            
    # 5. Llamar a Video Maker
    print("🎬 Renderizando video final...")
    video_maker = os.path.join(base_dir, "content_factory", "video_maker.py")
    subprocess.run([sys.executable, video_maker, event_name])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_event(sys.argv[1])
    else:
        print("Uso: python editing_reviewer.py <Nombre_Evento>")
