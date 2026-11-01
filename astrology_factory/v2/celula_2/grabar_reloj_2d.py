"""
grabar_reloj_2d.py — Capturador Cinemático del Reloj Astrológico 2D
Proyecto: El Glifo Maestro / Astrology Factory

Abre en Chromium headless el canvas de reloj.html, inyecta la fecha astronómica
exacta del tránsito, activa el modo tenebrista Ferri (fondo negro) y graba un loop
limpio en 1080x1920 (Shorts / Reels / TikTok) para ser incrustado en Toma 3.
"""

import os
import sys
import time
import base64
import argparse
import threading
import uvicorn
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
WEB_APP_DIR = FACTORY_ROOT / "web_app"
DEFAULT_OUTPUT_DIR = FACTORY_ROOT / "produccion" / "clips_reloj_2d"

def run_server(port=8765):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip_reloj(fecha_iso: str, duracion_s: float = 8.0, output_dir: Path = None, port: int = 8765) -> Path:
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = fecha_iso[:10]
    out_webm = output_dir / f"reloj_2d_{date_str}.webm"
    out_mp4 = output_dir / f"reloj_2d_{date_str}.mp4"

    # Si ya existe el clip MP4 generado para esa fecha y tiene tamaño válido (> 500 KB), reutilizarlo
    if out_mp4.exists() and out_mp4.stat().st_size > 500000:
        print(f"⚡ Clip del Reloj 2D ya existente y verificado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
        return out_mp4

    print(f"🎬 Iniciando captura del Reloj 2D para fecha {fecha_iso} ({duracion_s}s)...")

    # Iniciar servidor web si no está corriendo
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1.2)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="networkidle")

        # Inyectar configuración tenebrista y fecha exacta
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

        # Grabar canvas con MediaRecorder
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
            }}, {int(duracion_s * 1000)});
        }})
        """
        data_url = page.evaluate(record_script)
        header, encoded = data_url.split(",", 1)
        video_bytes = base64.b64decode(encoded)
        with open(out_webm, "wb") as f:
            f.write(video_bytes)

        browser.close()

    # Transcodificar a MP4 H264
    cmd_ffmpeg = f"ffmpeg -y -i '{out_webm}' -c:v libx264 -pix_fmt yuv420p -crf 18 '{out_mp4}' >/dev/null 2>&1"
    os.system(cmd_ffmpeg)
    print(f"✅ Clip MP4 del Reloj 2D generado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grabar clip del Reloj 2D para una fecha dada.")
    parser.add_argument("--fecha", type=str, default="2026-11-02T12:00:00", help="Fecha ISO (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--duracion", type=float, default=8.0, help="Duración en segundos")
    args = parser.parse_args()
    capturar_clip_reloj(args.fecha, args.duracion)
