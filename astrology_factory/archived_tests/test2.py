import sys
from dotenv import load_dotenv
load_dotenv()
import content_factory.vault_scraper as vs
videos = vs.search_pexels_videos('Scorpio', 15)
print(f"Got {len(videos)} videos from Pexels")
for v in videos:
    files = v.get("video_files", [])
    hd = [x for x in files if x.get("quality") == "hd"]
    print(f"Video {v['id']} has {len(files)} files, {len(hd)} hd files")
images = vs.search_pixabay_images('Scorpio', 15)
print(f"Got {len(images)} images from Pixabay")
for img in images:
    url = img.get("largeImageURL")
    print(f"Image {img['id']} url: {url}")
