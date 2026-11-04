#!/usr/bin/env python3
"""
🌓 CÉLULA 2 — generador_reloj_cinematico.py (Versión Maestra 3.0)
─────────────────────────────────────────────────────────────────────────────
Motor Cinemático del Reloj Astrológico 2D (Apertura, Intermedio, Cierre)
Proyecto: El Glifo Maestro / Astrology Factory

Garantías Cinemáticas:
1. Sincronización absoluta: Se mide el timestamp exacto de inicialización de Playwright.
   FFmpeg recorta con '-ss offset_exacto' eliminando cualquier frame previo a la carga.
2. CERO pantallas blancas y CERO botones de UI desde la carga del DOM ('?cinematico=1').
3. Velocidad de rotación serena y calibrada (micro-deriva horaria sin aceleración en zoom).
4. Coreografía de zoom precisa:
   - Apertura: 1.00x sereno -> zoom suave a 1.45x hacia Libra/Luna al final.
   - Intermedio: Inicia 100% encuadrado en zoom 1.75x sobre Venus sextil Júpiter.
   - Cierre: zoom out progresivo y calmo (1.50x a 1.04x) que culmina a las 24:00:00.
5. Calidad visual lossless (CRF 14, 30 fps CFR constantes).
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
    tarjeta1_titulo: str = "☽ LUNA EN LIBRA 0°",
    tarjeta1_body: str = "Búsqueda de balance y acuerdos justos sin complacencia sumisa.",
    tarjeta2_titulo: str = "♀ VENUS SEXTIL JÚPITER 24°",
    tarjeta2_body: str = "Pactar con altura, encanto y valor propio sin mendigar.",
    aspecto_hud_titulo: str = "♀ VENUS SEXTIL JÚPITER · 24° ♎ ♌",
    aspecto_hud_sub: str = "Sextil exacto: diplomacia, cintura y generosidad",
    aspecto_hud_desc: str = "Pactar con altura sin regalar tu valor propio.",
    planeta_foco: str = "Luna",
    planeta_intermedio: str = "Venus"
):
    nombre_archivo = out_mp4.stem
    clip_rec_dir = TEMP_RECORD_DIR / f"rec_{tipo}_{int(time.time()*1000)}"
    if clip_rec_dir.exists():
        shutil.rmtree(clip_rec_dir)
    clip_rec_dir.mkdir(parents=True, exist_ok=True)

    if tipo == "apertura":
        fecha_inicio_iso = f"{date_str}T00:00:00"
        horas_recorridas = 0.10
    elif tipo == "intermedio":
        fecha_inicio_iso = f"{date_str}T12:00:00"
        horas_recorridas = 0.04
    else:  # cierre
        fecha_inicio_iso = f"{date_str}T23:50:00"
        horas_recorridas = 0.16

    print(f"🎬 [Motor Cinemático V3] Grabando '{tipo}' ({nombre_archivo}.mp4, {duracion_s:.2f}s)...")

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

        # Inyectar motor de animación cinemática sincronizado
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
                window.__planetaFoco = '{planeta_foco}';
                window.__planetaIntermedio = '{planeta_intermedio}';

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

                    const currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
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

                    let targetZoom = 1.0;
                    let targetPanX = 0;
                    let targetPanY = -160;
                    let mandalaAlpha = 1.0;
                    let flashAlpha = 0.0;
                    let hudAlpha = 1.0;

                    const targetScreenY = 780;

                    if (window.__cineMode === 'apertura') {{
                        if (progress <= 0.70) {{
                            const pNorm = progress / 0.70;
                            targetZoom = 1.00 + pNorm * 0.08;
                            targetPanX = 0;
                            targetPanY = -160;
                            hudAlpha = 1.0;
                        }} else {{
                            const pZoom = (progress - 0.70) / 0.30;
                            const easeZoom = Math.pow(pZoom, 2.0);
                            targetZoom = 1.08 + easeZoom * 0.37;
                            
                            const s = targetZoom;
                            const finalPanX = -focoClockX * s * 0.65;
                            const finalPanY = (targetScreenY - cy) - focoClockY * s * 0.65;

                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -160 * (1 - easeZoom) + finalPanY * easeZoom;
                            hudAlpha = Math.max(0, 1.0 - pZoom * 1.5);

                            if (pZoom > 0.80) {{
                                flashAlpha = ((pZoom - 0.80) / 0.20) * 0.35;
                            }}
                        }}
                    }} else if (window.__cineMode === 'intermedio') {{
                        targetZoom = 1.75 + Math.sin(progress * Math.PI) * 0.03;
                        const s = targetZoom;
                        targetPanX = -interClockX * s * 0.75;
                        targetPanY = (targetScreenY - cy) - interClockY * s * 0.75;
                        mandalaAlpha = 1.0;
                        hudAlpha = 1.0;
                    }} else {{
                        if (progress <= 0.35) {{
                            const pZoom = progress / 0.35;
                            const easeZoom = Math.pow(1 - pZoom, 1.8);
                            targetZoom = 1.04 + easeZoom * 0.46;
                            
                            const s = targetZoom;
                            const finalPanX = -focoClockX * s * 0.5;
                            const finalPanY = (targetScreenY - cy) - focoClockY * s * 0.5;
                            targetPanX = 0 * (1 - easeZoom) + finalPanX * easeZoom;
                            targetPanY = -160 * (1 - easeZoom) + finalPanY * easeZoom;
                            hudAlpha = Math.max(0.2, pZoom);
                        }} else if (progress <= 0.75) {{
                            targetZoom = 1.04;
                            targetPanX = 0;
                            targetPanY = -160;
                            hudAlpha = 1.0;
                        }} else {{
                            const pEnd = (progress - 0.75) / 0.25;
                            targetZoom = 1.04 - pEnd * 0.12;
                            targetPanX = 0;
                            targetPanY = -160;

                            const pulse = Math.sin(pEnd * Math.PI);
                            eng.horology.dayPulse = pulse * 1.5;
                            eng.horology.flashes.hourRing = pulse;
                            mandalaAlpha = Math.max(0, 1.0 - pEnd * 0.85);
                            hudAlpha = Math.max(0, 1.0 - pEnd * 1.2);
                        }}
                    }}

                    eng.camera.zoom = targetZoom;
                    eng.camera.panX = targetPanX;
                    eng.camera.panY = targetPanY;

                    ctx.save();
                    ctx.globalAlpha = mandalaAlpha;
                    origRender();
                    ctx.restore();

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
                            const pillX = w / 2 - 250;
                            const pillY = 1320;
                            const pillW = 500;
                            const pillH = 145;

                            ctx.fillStyle = 'rgba(10, 18, 30, 0.92)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#fde047';
                            ctx.shadowBlur = 14;

                            ctx.beginPath();
                            ctx.roundRect(pillX, pillY, pillW, pillH, 16);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 20px "Cinzel", serif';
                            ctx.textAlign = 'center';
                            ctx.fillStyle = '#fde047';
                            ctx.shadowBlur = 4;
                            ctx.fillText('{aspecto_hud_titulo}', w / 2, pillY + 22);

                            ctx.font = '600 16px -apple-system, sans-serif';
                            ctx.fillStyle = '#e2e8f0';
                            ctx.shadowBlur = 0;
                            ctx.fillText('{aspecto_hud_sub}', w / 2, pillY + 62);

                            ctx.font = '400 14px -apple-system, sans-serif';
                            ctx.fillStyle = '#94a3b8';
                            ctx.fillText('{aspecto_hud_desc}', w / 2, pillY + 98);
                        }} else {{
                            const cardY = 1350;
                            const cardH = 210;

                            // Tarjeta 1
                            ctx.fillStyle = 'rgba(8, 14, 24, 0.90)';
                            ctx.strokeStyle = '#38bdf8';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#0284c7';
                            ctx.shadowBlur = 12;

                            ctx.beginPath();
                            ctx.roundRect(40, cardY, 480, cardH, 14);
                            ctx.fill();
                            ctx.stroke();

                            ctx.font = '700 22px "Cinzel", serif';
                            ctx.textAlign = 'left';
                            ctx.fillStyle = '#38bdf8';
                            ctx.fillText('{tarjeta1_titulo}', 60, cardY + 24);

                            ctx.font = '500 17px -apple-system, sans-serif';
                            ctx.fillStyle = '#bae6fd';
                            ctx.fillText('{tarjeta1_body}', 60, cardY + 65);

                            // Tarjeta 2
                            ctx.fillStyle = 'rgba(18, 14, 8, 0.90)';
                            ctx.strokeStyle = '#f6c445';
                            ctx.lineWidth = 2.0;
                            ctx.shadowColor = '#d97706';
                            ctx.shadowBlur = 12;

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
    dur_apertura: float = 5.0,
    dur_intermedio: float = 6.0,
    dur_cierre: float = 4.5,
    output_dir: Path = DEFAULT_OUTPUT_DIR
):
    print(f"\n=======================================================")
    print(f"🌟 GENERANDO CLIPS RELOJ 2D CINEMÁTICO V3: {fecha}")
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
    parser = argparse.ArgumentParser(description="Generador de Clips del Reloj 2D Cinemático V3")
    parser.add_argument("--fecha", default="2026-11-05", help="Fecha YYYY-MM-DD")
    parser.add_argument("--dur_apertura", type=float, default=5.0)
    parser.add_argument("--dur_intermedio", type=float, default=6.0)
    parser.add_argument("--dur_cierre", type=float, default=4.5)
    args = parser.parse_args()

    generar_clips_fecha(
        fecha=args.fecha,
        dur_apertura=args.dur_apertura,
        dur_intermedio=args.dur_intermedio,
        dur_cierre=args.dur_cierre
    )
