import json
import subprocess
from pathlib import Path

def run():
    with open('/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Guiones/guion_resaca_eclipse_oct03.json') as f:
        guion = json.load(f)
    
    tomas = guion['tomas']
    # Insertamos un punto si no lo hay para que edge-tts respire.
    # Pero lo unimos todo en un solo string
    textos_tomas = []
    for t in tomas:
        txt = t['texto'].strip()
        if not txt.endswith('.'):
            txt += '.'
        textos_tomas.append(txt)
        
    master_text = " ".join(textos_tomas)
    
    cmd = [
        "/home/LAB/astrology_factory/venv/bin/edge-tts",
        "--voice", "es-AR-ElenaNeural",
        "--text", master_text,
        "--write-media", "test.mp3",
        "--write-subtitles", "test.vtt",
        "--rate=+0%"
    ]
    subprocess.run(cmd)

run()
