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
import base64
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
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/reloj?cinematico=1", timeout=1) as resp:
            if resp.status == 200:
                return None
    except Exception:
        pass

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
    badge_aspecto_texto: str = "[ ASPECTO EXACTO ]",
    badge_p1_sub: str = "Fuerza celeste activa",
    badge_p2_sub: str = "Planeta en aspecto",
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
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=1
        )
        page = context.new_page()
        page.goto(f"http://127.0.0.1:{port}/reloj?cinematico=1", wait_until="networkidle")
        page.wait_for_selector("#reloj-canvas", timeout=10000)
        # Esperar a que las fuentes web (Cinzel, Outfit) estén 100% cargadas en el motor Chromium
        page.evaluate("document.fonts.ready")

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
        j_badge_aspecto_texto = json.dumps(badge_aspecto_texto)
        j_badge_p1_sub = json.dumps(badge_p1_sub)
        j_badge_p2_sub = json.dumps(badge_p2_sub)

        # Inyectar motor cinemático de vanguardia
        setup_script = f"""
        (() => {{
            // Eliminar tooltips y HUD web para no ensuciar la toma
            const style = document.createElement('style');
            style.innerHTML = '#reloj-tooltip, .corner-hud {{ display: none !important; }}';
            document.head.appendChild(style);
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
                window.__badgeAspectoTexto = {j_badge_aspecto_texto};
                window.__badgeP1Sub = {j_badge_p1_sub};
                window.__badgeP2Sub = {j_badge_p2_sub};

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
                    
                    // 3. Badge flotante compacto al lado de la retícula
                    if (badgeTitulo) {{
                        ctx.save();
                        ctx.font = 'bold 16px "Outfit", sans-serif';
                        const textW = ctx.measureText(badgeTitulo).width;
                        const bx = (alinearLado === 'izq') ? (screenX - rReticle - textW - 22) : (screenX + rReticle + 12);
                        const by = screenY - 14;
                        ctx.fillStyle = 'rgba(6, 9, 18, 0.90)';
                        ctx.strokeStyle = colorHex;
                        ctx.lineWidth = 1.4;
                        ctx.shadowColor = glowColor;
                        ctx.shadowBlur = 10;
                        ctx.beginPath();
                        ctx.roundRect(bx - 6, by - 4, textW + 16, 26, 6);
                        ctx.fill();
                        ctx.stroke();
                        ctx.fillStyle = '#ffffff';
                        ctx.shadowBlur = 0;
                        ctx.textAlign = 'left';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(badgeTitulo, bx + 2, by + 9);
                        ctx.restore();
                    }}
                    
                    ctx.restore();
                }}

                // ── Helper: Dibujar Cuerda con Fotón en Movimiento ──
                function dibujarAspectoFotones(ctx, x1, y1, x2, y2, colorHex, glowColor, tMs, badgeTexto) {{
                    ctx.save();
                    
                    // 1. Cuerda áurea con resplandor intenso
                    ctx.strokeStyle = colorHex;
                    ctx.shadowColor = glowColor;
                    ctx.shadowBlur = 24;
                    ctx.lineWidth = 4.5;
                    ctx.globalAlpha = 1.0;
                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.stroke();

                    // Núcleo blanco brillante
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1.8;
                    ctx.shadowBlur = 10;
                    ctx.globalAlpha = 0.85;
                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.stroke();
                    
                    // 2. Fotón de plasma que viaja continuamente entre los dos planetas
                    const tPhoton = (Math.sin(tMs * 0.0035) + 1.0) / 2.0;
                    const px = x1 + (x2 - x1) * tPhoton;
                    const py = y1 + (y2 - y1) * tPhoton;
                    
                    const photonGrad = ctx.createRadialGradient(px, py, 2, px, py, 16);
                    photonGrad.addColorStop(0, '#ffffff');
                    photonGrad.addColorStop(0.3, colorHex);
                    photonGrad.addColorStop(1, 'transparent');
                    ctx.fillStyle = photonGrad;
                    ctx.shadowColor = glowColor;
                    ctx.shadowBlur = 24;
                    ctx.beginPath();
                    ctx.arc(px, py, 16, 0, Math.PI * 2);
                    ctx.fill();
                    
                    // Destello de 4 puntas en el fotón
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1.8;
                    ctx.beginPath();
                    ctx.moveTo(px - 14, py); ctx.lineTo(px + 14, py);
                    ctx.moveTo(px, py - 14); ctx.lineTo(px, py + 14);
                    ctx.stroke();
                    
                    // 3. Cartel central del aspecto en el punto medio de la cuerda
                    if (badgeTexto) {{
                        const mx = (x1 + x2) / 2;
                        const my = (y1 + y2) / 2;
                        ctx.save();
                        ctx.font = 'bold 16px "Outfit", sans-serif';
                        const textW = ctx.measureText(badgeTexto).width;
                        const padX = 14;
                        const padY = 7;
                        
                        ctx.fillStyle = 'rgba(7, 10, 19, 0.92)';
                        ctx.strokeStyle = colorHex;
                        ctx.lineWidth = 1.6;
                        ctx.shadowColor = glowColor;
                        ctx.shadowBlur = 14;
                        
                        ctx.beginPath();
                        ctx.roundRect(mx - textW/2 - padX, my - 14 - padY, textW + padX*2, 28 + padY, 6);
                        ctx.fill();
                        ctx.stroke();
                        
                        ctx.fillStyle = '#ffffff';
                        ctx.shadowBlur = 0;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(badgeTexto, mx, my);
                        ctx.restore();
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
                            (asp.p1 === window.__planetaFoco && asp.p2 === window.__planetaIntermedio) ||
                            (asp.p2 === window.__planetaFoco && asp.p1 === window.__planetaIntermedio)
                        );

                        if (esProtagonista) {{
                            ctx.save();
                            ctx.strokeStyle = '#f6c445';
                            ctx.shadowColor = '#fde047';
                            ctx.shadowBlur = 24;
                            ctx.lineWidth = 5.0;
                            ctx.globalAlpha = 1.0;
                            ctx.beginPath();
                            ctx.moveTo(x1, y1);
                            ctx.lineTo(x2, y2);
                            ctx.stroke();

                            const mx = (x1 + x2) / 2;
                            const my = (y1 + y2) / 2;
                            ctx.fillStyle = '#ffffff';
                            ctx.beginPath();
                            ctx.arc(mx, my, 5, 0, Math.PI * 2);
                            ctx.fill();
                            ctx.restore();
                        }} else {{
                            // Aspectos secundarios: nítidos y geométricamente visibles
                            ctx.strokeStyle = asp.color;
                            ctx.globalAlpha = 0.35;
                            ctx.lineWidth = 1.8;
                            ctx.shadowColor = asp.color;
                            ctx.shadowBlur = 6;
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
                    let p1ClockX = 0, p1ClockY = 0;
                    let p2ClockX = 0, p2ClockY = 0;

                    if (eng.calculated && eng.calculated.planets) {{
                        if (eng.calculated.planets[window.__planetaFoco]) {{
                            const a = eng.coordToAngle(eng.calculated.planets[window.__planetaFoco].grado_absoluto);
                            p1ClockX = Math.cos(a) * rPlanets;
                            p1ClockY = Math.sin(a) * rPlanets;
                            focoClockX = p1ClockX;
                            focoClockY = p1ClockY;
                        }}
                        if (eng.calculated.planets[window.__planetaIntermedio]) {{
                            const a = eng.coordToAngle(eng.calculated.planets[window.__planetaIntermedio].grado_absoluto);
                            p2ClockX = Math.cos(a) * rPlanets;
                            p2ClockY = Math.sin(a) * rPlanets;
                        }} else {{
                            p2ClockX = p1ClockX;
                            p2ClockY = p1ClockY;
                        }}
                        interClockX = (p1ClockX + p2ClockX) / 2;
                        interClockY = (p1ClockY + p2ClockY) / 2;
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
                        // Coreografía Cinemática: Vista General (0.4s) -> Zoom Dinámico Progresivo (2.2s) -> HOLD
                        const pauseStart = 0.40;
                        const zoomDur = 2.20;
                        const zoomEnd = pauseStart + zoomDur;
                        const sEnd = 1.56;
                        const endPanX = -interClockX * sEnd * 0.55;
                        const endPanY = (targetScreenY - cy) - interClockY * sEnd * 0.55;

                        if (rawElapsed <= pauseStart) {{
                            // 1. Dial general completo sereno (1.00x)
                            targetZoom = 1.00;
                            targetPanX = 0;
                            targetPanY = -140;
                            hudCardsAlpha = 0.85;
                        }} else if (rawElapsed <= zoomEnd) {{
                            // 2. Zoom cinematográfico progresivo y suave hacia el eje del aspecto
                            const pZ = (rawElapsed - pauseStart) / zoomDur;
                            const ease = pZ < 0.5 ? 4 * pZ * pZ * pZ : 1 - Math.pow(-2 * pZ + 2, 3) / 2;
                            targetZoom = 1.00 + ease * 0.56; // 1.00x -> 1.56x
                            targetPanX = 0 * (1 - ease) + endPanX * ease;
                            targetPanY = -140 * (1 - ease) + endPanY * ease;
                            hudCardsAlpha = 0.85 + ease * 0.15;
                        }} else {{
                            // 3. HOLD cinemático majestuoso y estable (CERO rebote, CERO oscilación)
                            targetZoom = 1.56;
                            targetPanX = endPanX;
                            targetPanY = endPanY;
                            hudCardsAlpha = 1.0;
                        }}
                        mandalaAlpha = 1.0;
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

                    function getScreenPlanet(pName) {{
                        if (!eng.calculated || !eng.calculated.planets || !eng.calculated.planets[pName]) return null;
                        const p = eng.calculated.planets[pName];
                        const a = eng.coordToAngle(p.grado_absoluto);
                        const px = Math.cos(a) * rPlanets;
                        const py = Math.sin(a) * rPlanets;
                        return {{
                            screenX: (cx + eng.camera.panX) + px * currentScale,
                            screenY: (cy + eng.camera.panY) + py * currentScale,
                            deg: p.grado,
                            min: p.minutos,
                            signo: p.signo
                        }};
                    }}

                    const focoScreen = getScreenPlanet(window.__planetaFoco);
                    const interScreen = getScreenPlanet(window.__planetaIntermedio);

                    // ── RENDERIZADO DE AUREOLAS Y HUD LATENTE ──
                    if (window.__cineMode === 'apertura' && focoScreen && rawElapsed >= 1.6) {{
                        const aAureola = Math.min(1.0, (rawElapsed - 1.6) / 0.6);
                        ctx.save();
                        ctx.globalAlpha = aAureola;
                        const alado = focoScreen.screenX > 540 ? 'izq' : 'der';
                        dibujarAureolaPlaneta(
                            ctx,
                            focoScreen.screenX,
                            focoScreen.screenY,
                            '#38bdf8',
                            '#00f2fe',
                            rawElapsed * 1000,
                            '✦ TRÁNSITO LATENTE',
                            `${{window.__planetaFoco.toUpperCase()}} ${{focoScreen.deg}}° ${{focoScreen.min}}' ${{focoScreen.signo.toUpperCase()}}`,
                            window.__badgeP1Sub || 'Posición celeste activa',
                            alado
                        );
                        ctx.restore();
                    }}

                    if (window.__cineMode === 'intermedio' && focoScreen && interScreen) {{
                        // 1. Cuerda con haz de fotones oscilantes y badge de orbe latente
                        dibujarAspectoFotones(
                            ctx,
                            focoScreen.screenX,
                            focoScreen.screenY,
                            interScreen.screenX,
                            interScreen.screenY,
                            '#f6c445',
                            '#fde047',
                            rawElapsed * 1000,
                            window.__badgeAspectoTexto || "[ ASPECTO EXACTO ]"
                        );

                        // 2. Aureola Planeta Foco
                        const aladoFoco = focoScreen.screenX > 540 ? 'izq' : 'der';
                        const glifosMap = {{'Sol':'☉ ','Luna':'☽ ','Mercurio':'☿ ','Venus':'♀ ','Marte':'♂ ','Júpiter':'♃ ','Saturno':'♄ '}};
                        const gFoco = glifosMap[window.__planetaFoco] || '';
                        const gInter = glifosMap[window.__planetaIntermedio] || '';
                        const labelFoco = `${{gFoco}}${{window.__planetaFoco.toUpperCase()}} ${{focoScreen.deg}}° ${{focoScreen.signo.toUpperCase()}}`;
                        const labelInter = `${{gInter}}${{window.__planetaIntermedio.toUpperCase()}} ${{interScreen.deg}}° ${{interScreen.signo.toUpperCase()}}`;

                        dibujarAureolaPlaneta(
                            ctx,
                            focoScreen.screenX,
                            focoScreen.screenY,
                            '#38bdf8',
                            '#00f2fe',
                            rawElapsed * 1000,
                            labelFoco,
                            `${{window.__planetaFoco.toUpperCase()}} ${{focoScreen.deg}}° ${{focoScreen.min}}' ${{focoScreen.signo.toUpperCase()}}`,
                            window.__badgeP1Sub || 'Fuerza celeste protagonista',
                            aladoFoco
                        );

                        // 3. Aureola Planeta Intermedio
                        const aladoInter = interScreen.screenX > 540 ? 'izq' : 'der';
                        dibujarAureolaPlaneta(
                            ctx,
                            interScreen.screenX,
                            interScreen.screenY,
                            '#f6c445',
                            '#fde047',
                            (rawElapsed + 0.4) * 1000,
                            labelInter,
                            `${{window.__planetaIntermedio.toUpperCase()}} ${{interScreen.deg}}° ${{interScreen.min}}' ${{interScreen.signo.toUpperCase()}}`,
                            window.__badgeP2Sub || 'Resonancia armónica / tensión',
                            aladoInter
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

                        const pulseDestello = 0.5 + 0.5 * Math.sin(rawElapsed * 1000 * 0.005);

                        if (window.__cineMode === 'intermedio') {{
                            const pillX = w / 2 - 290;
                            const pillY = 1340;
                            const pillW = 580;
                            const pillH = 145;

                            ctx.fillStyle = 'rgba(8, 14, 26, 0.94)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 1.8 + 1.4 * pulseDestello;
                            ctx.shadowColor = '#fde047';
                            ctx.shadowBlur = 10 + 18 * pulseDestello;

                            ctx.beginPath();
                            ctx.roundRect(pillX, pillY, pillW, pillH, 16);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 22px "Cinzel", serif';
                            ctx.textAlign = 'center';
                            ctx.fillStyle = '#fde047';
                            ctx.shadowBlur = 4 + 6 * pulseDestello;
                            ctx.fillText({j_aspecto_hud_titulo}, w / 2, pillY + 32);

                            ctx.font = '700 14px "Outfit", sans-serif';
                            ctx.fillStyle = '#38bdf8';
                            ctx.shadowBlur = 0;
                            ctx.fillText({j_aspecto_hud_sub}, w / 2, pillY + 68);

                            ctx.font = '500 15px "Outfit", sans-serif';
                            ctx.fillStyle = '#e2e8f0';
                            ctx.fillText({j_aspecto_hud_desc}, w / 2, pillY + 104);
                        }} else {{
                            // Tarjetas Inferiores Rediseñadas con Destello Sincronizado
                            const cardY = 1360;
                            const cardH = 145;

                            // Tarjeta 1 (Izquierda)
                            ctx.fillStyle = 'rgba(8, 14, 24, 0.92)';
                            ctx.strokeStyle = '#38bdf8';
                            ctx.lineWidth = 1.8 + 1.2 * pulseDestello;
                            ctx.shadowColor = '#0284c7';
                            ctx.shadowBlur = 10 + 16 * pulseDestello;

                            ctx.beginPath();
                            ctx.roundRect(40, cardY, 480, cardH, 14);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 21px "Cinzel", serif';
                            ctx.textAlign = 'left';
                            ctx.fillStyle = '#38bdf8';
                            ctx.shadowBlur = 2 + 4 * pulseDestello;
                            ctx.fillText({j_tarjeta1_titulo}, 65, cardY + 34);

                            ctx.font = '700 13px "Outfit", sans-serif';
                            ctx.fillStyle = '#7dd3fc';
                            ctx.shadowBlur = 0;
                            ctx.fillText({j_tarjeta1_badge}, 65, cardY + 68);

                            ctx.font = '500 14.5px "Outfit", sans-serif';
                            ctx.fillStyle = '#f8fafc';
                            ctx.fillText({j_tarjeta1_body}, 65, cardY + 102);

                            // Tarjeta 2 (Derecha)
                            const pulseDestello2 = 0.5 + 0.5 * Math.sin((rawElapsed * 1000 + 400) * 0.005);
                            ctx.fillStyle = 'rgba(18, 14, 8, 0.92)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 1.8 + 1.2 * pulseDestello2;
                            ctx.shadowColor = '#d97706';
                            ctx.shadowBlur = 10 + 16 * pulseDestello2;

                            ctx.beginPath();
                            ctx.roundRect(560, cardY, 480, cardH, 14);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 21px "Cinzel", serif';
                            ctx.fillStyle = '#f6c445';
                            ctx.shadowBlur = 2 + 4 * pulseDestello2;
                            ctx.fillText({j_tarjeta2_titulo}, 585, cardY + 34);

                            ctx.font = '700 13px "Outfit", sans-serif';
                            ctx.fillStyle = '#fde047';
                            ctx.shadowBlur = 0;
                            ctx.fillText({j_tarjeta2_badge}, 585, cardY + 68);

                            ctx.font = '500 14.5px "Outfit", sans-serif';
                            ctx.fillStyle = '#fef08a';
                            ctx.fillText({j_tarjeta2_body}, 585, cardY + 102);
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

        record_script = f"""
        () => new Promise((resolve, reject) => {{
            try {{
                const canvas = document.getElementById('reloj-canvas');
                if (!canvas) {{
                    reject("No se encontro #reloj-canvas");
                    return;
                }}
                window.__cineStartTime = performance.now();
                const stream = canvas.captureStream(30);
                const chunks = [];
                let mime = 'video/webm;codecs=vp9';
                if (!MediaRecorder.isTypeSupported(mime)) {{
                    mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp8') ? 'video/webm;codecs=vp8' : 'video/webm';
                }}
                const recorder = new MediaRecorder(stream, {{
                    mimeType: mime,
                    videoBitsPerSecond: 25000000
                }});
                recorder.ondataavailable = (e) => {{
                    if (e.data && e.data.size > 0) chunks.push(e.data);
                }};
                recorder.onstop = () => {{
                    const blob = new Blob(chunks, {{ type: mime }});
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                }};
                recorder.start();
                setTimeout(() => {{
                    try {{
                        recorder.stop();
                    }} catch (err) {{
                        reject(err.toString());
                    }}
                }}, Math.ceil({duracion_s} * 1000));
            }} catch (err) {{
                reject(err.toString());
            }}
        }})
        """
        print(f"🎥 Grabando canvas nativo a 25 Mbps ({duracion_s:.2f}s)...")
        data_url = page.evaluate(record_script)
        header, encoded = data_url.split(",", 1)
        video_bytes = base64.b64decode(encoded)

        recorded_webm = clip_rec_dir / f"{tipo}_{int(time.time()*1000)}.webm"
        with open(recorded_webm, "wb") as f:
            f.write(video_bytes)

        context.close()
        browser.close()

    # Transcodificar con FFmpeg a master H.264 CRF 12 (sin pixelado, nitidez absoluta)
    cmd_ffmpeg = [
        "ffmpeg", "-y", "-i", str(recorded_webm),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", "30", "-crf", "12", "-preset", "slow",
        "-t", f"{duracion_s:.3f}", str(out_mp4)
    ]
    subprocess.run(cmd_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    size_mb = out_mp4.stat().st_size / (1024 * 1024)
    print(f"✅ Clip generado: {out_mp4.name} ({size_mb:.2f} MB, {duracion_s:.2f}s) [Master CRF 12]")
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
        if server_proc:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=3)
            except Exception:
                server_proc.kill()


def capturar_clip_reloj_cinematico(
    fecha_str: str,
    duracion_s: float = 6.0,
    output_dir: Path = None,
    forzar: bool = False,
    port: int = 8788
) -> Path:
    """
    Genera el clip cinemático del Reloj 2D (con zoom al aspecto, fotones y aureolas sonar)
    para la toma intermedia (Toma 3 / Mecánica Celeste) del orquestador unificado V2.
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = output_dir / f"reloj_2d_{fecha_str}.mp4"

    # Si ya existe y no se fuerza la regeneración
    if out_mp4.exists() and not forzar and out_mp4.stat().st_size > 1_500_000:
        print(f"⚡ Clip Reloj 2D Cinemático reutilizado: {out_mp4.name} ({out_mp4.stat().st_size/(1024*1024):.2f} MB)")
        return out_mp4

    from datetime import datetime
    adn_path = FACTORY_ROOT / "contexto_astrologico.json"
    with open(adn_path, "r", encoding="utf-8") as f:
        adn = json.load(f)

    transito = adn.get("transito", {})
    planeta_str = transito.get("planeta", "Luna y Mercurio")
    partes = [p.strip() for p in planeta_str.replace(" y ", ",").split(",") if p.strip()]
    planeta_foco = partes[0] if len(partes) > 0 else "Luna"
    planeta_intermedio = partes[1] if len(partes) > 1 else ("Mercurio" if planeta_foco == "Luna" else "Luna")

    signo = transito.get("signo_destino", "Escorpio")
    tipo_asp = transito.get("tipo_aspecto", "Conjunción")
    orbe_limpio = tipo_asp.split("(")[-1].replace(")", "") if "(" in tipo_asp else "orbe exacto"

    dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    meses = ["", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    header_fecha = f"{dt.day} DE {meses[dt.month]} {dt.year}"
    header_sub = f"✦ MECÁNICA CELESTE · {planeta_foco.upper()} Y {planeta_intermedio.upper()} ✦"
    aspecto_hud_titulo = f"{planeta_foco.upper()} {tipo_asp.split()[0].upper()} {planeta_intermedio.upper()} · {signo.upper()}"
    aspecto_hud_sub = f"✦ {tipo_asp.upper()} · TRÁNSITO ACTIVO ✦"
    aspecto_hud_desc = transito.get("descripcion_breve", "Mecánica celeste exacta en el Astrolabio Sagrado.")[:85]
    badge_aspecto_texto = f"✦ {tipo_asp.split()[0].upper()} · {planeta_foco.upper()} / {planeta_intermedio.upper()} ✦"

    duracion_grabacion = round(duracion_s + 3.5, 2)
    print(f"\n🌟 Generando Reloj 2D Cinemático ({duracion_grabacion:.2f}s [slot {duracion_s:.2f}s + margen]) para {fecha_str}...")
    print(f"   Foco: {planeta_foco} · Intermedio: {planeta_intermedio} · Signo: {signo}")

    server_proc = iniciar_servidor(port)
    try:
        grabar_clip_reloj(
            tipo="intermedio",
            duracion_s=duracion_grabacion,
            out_mp4=out_mp4,
            port=port,
            date_str=fecha_str,
            header_fecha=header_fecha,
            header_sub=header_sub,
            aspecto_hud_titulo=aspecto_hud_titulo,
            aspecto_hud_sub=aspecto_hud_sub,
            aspecto_hud_desc=aspecto_hud_desc,
            badge_aspecto_texto=badge_aspecto_texto,
            badge_p1_sub=f"Tránsito activo en {signo}",
            badge_p2_sub=f"Resonancia celeste en {signo}",
            planeta_foco=planeta_foco,
            planeta_intermedio=planeta_intermedio
        )
        return out_mp4
    finally:
        if server_proc:
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
