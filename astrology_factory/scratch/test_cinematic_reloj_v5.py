"""
test_cinematic_reloj_v5.py
─────────────────────────────────────────────────────────────────────────────
Capturador Cinemático de Triple Reloj 2D (Apertura, Intermedio, Cierre):
- Rotación pausada y armónica (2h en lugar de 6h o 12h, sin frenetismo).
- Fondo cósmico activo (espacio profundo / nebulosa).
- Toma 1 (Apertura):
    * Emergencia suave del mandala desde el espacio.
    * Zoom lento (0.90x -> 1.05x).
    * SEGUNDO FINAL: Zoom rápido y acelerado (ease-in a 3.0x) directo a 12° Escorpio
      (Mercurio Cazimi) + destello de salto hiperespacial para el xfade.
- Toma 3 (Intermedio - Mecánica Celeste del Relato):
    * Cámara directa en zoom (2.2x) sobre la Luna en Virgo (17° Virgo).
    * Paneo suave, rotación ultra lenta.
    * Viñeta/píldora orgánica cyan pulsante explicando el método clínico.
- Toma 5 (Cierre Inverso Simétrico):
    * PRIMER SEGUNDO: Zoom-out rápido desde 3.0x en Escorpio hacia 1.05x.
    * Parte media: Paneo fijo con tarjetas tácticas de síntesis.
    * SEGUNDO FINAL: Zoom lento a 0.90x, destello áureo de 24:00:00 hs en los anillos
      y desvanecimiento hacia el cosmos estelar (loop infinito).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import time
import base64
import threading
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
WEB_APP_DIR = FACTORY_ROOT / "web_app"
OUTPUT_DIR = FACTORY_ROOT / "produccion" / "clips_reloj_2d"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DURACION_APERTURA_S = 8.0
DURACION_INTERMEDIO_S = 6.5
DURACION_CIERRE_S = 7.5

def run_server(port=8784):
    sys.path.insert(0, str(WEB_APP_DIR))
    import uvicorn
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip(tipo: str, nombre_archivo: str, port: int = 8784):
    out_webm = OUTPUT_DIR / f"{nombre_archivo}.webm"
    out_mp4 = OUTPUT_DIR / f"{nombre_archivo}.mp4"

    if tipo == "apertura":
        duracion_slot = DURACION_APERTURA_S
        fecha_inicio_iso = "2026-11-04T00:00:00"
        horas_recorridas = 2.0
    elif tipo == "intermedio":
        duracion_slot = DURACION_INTERMEDIO_S
        fecha_inicio_iso = "2026-11-04T12:00:00"
        horas_recorridas = 0.5
    else: # cierre
        duracion_slot = DURACION_CIERRE_S
        fecha_inicio_iso = "2026-11-04T22:00:00"
        horas_recorridas = 2.0

    grabar_duracion = duracion_slot + 0.5

    print(f"🎬 Grabando clip cinemático V5 '{tipo}' ({nombre_archivo}, {duracion_slot}s)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1.0
        )
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="domcontentloaded")
        page.wait_for_selector("#reloj-canvas", timeout=10000)

        setup_script = f"""
        () => {{
            document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');
            
            if (window.relojEngine) {{
                const eng = window.relojEngine;
                eng.timeState.isLive = false;
                
                // Activar fondo estelar
                eng.cambiarFondo('estrellas');
                if (eng.videoBg) {{
                    eng.videoBg.play().catch(() => {{}});
                    eng.videoBg.playbackRate = 0.7; // cámara lenta elegante
                }}

                window.__cineMode = '{tipo}';
                window.__slotDuration = {duracion_slot};
                window.__cineStartTime = performance.now();
                window.__startMs = new Date('{fecha_inicio_iso}').getTime();
                window.__endMs = window.__startMs + {horas_recorridas} * 3600 * 1000;

                // Aspectos destacados
                eng.renderAspectLines = function(ctx) {{
                    const r = eng.radii.aspects;
                    ctx.save();

                    for (const asp of eng.calculated.aspects) {{
                        const p1 = eng.calculated.planets[asp.p1];
                        const p2 = eng.calculated.planets[asp.p2];
                        if (!p1 || !p2) continue;

                        const a1 = eng.coordToAngle(p1.grado_absoluto);
                        const a2 = eng.coordToAngle(p2.grado_absoluto);

                        const x1 = Math.cos(a1) * r;
                        const y1 = Math.sin(a1) * r;
                        const x2 = Math.cos(a2) * r;
                        const y2 = Math.sin(a2) * r;

                        const esProtagonista = (
                            (asp.p1 === 'Mercurio' && asp.p2 === 'Sol') ||
                            (asp.p1 === 'Sol' && asp.p2 === 'Mercurio') ||
                            (asp.p1 === 'Luna' && (asp.p2 === 'Mercurio' || asp.p2 === 'Sol')) ||
                            (asp.p2 === 'Luna' && (asp.p1 === 'Mercurio' || asp.p1 === 'Sol'))
                        );

                        if (esProtagonista) {{
                            ctx.save();
                            if (asp.tipo === 'Conjunción') {{
                                ctx.strokeStyle = '#f6c445';
                                ctx.shadowColor = '#fde047';
                                ctx.shadowBlur = 20;
                                ctx.lineWidth = 3.5;
                            }} else {{
                                ctx.strokeStyle = '#38bdf8';
                                ctx.shadowColor = '#00f2fe';
                                ctx.shadowBlur = 20;
                                ctx.lineWidth = 3.2;
                            }}
                            ctx.globalAlpha = 1.0;
                            ctx.beginPath();
                            ctx.moveTo(x1, y1);
                            ctx.lineTo(x2, y2);
                            ctx.stroke();

                            const mx = (x1 + x2) / 2;
                            const my = (y1 + y2) / 2;
                            ctx.fillStyle = '#ffffff';
                            ctx.beginPath();
                            ctx.arc(mx, my, 4, 0, Math.PI * 2);
                            ctx.fill();
                            ctx.restore();
                        }} else {{
                            ctx.strokeStyle = asp.color;
                            ctx.globalAlpha = 0.06;
                            ctx.lineWidth = 1.0;
                            ctx.shadowBlur = 0;
                            ctx.beginPath();
                            ctx.moveTo(x1, y1);
                            ctx.lineTo(x2, y2);
                            ctx.stroke();
                        }}
                    }}
                    ctx.restore();
                }};

                const origRender = eng.render.bind(eng);

                eng.render = function() {{
                    const now = performance.now();
                    const rawElapsed = (now - window.__cineStartTime) / 1000;
                    const elapsed = Math.min(rawElapsed, window.__slotDuration);
                    const progress = elapsed / window.__slotDuration;

                    // Rotación pausada del tiempo
                    const currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
                    eng.timeState.currentDate = new Date(currentClockMs);
                    eng.calculateAll();

                    const w = eng.width;
                    const h = eng.height;
                    const cx = w / 2;
                    const cy = h / 2;
                    const ctx = eng.ctx;

                    // Dibujar video de fondo espacial directamente en el canvas
                    if (eng.videoBg && eng.videoBg.readyState >= 2) {{
                        ctx.drawImage(eng.videoBg, 0, 0, w, h);
                        // Velo cósmico profundo
                        ctx.fillStyle = 'rgba(5, 7, 14, 0.72)';
                        ctx.fillRect(0, 0, w, h);
                    }} else {{
                        ctx.fillStyle = '#05070c';
                        ctx.fillRect(0, 0, w, h);
                    }}

                    // Posición de los planetas protagonistas en el espacio del reloj
                    const rPlanets = eng.radii.planets || 275;
                    let mercClockX = 0, mercClockY = 0;
                    let lunaClockX = 0, lunaClockY = 0;

                    if (eng.calculated && eng.calculated.planets) {{
                        if (eng.calculated.planets['Mercurio']) {{
                            const a = eng.coordToAngle(eng.calculated.planets['Mercurio'].grado_absoluto);
                            mercClockX = Math.cos(a) * rPlanets;
                            mercClockY = Math.sin(a) * rPlanets;
                        }}
                        if (eng.calculated.planets['Luna']) {{
                            const a = eng.coordToAngle(eng.calculated.planets['Luna'].grado_absoluto);
                            lunaClockX = Math.cos(a) * rPlanets;
                            lunaClockY = Math.sin(a) * rPlanets;
                        }}
                    }}

                    // ── CINEMÁTICA DE CÁMARA (ZOOM Y PAN) ──────────────────────
                    let targetZoom = 1.0;
                    let targetPanX = 0;
                    let targetPanY = -170; // Centrado sobre franja de lectura
                    let mandalaAlpha = 1.0;
                    let flashAlpha = 0.0;

                    const targetScreenY = 780; // Altura ideal para foco

                    if (window.__cineMode === 'apertura') {{
                        // APERTURA: 
                        // 0s -> 7.0s: Zoom lento (0.90 -> 1.04), emerge de las estrellas
                        // 7.0s -> 8.0s (Segundo final): Zoom rápido acelerado a 2.8x en Mercurio Cazimi
                        if (progress < 0.20) {{
                            mandalaAlpha = progress / 0.20; // Fade in cósmico
                        }} else {{
                            mandalaAlpha = 1.0;
                        }}

                        if (progress <= 0.85) {{
                            const pNorm = progress / 0.85;
                            targetZoom = 0.90 + pNorm * 0.14; // 0.90 a 1.04
                            targetPanX = 0;
                            targetPanY = -170;
                        }} else {{
                            // El segundo final: Salto hiperespacial hacia 12° Escorpio
                            const pZoom = (progress - 0.85) / 0.15; // 0 a 1
                            const easeZoom = Math.pow(pZoom, 2.5); // Aceleración exponencial
                            
                            targetZoom = 1.04 + easeZoom * 1.80; // Llega a 2.84x
                            
                            // Interpolar coordenadas de Mercurio
                            const s = targetZoom;
                            const finalPanX = -mercClockX * s;
                            const finalPanY = (targetScreenY - cy) - mercClockY * s;

                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -170 * (1 - easeZoom) + finalPanY * easeZoom;

                            // Destello en el último tramo
                            if (pZoom > 0.6) {{
                                flashAlpha = ((pZoom - 0.6) / 0.4) * 0.55;
                            }}
                        }}
                    }} else if (window.__cineMode === 'intermedio') {{
                        // INTERMEDIO:
                        // Enfocado directamente en Luna en Virgo a 17° con zoom 2.2x y paneo sutil
                        targetZoom = 2.15 + Math.sin(progress * Math.PI) * 0.08;
                        const s = targetZoom;
                        targetPanX = -lunaClockX * s;
                        targetPanY = (targetScreenY - cy) - lunaClockY * s;
                        mandalaAlpha = 1.0;
                    }} else {{
                        // CIERRE (Inverso Simétrico):
                        // 0s -> 0.15s: Zoom-out rápido desde 2.84x en Mercurio hacia 1.04x
                        // 0.15s -> 0.85s: Paneo fijo contemplativo
                        // 0.85s -> 1.0s: Zoom lento hacia 0.88x, destello áureo a las 24hs y fade out cósmico
                        if (progress <= 0.15) {{
                            const pZoom = progress / 0.15;
                            const easeZoom = Math.pow(1 - pZoom, 2.5);
                            targetZoom = 1.04 + easeZoom * 1.80;
                            
                            const s = targetZoom;
                            const finalPanX = -mercClockX * s;
                            const finalPanY = (targetScreenY - cy) - mercClockY * s;
                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -170 * (1 - easeZoom) + finalPanY * easeZoom;
                        }} else if (progress <= 0.85) {{
                            targetZoom = 1.04;
                            targetPanX = 0;
                            targetPanY = -170;
                        }} else {{
                            const pEnd = (progress - 0.85) / 0.15;
                            targetZoom = 1.04 - pEnd * 0.16; // 1.04 a 0.88
                            targetPanX = 0;
                            targetPanY = -170;

                            // Destello áureo a las 24:00:00
                            const pulse = Math.sin(pEnd * Math.PI);
                            eng.horology.dayPulse = pulse * 1.8;
                            eng.horology.flashes.hourRing = pulse;
                            mandalaAlpha = 1.0 - (pEnd * 0.25);
                        }}
                    }}

                    eng.camera.zoom = targetZoom;
                    eng.camera.panX = targetPanX;
                    eng.camera.panY = targetPanY;

                    // Renderizar el reloj con transparencia
                    ctx.save();
                    ctx.globalAlpha = mandalaAlpha;
                    origRender();
                    ctx.restore();

                    // ── HUD ORGÁNICO & VIÑETAS FLOTANTES ───────────────────────
                    ctx.save();
                    ctx.setTransform(1, 0, 0, 1, 0, 0);

                    // Header Tenebrista
                    const gradTop = ctx.createLinearGradient(0, 0, 0, 200);
                    gradTop.addColorStop(0, 'rgba(5, 7, 12, 0.96)');
                    gradTop.addColorStop(0.7, 'rgba(5, 7, 12, 0.75)');
                    gradTop.addColorStop(1, 'rgba(5, 7, 12, 0)');
                    ctx.fillStyle = gradTop;
                    ctx.fillRect(0, 0, w, 200);

                    ctx.font = '700 38px "Cinzel", "Times New Roman", serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillStyle = '#f6c445';
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 10;
                    ctx.fillText('4 DE NOVIEMBRE 2026', w / 2, 55);

                    ctx.font = '600 22px "Cinzel", "Times New Roman", serif';
                    ctx.fillStyle = '#f1f5f9';
                    ctx.shadowBlur = 6;
                    ctx.fillText('MERCURIO EN EL CORAZÓN DEL SOL · CAZIMI EN ESCORPIO', w / 2, 115);

                    // Si es el clip intermedio, mostrar píldora orgánica destacando Luna en Virgo
                    if (window.__cineMode === 'intermedio') {{
                        const pillX = w / 2 - 240;
                        const pillY = 1320;
                        const pillW = 480;
                        const pillH = 140;

                        ctx.fillStyle = 'rgba(10, 18, 30, 0.90)';
                        ctx.strokeStyle = '#38bdf8';
                        ctx.lineWidth = 2.0;
                        ctx.shadowColor = '#00f2fe';
                        ctx.shadowBlur = 20;
                        ctx.beginPath();
                        ctx.roundRect(pillX, pillY, pillW, pillH, 20);
                        ctx.fill();
                        ctx.stroke();

                        ctx.fillStyle = '#38bdf8';
                        ctx.font = '700 24px "Cinzel", sans-serif';
                        ctx.fillText('☽ LUNA EN VIRGO · 17° ♍', w / 2, pillY + 22);

                        ctx.fillStyle = '#e2e8f0';
                        ctx.font = '600 18px -apple-system, sans-serif';
                        ctx.fillText('Sextil exacto a Mercurio y Sol en Escorpio', w / 2, pillY + 62);

                        ctx.fillStyle = '#94a3b8';
                        ctx.font = '500 16px -apple-system, sans-serif';
                        ctx.fillText('Método clínico: ordenar los datos con precisión quirúrgica.', w / 2, pillY + 95);
                    }} else if (progress <= 0.85 || window.__cineMode === 'cierre') {{
                        // Tarjetas de Apertura y Cierre
                        const cardY = 1300;
                        const cardH = 200;

                        // Tarjeta Izquierda (Luna)
                        ctx.fillStyle = 'rgba(10, 16, 28, 0.88)';
                        ctx.strokeStyle = 'rgba(56, 189, 248, 0.65)';
                        ctx.lineWidth = 1.8;
                        ctx.shadowColor = '#38bdf8';
                        ctx.shadowBlur = 15;
                        ctx.beginPath();
                        ctx.roundRect(40, cardY, 480, cardH, 14);
                        ctx.fill();
                        ctx.stroke();

                        ctx.textAlign = 'left';
                        ctx.font = '700 22px "Cinzel", serif';
                        ctx.fillStyle = '#38bdf8';
                        ctx.fillText('☽ LUNA EN VIRGO 17°', 60, cardY + 24);

                        ctx.font = '500 17px -apple-system, sans-serif';
                        ctx.fillStyle = '#cbd5e1';
                        ctx.fillText('Sextil armónico: método clínico para', 60, cardY + 65);
                        ctx.fillText('ordenar sin quemarse en la intensidad.', 60, cardY + 95);

                        // Tarjeta Derecha (Mercurio Cazimi)
                        ctx.fillStyle = 'rgba(20, 15, 26, 0.88)';
                        ctx.strokeStyle = 'rgba(246, 196, 69, 0.70)';
                        ctx.lineWidth = 1.8;
                        ctx.shadowColor = '#f6c445';
                        ctx.shadowBlur = 15;
                        ctx.beginPath();
                        ctx.roundRect(560, cardY, 480, cardH, 14);
                        ctx.fill();
                        ctx.stroke();

                        ctx.font = '700 22px "Cinzel", serif';
                        ctx.fillStyle = '#f6c445';
                        ctx.fillText('☉☿ MERCURIO CAZIMI 12° ♏', 580, cardY + 24);

                        ctx.font = '500 17px -apple-system, sans-serif';
                        ctx.fillStyle = '#fef08a';
                        ctx.fillText('La mente en el corazón del Sol:', 580, cardY + 65);
                        ctx.fillText('caen las caretas y sale la verdad.', 580, cardY + 95);
                    }}

                    // Flash estelar de salto
                    if (flashAlpha > 0) {{
                        ctx.fillStyle = `rgba(255, 255, 255, ${{flashAlpha}})`;
                        ctx.fillRect(0, 0, w, h);
                    }}

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
            }}, {int(grabar_duracion * 1000)});
        }})
        """
        data_url = page.evaluate(record_script)
        header, encoded = data_url.split(",", 1)
        video_bytes = base64.b64decode(encoded)
        with open(out_webm, "wb") as f:
            f.write(video_bytes)

        browser.close()

    # Transcodificar a MP4
    cmd_ffmpeg = f"ffmpeg -y -i '{out_webm}' -c:v libx264 -pix_fmt yuv420p -crf 16 -preset slow '{out_mp4}' >/dev/null 2>&1"
    os.system(cmd_ffmpeg)
    print(f"✅ Clip generado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4

def main():
    port = 8784
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    for _ in range(40):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/reloj", timeout=1) as resp:
                if resp.status == 200:
                    print("🚀 Servidor FastAPI listo.")
                    break
        except Exception:
            time.sleep(0.3)

    # 1. Apertura (con fondo espacial, rotación pausada, y salto hiperespacial final)
    capturar_clip(tipo="apertura", nombre_archivo="reloj_2d_2026-11-04_cinematico_apertura", port=port)

    # 2. Intermedio (enfocado en Luna en Virgo, acompañando el relato de Toma 3)
    capturar_clip(tipo="intermedio", nombre_archivo="reloj_2d_2026-11-04_cinematico_intermedio", port=port)

    # 3. Cierre (zoom out rápido invertido, contemplación, destello 24hs y fade out)
    capturar_clip(tipo="cierre", nombre_archivo="reloj_2d_2026-11-04_cinematico_cierre", port=port)

    print("✨ ¡Los 3 clips cinematográficos V5 han sido generados con éxito!")

if __name__ == "__main__":
    main()

