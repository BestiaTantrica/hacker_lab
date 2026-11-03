"""
grabar_reloj_cinematico_04nov.py
─────────────────────────────────────────────────────────────────────────────
Capturador Cinemático de Doble Reloj 2D para el 4 de Noviembre de 2026:
- Tránsito: Mercurio en el Corazón del Sol (Cazimi 12° Escorpio, orbe 0.06°)
            + Luna en Virgo (17° Virgo) en Sextil armónico exacto.
- Velocidad reducida (recorre 6h en lugar de 12h, rotación suave y serena).
- Zoom calibrado a 0.98x - 1.05x (mandala 100% visible, sin cortes).
- Centro despejado: aspectos secundarios en alpha 0.08 (cero cuadros feos).
- Aspectos protagonistas iluminados con rayo láser cyan y halo áureo.
- Tarjetas tácticas periféricas en franja y=1280 a 1510 (líneas guía neón).
- Zona inferior y=1580 a 1920 100% despejada y libre para subtítulos.
- Cierre culmina a las 24:00:00 hs con destello áureo en los 3 anillos.
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

# Duraciones de slots de Toma 1 y Toma 5 (~7.5s y ~6.5s)
DURACION_APERTURA_S = 7.5
DURACION_CIERRE_S = 6.5

def run_server(port=8783):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def capturar_clip(tipo: str, nombre_archivo: str, port: int = 8783):
    out_webm = OUTPUT_DIR / f"{nombre_archivo}.webm"
    out_mp4 = OUTPUT_DIR / f"{nombre_archivo}.mp4"

    if out_mp4.exists() and out_mp4.stat().st_size > 500000:
        print(f"⚡ Clip ya existe y verificado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
        return out_mp4

    duracion_slot = DURACION_APERTURA_S if tipo == "apertura" else DURACION_CIERRE_S
    # Grabamos 0.8s extra para dar margen a transiciones y trim
    grabar_duracion = duracion_slot + 0.8

    # Apertura: 00:00 a 06:00 hs | Cierre: 18:00 a 24:00 hs
    fecha_inicio_iso = "2026-11-04T00:00:00" if tipo == "apertura" else "2026-11-04T18:00:00"
    horas_recorridas = 6.0

    print(f"🎬 Grabando clip cinemático 4 Nov '{tipo}' ({nombre_archivo}, {duracion_slot}s)...")

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
                eng.cambiarFondo('negro');
                eng.timeState.isLive = false;
                
                window.__cineMode = '{tipo}';
                window.__slotDuration = {duracion_slot};
                window.__cineStartTime = performance.now();
                window.__startMs = new Date('{fecha_inicio_iso}').getTime();
                window.__endMs = window.__startMs + {horas_recorridas} * 3600 * 1000;
                
                // Centrado optimizado: mandala en y=790 (acaba en y=1260)
                eng.camera.panX = 0;
                eng.camera.panY = -170;
                eng.camera.zoom = 0.98;

                // 1. Atenuar aspectos secundarios y destacar protagonistas
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
                                ctx.lineWidth = 3.2;
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
                            ctx.arc(mx, my, 3.5, 0, Math.PI * 2);
                            ctx.fill();
                            ctx.restore();
                        }} else {{
                            ctx.strokeStyle = asp.color;
                            ctx.globalAlpha = 0.08;
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

                    // Rotación suave del tiempo
                    const currentClockMs = window.__startMs + progress * (window.__endMs - window.__startMs);
                    eng.timeState.currentDate = new Date(currentClockMs);
                    eng.calculateAll();

                    // Si es cierre y estamos en el último segundo, activar destello de las 24hs
                    if (window.__cineMode === 'cierre' && progress >= 0.85) {{
                        const pulseFactor = (progress - 0.85) / 0.15;
                        eng.horology.dayPulse = Math.sin(pulseFactor * Math.PI) * 1.5;
                        eng.horology.flashes.hourRing = Math.sin(pulseFactor * Math.PI);
                    }}

                    // Renderizar mandala
                    origRender();

                    const ctx = eng.ctx;
                    const w = eng.width;
                    const h = eng.height;
                    const cx = w / 2;
                    const cy = h / 2;
                    const baseScale = Math.min(w, h) / 1080;
                    const currentScale = baseScale * eng.camera.zoom;
                    const clockScreenX = cx + eng.camera.panX;
                    const clockScreenY = cy + eng.camera.panY;

                    function getPlanetScreenCoords(planetName) {{
                        if (!eng.calculated || !eng.calculated.planets || !eng.calculated.planets[planetName]) return null;
                        const p = eng.calculated.planets[planetName];
                        const a = eng.coordToAngle(p.grado_absoluto);
                        const r = eng.radii.planets || 275;
                        const px = Math.cos(a) * r;
                        const py = Math.sin(a) * r;
                        return {{
                            x: clockScreenX + px * currentScale,
                            y: clockScreenY + py * currentScale,
                            a: a,
                            r: r
                        }};
                    }}

                    const merc = getPlanetScreenCoords('Mercurio');
                    const luna = getPlanetScreenCoords('Luna');

                    ctx.save();
                    ctx.setTransform(1, 0, 0, 1, 0, 0);

                    // ── 1. HEADER SUPERIOR ──────────────────────────────────
                    const gradTop = ctx.createLinearGradient(0, 0, 0, 220);
                    gradTop.addColorStop(0, 'rgba(5, 7, 12, 0.98)');
                    gradTop.addColorStop(0.7, 'rgba(5, 7, 12, 0.85)');
                    gradTop.addColorStop(1, 'rgba(5, 7, 12, 0)');
                    ctx.fillStyle = gradTop;
                    ctx.fillRect(0, 0, w, 220);

                    ctx.font = '700 40px "Cinzel", "Times New Roman", serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillStyle = '#f6c445';
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 10;
                    ctx.fillText('4 DE NOVIEMBRE 2026', w / 2, 60);

                    ctx.strokeStyle = 'rgba(246, 196, 69, 0.5)';
                    ctx.lineWidth = 1.4;
                    ctx.beginPath();
                    ctx.moveTo(w / 2 - 180, 116);
                    ctx.lineTo(w / 2 + 180, 116);
                    ctx.stroke();

                    ctx.fillStyle = '#f6c445';
                    ctx.beginPath();
                    ctx.arc(w / 2, 116, 3.5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.font = '600 23px "Cinzel", "Times New Roman", serif';
                    ctx.fillStyle = '#f1f5f9';
                    ctx.shadowBlur = 6;
                    ctx.fillText('MERCURIO EN EL CORAZÓN DEL SOL · 12° ♏ ESCORPIO', w / 2, 132);

                    // ── 2. RETÍCULAS ÓPTICAS ────────────────────────────────
                    if (merc) {{
                        ctx.strokeStyle = '#f6c445';
                        ctx.lineWidth = 2.6;
                        ctx.shadowColor = 'rgba(246, 196, 69, 0.95)';
                        ctx.shadowBlur = 18;
                        ctx.beginPath();
                        ctx.arc(merc.x, merc.y, 32, 0, Math.PI * 2);
                        ctx.stroke();

                        for (let i = 0; i < 4; i++) {{
                            const ang = (i * Math.PI / 2);
                            ctx.beginPath();
                            ctx.moveTo(merc.x + Math.cos(ang) * 24, merc.y + Math.sin(ang) * 24);
                            ctx.lineTo(merc.x + Math.cos(ang) * 40, merc.y + Math.sin(ang) * 40);
                            ctx.stroke();
                        }}
                    }}

                    if (luna) {{
                        ctx.strokeStyle = '#38bdf8';
                        ctx.lineWidth = 2.4;
                        ctx.shadowColor = 'rgba(56, 189, 248, 0.95)';
                        ctx.shadowBlur = 16;
                        ctx.beginPath();
                        ctx.arc(luna.x, luna.y, 28, 0, Math.PI * 2);
                        ctx.stroke();

                        for (let i = 0; i < 4; i++) {{
                            const ang = (i * Math.PI / 2) + Math.PI / 4;
                            ctx.beginPath();
                            ctx.moveTo(luna.x + Math.cos(ang) * 22, luna.y + Math.sin(ang) * 22);
                            ctx.lineTo(luna.x + Math.cos(ang) * 36, luna.y + Math.sin(ang) * 36);
                            ctx.stroke();
                        }}
                    }}

                    // ── 3. TARJETAS TÁCTICAS PERIFÉRICAS (y=1280 a 1510) ────
                    const cardY = 1280;
                    const cardH = 230;

                    // TARJETA 1: LUNA EN VIRGO
                    const card1X = 50;
                    const card1W = 470;

                    if (luna) {{
                        ctx.strokeStyle = 'rgba(56, 189, 248, 0.85)';
                        ctx.lineWidth = 2.0;
                        ctx.shadowColor = '#38bdf8';
                        ctx.shadowBlur = 10;
                        ctx.beginPath();
                        ctx.moveTo(luna.x, luna.y + 32);
                        ctx.lineTo(luna.x - 15, 1220);
                        ctx.lineTo(card1X + card1W / 2, cardY - 5);
                        ctx.stroke();

                        ctx.fillStyle = '#38bdf8';
                        ctx.beginPath();
                        ctx.arc(luna.x, luna.y + 32, 4, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.beginPath();
                        ctx.moveTo(card1X + card1W / 2 - 7, cardY - 12);
                        ctx.lineTo(card1X + card1W / 2 + 7, cardY - 12);
                        ctx.lineTo(card1X + card1W / 2, cardY - 3);
                        ctx.closePath();
                        ctx.fill();
                    }}

                    ctx.fillStyle = 'rgba(10, 16, 28, 0.95)';
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.75)';
                    ctx.lineWidth = 2.0;
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 24;
                    ctx.beginPath();
                    ctx.roundRect(card1X, cardY, card1W, cardH, 14);
                    ctx.fill();
                    ctx.stroke();

                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 3.5;
                    ctx.beginPath();
                    ctx.moveTo(card1X + 22, cardY);
                    ctx.lineTo(card1X + card1W - 22, cardY);
                    ctx.stroke();

                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'top';

                    ctx.font = '700 17px "Cinzel", sans-serif';
                    ctx.fillStyle = '#38bdf8';
                    ctx.shadowBlur = 5;
                    ctx.fillText('☽ LUMINARIA GUÍA', card1X + 24, cardY + 18);

                    ctx.font = '700 26px "Cinzel", "Times New Roman", serif';
                    ctx.fillStyle = '#ffffff';
                    ctx.fillText('LUNA EN VIRGO · 17° ♍', card1X + 24, cardY + 46);

                    ctx.font = '700 19px -apple-system, sans-serif';
                    ctx.fillStyle = '#e2e8f0';
                    ctx.fillText('Sextil armónico a Mercurio y Sol.', card1X + 24, cardY + 86);

                    ctx.font = '500 18px -apple-system, sans-serif';
                    ctx.fillStyle = '#94a3b8';
                    ctx.fillText('Discernimiento clínico y método:', card1X + 24, cardY + 122);
                    ctx.fillText('ordenar el caos y los datos para', card1X + 24, cardY + 150);
                    ctx.fillText('tomar decisiones sin quemarse.', card1X + 24, cardY + 178);

                    // TARJETA 2: MERCURIO EN EL CORAZÓN DEL SOL
                    const card2X = 560;
                    const card2W = 470;

                    if (merc) {{
                        ctx.strokeStyle = 'rgba(246, 196, 69, 0.85)';
                        ctx.lineWidth = 2.0;
                        ctx.shadowColor = '#f6c445';
                        ctx.shadowBlur = 10;
                        ctx.beginPath();
                        ctx.moveTo(merc.x, merc.y + 36);
                        ctx.lineTo(merc.x + 20, 1220);
                        ctx.lineTo(card2X + card2W / 2, cardY - 5);
                        ctx.stroke();

                        ctx.fillStyle = '#f6c445';
                        ctx.beginPath();
                        ctx.arc(merc.x, merc.y + 36, 4, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.beginPath();
                        ctx.moveTo(card2X + card2W / 2 - 7, cardY - 12);
                        ctx.lineTo(card2X + card2W / 2 + 7, cardY - 12);
                        ctx.lineTo(card2X + card2W / 2, cardY - 3);
                        ctx.closePath();
                        ctx.fill();
                    }}

                    ctx.fillStyle = 'rgba(20, 15, 26, 0.95)';
                    ctx.strokeStyle = 'rgba(246, 196, 69, 0.8)';
                    ctx.lineWidth = 2.0;
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 24;
                    ctx.beginPath();
                    ctx.roundRect(card2X, cardY, card2W, cardH, 14);
                    ctx.fill();
                    ctx.stroke();

                    ctx.strokeStyle = '#f6c445';
                    ctx.lineWidth = 3.5;
                    ctx.beginPath();
                    ctx.moveTo(card2X + 22, cardY);
                    ctx.lineTo(card2X + card2W - 22, cardY);
                    ctx.stroke();

                    ctx.font = '700 17px "Cinzel", sans-serif';
                    ctx.fillStyle = '#f6c445';
                    ctx.fillText('⚡ ALINEACIÓN EXACTA (0.06°)', card2X + 24, cardY + 18);

                    ctx.font = '700 26px "Cinzel", "Times New Roman", serif';
                    ctx.fillStyle = '#ffffff';
                    ctx.fillText('MERCURIO EN EL SOL · 12° ♏', card2X + 24, cardY + 46);

                    ctx.font = '700 19px -apple-system, sans-serif';
                    ctx.fillStyle = '#fef08a';
                    ctx.fillText('Lucidez total: caen las caretas.', card2X + 24, cardY + 86);

                    ctx.font = '500 18px -apple-system, sans-serif';
                    ctx.fillStyle = '#cbd5e1';
                    ctx.fillText('El intelecto se funde en la luz.', card2X + 24, cardY + 122);
                    ctx.fillText('Lo que estaba bajo siete llaves', card2X + 24, cardY + 150);
                    ctx.fillText('sale a la superficie sin filtro.', card2X + 24, cardY + 178);

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

    # Transcodificar a MP4 H.264 de alta tasa de bits y calidad cinemática
    cmd_ffmpeg = f"ffmpeg -y -i '{out_webm}' -c:v libx264 -pix_fmt yuv420p -crf 15 -preset slow '{out_mp4}' >/dev/null 2>&1"
    os.system(cmd_ffmpeg)
    print(f"✅ Clip generado: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4

def main():
    import urllib.request
    port = 8783
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Esperar hasta que el servidor FastAPI responda
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/reloj", timeout=1) as resp:
                if resp.status == 200:
                    print("🚀 Servidor FastAPI listo.")
                    break
        except Exception:
            time.sleep(0.3)
    else:
        print("⚠️ Advertencia: tiempo de espera de servidor agotado, continuando...")

    # 1. Clip Apertura
    capturar_clip(tipo="apertura", nombre_archivo="reloj_2d_2026-11-04_apertura", port=port)

    # 2. Clip Cierre
    capturar_clip(tipo="cierre", nombre_archivo="reloj_2d_2026-11-04_cierre", port=port)

    print("✨ Clips cinematográficos del 4 de Noviembre generados con éxito!")

if __name__ == "__main__":
    main()
