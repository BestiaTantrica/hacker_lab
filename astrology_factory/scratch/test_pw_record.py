import os
import sys
import time
import shutil
import threading
import subprocess
from pathlib import Path

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
WEB_APP_DIR = FACTORY_ROOT / "web_app"
sys.path.insert(0, str(WEB_APP_DIR))

import uvicorn
from main import app
from playwright.sync_api import sync_playwright

TEMP_REC_DIR = Path("/tmp/pw_rec_test")
TEMP_REC_DIR.mkdir(parents=True, exist_ok=True)

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8795, log_level="error")

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
time.sleep(1.5)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
        ]
    )
    context = browser.new_context(
        record_video_dir=str(TEMP_REC_DIR),
        record_video_size={"width": 1080, "height": 1920},
        viewport={"width": 1080, "height": 1920}
    )
    page = context.new_page()
    page.goto("http://127.0.0.1:8795/reloj", wait_until="domcontentloaded")
    page.wait_for_selector("#reloj-canvas", timeout=10000)
    
    # Hide UI
    page.evaluate("document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');")
    
    # Run for 5 seconds
    t0 = time.time()
    while time.time() - t0 < 5.0:
        time.sleep(0.1)
        
    context.close()
    browser.close()

files = list(TEMP_REC_DIR.glob("*.webm"))
if files:
    latest = max(files, key=lambda f: f.stat().st_mtime)
    print(f"Recorded file: {latest} ({latest.stat().st_size / (1024*1024):.2f} MB)")
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames,duration,avg_frame_rate,r_frame_rate", str(latest)],
        capture_output=True, text=True
    )
    print(res.stdout)
