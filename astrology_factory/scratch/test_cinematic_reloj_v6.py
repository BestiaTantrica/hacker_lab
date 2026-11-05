"""
test_cinematic_reloj_v6.py
─────────────────────────────────────────────────────────────────────────────
Capturador Cinemático de Triple Reloj 2D (Apertura, Intermedio, Cierre)
Arquitectura V6:
- Grabación nativa vía screencast CDP (Playwright record_video_dir):
    * 25-30 fps constantes, CERO caídas de frames, CERO tartamudeo.
- Velocidad de giro ultra pausada y serena (0.25h en lugar de 2h o 6h).
- Fondo cósmico activo con nebulosa / espacio profundo en cámara lenta.
- Toma 1 (Apertura - 8.0s):
    * 0.0s - 1.2s: Emergencia etérea del mandala desde el espacio estelar.
    * 1.2s - 6.8s: Contemplación majestuosa, zoom lento (0.95x -> 1.04x).
    * 6.8s - 8.0s: Salto hiperespacial acelerado (zoom 3.2x directo a 12° Escorpio)
                   + destello estelar para empalmar con xfade dissolve hacia el glifo.
- Toma 3 (Intermedio - 6.5s):
    * Encuadre directo en zoom (2.25x) sobre Luna en Virgo (17° Virgo).
    * Giro pausado, calma clínica, aspecto de sextil resaltado.
    * Píldora orgánica cyan flotante explicando el método clínico.
- Toma 5 (Cierre Inverso Simétrico - 7.5s):
    * 0.0s - 1.2s: Zoom-out rápido desde 3.2x en Escorpio hasta 1.04x.
    * 1.2s - 6.2s: Paneo fijo contemplativo con tarjetas tácticas de síntesis.
    * 6.2s - 7.5s: Zoom lento hacia 0.88x, destello áureo a las 24:00:00 hs
                   y disolvencia del mandala hacia las estrellas (loop infinito).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import time
import shutil
import threading
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
WEB_APP_DIR = FACTORY_ROOT / "web_app"
OUTPUT_DIR = FACTORY_ROOT / "produccion" / "clips_reloj_2d"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_RECORD_DIR = Path("/tmp/pw_cine_v6")
TEMP_RECORD_DIR.mkdir(parents=True, exist_ok=True)

DURACION_APERTURA_S = 8.0
DURACION_INTERMEDIO_S = 6.5
DURACION_CIERRE_S = 7.5

def run_server(port=8786):
    sys.path.insert(0, str(WEB_APP_DIR))
    import uvicorn
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip_cinematico(tipo: str, nombre_archivo: str, port: int = 8786):
    out_mp4 = OUTPUT_DIR / f"{nombre_archivo}.mp4"
    clip_rec_dir = TEMP_RECORD_DIR / tipo
    if clip_rec_dir.exists():
        shutil.rmtree(clip_rec_dir)
    clip_rec_dir.mkdir(parents=True, exist_ok=True)

    if tipo == "apertura":
        duracion_slot = DURACION_APERTURA_S
        fecha_inicio_iso = "2026-11-04T00:00:00"
        horas_recorridas = 0.25  # ~15 minutos en 8s = 3.75° (giro pausado y sereno)
    elif tipo == "intermedio":
        duracion_slot = DURACION_INTERMEDIO_S
        fecha_inicio_iso = "2026-11-04T12:00:00"
        horas_recorridas = 0.08  # ~5 minutos en 6.5s = 1.25° (prácticamente estático)
    else:  # cierre
        duracion_slot = DURACION_CIERRE_S
        fecha_inicio_iso = "2026-11-04T23:45:00"
        horas_recorridas = 0.25  # culmina exacto a las 24:00:00 hs (00:00:00 del 5 nov)

    print(f"🎬 [V6] Grabando clip cinemático '{tipo}' ({nombre_archivo}, {duracion_slot}s)...")

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
            record_video_dir=str(clip_rec_dir),
            record_video_size={"width": 1080, "height": 1920},
            viewport={"width": 1080, "height": 1920}
        )
        page = context.new_page()
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="domcontentloaded")
        page.wait_for_selector("#reloj-canvas", timeout=10000)

        # Inyectar motor cinemático
        setup_script = f"""
        () => {{
            document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');
            
            if (window.relojEngine) {{
                const eng = window.relojEngine;
                eng.timeState.isLive = false;
                
                // Activar fondo estelar cósmico
                eng.cambiarFondo('estrellas');
                if (eng.videoBg) {{
                    eng.videoBg.play().catch(() => {{}});
                    eng.videoBg.playbackRate = 0.65; // Cámara lenta majestuosa
                }}

                window.__cineMode = '{tipo}';
                window.__slotDuration = {duracion_slot};
                window.__cineStartTime = performance.now();
                window.__startMs = new Date('{fecha_inicio_iso}').getTime();
                window.__endMs = window.__startMs + {horas_recorridas} * 3600 * 1000;

                // ── ILUMINACIÓN DE ASPECTOS SAGRADOS ───────────────────────
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
                                ctx.shadowBlur = 18;
                                ctx.lineWidth = 3.5;
                            }} else {{
                                ctx.strokeStyle = '#38bdf8';
                                ctx.shadowColor = '#00f2fe';
                                ctx.shadowBlur = 18;
                                ctx.lineWidth = 3.0;
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
                            // Atenuación secundaria para no ensuciar la lectura
                            ctx.strokeStyle = asp.color;
                            ctx.globalAlpha = 0.05;
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

                    // Rotación armónica y serena del tiempo
                    const currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
                    eng.timeState.currentDate = new Date(currentClockMs);
                    eng.calculateAll();

                    const w = eng.width;
                    const h = eng.height;
                    const cx = w / 2;
                    const cy = h / 2;
                    const ctx = eng.ctx;

                    // Dibujar video espacial de fondo directamente
                    if (eng.videoBg && eng.videoBg.readyState >= 2) {{
                        ctx.drawImage(eng.videoBg, 0, 0, w, h);
                        ctx.fillStyle = 'rgba(5, 7, 14, 0.70)';
                        ctx.fillRect(0, 0, w, h);
                    }} else {{
                        ctx.fillStyle = '#05070c';
                        ctx.fillRect(0, 0, w, h);
                    }}

                    // Posición de los planetas protagonistas en el mandala
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
                    let targetPanY = -170; // Centrado armonioso sobre franja superior
                    let mandalaAlpha = 1.0;
                    let flashAlpha = 0.0;
                    let hudAlpha = 1.0;

                    const targetScreenY = 780; // Altura ideal de foco visual

                    if (window.__cineMode === 'apertura') {{
                        // APERTURA:
                        // 0s -> 1.2s: Emergencia suave del mandala desde el espacio estelar
                        // 1.2s -> 6.8s: Contemplación majestuosa, zoom lento (0.95 -> 1.04)
                        // 6.8s -> 8.0s: Salto hiperespacial acelerado hacia 12° Escorpio (Mercurio Cazimi)
                        if (progress < 0.15) {{
                            mandalaAlpha = progress / 0.15;
                        }} else {{
                            mandalaAlpha = 1.0;
                        }}

                        if (progress <= 0.85) {{
                            const pNorm = progress / 0.85;
                            targetZoom = 0.95 + pNorm * 0.09; // 0.95 a 1.04
                            targetPanX = 0;
                            targetPanY = -170;
                            hudAlpha = 1.0;
                        }} else {{
                            // SEGUNDO FINAL: Salto acelerado hacia 12° Escorpio
                            const pZoom = (progress - 0.85) / 0.15;
                            const easeZoom = Math.pow(pZoom, 2.6); // Aceleración exponencial
                            
                            targetZoom = 1.04 + easeZoom * 2.16; // Llega a 3.20x
                            
                            const s = targetZoom;
                            const finalPanX = -mercClockX * s;
                            const finalPanY = (targetScreenY - cy) - mercClockY * s;

                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -170 * (1 - easeZoom) + finalPanY * easeZoom;
                            hudAlpha = Math.max(0, 1.0 - pZoom * 2.0); // Desvanecer HUD

                            // Destello para el corte xfade
                            if (pZoom > 0.65) {{
                                flashAlpha = ((pZoom - 0.65) / 0.35) * 0.60;
                            }}
                        }}
                    }} else if (window.__cineMode === 'intermedio') {{
                        // INTERMEDIO:
                        // Entra DIRECTO con zoom (2.25x) sobre Luna en Virgo a 17°
                        targetZoom = 2.25 + Math.sin(progress * Math.PI) * 0.05;
                        const s = targetZoom;
                        targetPanX = -lunaClockX * s;
                        targetPanY = (targetScreenY - cy) - lunaClockY * s;
                        mandalaAlpha = 1.0;
                        hudAlpha = 1.0;
                    }} else {{
                        // CIERRE (Inverso Simétrico):
                        // 0s -> 1.2s: Zoom-out rápido desde 3.20x en Mercurio hasta 1.04x
                        // 1.2s -> 6.2s: Paneo fijo contemplativo con tarjetas tácticas
                        // 6.2s -> 7.5s: Zoom lento hacia 0.88x, destello áureo a las 24hs y fade out al cosmos
                        if (progress <= 0.16) {{
                            const pZoom = progress / 0.16;
                            const easeZoom = Math.pow(1 - pZoom, 2.6);
                            targetZoom = 1.04 + easeZoom * 2.16;
                            
                            const s = targetZoom;
                            const finalPanX = -mercClockX * s;
                            const finalPanY = (targetScreenY - cy) - mercClockY * s;
                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -170 * (1 - easeZoom) + finalPanY * easeZoom;
                            hudAlpha = pZoom;
                        }} else if (progress <= 0.84) {{
                            targetZoom = 1.04;
                            targetPanX = 0;
                            targetPanY = -170;
                            hudAlpha = 1.0;
                        }} else {{
                            const pEnd = (progress - 0.84) / 0.16;
                            targetZoom = 1.04 - pEnd * 0.16; // 1.04 a 0.88
                            targetPanX = 0;
                            targetPanY = -170;

                            // Chime y destello áureo al tocar 24:00:00 hs
                            const pulse = Math.sin(pEnd * Math.PI);
                            eng.horology.dayPulse = pulse * 1.8;
                            eng.horology.flashes.hourRing = pulse;
                            mandalaAlpha = Math.max(0, 1.0 - pEnd * 0.70);
                            hudAlpha = Math.max(0, 1.0 - pEnd * 1.5);
                        }}
                    }}

                    eng.camera.zoom = targetZoom;
                    eng.camera.panX = targetPanX;
                    eng.camera.panY = targetPanY;

                    // Renderizar el reloj con transparencia de emergencia / disolvencia
                    ctx.save();
                    ctx.globalAlpha = mandalaAlpha;
                    origRender();
                    ctx.restore();

                    // ── HUD ORGÁNICO & VIÑETAS FLOTANTES ───────────────────────
                    if (hudAlpha > 0.01) {{
                        ctx.save();
                        ctx.globalAlpha = hudAlpha;
                        ctx.setTransform(1, 0, 0, 1, 0, 0);

                        // Header Tenebrista
                        const gradTop = ctx.createLinearGradient(0, 0, 0, 200);
                        gradTop.addColorStop(0, 'rgba(5, 7, 12, 0.95)');
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

                        if (window.__cineMode === 'intermedio') {{
                            // Viñeta orgánica cyan para Luna en Virgo
                            const pillX = w / 2 - 240;
                            const pillY = 1320;
                            const pillW = 480;
                            const pillH = 140;

                            ctx.fillStyle = 'rgba(10, 18, 30, 0.90)';
                            ctx.strokeStyle = '#38bdf8';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#00f2fe';
                            ctx.shadowBlur = 16;
                            ctx.beginPath();
                            ctx.roundRect(pillX, pillY, pillW, pillH, 18);
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
                            ctx.shadowBlur = 14;
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
                            ctx.shadowBlur = 14;
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

                        ctx.restore();
                    }}

                    // Flash estelar de salto
                    if (flashAlpha > 0) {{
                        ctx.save();
                        ctx.setTransform(1, 0, 0, 1, 0, 0);
                        ctx.fillStyle = `rgba(255, 255, 255, ${{flashAlpha}})`;
                        ctx.fillRect(0, 0, w, h);
                        ctx.restore();
                    }}
                }};

                eng.calculateAll();
            }}
        }}
        """
        page.evaluate(setup_script)
        page.wait_for_timeout(300)

        # Dejar correr exactamente la duración requerida
        t_start = time.time()
        while time.time() - t_start < duracion_slot:
            time.sleep(0.05)

        context.close()
        browser.close()

    # Obtener el archivo WebM grabado
    webm_files = list(clip_rec_dir.glob("*.webm"))
    if not webm_files:
        raise RuntimeError(f"No se encontró archivo WebM grabado en {clip_rec_dir}")
    recorded_webm = max(webm_files, key=lambda f: f.stat().st_mtime)

    # Transcodificar a MP4 a 30 FPS exactos con libx264
    cmd_ffmpeg = (
        f"ffmpeg -y -i '{recorded_webm}' -c:v libx264 -pix_fmt yuv420p "
        f"-r 30 -crf 16 -preset slow -t {duracion_slot} '{out_mp4}' >/dev/null 2>&1"
    )
    os.system(cmd_ffmpeg)
    print(f"✅ Clip generado V6: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4

def main():
    port = 8786
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

    # 1. Apertura
    capturar_clip_cinematico(tipo="apertura", nombre_archivo="reloj_2d_2026-11-04_cinematico_apertura", port=port)

    # 2. Intermedio
    capturar_clip_cinematico(tipo="intermedio", nombre_archivo="reloj_2d_2026-11-04_cinematico_intermedio", port=port)

    # 3. Cierre
    capturar_clip_cinematico(tipo="cierre", nombre_archivo="reloj_2d_2026-11-04_cinematico_cierre", port=port)

    print("✨ ¡Los 3 clips cinemáticos V6 han sido generados con éxito!")

if __name__ == "__main__":
    main()

