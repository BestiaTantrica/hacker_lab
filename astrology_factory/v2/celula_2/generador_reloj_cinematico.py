#!/usr/bin/env python3
"""
🌓 CÉLULA 2 — generador_reloj_cinematico.py
─────────────────────────────────────────────────────────────────────────────
Motor Cinemático del Reloj Astrológico 2D (Apertura, Intermedio, Cierre)
Proyecto: El Glifo Maestro / Astrology Factory

Arquitectura y Coreografía Visual:
1. Grabación nativa vía screencast CDP en Playwright (30 FPS constantes, cero drops).
2. Velocidad de rotación ultra pausada y serena (micro-drift de 3° a 4° en total).
3. Fondo cósmico activo en cámara lenta con velo tenebrista.
4. Separación Cielo ↔ Tierra:
   - Cielo (Tomas 1, 3, 5): Reloj 2D cósmico inmersivo.
   - Tierra (Tomas 2, 4): Glifos canónicos tenebristas (vivencia psicológica humana).
5. Toma 1 (Apertura):
   - 0.0s a 1.0s: Emergencia suave del mandala desde el espacio profundo.
   - 1.0s a 5.8s: Contemplación majestuosa, zoom lento (0.95x -> 1.04x).
   - 5.8s a 7.1s (SEGUNDO FINAL): Salto hiperespacial acelerado (zoom a 3.2x directo
     al grado del tránsito clave) + destello estelar para fundir en xfade.
6. Toma 3 (Intermedio - Mecánica Celeste del Relato):
   - Encuadre directo en zoom (2.25x) sobre el planeta o aspecto que narra el relato
     (ej: Luna en Virgo 17° con sextil a Mercurio/Sol).
   - Giro sereno, calma clínica, píldora orgánica cyan pulsante.
7. Toma 5 (Cierre Inverso Simétrico):
   - 0.0s a 1.0s: Salida del hiperespacio (zoom-out rápido de 3.2x a 1.04x).
   - 1.0s a 5.2s: Paneo fijo contemplativo con tarjetas tácticas y llamada a la acción.
   - 5.2s a 6.35s: Zoom lento hacia 0.88x, destello áureo a las 24:00:00 hs
     y desvanecimiento hacia el cosmos estelar (loop infinito).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import time
import json
import shutil
import argparse
import threading
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path(__file__).resolve().parents[2]
WEB_APP_DIR = FACTORY_ROOT / "web_app"
DEFAULT_OUTPUT_DIR = FACTORY_ROOT / "produccion" / "clips_reloj_2d"
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_RECORD_DIR = Path("/tmp/pw_cine_engine")
TEMP_RECORD_DIR.mkdir(parents=True, exist_ok=True)

def iniciar_servidor(port: int = 8788):
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", str(port),
        "--log-level", "error"
    ]
    proc = subprocess.Popen(cmd, cwd=str(WEB_APP_DIR), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Esperar hasta que responda HTTP 200
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/reloj", timeout=1.0) as resp:
                if resp.status == 200:
                    print(f"🚀 Servidor FastAPI listo en puerto {port} (PID: {proc.pid}).")
                    return proc
        except Exception:
            time.sleep(0.3)
    proc.terminate()
    raise RuntimeError(f"No se pudo iniciar el servidor web en el puerto {port}")

def capturar_clip(
    tipo: str,
    nombre_archivo: str,
    fecha_iso: str,
    duracion_s: float,
    planeta_foco: str = "Luna",
    planeta_intermedio: str = "Venus",
    header_fecha: str = "5 DE NOVIEMBRE 2026",
    header_sub: str = "LUNA EN LIBRA · SEXTIL VENUS Y JÚPITER",
    pildora_titulo: str = "♀ VENUS SEXTIL JÚPITER · 24° ♎ ♌",
    pildora_sub: str = "Sextil exacto: diplomacia, encanto y generosidad",
    pildora_body: str = "Pactar con altura sin regalar tu valor propio.",
    tarjeta1_titulo: str = "☽ LUNA EN LIBRA 0°",
    tarjeta1_body: str = "Gran Trígono de Aire: visión y balance sin complacencia sumisa.",
    tarjeta2_titulo: str = "♀ VENUS SEXTIL JÚPITER 24°",
    tarjeta2_body: str = "Generosidad soberana: acordar con altura y valor propio.",
    port: int = 8788,
    output_dir: Path = DEFAULT_OUTPUT_DIR
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = output_dir / f"{nombre_archivo}.mp4"
    clip_rec_dir = TEMP_RECORD_DIR / tipo
    if clip_rec_dir.exists():
        shutil.rmtree(clip_rec_dir)
    clip_rec_dir.mkdir(parents=True, exist_ok=True)

    date_str = fecha_iso[:10]
    
    if tipo == "apertura":
        fecha_inicio_iso = f"{date_str}T00:00:00"
        horas_recorridas = 0.25  # ~15 min en 7s = 3.75° (giro suave y sereno)
    elif tipo == "intermedio":
        fecha_inicio_iso = f"{date_str}T12:00:00"
        horas_recorridas = 0.08  # ~5 min (prácticamente estático)
    else:  # cierre
        fecha_inicio_iso = f"{date_str}T23:45:00"
        horas_recorridas = 0.25  # culmina exacto a las 24:00:00 hs

    print(f"🎬 [Motor Cinemático] Grabando '{tipo}' ({nombre_archivo}.mp4, {duracion_s:.2f}s)...")

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

        # Inyectar motor de animación cinemática
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
                    eng.videoBg.playbackRate = 0.65;
                }}

                window.__cineMode = '{tipo}';
                window.__slotDuration = {duracion_s};
                window.__cineStartTime = performance.now();
                window.__startMs = new Date('{fecha_inicio_iso}').getTime();
                window.__endMs = window.__startMs + {horas_recorridas} * 3600 * 1000;
                window.__planetaFoco = '{planeta_foco}';
                window.__planetaIntermedio = '{planeta_intermedio}';

                // Iluminación quirúrgica de aspectos protagonistas
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
                            (asp.p1 === 'Venus' && asp.p2 === 'Júpiter') ||
                            (asp.p2 === 'Venus' && asp.p1 === 'Júpiter') ||
                            (asp.p1 === 'Luna' && (asp.p2 === 'Plutón' || asp.p2 === 'Urano' || asp.p2 === 'Neptuno')) ||
                            (asp.p2 === 'Luna' && (asp.p1 === 'Plutón' || asp.p1 === 'Urano' || asp.p1 === 'Neptuno'))
                        );

                        if (esProtagonista) {{
                            ctx.save();
                            if (asp.tipo === 'Sextil' || asp.tipo === 'Trígono') {{
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

                    // Avance de tiempo armónico
                    const currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
                    eng.timeState.currentDate = new Date(currentClockMs);
                    eng.calculateAll();

                    const w = eng.width;
                    const h = eng.height;
                    const cx = w / 2;
                    const cy = h / 2;
                    const ctx = eng.ctx;

                    // Fondo cósmico activo con velo tenebrista
                    if (eng.videoBg && eng.videoBg.readyState >= 2) {{
                        ctx.drawImage(eng.videoBg, 0, 0, w, h);
                        ctx.fillStyle = 'rgba(5, 7, 14, 0.70)';
                        ctx.fillRect(0, 0, w, h);
                    }} else {{
                        ctx.fillStyle = '#05070c';
                        ctx.fillRect(0, 0, w, h);
                    }}

                    // Posiciones de los planetas protagonistas
                    const rPlanets = eng.radii.planets || 275;
                    let focoClockX = 0, focoClockY = 0;
                    let interClockX = 0, interClockY = 0;

                    if (eng.calculated && eng.calculated.planets) {{
                        if (eng.calculated.planets[window.__planetaFoco]) {{
                            const a = eng.coordToAngle(eng.calculated.planets[window.__planetaFoco].grado_absoluto);
                            focoClockX = Math.cos(a) * rPlanets;
                            focoClockY = Math.sin(a) * rPlanets;
                        }}
                        if (eng.calculated.planets[window.__planetaIntermedio]) {{
                            const a = eng.coordToAngle(eng.calculated.planets[window.__planetaIntermedio].grado_absoluto);
                            interClockX = Math.cos(a) * rPlanets;
                            interClockY = Math.sin(a) * rPlanets;
                        }}
                    }}

                    // ── CINEMÁTICA DE CÁMARA (ZOOM Y PAN) ──────────────────────
                    let targetZoom = 1.0;
                    let targetPanX = 0;
                    let targetPanY = -170; // Centrado en franja de lectura
                    let mandalaAlpha = 1.0;
                    let flashAlpha = 0.0;
                    let hudAlpha = 1.0;

                    const targetScreenY = 780;

                    if (window.__cineMode === 'apertura') {{
                        // APERTURA:
                        // 0% - 15%: Emergencia suave desde el cosmos
                        // 15% - 82%: Contemplación majestuosa, zoom lento (0.95 -> 1.04)
                        // 82% - 100% (SEGUNDO FINAL): Salto hiperespacial exponencial directo a foco
                        if (progress < 0.15) {{
                            mandalaAlpha = progress / 0.15;
                        }} else {{
                            mandalaAlpha = 1.0;
                        }}

                        if (progress <= 0.82) {{
                            const pNorm = progress / 0.82;
                            targetZoom = 0.95 + pNorm * 0.09;
                            targetPanX = 0;
                            targetPanY = -170;
                            hudAlpha = 1.0;
                        }} else {{
                            const pZoom = (progress - 0.82) / 0.18;
                            const easeZoom = Math.pow(pZoom, 2.6);
                            targetZoom = 1.04 + easeZoom * 2.16; // 3.20x
                            
                            const s = targetZoom;
                            const finalPanX = -focoClockX * s;
                            const finalPanY = (targetScreenY - cy) - focoClockY * s;

                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -170 * (1 - easeZoom) + finalPanY * easeZoom;
                            hudAlpha = Math.max(0, 1.0 - pZoom * 2.2);

                            if (pZoom > 0.60) {{
                                flashAlpha = ((pZoom - 0.60) / 0.40) * 0.60;
                            }}
                        }}
                    }} else if (window.__cineMode === 'intermedio') {{
                        // INTERMEDIO:
                        // Entra directo en zoom (2.25x) centrado en planeta del relato
                        targetZoom = 2.25 + Math.sin(progress * Math.PI) * 0.05;
                        const s = targetZoom;
                        targetPanX = -interClockX * s;
                        targetPanY = (targetScreenY - cy) - interClockY * s;
                        mandalaAlpha = 1.0;
                        hudAlpha = 1.0;
                    }} else {{
                        // CIERRE (Inverso Simétrico):
                        // 0% - 18%: Zoom-out rápido desde 3.20x hasta 1.04x
                        // 18% - 82%: Paneo fijo contemplativo con síntesis
                        // 82% - 100%: Zoom lento a 0.88x, destello 24hs y fade-out estelar
                        if (progress <= 0.18) {{
                            const pZoom = progress / 0.18;
                            const easeZoom = Math.pow(1 - pZoom, 2.6);
                            targetZoom = 1.04 + easeZoom * 2.16;
                            
                            const s = targetZoom;
                            const finalPanX = -focoClockX * s;
                            const finalPanY = (targetScreenY - cy) - focoClockY * s;
                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -170 * (1 - easeZoom) + finalPanY * easeZoom;
                            hudAlpha = pZoom;
                        }} else if (progress <= 0.82) {{
                            targetZoom = 1.04;
                            targetPanX = 0;
                            targetPanY = -170;
                            hudAlpha = 1.0;
                        }} else {{
                            const pEnd = (progress - 0.82) / 0.18;
                            targetZoom = 1.04 - pEnd * 0.16;
                            targetPanX = 0;
                            targetPanY = -170;

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

                    ctx.save();
                    ctx.globalAlpha = mandalaAlpha;
                    origRender();
                    ctx.restore();

                    // ── HUD ORGÁNICO TENEBRISTA ────────────────────────────────
                    if (hudAlpha > 0.01) {{
                        ctx.save();
                        ctx.globalAlpha = hudAlpha;
                        ctx.setTransform(1, 0, 0, 1, 0, 0);

                        // Header Superior
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
                        ctx.fillText('{header_fecha}', w / 2, 55);

                        ctx.font = '600 22px "Cinzel", "Times New Roman", serif';
                        ctx.fillStyle = '#f1f5f9';
                        ctx.shadowBlur = 6;
                        ctx.fillText('{header_sub}', w / 2, 115);

                        if (window.__cineMode === 'intermedio') {{
                            // Píldora orgánica cyan / dorada
                            const pillX = w / 2 - 250;
                            const pillY = 1320;
                            const pillW = 500;
                            const pillH = 145;

                            ctx.fillStyle = 'rgba(10, 18, 30, 0.92)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#fde047';
                            ctx.shadowBlur = 16;
                            ctx.beginPath();
                            ctx.roundRect(pillX, pillY, pillW, pillH, 18);
                            ctx.fill();
                            ctx.stroke();

                            ctx.fillStyle = '#f6c445';
                            ctx.font = '700 24px "Cinzel", sans-serif';
                            ctx.fillText('{pildora_titulo}', w / 2, pillY + 22);

                            ctx.fillStyle = '#e2e8f0';
                            ctx.font = '600 18px -apple-system, sans-serif';
                            ctx.fillText('{pildora_sub}', w / 2, pillY + 64);

                            ctx.fillStyle = '#94a3b8';
                            ctx.font = '500 16px -apple-system, sans-serif';
                            ctx.fillText('{pildora_body}', w / 2, pillY + 98);
                        }} else if (progress <= 0.82 || window.__cineMode === 'cierre') {{
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
                            ctx.fillText('{tarjeta1_titulo}', 60, cardY + 24);

                            ctx.font = '500 17px -apple-system, sans-serif';
                            ctx.fillStyle = '#cbd5e1';
                            ctx.fillText('{tarjeta1_body}', 60, cardY + 65);

                            // Tarjeta Derecha (Venus / Júpiter)
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
                            ctx.fillText('{tarjeta2_titulo}', 580, cardY + 24);

                            ctx.font = '500 17px -apple-system, sans-serif';
                            ctx.fillStyle = '#fef08a';
                            ctx.fillText('{tarjeta2_body}', 580, cardY + 65);
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

        # Grabar la duración exacta del slot
        t_start = time.time()
        while time.time() - t_start < duracion_s:
            time.sleep(0.04)

        context.close()
        browser.close()

    webm_files = list(clip_rec_dir.glob("*.webm"))
    if not webm_files:
        raise RuntimeError(f"No se encontró archivo WebM grabado en {clip_rec_dir}")
    recorded_webm = max(webm_files, key=lambda f: f.stat().st_mtime)

    # Transcodificar a MP4 con 30 FPS constantes y máxima calidad (CRF 16)
    cmd_ffmpeg = (
        f"ffmpeg -y -i '{recorded_webm}' -c:v libx264 -pix_fmt yuv420p "
        f"-r 30 -crf 16 -preset slow -t {duracion_s} '{out_mp4}' >/dev/null 2>&1"
    )
    subprocess.run(cmd_ffmpeg, shell=True, check=True)
    size_mb = out_mp4.stat().st_size / (1024 * 1024)
    print(f"✅ Clip generado: {out_mp4.name} ({size_mb:.2f} MB, {duracion_s:.2f}s)")
    return out_mp4

def generar_clips_fecha(
    fecha: str = "2026-11-05",
    dur_apertura: float = 7.72,
    dur_intermedio: float = 8.98,
    dur_cierre: float = 5.20,
    planeta_foco: str = "Luna",
    planeta_intermedio: str = "Venus",
    header_fecha: str = "5 DE NOVIEMBRE 2026",
    header_sub: str = "LUNA EN LIBRA · SEXTIL VENUS Y JÚPITER",
    pildora_titulo: str = "♀ VENUS SEXTIL JÚPITER · 24° ♎ ♌",
    pildora_sub: str = "Sextil exacto: diplomacia, encanto y generosidad",
    pildora_body: str = "Pactar con altura sin regalar tu valor propio.",
    tarjeta1_titulo: str = "☽ LUNA EN LIBRA 0°",
    tarjeta1_body: str = "Gran Trígono de Aire: visión y balance sin complacencia sumisa.",
    tarjeta2_titulo: str = "♀ VENUS SEXTIL JÚPITER 24°",
    tarjeta2_body: str = "Generosidad soberana: acordar con altura y valor propio.",
    port: int = 8788
):
    proc = iniciar_servidor(port)
    try:
        # 1. Apertura
        capturar_clip(
            tipo="apertura",
            nombre_archivo=f"reloj_2d_{fecha}_cinematico_apertura",
            fecha_iso=f"{fecha}T00:00:00",
            duracion_s=dur_apertura,
            planeta_foco=planeta_foco,
            planeta_intermedio=planeta_intermedio,
            header_fecha=header_fecha,
            header_sub=header_sub,
            pildora_titulo=pildora_titulo,
            pildora_sub=pildora_sub,
            pildora_body=pildora_body,
            tarjeta1_titulo=tarjeta1_titulo,
            tarjeta1_body=tarjeta1_body,
            tarjeta2_titulo=tarjeta2_titulo,
            tarjeta2_body=tarjeta2_body,
            port=port
        )

        # 2. Intermedio
        capturar_clip(
            tipo="intermedio",
            nombre_archivo=f"reloj_2d_{fecha}_cinematico_intermedio",
            fecha_iso=f"{fecha}T12:00:00",
            duracion_s=dur_intermedio,
            planeta_foco=planeta_foco,
            planeta_intermedio=planeta_intermedio,
            header_fecha=header_fecha,
            header_sub=header_sub,
            pildora_titulo=pildora_titulo,
            pildora_sub=pildora_sub,
            pildora_body=pildora_body,
            tarjeta1_titulo=tarjeta1_titulo,
            tarjeta1_body=tarjeta1_body,
            tarjeta2_titulo=tarjeta2_titulo,
            tarjeta2_body=tarjeta2_body,
            port=port
        )

        # 3. Cierre
        capturar_clip(
            tipo="cierre",
            nombre_archivo=f"reloj_2d_{fecha}_cinematico_cierre",
            fecha_iso=f"{fecha}T23:45:00",
            duracion_s=dur_cierre,
            planeta_foco=planeta_foco,
            planeta_intermedio=planeta_intermedio,
            header_fecha=header_fecha,
            header_sub=header_sub,
            pildora_titulo=pildora_titulo,
            pildora_sub=pildora_sub,
            pildora_body=pildora_body,
            tarjeta1_titulo=tarjeta1_titulo,
            tarjeta1_body=tarjeta1_body,
            tarjeta2_titulo=tarjeta2_titulo,
            tarjeta2_body=tarjeta2_body,
            port=port
        )

        print("✨ ¡Tríptico cinemático generado con éxito!")
    finally:
        proc.terminate()

def main():
    parser = argparse.ArgumentParser(description="Generador Cinemático de Reloj Astrológico 2D")
    parser.add_argument("--fecha", default="2026-11-04", help="Fecha del tránsito (YYYY-MM-DD)")
    parser.add_argument("--dur_apertura", type=float, default=7.1, help="Duración del clip de apertura en s")
    parser.add_argument("--dur_intermedio", type=float, default=7.1, help="Duración del clip intermedio en s")
    parser.add_argument("--dur_cierre", type=float, default=6.35, help="Duración del clip de cierre en s")
    parser.add_argument("--planeta_foco", default="Mercurio", help="Planeta principal del tránsito")
    parser.add_argument("--planeta_intermedio", default="Luna", help="Planeta destacado en el relato de Toma 3")
    parser.add_argument("--puerto", type=int, default=8788, help="Puerto para servidor temporal")
    args = parser.parse_args()

    generar_clips_fecha(
        fecha=args.fecha,
        dur_apertura=args.dur_apertura,
        dur_intermedio=args.dur_intermedio,
        dur_cierre=args.dur_cierre,
        planeta_foco=args.planeta_foco,
        planeta_intermedio=args.planeta_intermedio,
        port=args.puerto
    )

if __name__ == "__main__":
    main()
