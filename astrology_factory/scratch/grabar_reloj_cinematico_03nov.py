"""
grabar_reloj_cinematico_03nov.py
─────────────────────────────────────────────────────────────────────────────
Capturador Cinemático de Alta Fidelidad para el 3 de Noviembre:
1. Apertura (Toma 1): 00:00 a 12:00 hs (7.5s).
   - 0.0s a 2.2s: Plano General Cósmico Completo (zoom 1.0x, centrado).
   - 2.2s a 7.5s: Zoom-in suave (1.0x -> 1.35x) con paneo inteligente hacia
     la posición de la Luna ingresando a Virgo.
   - Header superior: 3 DE NOVIEMBRE 2026 | LUNA ENTRA EN VIRGO · 1° ♍
2. Cierre (Toma 5): 12:00 a 24:00 hs (6.1s).
   - Inicia con zoom 1.35x en el tránsito.
   - Zoom-out suave regresando al centro cósmico (1.35x -> 1.0x).
   - A las 24:00:00 hs: destello áureo de fin de día (dayPulse) en los 3 anillos.
   - Termina en plano general idéntico al frame 0 de la apertura para LOOP perfecto.
─────────────────────────────────────────────────────────────────────────────
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

def run_server(port=8775):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip_cinematico(
    fecha_inicio_iso: str,
    duracion_s: float,
    multiplicador: float,
    tipo: str,
    nombre_archivo: str,
    port: int = 8775
):
    out_webm = OUTPUT_DIR / f"{nombre_archivo}.webm"
    out_mp4 = OUTPUT_DIR / f"{nombre_archivo}.mp4"

    print(f"🎬 Grabando clip cinemático '{tipo}' ({nombre_archivo}): inicio={fecha_inicio_iso}, dur={duracion_s}s...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1.0
        )
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="networkidle")

        # Configurar animación y header
        setup_script = f"""
        () => {{
            document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');
            
            if (window.relojEngine) {{
                const eng = window.relojEngine;
                eng.cambiarFondo('negro');
                eng.timeState.currentDate = new Date('{fecha_inicio_iso}');
                eng.timeState.isLive = true;
                eng.timeState.timeMultiplier = {multiplicador};
                
                window.__cineMode = '{tipo}';
                window.__cineDuration = {duracion_s};
                window.__cineStartTime = performance.now();
                window.__targetZoom = 1.35;

                const origRender = eng.render.bind(eng);
                eng.render = function() {{
                    const now = performance.now();
                    const elapsed = Math.min((now - window.__cineStartTime) / 1000, window.__cineDuration);
                    const progress = elapsed / window.__cineDuration;

                    // Easing suave cubic
                    const easeInOut = (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
                    
                    // Calcular posición actual de la Luna en coordenadas relativas al centro
                    let moonX = 0, moonY = 280; // fallback Virgo zona inferior
                    if (eng.calculated && eng.calculated.planets && eng.calculated.planets['Luna']) {{
                        const a = eng.coordToAngle(eng.calculated.planets['Luna'].grado_absoluto);
                        const r = eng.radii.planets || 310;
                        moonX = Math.cos(a) * r;
                        moonY = Math.sin(a) * r;
                    }}
                    const targetPanX = -moonX * 0.42;
                    const targetPanY = -moonY * 0.42;

                    if (window.__cineMode === 'apertura') {{
                        // Apertura:
                        // 0.0 a 2.0s: Orbe Completo centrado (zoom 1.0, pan 0,0)
                        // 2.0 a fin: Zoom suave in (1.0 -> 1.35) y paneo guiado hacia la Luna
                        if (elapsed < 2.0) {{
                            eng.camera.zoom = 1.0;
                            eng.camera.panX = 0;
                            eng.camera.panY = 0;
                        }} else {{
                            const pZoom = (elapsed - 2.0) / (window.__cineDuration - 2.0);
                            const e = easeInOut(pZoom);
                            eng.camera.zoom = 1.0 + (window.__targetZoom - 1.0) * e;
                            eng.camera.panX = targetPanX * e;
                            eng.camera.panY = targetPanY * e;
                        }}
                    }} else if (window.__cineMode === 'cierre') {{
                        // Cierre:
                        // Empieza con zoom 1.35x en el tránsito y regresa suavemente al centro (1.0x)
                        const e = easeInOut(progress);
                        eng.camera.zoom = window.__targetZoom - (window.__targetZoom - 1.0) * e;
                        eng.camera.panX = targetPanX * (1 - e);
                        eng.camera.panY = targetPanY * (1 - e);

                        // En el último tramo (fin del día 24:00 hs), activar destello cósmico
                        if (progress > 0.82) {{
                            const pFlash = (progress - 0.82) / 0.18;
                            eng.horology.flashes.dayPulse = Math.sin(pFlash * Math.PI) * 1.35;
                            eng.horology.flashes.secRing = 1.0;
                            eng.horology.flashes.minRing = 1.0;
                        }}
                    }}

                    // Renderizar mandala astrológico
                    origRender();

                    // Dibujar Header Superior Cinemático Limpio
                    const ctx = eng.ctx;
                    const w = eng.width;
                    ctx.save();
                    ctx.setTransform(1, 0, 0, 1, 0, 0);

                    // 1. Fecha Superior Principal (Oro Alquímico)
                    ctx.font = '700 36px "Cinzel", "Times New Roman", serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillStyle = '#f6c445';
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 5;
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 2;
                    ctx.fillText('3 DE NOVIEMBRE 2026', w / 2, 75);

                    // 2. Línea divisoria fina dorada
                    ctx.shadowBlur = 0;
                    ctx.strokeStyle = 'rgba(246, 196, 69, 0.45)';
                    ctx.lineWidth = 1.2;
                    ctx.beginPath();
                    ctx.moveTo(w / 2 - 160, 126);
                    ctx.lineTo(w / 2 + 160, 126);
                    ctx.stroke();

                    // Rombo áureo central
                    ctx.fillStyle = '#f6c445';
                    ctx.beginPath();
                    ctx.arc(w / 2, 126, 2.5, 0, Math.PI * 2);
                    ctx.fill();

                    // 3. Subtítulo del Tránsito (Marfil Sideral)
                    ctx.font = '600 22px "Cinzel", "Times New Roman", serif';
                    ctx.fillStyle = '#f1f5f9';
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 4;
                    ctx.shadowOffsetY = 2;
                    ctx.fillText('LUNA ENTRA EN VIRGO · 1° ♍', w / 2, 138);

                    ctx.restore();
                }};

                eng.calculateAll();
            }}
        }}
        """
        page.evaluate(setup_script)
        page.wait_for_timeout(500)

        record_script = f"""
        () => new Promise((resolve) => {{
            const canvas = document.getElementById('reloj-canvas');
            const stream = canvas.captureStream(30);
            const chunks = [];
            const mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
            const recorder = new MediaRecorder(stream, {{ mimeType: mime, videoBitsPerSecond: 25000000 }});
            
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
            
            window.__cineStartTime = performance.now();
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

    cmd_ffmpeg = f"ffmpeg -y -i '{out_webm}' -c:v libx264 -pix_fmt yuv420p -crf 15 -preset slow '{out_mp4}' >/dev/null 2>&1"
    os.system(cmd_ffmpeg)
    print(f"✅ Clip generado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4

def main():
    port = 8775
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1.5)

    # 1. Apertura: 00:00 a 12:00 (12 horas = 43200s). Duración: 7.5s -> mult = 43200/7.5 = 5760.0x
    capturar_clip_cinematico(
        fecha_inicio_iso="2026-11-03T00:00:00",
        duracion_s=7.5,
        multiplicador=5760.0,
        tipo="apertura",
        nombre_archivo="reloj_2d_2026-11-03_apertura",
        port=port
    )

    # 2. Cierre: 12:00 a 24:00 (12 horas = 43200s). Duración: 6.1s -> mult = 43200/6.1 = 7081.96x
    capturar_clip_cinematico(
        fecha_inicio_iso="2026-11-03T12:00:00",
        duracion_s=6.1,
        multiplicador=7081.96,
        tipo="cierre",
        nombre_archivo="reloj_2d_2026-11-03_cierre",
        port=port
    )
    print("✨ Ambos clips cinemáticos generados exitosamente!")

if __name__ == "__main__":
    main()
