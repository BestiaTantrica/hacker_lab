#!/usr/bin/env python3
"""
🌟 CÉLULA 2 — generador_astrolabio_continuo_40s.py (Versión Maestra 1.0)
─────────────────────────────────────────────────────────────────────────────
Generador del Astrolabio Continuo 40s (Giro Completo de las 24hs del Día)
Instrumento Canónico: El Astrolabio Sagrado de El Glifo Maestro
Fecha Objetivo: 2026-11-06

Arquitectura Cinemática de Velocidad Variable (Caja de Cambios Dinámica):
1. 00.0s – 03.5s: Panorámico Madrugada/Amanecer (Velocidad RÁPIDA: 00:00 a 09:30 hs).
2. 03.5s – 06.0s: Zoom-in progresivo hacia el Eje de Oposición Luna ♎ - Saturno ♈.
3. 06.0s – 15.0s: ¡HOLD 1 (9 SEGUNDOS)! Mediodía en micro-deriva (11:30 a 12:00 hs).
                 Aureolas Sonar, cuerda de tensión 180°, fotón y badge latente.
4. 15.0s – 18.5s: Zoom-out panorámico y aceleración de la tarde (12:00 a 16:00 hs).
5. 18.5s – 21.0s: Zoom-in progresivo hacia el Sextil Venus ♎ - Júpiter/Marte ♌.
6. 21.0s – 29.5s: ¡HOLD 2 (8.5 SEGUNDOS)! Atardecer en micro-deriva (17:00 a 17:30 hs).
                 Aureolas Sonar, cuerda áurea 60°, fotón de plasma y badge armónico.
7. 29.5s – 33.5s: Zoom Invertido de salida / Des-zoom hacia la noche (17:30 a 22:00 hs).
8. 33.5s – 37.0s: Carrera final hacia el final del día en vista panorámica (22:00 a 24:00 hs).
9. 37.0s – 40.0s: ¡HOLD DE MEDIANOCHE 24:00:00! Campanada áurea y disolución para loop infinito.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import time
import json
import shutil
import argparse
import subprocess
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path(__file__).resolve().parents[2]
WEB_APP_DIR = FACTORY_ROOT / "web_app"
DEFAULT_OUTPUT_DIR = FACTORY_ROOT / "produccion" / "clips_reloj_2d"
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_RECORD_DIR = Path("/tmp/pw_astrolabio_40s")
TEMP_RECORD_DIR.mkdir(parents=True, exist_ok=True)


def iniciar_servidor(port: int = 8788):
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", str(port),
        "--log-level", "error"
    ]
    proc = subprocess.Popen(cmd, cwd=str(WEB_APP_DIR), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/reloj?cinematico=1", timeout=1) as resp:
                if resp.status == 200:
                    return proc
        except Exception:
            time.sleep(0.2)
    return proc


def generar_astrolabio_continuo_40s(
    fecha: str = "2026-11-06",
    duracion_s: float = 40.0,
    out_mp4: Path = None,
    port: int = 8788
):
    if out_mp4 is None:
        out_mp4 = DEFAULT_OUTPUT_DIR / f"astrolabio_continuo_{fecha}_40s.mp4"

    clip_rec_dir = TEMP_RECORD_DIR / f"rec_cont_{int(time.time()*1000)}"
    if clip_rec_dir.exists():
        shutil.rmtree(clip_rec_dir)
    clip_rec_dir.mkdir(parents=True, exist_ok=True)

    server_proc = iniciar_servidor(port)
    print(f"\n=======================================================")
    print(f"🌌 ASTROLABIO CONTINUO 40s (EL GLIFO MAESTRO): {fecha}")
    print(f"=======================================================")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                ]
            )
            t_record_start = time.time()
            context = browser.new_context(
                record_video_dir=str(clip_rec_dir),
                record_video_size={"width": 1080, "height": 1920},
                viewport={"width": 1080, "height": 1920}
            )
            page = context.new_page()
            page.goto(f"http://127.0.0.1:{port}/reloj?cinematico=1", wait_until="domcontentloaded")
            page.wait_for_selector("#reloj-canvas", timeout=10000)

            # Inyectar motor de animación continua de 40s con caja de cambios
            setup_script = f"""
            (() => {{
                document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');
                
                if (window.relojEngine) {{
                    const eng = window.relojEngine;
                    eng.timeState.isLive = false;
                    
                    eng.cambiarFondo('estrellas');
                    if (eng.videoBg) {{
                        eng.videoBg.play().catch(() => {{}});
                        eng.videoBg.playbackRate = 0.50;
                    }}

                    window.__slotDuration = {duracion_s};
                    window.__cineStartTime = performance.now();
                    window.__dateBase = '{fecha}';
                    window.__midnightMs = new Date('{fecha}T23:59:59.999').getTime();

                    // ── Helper: Dibujar Aureola Sonar, Retícula y Badge HUD ──
                    function dibujarAureolaPlaneta(ctx, screenX, screenY, colorHex, glowColor, tMs, badgeTitulo, badgeDetalle, badgeSub, alinearLado) {{
                        ctx.save();
                        
                        // 1. Tres Ondas Sonar de radar expansivas con disolución
                        for (let i = 0; i < 3; i++) {{
                            const waveProgress = ((tMs * 0.0013 + i * 0.333) % 1.0);
                            const waveRadius = 26 + waveProgress * 68;
                            const waveAlpha = (1.0 - waveProgress) * 0.85;
                            
                            ctx.strokeStyle = colorHex;
                            ctx.globalAlpha = waveAlpha;
                            ctx.lineWidth = 2.2 * (1.0 - waveProgress * 0.4);
                            ctx.shadowColor = glowColor;
                            ctx.shadowBlur = 14;
                            
                            ctx.beginPath();
                            ctx.arc(screenX, screenY, waveRadius, 0, Math.PI * 2);
                            ctx.stroke();
                        }}
                        
                        // 2. Retícula de Mira Telescópica Giratoria
                        ctx.globalAlpha = 0.90;
                        const pulseReticle = 1.0 + Math.sin(tMs * 0.005) * 0.08;
                        const rReticle = 30 * pulseReticle;
                        const angRot = tMs * 0.0008;
                        ctx.strokeStyle = colorHex;
                        ctx.lineWidth = 1.8;
                        ctx.shadowColor = glowColor;
                        ctx.shadowBlur = 10;
                        
                        ctx.beginPath();
                        ctx.arc(screenX, screenY, rReticle, 0, Math.PI * 2);
                        ctx.stroke();
                        
                        const tickLen = 7;
                        for (let k = 0; k < 4; k++) {{
                            const th = angRot + (k * Math.PI / 2);
                            ctx.beginPath();
                            ctx.moveTo(screenX + Math.cos(th) * (rReticle - tickLen), screenY + Math.sin(th) * (rReticle - tickLen));
                            ctx.lineTo(screenX + Math.cos(th) * (rReticle + tickLen), screenY + Math.sin(th) * (rReticle + tickLen));
                            ctx.stroke();
                        }}
                        
                        // 3. Floating HUD Badge ("Cartel Latente")
                        if (badgeTitulo) {{
                            ctx.shadowBlur = 0;
                            ctx.globalAlpha = 0.98;
                            
                            const isDer = (alinearLado !== 'izq');
                            const boxW = 265;
                            const boxH = badgeSub ? 64 : 52;
                            const boxX = isDer ? (screenX + 46) : (screenX - 46 - boxW);
                            const boxY = screenY - boxH / 2;
                            
                            // Línea conectora fina
                            ctx.strokeStyle = colorHex;
                            ctx.lineWidth = 1.4;
                            ctx.beginPath();
                            ctx.moveTo(isDer ? (screenX + rReticle) : (screenX - rReticle), screenY);
                            ctx.lineTo(isDer ? (screenX + 44) : (screenX - 44), screenY);
                            ctx.stroke();
                            
                            ctx.fillStyle = colorHex;
                            ctx.beginPath();
                            ctx.arc(isDer ? (screenX + 44) : (screenX - 44), screenY, 2.5, 0, Math.PI * 2);
                            ctx.fill();
                            
                            // Fondo Glassmorphism Oscuro
                            ctx.fillStyle = 'rgba(6, 12, 22, 0.94)';
                            ctx.strokeStyle = colorHex;
                            ctx.lineWidth = 1.5;
                            ctx.shadowColor = glowColor;
                            ctx.shadowBlur = 12;
                            ctx.beginPath();
                            ctx.roundRect(boxX, boxY, boxW, boxH, 8);
                            ctx.fill();
                            ctx.stroke();
                            
                            // Textos dentro del cartel
                            ctx.shadowBlur = 0;
                            ctx.textAlign = 'left';
                            ctx.textBaseline = 'top';
                            ctx.font = '700 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
                            ctx.fillStyle = colorHex;
                            ctx.fillText(badgeTitulo, boxX + 12, boxY + 8);
                            
                            ctx.font = '700 15px "Cinzel", Georgia, serif';
                            ctx.fillStyle = '#ffffff';
                            ctx.fillText(badgeDetalle || '', boxX + 12, boxY + 24);
                            
                            if (badgeSub) {{
                                ctx.font = '500 11px -apple-system, sans-serif';
                                ctx.fillStyle = '#94a3b8';
                                ctx.fillText(badgeSub, boxX + 12, boxY + 44);
                            }}
                        }}
                        
                        ctx.restore();
                    }}

                    // ── Helper: Dibujar Cuerda con Fotón en Movimiento y Badge de Aspecto ──
                    function dibujarAspectoFotones(ctx, x1, y1, x2, y2, colorHex, glowColor, tMs, badgeTexto) {{
                        ctx.save();
                        
                        // 1. Cuerda áurea con resplandor intenso
                        ctx.strokeStyle = colorHex;
                        ctx.shadowColor = glowColor;
                        ctx.shadowBlur = 18;
                        ctx.lineWidth = 3.5;
                        ctx.globalAlpha = 0.95;
                        ctx.beginPath();
                        ctx.moveTo(x1, y1);
                        ctx.lineTo(x2, y2);
                        ctx.stroke();
                        
                        // 2. Fotón de plasma que viaja continuamente entre los dos planetas
                        const tPhoton = (Math.sin(tMs * 0.0035) + 1.0) / 2.0;
                        const px = x1 + (x2 - x1) * tPhoton;
                        const py = y1 + (y2 - y1) * tPhoton;
                        
                        const photonGrad = ctx.createRadialGradient(px, py, 2, px, py, 14);
                        photonGrad.addColorStop(0, '#ffffff');
                        photonGrad.addColorStop(0.3, colorHex);
                        photonGrad.addColorStop(1, 'transparent');
                        ctx.fillStyle = photonGrad;
                        ctx.shadowColor = glowColor;
                        ctx.shadowBlur = 22;
                        ctx.beginPath();
                        ctx.arc(px, py, 14, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // Destello de 4 puntas en el fotón
                        ctx.strokeStyle = '#ffffff';
                        ctx.lineWidth = 1.4;
                        ctx.beginPath();
                        ctx.moveTo(px - 10, py); ctx.lineTo(px + 10, py);
                        ctx.moveTo(px, py - 10); ctx.lineTo(px, py + 10);
                        ctx.stroke();
                        
                        // 3. Badge en el Punto Medio del Aspecto
                        if (badgeTexto) {{
                            const mx = (x1 + x2) / 2;
                            const my = (y1 + y2) / 2;
                            const bw = 280;
                            const bh = 34;
                            
                            ctx.fillStyle = 'rgba(8, 14, 26, 0.94)';
                            ctx.strokeStyle = colorHex;
                            ctx.lineWidth = 1.5;
                            ctx.shadowColor = glowColor;
                            ctx.shadowBlur = 10;
                            ctx.beginPath();
                            ctx.roundRect(mx - bw / 2, my - bh / 2, bw, bh, 6);
                            ctx.fill();
                            ctx.stroke();
                            
                            ctx.shadowBlur = 0;
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.font = '700 12px "Courier New", monospace, sans-serif';
                            ctx.fillStyle = colorHex;
                            ctx.fillText(badgeTexto, mx, my);
                        }}
                        
                        ctx.restore();
                    }}

                    // Override de líneas de aspectos del reloj
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
                                (asp.p1 === 'Luna' && asp.p2 === 'Saturno') ||
                                (asp.p2 === 'Luna' && asp.p1 === 'Saturno') ||
                                (asp.p1 === 'Venus' && asp.p2 === 'Júpiter') ||
                                (asp.p2 === 'Venus' && asp.p1 === 'Júpiter')
                            );

                            if (esProtagonista) {{
                                ctx.save();
                                ctx.strokeStyle = asp.tipo === 'Oposición' ? '#ef4444' : '#f6c445';
                                ctx.shadowColor = asp.tipo === 'Oposición' ? '#f87171' : '#fde047';
                                ctx.shadowBlur = 16;
                                ctx.lineWidth = 3.2;
                                ctx.globalAlpha = 0.90;
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
                                ctx.globalAlpha = 0.04;
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
                        const elapsed = Math.max(0, Math.min(rawElapsed, window.__slotDuration));

                        // ── CAJA DE CAMBIOS CINEMÁTICA: HORA Y CÁMARA DINÁMICA ──
                        let horaCielo = 0.0;
                        let targetZoom = 1.00;
                        let faseActual = '';
                        let pFase = 0.0;

                        if (elapsed <= 3.5) {{
                            // Fase 1: Madrugada & Amanecer Rápido (00:00 a 09:30 hs)
                            pFase = elapsed / 3.5;
                            horaCielo = 0.0 + pFase * 9.5;
                            targetZoom = 1.00;
                            faseActual = 'PANORAMA_MANANA';
                        }} else if (elapsed <= 6.0) {{
                            // Fase 2: Zoom-in y Freno Suave hacia Oposición Luna-Saturno
                            pFase = (elapsed - 3.5) / 2.5;
                            const ease = pFase * pFase * (3 - 2 * pFase);
                            horaCielo = 9.5 + ease * 2.0;
                            targetZoom = 1.00 + ease * 0.70; // Llega a 1.70x
                            faseActual = 'ZOOM_IN_OPOSICION';
                        }} else if (elapsed <= 15.0) {{
                            // Fase 3: HOLD 1 (9 SEGUNDOS) sobre Luna opuesta Saturno (11:30 a 12:00 hs)
                            pFase = (elapsed - 6.0) / 9.0;
                            horaCielo = 11.5 + pFase * 0.5; // Micro-deriva de 30 min en 9s
                            targetZoom = 1.70 + Math.sin(pFase * Math.PI) * 0.02;
                            faseActual = 'HOLD_OPOSICION';
                        }} else if (elapsed <= 18.5) {{
                            // Fase 4: Zoom-out y Aceleración de la Tarde (12:00 a 16:00 hs)
                            pFase = (elapsed - 15.0) / 3.5;
                            const ease = pFase * pFase * (3 - 2 * pFase);
                            horaCielo = 12.0 + ease * 4.0;
                            targetZoom = 1.70 - ease * 0.66; // Vuelve a 1.04x
                            faseActual = 'ZOOM_OUT_TARDE';
                        }} else if (elapsed <= 21.0) {{
                            // Fase 5: Zoom-in hacia el Sextil Venus-Júpiter-Marte
                            pFase = (elapsed - 18.5) / 2.5;
                            const ease = pFase * pFase * (3 - 2 * pFase);
                            horaCielo = 16.0 + ease * 1.0;
                            targetZoom = 1.04 + ease * 0.71; // Llega a 1.75x
                            faseActual = 'ZOOM_IN_SEXTIL';
                        }} else if (elapsed <= 29.5) {{
                            // Fase 6: HOLD 2 (8.5 SEGUNDOS) sobre Sextil Armónico (17:00 a 17:30 hs)
                            pFase = (elapsed - 21.0) / 8.5;
                            horaCielo = 17.0 + pFase * 0.5; // Micro-deriva de 30 min en 8.5s
                            targetZoom = 1.75 + Math.sin(pFase * Math.PI) * 0.02;
                            faseActual = 'HOLD_SEXTIL';
                        }} else if (elapsed <= 33.5) {{
                            // Fase 7: Zoom Invertido hacia la Noche (17:30 a 22:00 hs)
                            pFase = (elapsed - 29.5) / 4.0;
                            const ease = pFase * pFase * (3 - 2 * pFase);
                            horaCielo = 17.5 + ease * 4.5;
                            targetZoom = 1.75 - ease * 0.75; // Vuelve a 1.00x
                            faseActual = 'ZOOM_OUT_NOCHE';
                        }} else if (elapsed <= 37.0) {{
                            // Fase 8: Carrera Final hacia las 24:00:00 (22:00 a 24:00 hs)
                            pFase = (elapsed - 33.5) / 3.5;
                            const ease = pFase * pFase * (3 - 2 * pFase);
                            horaCielo = 22.0 + ease * 2.0;
                            targetZoom = 1.00;
                            faseActual = 'CARRERA_MEDIANOCHE';
                        }} else {{
                            // Fase 9: ¡HOLD DE MEDIANOCHE 24:00:00 (3s)! Campanada y Disolución de Loop
                            horaCielo = 24.0;
                            targetZoom = 1.00;
                            faseActual = 'HOLD_24HS';
                        }}

                        // Convertir hora decimal en timestamp exacto
                        const hInt = Math.floor(horaCielo);
                        const mFloat = (horaCielo - hInt) * 60;
                        const mInt = Math.floor(mFloat);
                        const sInt = Math.floor((mFloat - mInt) * 60);

                        let currentClockMs;
                        if (horaCielo >= 24.0) {{
                            currentClockMs = window.__midnightMs;
                        }} else {{
                            const timeStr = `${{window.__dateBase}}T${{String(hInt).padStart(2, '0')}}:${{String(mInt).padStart(2, '0')}}:${{String(sInt).padStart(2, '0')}}`;
                            currentClockMs = new Date(timeStr).getTime();
                        }}

                        eng.timeState.currentDate = new Date(currentClockMs);
                        eng.calculateAll();

                        const w = eng.width;
                        const h = eng.height;
                        const cx = w / 2;
                        const cy = h / 2;
                        const ctx = eng.ctx;

                        ctx.fillStyle = '#020308';
                        ctx.fillRect(0, 0, w, h);
                        if (eng.videoBg && eng.videoBg.readyState >= 2) {{
                            ctx.drawImage(eng.videoBg, 0, 0, w, h);
                            ctx.fillStyle = 'rgba(2, 3, 8, 0.75)';
                            ctx.fillRect(0, 0, w, h);
                        }}

                        const rPlanets = eng.radii.planets || 275;
                        const baseScale = Math.min(w, h) / 1080;

                        let lunaClockX = 0, lunaClockY = 0;
                        let saturnoClockX = 0, saturnoClockY = 0;
                        let venusClockX = 0, venusClockY = 0;
                        let jupiterClockX = 0, jupiterClockY = 0;

                        if (eng.calculated && eng.calculated.planets) {{
                            if (eng.calculated.planets['Luna']) {{
                                const a = eng.coordToAngle(eng.calculated.planets['Luna'].grado_absoluto);
                                lunaClockX = Math.cos(a) * rPlanets;
                                lunaClockY = Math.sin(a) * rPlanets;
                            }}
                            if (eng.calculated.planets['Saturno']) {{
                                const a = eng.coordToAngle(eng.calculated.planets['Saturno'].grado_absoluto);
                                saturnoClockX = Math.cos(a) * rPlanets;
                                saturnoClockY = Math.sin(a) * rPlanets;
                            }}
                            if (eng.calculated.planets['Venus']) {{
                                const a = eng.coordToAngle(eng.calculated.planets['Venus'].grado_absoluto);
                                venusClockX = Math.cos(a) * rPlanets;
                                venusClockY = Math.sin(a) * rPlanets;
                            }}
                            if (eng.calculated.planets['Júpiter']) {{
                                const a = eng.coordToAngle(eng.calculated.planets['Júpiter'].grado_absoluto);
                                jupiterClockX = Math.cos(a) * rPlanets;
                                jupiterClockY = Math.sin(a) * rPlanets;
                            }}
                        }}

                        let targetPanX = 0;
                        let targetPanY = -140;
                        let mandalaAlpha = 1.0;
                        const targetScreenY = 780;

                        // Paneo inteligente según la fase
                        if (faseActual === 'ZOOM_IN_OPOSICION' || faseActual === 'HOLD_OPOSICION') {{
                            // Enfocar hacia el cuadrante de la Luna y Saturno
                            const midX = (lunaClockX + saturnoClockX) / 2;
                            const midY = (lunaClockY + saturnoClockY) / 2;
                            const s = targetZoom;
                            const finalPanX = -midX * s * 0.40;
                            const finalPanY = (targetScreenY - cy) - midY * s * 0.40;
                            
                            if (faseActual === 'ZOOM_IN_OPOSICION') {{
                                const pEase = (elapsed - 3.5) / 2.5;
                                targetPanX = finalPanX * pEase;
                                targetPanY = -140 * (1 - pEase) + finalPanY * pEase;
                            }} else {{
                                targetPanX = finalPanX;
                                targetPanY = finalPanY;
                            }}
                        }} else if (faseActual === 'ZOOM_OUT_TARDE') {{
                            const pEase = (elapsed - 15.0) / 3.5;
                            const midX = (lunaClockX + saturnoClockX) / 2;
                            const midY = (lunaClockY + saturnoClockY) / 2;
                            const s = targetZoom;
                            const startPanX = -midX * s * 0.40;
                            const startPanY = (targetScreenY - cy) - midY * s * 0.40;
                            targetPanX = startPanX * (1 - pEase);
                            targetPanY = startPanY * (1 - pEase) - 140 * pEase;
                        }} else if (faseActual === 'ZOOM_IN_SEXTIL' || faseActual === 'HOLD_SEXTIL') {{
                            // Enfocar hacia Venus y Júpiter
                            const midX = (venusClockX + jupiterClockX) / 2;
                            const midY = (venusClockY + jupiterClockY) / 2;
                            const s = targetZoom;
                            const finalPanX = -midX * s * 0.60;
                            const finalPanY = (targetScreenY - cy) - midY * s * 0.60;

                            if (faseActual === 'ZOOM_IN_SEXTIL') {{
                                const pEase = (elapsed - 18.5) / 2.5;
                                targetPanX = finalPanX * pEase;
                                targetPanY = -140 * (1 - pEase) + finalPanY * pEase;
                            }} else {{
                                targetPanX = finalPanX;
                                targetPanY = finalPanY;
                            }}
                        }} else if (faseActual === 'ZOOM_OUT_NOCHE') {{
                            const pEase = (elapsed - 29.5) / 4.0;
                            const midX = (venusClockX + jupiterClockX) / 2;
                            const midY = (venusClockY + jupiterClockY) / 2;
                            const s = targetZoom;
                            const startPanX = -midX * s * 0.60;
                            const startPanY = (targetScreenY - cy) - midY * s * 0.60;
                            targetPanX = startPanX * (1 - pEase);
                            targetPanY = startPanY * (1 - pEase) - 140 * pEase;
                        }} else if (faseActual === 'HOLD_24HS') {{
                            targetPanX = 0;
                            targetPanY = -140;

                            const pChime = (elapsed - 37.0) / 3.0;
                            const pulse = Math.sin(pChime * Math.PI);
                            eng.horology.dayPulse = pulse * 2.0;
                            eng.horology.flashes.hourRing = 1.0;

                            // Disolución final en el cosmos estelar para cerrar el loop
                            if (pChime > 0.50) {{
                                const pFade = (pChime - 0.50) / 0.50;
                                mandalaAlpha = Math.max(0, 1.0 - pFade * 0.90);
                            }}
                        }}

                        eng.camera.zoom = targetZoom;
                        eng.camera.panX = targetPanX;
                        eng.camera.panY = targetPanY;

                        ctx.save();
                        ctx.globalAlpha = mandalaAlpha;
                        origRender();
                        ctx.restore();

                        // Coordenadas en pantalla
                        const currentScale = baseScale * eng.camera.zoom;
                        const planets = eng.calculated ? eng.calculated.planets : null;

                        let lunaScreen = null, saturnoScreen = null;
                        let venusScreen = null, jupiterScreen = null;

                        if (planets) {{
                            if (planets['Luna']) {{
                                const a = eng.coordToAngle(planets['Luna'].grado_absoluto);
                                const px = Math.cos(a) * rPlanets;
                                const py = Math.sin(a) * rPlanets;
                                lunaScreen = {{
                                    screenX: (cx + eng.camera.panX) + px * currentScale,
                                    screenY: (cy + eng.camera.panY) + py * currentScale,
                                    deg: planets['Luna'].grado,
                                    min: planets['Luna'].minutos,
                                    signo: planets['Luna'].signo
                                }};
                            }}
                            if (planets['Saturno']) {{
                                const a = eng.coordToAngle(planets['Saturno'].grado_absoluto);
                                const px = Math.cos(a) * rPlanets;
                                const py = Math.sin(a) * rPlanets;
                                saturnoScreen = {{
                                    screenX: (cx + eng.camera.panX) + px * currentScale,
                                    screenY: (cy + eng.camera.panY) + py * currentScale,
                                    deg: planets['Saturno'].grado,
                                    min: planets['Saturno'].minutos,
                                    signo: planets['Saturno'].signo
                                }};
                            }}
                            if (planets['Venus']) {{
                                const a = eng.coordToAngle(planets['Venus'].grado_absoluto);
                                const px = Math.cos(a) * rPlanets;
                                const py = Math.sin(a) * rPlanets;
                                venusScreen = {{
                                    screenX: (cx + eng.camera.panX) + px * currentScale,
                                    screenY: (cy + eng.camera.panY) + py * currentScale,
                                    deg: planets['Venus'].grado,
                                    min: planets['Venus'].minutos,
                                    signo: planets['Venus'].signo
                                }};
                            }}
                            if (planets['Júpiter']) {{
                                const a = eng.coordToAngle(planets['Júpiter'].grado_absoluto);
                                const px = Math.cos(a) * rPlanets;
                                const py = Math.sin(a) * rPlanets;
                                jupiterScreen = {{
                                    screenX: (cx + eng.camera.panX) + px * currentScale,
                                    screenY: (cy + eng.camera.panY) + py * currentScale,
                                    deg: planets['Júpiter'].grado,
                                    min: planets['Júpiter'].minutos,
                                    signo: planets['Júpiter'].signo
                                }};
                            }}
                        }}

                        // ── RENDERIZADO DE AUREOLAS SEGÚN LA FASE ──
                        if ((faseActual === 'ZOOM_IN_OPOSICION' || faseActual === 'HOLD_OPOSICION') && lunaScreen && saturnoScreen) {{
                            const aAlpha = faseActual === 'ZOOM_IN_OPOSICION' ? Math.min(1.0, (elapsed - 3.5) / 2.0) : 1.0;
                            ctx.save();
                            ctx.globalAlpha = aAlpha;

                            // Cuerda de oposición con fotón
                            dibujarAspectoFotones(
                                ctx,
                                lunaScreen.screenX, lunaScreen.screenY,
                                saturnoScreen.screenX, saturnoScreen.screenY,
                                '#ef4444', '#f87171',
                                rawElapsed * 1000,
                                "[ OPOSICIÓN 180° · ORBE 2° 36' · TENSIÓN ]"
                            );

                            // Aureola Luna
                            dibujarAureolaPlaneta(
                                ctx,
                                lunaScreen.screenX, lunaScreen.screenY,
                                '#38bdf8', '#00f2fe',
                                rawElapsed * 1000,
                                '✦ TRÁNSITO ACTIVO',
                                `☽ LUNA ${{lunaScreen.deg}}° ${{lunaScreen.min}}' ${{lunaScreen.signo.toUpperCase()}}`,
                                'Vínculos · Deseo de balance',
                                'der'
                            );

                            // Aureola Saturno
                            dibujarAureolaPlaneta(
                                ctx,
                                saturnoScreen.screenX, saturnoScreen.screenY,
                                '#ef4444', '#f87171',
                                (rawElapsed + 0.5) * 1000,
                                '✦ PUNTO DE TENSIÓN',
                                `♄ SATURNO ${{saturnoScreen.deg}}° ${{saturnoScreen.min}}' ${{saturnoScreen.signo.toUpperCase()}}`,
                                'Límite y realidad · Rigidez externa',
                                'izq'
                            );
                            ctx.restore();
                        }}

                        if ((faseActual === 'ZOOM_IN_SEXTIL' || faseActual === 'HOLD_SEXTIL') && venusScreen && jupiterScreen) {{
                            const aAlpha = faseActual === 'ZOOM_IN_SEXTIL' ? Math.min(1.0, (elapsed - 18.5) / 2.0) : 1.0;
                            ctx.save();
                            ctx.globalAlpha = aAlpha;

                            // Cuerda de sextil con fotón áureo
                            dibujarAspectoFotones(
                                ctx,
                                venusScreen.screenX, venusScreen.screenY,
                                jupiterScreen.screenX, jupiterScreen.screenY,
                                '#f6c445', '#fde047',
                                rawElapsed * 1000,
                                "[ SEXTIL 60° · ORBE 0° 57' · ARMÓNICO ]"
                            );

                            // Aureola Venus
                            dibujarAureolaPlaneta(
                                ctx,
                                venusScreen.screenX, venusScreen.screenY,
                                '#f6c445', '#fde047',
                                rawElapsed * 1000,
                                '✦ TRÁNSITO LATENTE',
                                `♀ VENUS ${{venusScreen.deg}}° ${{venusScreen.min}}' ${{venusScreen.signo.toUpperCase()}}`,
                                'En rectoría · Diplomacia lúcida',
                                'der'
                            );

                            // Aureola Júpiter
                            dibujarAureolaPlaneta(
                                ctx,
                                jupiterScreen.screenX, jupiterScreen.screenY,
                                '#f97316', '#fb923c',
                                (rawElapsed + 0.4) * 1000,
                                '✦ PLANETA RECEPTOR',
                                `♃ JÚPITER ${{jupiterScreen.deg}}° ${{jupiterScreen.min}}' ${{jupiterScreen.signo.toUpperCase()}}`,
                                'Fuego magno · Generosidad y valor',
                                'izq'
                            );
                            ctx.restore();
                        }}

                        // ── RENDERIZADO DEL HEADER Y CARTELES INFERIORES ──
                        ctx.save();
                        ctx.setTransform(1, 0, 0, 1, 0, 0);

                        // Header Superior
                        const gradTop = ctx.createLinearGradient(0, 0, 0, 190);
                        gradTop.addColorStop(0, 'rgba(5, 7, 12, 0.95)');
                        gradTop.addColorStop(0.7, 'rgba(5, 7, 12, 0.75)');
                        gradTop.addColorStop(1, 'rgba(5, 7, 12, 0)');
                        ctx.fillStyle = gradTop;
                        ctx.fillRect(0, 0, w, 190);

                        ctx.font = '700 36px "Cinzel", serif';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'top';
                        ctx.fillStyle = '#f6c445';
                        ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                        ctx.shadowBlur = 10;
                        ctx.fillText("EL GLIFO MAESTRO · ASTROLABIO VIVO", w / 2, 50);

                        ctx.font = '600 20px "Cinzel", serif';
                        ctx.fillStyle = '#f1f5f9';
                        ctx.shadowBlur = 6;
                        ctx.fillText("6 DE NOVIEMBRE 2026 · EL PULSO DEL CIELO", w / 2, 105);

                        // Tarjeta Inferior Reubicada (Y = 1450: Despeja totalmente el aro del astrolabio)
                        const cardY = 1450;
                        const cardH = 135;
                        const cardW = 960;
                        const cardX = (w - cardW) / 2;

                        ctx.fillStyle = 'rgba(8, 14, 26, 0.93)';
                        ctx.strokeStyle = '#f6c445';
                        ctx.lineWidth = 1.8;
                        ctx.shadowColor = '#d97706';
                        ctx.shadowBlur = 12;

                        ctx.beginPath();
                        ctx.roundRect(cardX, cardY, cardW, cardH, 14);
                        ctx.fill();
                        ctx.stroke();

                        ctx.shadowBlur = 0;
                        ctx.textAlign = 'center';

                        if (faseActual === 'ZOOM_IN_OPOSICION' || faseActual === 'HOLD_OPOSICION') {{
                            ctx.font = '700 21px "Cinzel", serif';
                            ctx.fillStyle = '#f87171';
                            ctx.fillText("✦ EJE DE TENSIÓN: EL LÍMITE Y LA REALIDAD ✦", w / 2, cardY + 22);

                            ctx.font = '700 13px "Courier New", monospace';
                            ctx.fillStyle = '#38bdf8';
                            ctx.fillText("☽ LUNA 11° LIBRA  ·  OPOSICIÓN 180°  ·  ♄ SATURNO 9° ARIES", w / 2, cardY + 58);

                            ctx.font = '400 15px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#e2e8f0';
                            ctx.fillText("El otro pone un freno o una frialdad: no mendigues aprobación ni te aisles con rencor.", w / 2, cardY + 92);
                        }} else if (faseActual === 'ZOOM_IN_SEXTIL' || faseActual === 'HOLD_SEXTIL') {{
                            ctx.font = '700 21px "Cinzel", serif';
                            ctx.fillStyle = '#fde047';
                            ctx.fillText("✦ APERTURA ARMÓNICA: PACTAR CON SOBERANÍA ✦", w / 2, cardY + 22);

                            ctx.font = '700 13px "Courier New", monospace';
                            ctx.fillStyle = '#38bdf8';
                            ctx.fillText("♀ VENUS 24° LIBRA  ·  SEXTIL 60°  ·  ♃ JÚPITER 25° LEO (Y MARTE 21°)", w / 2, cardY + 58);

                            ctx.font = '400 15px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#e2e8f0';
                            ctx.fillText("Diplomacia y fuego: defendé tu postura con calma y encanto, sin regalar tu valor.", w / 2, cardY + 92);
                        }} else if (faseActual === 'HOLD_24HS') {{
                            ctx.font = '700 22px "Cinzel", serif';
                            ctx.fillStyle = '#fde047';
                            ctx.fillText("✦ MEDIANOCHE 24:00:00 · CIERRE DEL DÍA ✦", w / 2, cardY + 22);

                            ctx.font = '700 13px "Courier New", monospace';
                            ctx.fillStyle = '#7dd3fc';
                            ctx.fillText("[ EL CIELO SE COMPLETA · CICLO SINCRÓNICO CONTINUO ]", w / 2, cardY + 58);

                            ctx.font = '400 15px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#f8fafc';
                            ctx.fillText("El pulso astrológico culmina y se enlaza al nuevo amanecer.", w / 2, cardY + 92);
                        }} else {{
                            // Panorámico general
                            ctx.font = '700 21px "Cinzel", serif';
                            ctx.fillStyle = '#f6c445';
                            ctx.fillText("EL MAPA DEL CIELO EN TIEMPO VIVO", w / 2, cardY + 22);

                            ctx.font = '700 13px "Courier New", monospace';
                            ctx.fillStyle = '#38bdf8';
                            ctx.fillText("LUNA EN LIBRA  ·  OPOSICIÓN SATURNO  ·  SEXTIL VENUS-JÚPITER", w / 2, cardY + 58);

                            ctx.font = '400 15px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#e2e8f0';
                            ctx.fillText("Rotación celeste de 24 horas: observá la danza planetaria sobre el astrolabio.", w / 2, cardY + 92);
                        }}

                        ctx.restore();
                    }};

                    eng.calculateAll();
                }}
            }})();
            """
            page.evaluate(setup_script)
            t_setup_done = time.time()
            offset_seconds = round(t_setup_done - t_record_start, 2)
            print(f"⏱️ Astrolabio listo en {offset_seconds:.2f}s. Grabando ciclo completo {duracion_s:.1f}s...")

            t_start_record = time.time()
            while time.time() - t_start_record < (duracion_s + 4.5):
                time.sleep(0.04)

            context.close()
            browser.close()

        webm_files = list(clip_rec_dir.glob("*.webm"))
        if not webm_files:
            raise RuntimeError(f"No se encontró archivo WebM grabado en {clip_rec_dir}")
        recorded_webm = max(webm_files, key=lambda f: f.stat().st_mtime)

        # Transcodificar recortando exactamente el offset de inicialización
        print(f"⚡ Transcodificando Master Continuo 40s con FFmpeg...")
        cmd_ffmpeg = (
            f"ffmpeg -y -i '{recorded_webm}' -ss {offset_seconds} -c:v libx264 -pix_fmt yuv420p "
            f"-r 30 -crf 14 -preset slow -t {duracion_s} '{out_mp4}' >/dev/null 2>&1"
        )
        subprocess.run(cmd_ffmpeg, shell=True, check=True)
        size_mb = out_mp4.stat().st_size / (1024 * 1024)
        print(f"✅ ¡Master Continuo Generado!: {out_mp4.name} ({size_mb:.2f} MB, {duracion_s:.1f}s)")
        return out_mp4

    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except Exception:
            server_proc.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador del Astrolabio Continuo 40s")
    parser.add_argument("--fecha", default="2026-11-06", help="Fecha YYYY-MM-DD")
    parser.add_argument("--duracion", type=float, default=40.0, help="Duración en segundos")
    args = parser.parse_args()

    generar_astrolabio_continuo_40s(
        fecha=args.fecha,
        duracion_s=args.duracion
    )
