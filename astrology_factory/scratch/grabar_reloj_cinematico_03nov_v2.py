"""
grabar_reloj_cinematico_03nov_v2.py
─────────────────────────────────────────────────────────────────────────────
Capturador Cinemático de Máxima Precisión Matemática (3 de Noviembre 2026):

Slot exacto: 6.296 segundos (6296 ms)

1. Apertura (Toma 1): 00:00 a 12:00 hs (exacto).
   - Inicia de inmediato (t=0) con zoom fluido y directo al hueso (1.0x -> 1.38x).
   - Paneo guiado exacto: centra la Luna en Virgo en el punto focal (540, 880).
   - A los 2.6s ya queda encuadrado el tránsito.
   - De 2.6s a 6.296s (3.7s completos): sostiene el plano fijo sobre la Luna en Virgo,
     legible, nítido y claro antes de la transición.
   - Header superior limpio: "3 DE NOVIEMBRE 2026 | LUNA ENTRA EN VIRGO · 1° ♍"

2. Cierre (Toma 5): 12:00 a 24:00 hs (exacto).
   - De 0.0s a 1.0s: inicia encuadrado en el tránsito en Virgo (reconocimiento visual).
   - De 1.0s a 4.4s: zoom-out suave regresando al centro cósmico (1.38x -> 1.0x).
   - De 4.4s a 6.296s: orbe 100% centrado a 1.0x.
   - En t=5.2s a 6.296s: el reloj alcanza con exactitud matemática las 24:00:00 hs
     y activa el destello áureo en los 3 anillos (dayPulse).
   - En t=6.296s clava EXACTAMENTE en 24:00:00 (00:00:00), idéntico a frame 0 de Apertura.
   - Cero desfasaje, cero sobrevuelo del tiempo, loop infinito perfecto.
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

SLOT_DURACION_S = 6.296  # Exacto según lista_de_corte_validada
GRABAR_DURACION_S = 7.5  # Grabamos 7.5s para que el video dure ~7.2s y validador aplique TRIM a 6.296s (cero loop)

def run_server(port=8782):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip(tipo: str, nombre_archivo: str, port: int = 8782):
    out_webm = OUTPUT_DIR / f"{nombre_archivo}.webm"
    out_mp4 = OUTPUT_DIR / f"{nombre_archivo}.mp4"

    fecha_inicio_iso = "2026-11-03T00:00:00" if tipo == "apertura" else "2026-11-03T12:00:00"
    print(f"🎬 Grabando clip cinemático V2 '{tipo}' ({nombre_archivo})...")

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
                eng.timeState.isLive = false; // Control determinista por cuadro
                
                window.__cineMode = '{tipo}';
                window.__slotDuration = {SLOT_DURACION_S};
                window.__cineStartTime = performance.now();
                window.__startMs = new Date('{fecha_inicio_iso}').getTime();
                window.__endMs = window.__startMs + 12 * 3600 * 1000; // Exacto 12 horas
                window.__targetZoom = 1.38;

                const origRender = eng.render.bind(eng);
                eng.render = function() {{
                    const now = performance.now();
                    const rawElapsed = (now - window.__cineStartTime) / 1000;
                    // El tiempo se congela en el slot exacto (6.296s)
                    const elapsed = Math.min(rawElapsed, window.__slotDuration);
                    const progress = elapsed / window.__slotDuration; // 0.0 a 1.0 exacto

                    // 1. Reloj astronómico: fecha exacta sin desfasaje
                    const currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
                    eng.timeState.currentDate = new Date(currentClockMs);
                    eng.calculateAll();

                    // 2. Coordenadas de la Luna para paneo inteligente al punto focal (540, 880)
                    let moonX = 0, moonY = 300;
                    if (eng.calculated && eng.calculated.planets && eng.calculated.planets['Luna']) {{
                        const a = eng.coordToAngle(eng.calculated.planets['Luna'].grado_absoluto);
                        const r = eng.radii.planets || 310;
                        moonX = Math.cos(a) * r;
                        moonY = Math.sin(a) * r;
                    }}

                    // Para situar la Luna cómodamente encuadrada en (540, 960-980) sin colisionar con el header:
                    const targetPanX = -moonX * window.__targetZoom;
                    const targetPanY = 20 - moonY * window.__targetZoom;

                    // Curvas de animación cinemática
                    if (window.__cineMode === 'apertura') {{
                        // Apertura:
                        // 0.0s a 2.6s: Zoom directo al hueso y fluido (1.0x -> 1.38x) con desaceleración suave
                        // 2.6s a 6.296s: Sostiene encuadre perfecto en la Luna para máxima legibilidad
                        const pIn = Math.min(1.0, elapsed / 2.6);
                        const easeOut = 1 - Math.pow(1 - pIn, 2.5); // Rápido al inicio, se posa suave
                        
                        eng.camera.zoom = 1.0 + (window.__targetZoom - 1.0) * easeOut;
                        eng.camera.panX = targetPanX * easeOut;
                        eng.camera.panY = targetPanY * easeOut;

                    }} else if (window.__cineMode === 'cierre') {{
                        // Cierre:
                        // 0.0s a 1.0s: Inicia encuadrado en la Luna en Virgo (reconocimiento visual)
                        // 1.0s a 4.4s: Zoom-out suave regresando al centro cósmico (1.38x -> 1.0x)
                        // 4.4s a 6.296s: Cámara 100% centrada (1.0x, pan 0,0)
                        if (elapsed < 1.0) {{
                            eng.camera.zoom = window.__targetZoom;
                            eng.camera.panX = targetPanX;
                            eng.camera.panY = targetPanY;
                        }} else if (elapsed < 4.4) {{
                            const pOut = (elapsed - 1.0) / (4.4 - 1.0);
                            const easeInOut = pOut < 0.5 ? 4 * pOut * pOut * pOut : 1 - Math.pow(-2 * pOut + 2, 3) / 2;
                            eng.camera.zoom = window.__targetZoom - (window.__targetZoom - 1.0) * easeInOut;
                            eng.camera.panX = targetPanX * (1 - easeInOut);
                            eng.camera.panY = targetPanY * (1 - easeInOut);
                        }} else {{
                            eng.camera.zoom = 1.0;
                            eng.camera.panX = 0;
                            eng.camera.panY = 0;
                        }}

                        // Destello áureo cósmico en las 24:00:00 hs (último 15% del tiempo)
                        if (progress > 0.85) {{
                            const pFlash = (progress - 0.85) / 0.15;
                            const flashIntensity = Math.sin(pFlash * Math.PI);
                            eng.horology.flashes.dayPulse = flashIntensity * 1.5;
                            eng.horology.flashes.secRing = flashIntensity * 1.2;
                            eng.horology.flashes.minRing = flashIntensity * 1.2;
                        }} else {{
                            eng.horology.flashes.dayPulse = 0;
                            eng.horology.flashes.secRing = 0;
                            eng.horology.flashes.minRing = 0;
                        }}
                    }}

                    // Renderizar mandala astrológico
                    origRender();

                    // Dibujar Header Superior Cinemático Limpio con Velo Tenebrista
                    const ctx = eng.ctx;
                    const w = eng.width;
                    ctx.save();
                    ctx.setTransform(1, 0, 0, 1, 0, 0);

                    // Velo sutil degradado para aislamiento del título
                    const grad = ctx.createLinearGradient(0, 0, 0, 210);
                    grad.addColorStop(0, 'rgba(0, 0, 0, 0.95)');
                    grad.addColorStop(0.65, 'rgba(0, 0, 0, 0.75)');
                    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
                    ctx.fillStyle = grad;
                    ctx.fillRect(0, 0, w, 210);

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
        page.wait_for_timeout(400)

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
            }}, {int(GRABAR_DURACION_S * 1000)});
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
    port = 8782
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(2.0)

    # 1. Apertura
    capturar_clip(tipo="apertura", nombre_archivo="reloj_2d_2026-11-03_apertura", port=port)

    # 2. Cierre
    capturar_clip(tipo="cierre", nombre_archivo="reloj_2d_2026-11-03_cierre", port=port)

    print("✨ Clips cinematográficos V2 generados con máxima precisión!")

if __name__ == "__main__":
    main()
