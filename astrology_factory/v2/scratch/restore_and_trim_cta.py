import os
import json
import re

vademecum_path = "content_factory/vademecum.json"
base_dir = "produccion"

if not os.path.exists(vademecum_path):
    print("No vademecum.json found.")
    exit(1)

with open(vademecum_path, "r", encoding="utf-8") as f:
    data = json.load(f)

restored = 0
for item in data:
    event_name = item.get("event_name")
    if not event_name or "Octubre" not in event_name or "Resumen" in event_name:
        continue
        
    event_dir = os.path.join(base_dir, event_name)
    os.makedirs(event_dir, exist_ok=True)
    
    guion_path = os.path.join(event_dir, "guion.txt")
    if not os.path.exists(guion_path):
        guion_text = item.get("guion", "")
        # Trim the long CTA if it exists
        long_cta = "Este clima general es solo teoría hasta que cruza tu carta natal. Andá al link de mi perfil, poné tus datos exactos y calculá el impacto en tu propia vida. Tu apoyo nos permite continuar."
        short_cta = "Calculá el impacto de este tránsito en tu carta natal en el link."
        
        guion_text = guion_text.replace(long_cta, short_cta)
        
        # If they had a slightly different long CTA, let's try a regex for the last sentence
        if long_cta not in item.get("guion", "") and "link" in guion_text.lower():
             lines = guion_text.strip().split('\n')
             if len(lines) > 0 and "link" in lines[-1].lower():
                 lines[-1] = short_cta
                 guion_text = "\n".join(lines)
        
        with open(guion_path, "w", encoding="utf-8") as gf:
            gf.write(guion_text)
            
        storyboard_text = item.get("storyboard", "")
        if storyboard_text:
            with open(os.path.join(event_dir, "storyboard.txt"), "w", encoding="utf-8") as sf:
                sf.write(storyboard_text)
                
        restored += 1
        print(f"Restaurado y ajustado CTA para: {event_name}")

print(f"Total restaurados: {restored}")
