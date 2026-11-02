"""
test_grabador_reloj.py
Prueba de captura automatizada del Reloj Astrológico 2D usando Playwright y MediaRecorder.
"""
import os
import sys
import time
import base64
import threading
import uvicorn
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
WEB_APP_DIR = FACTORY_ROOT / "web_app"
OUTPUT_DIR = FACTORY_ROOT / "produccion" / "clips_reloj_2d"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_server(port=8765):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

def grabar_clip_reloj(fecha_iso="2026-11-02T12:00:00", duracion_seg=8, port=8765):
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1.5)

    out_file = OUTPUT_DIR / f"reloj_2d_{fecha_iso[:10]}.webm"
    print(f"🎬 Iniciando captura del Reloj 2D para fecha: {fecha_iso} ({duracion_seg}s)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="networkidle")

        setup_script = f"""
        () => {{
            document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');
            if (window.relojEngine) {{
                window.relojEngine.cambiarFondo('negro');
                window.relojEngine.timeState.currentDate = new Date('{fecha_iso}');
                window.relojEngine.timeState.isLive = true;
                window.relojEngine.timeState.timeMultiplier = 120.0;
                window.relojEngine.calculateAll();
            }}
        }}
        """
        page.evaluate(setup_script)
        page.wait_for_timeout(1000)

        record_script = f"""
        () => new Promise((resolve) => {{
            const canvas = document.getElementById('reloj-canvas');
            const stream = canvas.captureStream(30);
            const chunks = [];
            const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
            const recorder = new MediaRecorder(stream, {{ mimeType: mime, videoBitsPerSecond: 12000000 }});
            
            recorder.ondataavailable = (e) => {{
                if (e.data.size > 0) chunks.push(e.data);
            }};
            
            recorder.onstop = async () => {{
                const blob = new Blob(chunks, {{ type: 'video/webm' }});
                const reader = new FileReader();
                reader.onloadend = () => {{
                    resolve(reader.result);
                }};
                reader.readAsDataURL(blob);
            }};
            
            recorder.start();
            setTimeout(() => {{
                recorder.stop();
            }}, {duracion_seg * 1000});
        }})
        """
        print(f"⏱  Grabando canvas en vivo por {duracion_seg} segundos...")
        data_url = page.evaluate(record_script)

        header, encoded = data_url.split(",", 1)
        video_bytes = base64.b64decode(encoded)
        with open(out_file, "wb") as f:
            f.write(video_bytes)

        browser.close()

    print(f"✅ Video WebM grabado con éxito: {out_file} ({out_file.stat().st_size / (1024*1024):.2f} MB)")
    
    mp4_file = out_file.with_suffix(".mp4")
    cmd_ffmpeg = f"ffmpeg -y -i '{out_file}' -c:v libx264 -pix_fmt yuv420p -crf 18 '{mp4_file}'"
    os.system(cmd_ffmpeg)
    print(f"🚀 Video MP4 listo para edición: {mp4_file} ({mp4_file.stat().st_size / (1024*1024):.2f} MB)")
    return mp4_file

if __name__ == "__main__":
    grabar_clip_reloj("2026-11-02T12:00:00", 8)
