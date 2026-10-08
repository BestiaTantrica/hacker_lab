import sys
import os
import subprocess
from content_factory.audio_generator import AudioGenerator

events = ["Semana1_Octubre_Martes", "Semana1_Octubre_Miercoles"]
base_dir = os.path.dirname(__file__)
prod_dir = os.path.join(base_dir, "produccion")
audio_gen = AudioGenerator()
reviewer_script = os.path.join(base_dir, "content_factory", "editing_reviewer.py")

for event in events:
    event_dir = os.path.join(prod_dir, event)
    guion_path = os.path.join(event_dir, "guion.txt")
    mp3_path = os.path.join(event_dir, f"{event}.mp3")
    
    if os.path.exists(guion_path):
        with open(guion_path, "r", encoding="utf-8") as f:
            guion_text = f.read()
        if not os.path.exists(mp3_path):
            print(f"🎙️ Generando audio para {event}...")
            audio_gen.generate_audio(guion_text, mp3_path)
            
        print(f"🎬 Orquestando video con Glitches para {event}...")
        subprocess.run([sys.executable, reviewer_script, event])
