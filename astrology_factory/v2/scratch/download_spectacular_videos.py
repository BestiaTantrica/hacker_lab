import os, requests, urllib.parse
from pathlib import Path
import random

PEXELS_API_KEY = "7K2mt0pIWQ3Ic5hBDhqHC2QCaxrhAIIrdN8UEGxbtHiztwJxsBf20zG3"
queries = [
    "space nebula animation",
    "galaxy zoom fly",
    "sacred geometry loop",
    "esoteric energy flowing",
    "abstract mystical light",
    "wormhole space travel",
    "stars hyperspace"
]

dest_dir = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Oct_W1")
dest_dir.mkdir(parents=True, exist_ok=True)

headers = {"Authorization": PEXELS_API_KEY}

downloaded = 0
for q in queries:
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&per_page=3&orientation=portrait"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        videos = r.json().get("videos", [])
        for v in videos:
            files = sorted(v.get("video_files", []), key=lambda x: x.get("width", 0), reverse=True)
            if files:
                best_url = files[0]["link"]
                dest = dest_dir / f"spectacular_{q.replace(' ', '_')}_{v['id']}.mp4"
                if not dest.exists():
                    print(f"Downloading {q} -> {dest.name}")
                    r2 = requests.get(best_url, stream=True)
                    with open(dest, "wb") as f:
                        for chunk in r2.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded += 1
                    if downloaded >= 20:
                        break
    if downloaded >= 20:
        break

print(f"Downloaded {downloaded} spectacular videos!")
