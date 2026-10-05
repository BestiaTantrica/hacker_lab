import os
import subprocess
from pathlib import Path

def run():
    dest_dir = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Audios")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # We will download short 10-minute ambient tracks to avoid massive file sizes
    tracks = [
        {"url": "https://www.youtube.com/watch?v=1ZYbU82GVz4", "name": "432Hz_Ambient"}, # Generic known meditation audio
        {"url": "https://www.youtube.com/watch?v=FjHGZj2IjT0", "name": "Om_Mantra_Bowls"},
        {"url": "https://www.youtube.com/watch?v=WUXEau5CuPM", "name": "Gregorian_Chant_Dark"}
    ]
    
    for t in tracks:
        out_path = dest_dir / f"{t['name']}.mp3"
        if out_path.exists():
            print(f"Ya existe {out_path.name}")
            continue
            
        print(f"Descargando {t['name']}...")
        # Limitar a 10 minutos (600s) para que no tarde 1 hora
        cmd = [
            "python3", "-m", "yt_dlp",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "5",
            "--max-filesize", "50M",
            "--match-filter", "duration < 1200",
            "-o", str(out_path),
            t["url"]
        ]
        # Si fallamos por ID específico, intentamos buscar genéricamente
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"Falla directa con ID, intentando búsqueda genérica para {t['name']}...")
                cmd_search = [
                    "python3", "-m", "yt_dlp",
                    "-x", "--audio-format", "mp3",
                    "--match-filter", "duration < 600",
                    "ytsearch1:" + t['name'].replace("_", " "),
                    "-o", str(out_path)
                ]
                subprocess.run(cmd_search, check=True)
        except Exception as e:
            print(f"Error descargando {t['name']}: {e}")

if __name__ == "__main__":
    run()
