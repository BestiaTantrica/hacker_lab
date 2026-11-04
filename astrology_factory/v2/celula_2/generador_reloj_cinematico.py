#!/usr/bin/env python3
"""
🌓 CÉLULA 2 — generador_reloj_cinematico.py (Versión Maestra 3.1)
─────────────────────────────────────────────────────────────────────────────
Motor Cinemático del Reloj Astrológico 2D (Apertura, Intermedio, Cierre)
Proyecto: El Glifo Maestro / Astrology Factory

Garantías Cinemáticas:
1. Sincronización absoluta: Se mide el timestamp exacto de inicialización de Playwright.
   FFmpeg recorta con '-ss offset_exacto' eliminando cualquier frame previo a la carga.
2. CERO pantallas blancas y CERO botones de UI desde la carga del DOM ('?cinematico=1').
3. Aureolas Latentes de Radar:
   - Ondas de sonar expansivas en planetas protagonistas.
   - Retículas telescópicas giratorias.
   - Badges flotantes HUD ("Cartel Latente") con grado, signo y estado latente.
4. Rayo de Fotones Dinámico en Aspectos:
   - Cuerda áurea con fotón de energía viajando entre los planetas del aspecto.
   - Badge en el punto medio: [ SEXTIL 60° · ORBE 0° 34' · LATENTE ].
5. Coreografía de Cámara y Sistema de HOLD:
   - Apertura: 1.00x sereno -> zoom suave a 1.65x -> HOLD 3.5s sobre Luna en Libra.
   - Intermedio: Inicia 100% en zoom 1.80x -> HOLD 8.25s con aureolas duales Venus/Júpiter.
   - Cierre: zoom out progresivo a 1.04x -> campanada exacta 24:00:00 -> HOLD 2.2s en medianoche
     y disolución sutil en el vacío cósmico estelar para loop infinito.
6. Proporciones HUD Milimétricas:
   - Tarjetas inferiores compactas (cardH = 145px) con datos astronómicos densos y cero vacíos.
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

TEMP_RECORD_DIR = Path("/tmp/pw_cine_engine")
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


def grabar_clip_reloj(
    tipo: str,
    duracion_s: float,
    out_mp4: Path,
    port: int = 8788,
    date_str: str = "2026-11-05",
    header_fecha: str = "5 DE NOVIEMBRE 2026",
    header_sub: str = "LUNA EN LIBRA · SEXTIL VENUS Y JÚPITER",
    tarjeta1_titulo: str = "☽ LUNA EN LIBRA 0° 11'",
    tarjeta1_badge: str = "[ TRÁNSITO LATENTE · INGRESO ]",
    tarjeta1_body: str = "Búsqueda de balance y acuerdos justos sin complacencia sumisa.",
    tarjeta2_titulo: str = "♀ VENUS SEXTIL JÚPITER 24°",
    tarjeta2_badge: str = "[ SEXTIL ARMÓNICO · ORBE 0° 34' ]",
    tarjeta2_body: str = "Pactar con altura, encanto y valor propio sin mendigar.",
    aspecto_hud_titulo: str = "♀ VENUS SEXTIL JÚPITER · 24° ♎ ♌",
    aspecto_hud_sub: str = "✦ ASPECTO MAYOR ARMÓNICO · ORBE 0° 34' LATENTE",
    aspecto_hud_desc: str = "Diplomacia y generosidad: pactar con altura sin regalar tu valor.",
    planeta_foco: str = "Luna",
    planeta_intermedio: str = "Venus"
):
    nombre_archivo = out_mp4.stem
    clip_rec_dir = TEMP_RECORD_DIR / f"rec_{tipo}_{int(time.time()*1000)}"
    if clip_rec_dir.exists():
        shutil.rmtree(clip_rec_dir)
    clip_rec_dir.mkdir(parents=True, exist_ok=True)

    if tipo == "apertura":
        fecha_inicio_iso = f"{date_str}T14:28:00"
        horas_recorridas = 0.08
    elif tipo == "intermedio":
        fecha_inicio_iso = f"{date_str}T14:30:00"
        horas_recorridas = 0.04
    else:  # cierre
        fecha_inicio_iso = f"{date_str}T23:35:00"
        horas_recorridas = 0.42

    print(f"🎬 [Motor Cinemático V3.1] Grabando '{tipo}' ({nombre_archivo}.mp4, {duracion_s:.2f}s)...")

    with sync_playwright() as p:
        t_browser_start = time.time()
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
        page.goto(f"http://127.0.0.1:{port}/reloj?cinematico=1", wait_until="domcontentloaded")
        page.wait_for_selector("#reloj-canvas", timeout=10000)

        # Serializar strings de forma segura para JavaScript
        j_header_fecha = json.dumps(header_fecha)
        j_header_sub = json.dumps(header_sub)
        j_aspecto_hud_titulo = json.dumps(aspecto_hud_titulo)
        j_aspecto_hud_sub = json.dumps(aspecto_hud_sub)
        j_aspecto_hud_desc = json.dumps(aspecto_hud_desc)
        j_tarjeta1_titulo = json.dumps(tarjeta1_titulo)
        j_tarjeta1_badge = json.dumps(tarjeta1_badge)
        j_tarjeta1_body = json.dumps(tarjeta1_body)
        j_tarjeta2_titulo = json.dumps(tarjeta2_titulo)
        j_tarjeta2_badge = json.dumps(tarjeta2_badge)
        j_tarjeta2_body = json.dumps(tarjeta2_body)

        # Inyectar motor cinemático de vanguardia
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

                window.__cineMode = '{tipo}';
                window.__slotDuration = {duracion_s};
                window.__cineStartTime = performance.now();
                window.__startMs = new Date('{fecha_inicio_iso}').getTime();
                window.__endMs = window.__startMs + {horas_recorridas} * 3600 * 1000;
                window.__midnightMs = new Date('{date_str}T23:59:59.999').getTime();
                window.__planetaFoco = '{planeta_foco}';
                window.__planetaIntermedio = '{planeta_intermedio}';

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
                        const boxW = 260;
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
                        const bw = 270;
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
                            (asp.p1 === 'Venus' && asp.p2 === 'Júpiter') ||
                            (asp.p2 === 'Venus' && asp.p1 === 'Júpiter')
                        );

                        if (esProtagonista) {{
                            ctx.save();
                            ctx.strokeStyle = '#f6c445';
                            ctx.shadowColor = '#fde047';
                            ctx.shadowBlur = 18;
                            ctx.lineWidth = 3.5;
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
                    const progress = elapsed / window.__slotDuration;

                    // Manejo del tiempo del reloj astronómico
                    let currentClockMs;
                    if (window.__cineMode === 'cierre') {{
                        const tToMidnight = 3.0; // Alcanza medianoche exacta a los 3.0s
                        if (rawElapsed < tToMidnight) {{
                            const pMid = rawElapsed / tToMidnight;
                            currentClockMs = window.__startMs + pMid * (window.__midnightMs - window.__startMs);
                        }} else {{
                            currentClockMs = window.__midnightMs; // CONGELADO EN 24:00:00 (HOLD DE 2.2s)
                        }}
                    }} else {{
                        currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
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

                    let focoClockX = 0, focoClockY = 0;
                    let interClockX = 0, interClockY = 0;
                    let venusClockX = 0, venusClockY = 0;
                    let jupiterClockX = 0, jupiterClockY = 0;

                    if (eng.calculated && eng.calculated.planets) {{
                        if (eng.calculated.planets[window.__planetaFoco]) {{
                            const a = eng.coordToAngle(eng.calculated.planets[window.__planetaFoco].grado_absoluto);
                            focoClockX = Math.cos(a) * rPlanets;
                            focoClockY = Math.sin(a) * rPlanets;
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
                        interClockX = (venusClockX + jupiterClockX) / 2;
                        interClockY = (venusClockY + jupiterClockY) / 2;
                    }}

                    let targetZoom = 1.0;
                    let targetPanX = 0;
                    let targetPanY = -160;
                    let mandalaAlpha = 1.0;
                    let flashAlpha = 0.0;
                    let hudCardsAlpha = 1.0;

                    const targetScreenY = 820;

                    // ── COREOGRAFÍA DE CÁMARA CON SISTEMA DE HOLD ──
                    if (window.__cineMode === 'apertura') {{
                        if (rawElapsed <= 1.30) {{
                            // Fase 1: Dial general sereno (1.00x)
                            targetZoom = 1.00;
                            targetPanX = 0;
                            targetPanY = -160;
                            hudCardsAlpha = 1.0;
                        }} else if (rawElapsed <= 2.80) {{
                            // Fase 2: Zoom progresivo y suave hacia Luna en Libra (1.50s)
                            const pZoom = (rawElapsed - 1.30) / 1.50;
                            const ease = pZoom < 0.5 ? 2 * pZoom * pZoom : 1 - Math.pow(-2 * pZoom + 2, 2) / 2;
                            targetZoom = 1.00 + ease * 0.65; // Llega a 1.65x
                            
                            const s = targetZoom;
                            const finalPanX = -focoClockX * s * 0.65;
                            const finalPanY = (targetScreenY - cy) - focoClockY * s * 0.65;

                            targetPanX = 0 * (1 - ease) + finalPanX * ease;
                            targetPanY = -160 * (1 - ease) + finalPanY * ease;
                            hudCardsAlpha = Math.max(0, 1.0 - ease * 1.5);
                        }} else if (rawElapsed <= 6.30) {{
                            // Fase 3: ¡HOLD EN ZOOM 1.65x DURANTE 3.50 SEGUNDOS!
                            targetZoom = 1.65;
                            const s = targetZoom;
                            targetPanX = -focoClockX * s * 0.65;
                            targetPanY = (targetScreenY - cy) - focoClockY * s * 0.65;
                            hudCardsAlpha = 0.0;
                        }} else {{
                            // Fase 4: Transición esfumada final
                            targetZoom = 1.65;
                            const s = targetZoom;
                            targetPanX = -focoClockX * s * 0.65;
                            targetPanY = (targetScreenY - cy) - focoClockY * s * 0.65;
                            hudCardsAlpha = 0.0;
                            flashAlpha = ((rawElapsed - 6.30) / 0.70) * 0.35;
                        }}
                    }} else if (window.__cineMode === 'intermedio') {{
                        // ¡INICIA Y SE MANTIENE 100% EN ZOOM 1.80x DURANTE TODO EL CLIP (8.25s)!
                        targetZoom = 1.80 + Math.sin(progress * Math.PI) * 0.02;
                        const s = targetZoom;
                        targetPanX = -interClockX * s * 0.65;
                        targetPanY = (targetScreenY - cy) - interClockY * s * 0.65;
                        mandalaAlpha = 1.0;
                        hudCardsAlpha = 1.0;
                    }} else {{ // cierre
                        if (rawElapsed <= 1.20) {{
                            // Fase 1: Des-zoom suave de 1.45x a 1.04x
                            const pZoom = rawElapsed / 1.20;
                            const ease = pZoom < 0.5 ? 2 * pZoom * pZoom : 1 - Math.pow(-2 * pZoom + 2, 2) / 2;
                            targetZoom = 1.45 - ease * 0.41;
                            
                            const s = targetZoom;
                            const startPanX = -focoClockX * s * 0.5;
                            const startPanY = (targetScreenY - cy) - focoClockY * s * 0.5;
                            targetPanX = startPanX * (1 - ease);
                            targetPanY = startPanY * (1 - ease) - 160 * ease;
                            hudCardsAlpha = Math.max(0.2, pZoom);
                        }} else if (rawElapsed <= 3.00) {{
                            // Fase 2: Paneo general contemplando el final del día
                            targetZoom = 1.04;
                            targetPanX = 0;
                            targetPanY = -160;
                            hudCardsAlpha = 1.0;
                        }} else {{
                            // Fase 3: ¡HOLD DE MEDIANOCHE 24:00:00 (2.2s)! Campanada y disolución cósmica
                            targetZoom = 1.04;
                            targetPanX = 0;
                            targetPanY = -160;

                            const pChime = (rawElapsed - 3.00) / 2.20;
                            const pulse = Math.sin(pChime * Math.PI);
                            eng.horology.dayPulse = pulse * 1.8;
                            eng.horology.flashes.hourRing = 1.0;

                            // Disolución elegante en el vacío cósmico para empalmar el loop infinito
                            if (pChime > 0.45) {{
                                const pFade = (pChime - 0.45) / 0.55;
                                mandalaAlpha = Math.max(0, 1.0 - pFade * 0.90);
                                hudCardsAlpha = Math.max(0, 1.0 - pFade * 1.5);
                            }}
                        }}
                    }}

                    eng.camera.zoom = targetZoom;
                    eng.camera.panX = targetPanX;
                    eng.camera.panY = targetPanY;

                    ctx.save();
                    ctx.globalAlpha = mandalaAlpha;
                    origRender();
                    ctx.restore();

                    // Proyectar coordenadas en pantalla exacta para Aureolas y Badges
                    const currentScale = baseScale * eng.camera.zoom;
                    const planets = eng.calculated ? eng.calculated.planets : null;

                    let lunaScreen = null;
                    let venusScreen = null;
                    let jupiterScreen = null;

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

                    // ── RENDERIZADO DE AUREOLAS Y HUD LATENTE ──
                    if (window.__cineMode === 'apertura' && lunaScreen && rawElapsed >= 1.6) {{
                        const aAureola = Math.min(1.0, (rawElapsed - 1.6) / 0.6);
                        ctx.save();
                        ctx.globalAlpha = aAureola;
                        const alado = lunaScreen.screenX > 540 ? 'izq' : 'der';
                        dibujarAureolaPlaneta(
                            ctx,
                            lunaScreen.screenX,
                            lunaScreen.screenY,
                            '#38bdf8',
                            '#00f2fe',
                            rawElapsed * 1000,
                            '✦ TRÁNSITO LATENTE',
                            `☽ LUNA ${{lunaScreen.deg}}° ${{lunaScreen.min}}' ${{lunaScreen.signo.toUpperCase()}}`,
                            'Ingreso zodiacal · Balance y templanza',
                            alado
                        );
                        ctx.restore();
                    }}

                    if (window.__cineMode === 'intermedio' && venusScreen && jupiterScreen) {{
                        // 1. Cuerda con haz de fotones oscilantes y badge de orbe latente
                        dibujarAspectoFotones(
                            ctx,
                            venusScreen.screenX,
                            venusScreen.screenY,
                            jupiterScreen.screenX,
                            jupiterScreen.screenY,
                            '#f6c445',
                            '#fde047',
                            rawElapsed * 1000,
                            "[ SEXTIL 60° · ORBE 0° 34' · LATENTE ]"
                        );

                        // 2. Aureola Venus
                        dibujarAureolaPlaneta(
                            ctx,
                            venusScreen.screenX,
                            venusScreen.screenY,
                            '#f6c445',
                            '#fde047',
                            rawElapsed * 1000,
                            '✦ TRÁNSITO LATENTE',
                            `♀ VENUS ${{venusScreen.deg}}° ${{venusScreen.min}}' ${{venusScreen.signo.toUpperCase()}}`,
                            'En rectoría · Diplomacia y valor',
                            'der'
                        );

                        // 3. Aureola Júpiter
                        dibujarAureolaPlaneta(
                            ctx,
                            jupiterScreen.screenX,
                            jupiterScreen.screenY,
                            '#f97316',
                            '#fb923c',
                            (rawElapsed + 0.4) * 1000,
                            '✦ PLANETA RECEPTOR',
                            `♃ JÚPITER ${{jupiterScreen.deg}}° ${{jupiterScreen.min}}' ${{jupiterScreen.signo.toUpperCase()}}`,
                            'Fuego magno · Generosidad',
                            'izq'
                        );
                    }}

                    // ── RENDERIZADO DEL HEADER Y CARTELES INFERIORES ──
                    if (hudCardsAlpha > 0.01) {{
                        ctx.save();
                        ctx.globalAlpha = hudCardsAlpha;
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
                        ctx.fillText({j_header_fecha}, w / 2, 55);

                        ctx.font = '600 22px "Cinzel", "Times New Roman", serif';
                        ctx.fillStyle = '#f1f5f9';
                        ctx.shadowBlur = 6;
                        ctx.fillText({j_header_sub}, w / 2, 115);

                        if (window.__cineMode === 'intermedio') {{
                            const pillX = w / 2 - 290;
                            const pillY = 1340;
                            const pillW = 580;
                            const pillH = 145;

                            ctx.fillStyle = 'rgba(8, 14, 26, 0.94)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#fde047';
                            ctx.shadowBlur = 14;

                            ctx.beginPath();
                            ctx.roundRect(pillX, pillY, pillW, pillH, 16);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 21px "Cinzel", serif';
                            ctx.textAlign = 'center';
                            ctx.fillStyle = '#fde047';
                            ctx.shadowBlur = 4;
                            ctx.fillText({j_aspecto_hud_titulo}, w / 2, pillY + 22);

                            ctx.font = '700 13px "Courier New", monospace, sans-serif';
                            ctx.fillStyle = '#38bdf8';
                            ctx.shadowBlur = 0;
                            ctx.fillText({j_aspecto_hud_sub}, w / 2, pillY + 62);

                            ctx.font = '400 15px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#e2e8f0';
                            ctx.fillText({j_aspecto_hud_desc}, w / 2, pillY + 98);
                        }} else {{
                            // Tarjetas Inferiores Rediseñadas (cardH = 145px: Proporción Perfecta y Cero Vacíos)
                            const cardY = 1360;
                            const cardH = 145;

                            // Tarjeta 1 (Izquierda)
                            ctx.fillStyle = 'rgba(8, 14, 24, 0.92)';
                            ctx.strokeStyle = '#38bdf8';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#0284c7';
                            ctx.shadowBlur = 12;

                            ctx.beginPath();
                            ctx.roundRect(40, cardY, 480, cardH, 14);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 20px "Cinzel", serif';
                            ctx.textAlign = 'left';
                            ctx.fillStyle = '#38bdf8';
                            ctx.fillText({j_tarjeta1_titulo}, 60, cardY + 22);

                            ctx.font = '700 12px "Courier New", monospace, sans-serif';
                            ctx.fillStyle = '#7dd3fc';
                            ctx.fillText({j_tarjeta1_badge}, 60, cardY + 54);

                            ctx.font = '400 14px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#f8fafc';
                            ctx.fillText({j_tarjeta1_body}, 60, cardY + 84);

                            // Tarjeta 2 (Derecha)
                            ctx.fillStyle = 'rgba(18, 14, 8, 0.92)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#d97706';
                            ctx.shadowBlur = 12;

                            ctx.beginPath();
                            ctx.roundRect(560, cardY, 480, cardH, 14);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 20px "Cinzel", serif';
                            ctx.fillStyle = '#f6c445';
                            ctx.fillText({j_tarjeta2_titulo}, 580, cardY + 22);

                            ctx.font = '700 12px "Courier New", monospace, sans-serif';
                            ctx.fillStyle = '#fde047';
                            ctx.fillText({j_tarjeta2_badge}, 580, cardY + 54);

                            ctx.font = '400 14px -apple-system, BlinkMacSystemFont, sans-serif';
                            ctx.fillStyle = '#fef08a';
                            ctx.fillText({j_tarjeta2_body}, 580, cardY + 84);
                        }}

                        ctx.restore();
                    }}

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
        }})();
        """
        page.evaluate(setup_script)
        t_setup_done = time.time()
        offset_seconds = round(t_setup_done - t_browser_start, 2)
        print(f"⏱️ Inicialización lista en {offset_seconds:.2f}s. Grabando slot {duracion_s:.2f}s...")

        # Grabar la duración del slot
        t_start_record = time.time()
        while time.time() - t_start_record < (duracion_s + 0.3):
            time.sleep(0.04)

        context.close()
        browser.close()

    webm_files = list(clip_rec_dir.glob("*.webm"))
    if not webm_files:
        raise RuntimeError(f"No se encontró archivo WebM grabado en {clip_rec_dir}")
    recorded_webm = max(webm_files, key=lambda f: f.stat().st_mtime)

    # Transcodificar recortando EXACTAMENTE el tiempo de carga medido: 100% CERO GLITCH
    cmd_ffmpeg = (
        f"ffmpeg -y -i '{recorded_webm}' -ss {offset_seconds} -c:v libx264 -pix_fmt yuv420p "
        f"-r 30 -crf 14 -preset slow -t {duracion_s} '{out_mp4}' >/dev/null 2>&1"
    )
    subprocess.run(cmd_ffmpeg, shell=True, check=True)
    size_mb = out_mp4.stat().st_size / (1024 * 1024)
    print(f"✅ Clip generado: {out_mp4.name} ({size_mb:.2f} MB, {duracion_s:.2f}s)")
    return out_mp4


def generar_clips_fecha(
    fecha: str = "2026-11-05",
    dur_apertura: float = 7.0,
    dur_intermedio: float = 8.25,
    dur_cierre: float = 5.2,
    output_dir: Path = DEFAULT_OUTPUT_DIR
):
    print(f"\n=======================================================")
    print(f"🌟 GENERANDO CLIPS RELOJ 2D CINEMÁTICO V3.1: {fecha}")
    print(f"=======================================================")
    
    server_proc = iniciar_servidor(8788)
    try:
        f_apertura = output_dir / f"reloj_2d_{fecha}_cinematico_apertura.mp4"
        grabar_clip_reloj(
            tipo="apertura",
            duracion_s=dur_apertura,
            out_mp4=f_apertura,
            port=8788,
            date_str=fecha,
            planeta_foco="Luna",
            planeta_intermedio="Venus"
        )

        f_intermedio = output_dir / f"reloj_2d_{fecha}_cinematico_intermedio.mp4"
        grabar_clip_reloj(
            tipo="intermedio",
            duracion_s=dur_intermedio,
            out_mp4=f_intermedio,
            port=8788,
            date_str=fecha,
            planeta_foco="Luna",
            planeta_intermedio="Venus"
        )

        f_cierre = output_dir / f"reloj_2d_{fecha}_cinematico_cierre.mp4"
        grabar_clip_reloj(
            tipo="cierre",
            duracion_s=dur_cierre,
            out_mp4=f_cierre,
            port=8788,
            date_str=fecha,
            planeta_foco="Luna",
            planeta_intermedio="Venus"
        )

        print("\n✨ [ÉXITO] Todos los clips del reloj generados sin drop frames ni glitches.")
        return [f_apertura, f_intermedio, f_cierre]

    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except Exception:
            server_proc.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de Clips del Reloj 2D Cinemático V3.1")
    parser.add_argument("--fecha", default="2026-11-05", help="Fecha YYYY-MM-DD")
    parser.add_argument("--dur_apertura", type=float, default=7.0)
    parser.add_argument("--dur_intermedio", type=float, default=8.25)
    parser.add_argument("--dur_cierre", type=float, default=5.2)
    args = parser.parse_args()

    generar_clips_fecha(
        fecha=args.fecha,
        dur_apertura=args.dur_apertura,
        dur_intermedio=args.dur_intermedio,
        dur_cierre=args.dur_cierre
    )
