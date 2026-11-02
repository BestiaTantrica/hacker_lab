"""
test_grabador_reloj_loop.py
Prueba de captura de dos clips del Reloj 2D para Noviembre 3:
1. Apertura (Toma 1): 00:00 a 12:00 (12 horas exactas, 180° de ciclo celestial) con zoom sutil hacia la Luna en Virgo.
2. Cierre (Toma 5): 12:00 a 24:00 (12 horas exactas, completando las 24h del día para loop perfecto).
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

def run_server(port=8766):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip(fecha_inicio_iso: str, duracion_s: float, multiplicador: float, zoom: float, pan_x: float, pan_y: float, nombre_archivo: str, port=8766):
    out_webm = OUTPUT_DIR / f"{nombre_archivo}.webm"
    out_mp4 = OUTPUT_DIR / f"{nombre_archivo}.mp4"

    print(f"🎬 Grabando {nombre_archivo}: inicio={fecha_inicio_iso}, dur={duracion_s}s, vel={multiplicador}x, zoom={zoom}x...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="networkidle")

        # Configurar cámara, fecha y fondo
        setup_script = f"""
        () => {{
            document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');
            if (window.relojEngine) {{
                window.relojEngine.cambiarFondo('negro');
                window.relojEngine.timeState.currentDate = new Date('{fecha_inicio_iso}');
                window.relojEngine.timeState.isLive = true;
                window.relojEngine.timeState.timeMultiplier = {multiplicador};
                window.relojEngine.camera.zoom = {zoom};
                window.relojEngine.camera.panX = {pan_x};
                window.relojEngine.camera.panY = {pan_y};
                window.relojEngine.calculateAll();
            }}
        }}
        """
        page.evaluate(setup_script)
        page.wait_for_timeout(800)

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
            
            recorder.onstop = () => {{
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

    cmd_ffmpeg = f"ffmpeg -y -i '{out_webm}' -c:v libx264 -pix_fmt yuv420p -crf 18 '{out_mp4}' >/dev/null 2>&1"
    os.system(cmd_ffmpeg)
    print(f"✅ Clip generado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4

def main():
    port = 8766
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1.2)

    # 1. Clip Apertura (Toma 1): 3 de Noviembre 00:00 a 12:00 (12 horas = 43200s). En 7.5s -> mult = 43200/7.5 = 5760.
    # Zoom suave 1.3x hacia la zona de Virgo / Horizonte oriental
    capturar_clip(
        fecha_inicio_iso="2026-11-03T00:00:00",
        duracion_s=7.5,
        multiplicador=5760.0,
        zoom=1.35,
        pan_x=-80,
        pan_y=50,
        nombre_archivo="reloj_2d_2026-11-03_apertura",
        port=port
    )

    # 2. Clip Cierre (Toma 5): 3 de Noviembre 12:00 a 24:00 (otras 12 horas). Cierre en plano general cósmico (zoom 1.0x)
    capturar_clip(
        fecha_inicio_iso="2026-11-03T12:00:00",
        duracion_s=6.5,
        multiplicador=6646.0,  # 43200s / 6.5s = 6646.15x
        zoom=1.0,
        pan_x=0,
        pan_y=0,
        nombre_archivo="reloj_2d_2026-11-03_cierre",
        port=port
    )
    print("🚀 Ambos clips de inicio y cierre generados exitosamente!")

if __name__ == "__main__":
    main()
