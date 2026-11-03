"""
test_hud_cinematico_4nov.py — Versión con Zona Segura de Subtítulos y Plataforma
─────────────────────────────────────────────────────────────────────────────
ARQUITECTURA VERTICAL 1080x1920 (ZERO COLLISION):
- [y: 0000 - 0240] Header Cinemático (Fecha + Aspecto Clave).
- [y: 0260 - 1260] Mandála Sagrado (Center y=800, r=460) · Aspecto Láser 100% despejado.
- [y: 1280 - 1530] Tarjetas Tácticas Periféricas (Líneas guía neón desde los astros).
- [y: 1580 - 1790] ZONA PROTEGIDA DE SUBTÍTULOS (Cero superposición, legibilidad máxima).
- [y: 1800 - 1920] Margen de Seguridad de Interfaz TikTok/Shorts (Like, título, audio).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import time
import threading
import uvicorn
from pathlib import Path
from playwright.sync_api import sync_playwright

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
WEB_APP_DIR = FACTORY_ROOT / "web_app"
ARTIFACT_DIR = Path("/home/tomas2/.gemini/antigravity-ide/brain/4227c4cd-6469-4951-8124-cec7ed3517b4")
OUTPUT_PNG = ARTIFACT_DIR / "muestra_reloj_hud_4nov.png"

def run_server(port=8791):
    sys.path.insert(0, str(WEB_APP_DIR))
    from main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def generar_muestra_hd():
    port = 8791
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(2.0)

    print("🚀 Levantando Playwright con Retina Scale (2.0x) para máxima nitidez...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 1080, "height": 1920},
            device_scale_factor=2.0
        )
        page.goto(f"http://127.0.0.1:{port}/reloj", wait_until="networkidle")

        setup_script = """
        () => {
            document.querySelectorAll('.corner-hud, #reloj-tooltip').forEach(el => el.style.display = 'none');

            if (window.relojEngine) {
                const eng = window.relojEngine;
                eng.cambiarFondo('negro');
                eng.timeState.isLive = false;
                
                // Fecha: 4 de Noviembre 2026, 12:00 hs
                eng.timeState.currentDate = new Date('2026-11-04T12:00:00');
                eng.calculateAll();

                // ── CENTRADO VERTICAL OPTIMIZADO PARA SUBTÍTULOS ──────────────
                // Elevamos el centro del reloj a y = 790 (panY = -170, zoom = 0.98)
                // El mandala ocupa de y = 320 a y = 1260.
                eng.camera.zoom = 0.98;
                eng.camera.panX = 0;
                eng.camera.panY = -170;

                // 1. Modificar renderAspectLines para que los aspectos secundarios
                // sean un sutil velo geométrico (alpha 0.08) y no formen un cuadro tosco
                eng.renderAspectLines = function(ctx) {
                    const r = eng.radii.aspects;
                    ctx.save();

                    for (const asp of eng.calculated.aspects) {
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

                        if (esProtagonista) {
                            ctx.save();
                            if (asp.tipo === 'Conjunción') {
                                ctx.strokeStyle = '#f6c445';
                                ctx.shadowColor = '#fde047';
                                ctx.shadowBlur = 18;
                                ctx.lineWidth = 3.5;
                            } else {
                                ctx.strokeStyle = '#38bdf8';
                                ctx.shadowColor = '#00f2fe';
                                ctx.shadowBlur = 18;
                                ctx.lineWidth = 3.0;
                            }
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
                        } else {
                            ctx.strokeStyle = asp.color;
                            ctx.globalAlpha = 0.08;
                            ctx.lineWidth = 1.0;
                            ctx.shadowBlur = 0;
                            ctx.beginPath();
                            ctx.moveTo(x1, y1);
                            ctx.lineTo(x2, y2);
                            ctx.stroke();
                        }
                    }
                    ctx.restore();
                };

                const origRender = eng.render.bind(eng);
                eng.render = function() {
                    const ctx = eng.ctx;
                    const w = eng.width;   // 1080 CSS
                    const h = eng.height;  // 1920 CSS
                    const cx = w / 2;
                    const cy = h / 2;
                    const baseScale = Math.min(w, h) / 1080;
                    const currentScale = baseScale * eng.camera.zoom;
                    const dpr = window.devicePixelRatio || 1;

                    // Renderizar mandala base
                    origRender();

                    const clockScreenX = cx + eng.camera.panX;
                    const clockScreenY = cy + eng.camera.panY;

                    function getPlanetScreenCoords(planetName) {
                        if (!eng.calculated || !eng.calculated.planets || !eng.calculated.planets[planetName]) return null;
                        const p = eng.calculated.planets[planetName];
                        const a = eng.coordToAngle(p.grado_absoluto);
                        const r = eng.radii.planets || 275;
                        const px = Math.cos(a) * r;
                        const py = Math.sin(a) * r;
                        return {
                            x: clockScreenX + px * currentScale,
                            y: clockScreenY + py * currentScale,
                            a: a,
                            r: r,
                            degStr: `${(p.grado_absoluto % 30).toFixed(1)}°`,
                            signo: p.signo,
                            color: p.color
                        };
                    }

                    const merc = getPlanetScreenCoords('Mercurio');
                    const luna = getPlanetScreenCoords('Luna');

                    ctx.save();
                    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

                    // ─────────────────────────────────────────────────────────
                    // 1. HEADER SUPERIOR TROPICAL CINEMÁTICO
                    // ─────────────────────────────────────────────────────────
                    const gradTop = ctx.createLinearGradient(0, 0, 0, 230);
                    gradTop.addColorStop(0, 'rgba(5, 7, 12, 0.98)');
                    gradTop.addColorStop(0.7, 'rgba(5, 7, 12, 0.85)');
                    gradTop.addColorStop(1, 'rgba(5, 7, 12, 0)');
                    ctx.fillStyle = gradTop;
                    ctx.fillRect(0, 0, w, 230);

                    ctx.font = '700 42px "Cinzel", "Times New Roman", serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillStyle = '#f6c445';
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 12;
                    ctx.fillText('4 DE NOVIEMBRE 2026', w / 2, 60);

                    ctx.strokeStyle = 'rgba(246, 196, 69, 0.5)';
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.moveTo(w / 2 - 200, 118);
                    ctx.lineTo(w / 2 + 200, 118);
                    ctx.stroke();

                    ctx.fillStyle = '#f6c445';
                    ctx.beginPath();
                    ctx.arc(w / 2, 118, 4, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.font = '600 24px "Cinzel", "Times New Roman", serif';
                    ctx.fillStyle = '#f1f5f9';
                    ctx.shadowBlur = 8;
                    ctx.fillText('MERCURIO EN EL CORAZÓN DEL SOL · 12° ♏ ESCORPIO', w / 2, 134);

                    // ─────────────────────────────────────────────────────────
                    // 2. RETÍCULAS ÓPTICAS DIRECTO SOBRE LOS ASTROS
                    // ─────────────────────────────────────────────────────────
                    if (merc) {
                        ctx.strokeStyle = '#f6c445';
                        ctx.lineWidth = 2.8;
                        ctx.shadowColor = 'rgba(246, 196, 69, 0.95)';
                        ctx.shadowBlur = 20;
                        ctx.beginPath();
                        ctx.arc(merc.x, merc.y, 34, 0, Math.PI * 2);
                        ctx.stroke();

                        for (let i = 0; i < 4; i++) {
                            const ang = (i * Math.PI / 2);
                            ctx.beginPath();
                            ctx.moveTo(merc.x + Math.cos(ang) * 26, merc.y + Math.sin(ang) * 26);
                            ctx.lineTo(merc.x + Math.cos(ang) * 44, merc.y + Math.sin(ang) * 44);
                            ctx.stroke();
                        }
                    }

                    if (luna) {
                        ctx.strokeStyle = '#38bdf8';
                        ctx.lineWidth = 2.5;
                        ctx.shadowColor = 'rgba(56, 189, 248, 0.95)';
                        ctx.shadowBlur = 18;
                        ctx.beginPath();
                        ctx.arc(luna.x, luna.y, 30, 0, Math.PI * 2);
                        ctx.stroke();

                        for (let i = 0; i < 4; i++) {
                            const ang = (i * Math.PI / 2) + Math.PI / 4;
                            ctx.beginPath();
                            ctx.moveTo(luna.x + Math.cos(ang) * 24, luna.y + Math.sin(ang) * 24);
                            ctx.lineTo(luna.x + Math.cos(ang) * 40, luna.y + Math.sin(ang) * 40);
                            ctx.stroke();
                        }
                    }

                    // ─────────────────────────────────────────────────────────
                    // 3. TARJETAS TÁCTICAS PERIFÉRICAS (y = 1275 a 1515)
                    // Situadas ENTRE el final del mandala (y=1260) y el inicio de subtítulos (y=1580)
                    // ¡100% LIBRES DE COLISIÓN!
                    // ─────────────────────────────────────────────────────────
                    const cardY = 1280;
                    const cardH = 230;

                    // --- TARJETA 1 (IZQUIERDA): LUNA EN VIRGO 17° ---
                    const card1X = 50;
                    const card1W = 470;

                    if (luna) {
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
                    }

                    // Render Tarjeta 1
                    ctx.fillStyle = 'rgba(10, 16, 28, 0.95)';
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.75)';
                    ctx.lineWidth = 2.0;
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 24;
                    ctx.beginPath();
                    ctx.roundRect(card1X, cardY, card1W, cardH, 14);
                    ctx.fill();
                    ctx.stroke();

                    // Borde superior luminoso Cyan
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


                    // --- TARJETA 2 (DERECHA): MERCURIO EN EL CORAZÓN DEL SOL ---
                    const card2X = 560;
                    const card2W = 470;

                    if (merc) {
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
                    }

                    // Render Tarjeta 2
                    ctx.fillStyle = 'rgba(20, 15, 26, 0.95)';
                    ctx.strokeStyle = 'rgba(246, 196, 69, 0.8)';
                    ctx.lineWidth = 2.0;
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
                    ctx.shadowBlur = 24;
                    ctx.beginPath();
                    ctx.roundRect(card2X, cardY, card2W, cardH, 14);
                    ctx.fill();
                    ctx.stroke();

                    // Borde superior luminoso Oro
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

                    // ─────────────────────────────────────────────────────────
                    // 4. DEMOSTRACIÓN DE ZONA SEGURA DE SUBTÍTULOS (y = 1620 a 1760)
                    // Mostramos cómo se renderiza el subtítulo real en video
                    // con espacio 100% limpio y protegido
                    // ─────────────────────────────────────────────────────────
                    
                    // Indicador sutil de marco de subtítulos
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    
                    // Frase real de Tomás
                    const subY = 1680;
                    ctx.font = '900 48px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
                    
                    // Sombra gruesa ASS estándar para legibilidad extrema
                    ctx.shadowColor = 'rgba(0, 0, 0, 1)';
                    ctx.shadowBlur = 12;
                    ctx.lineWidth = 6;
                    ctx.strokeStyle = '#000000';
                    
                    // Texto: "Para ver en qué casa te cae, fijate Escorpio"
                    const textoSub = "Para ver en qué casa te cae...";
                    ctx.strokeText(textoSub, w / 2, subY);
                    ctx.fillStyle = '#ffffff';
                    ctx.fillText(textoSub, w / 2, subY);

                    // Pequeño badge guía que confirma el margen de seguridad
                    ctx.font = '600 14px "Cinzel", monospace';
                    ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
                    ctx.shadowBlur = 0;
                    ctx.fillText('── ZONA SEGURA DE SUBTÍTULOS Y PLATAFORMA (100% DESPEJADA) ──', w / 2, 1780);

                    ctx.restore();
                };

                eng.calculateAll();
            }
        }
        """

        page.evaluate(setup_script)
        page.wait_for_timeout(800)

        print(f"📸 Guardando snapshot PNG de alta resolución en {OUTPUT_PNG}...")
        page.screenshot(path=str(OUTPUT_PNG))
        browser.close()

    print(f"✅ Imagen generada exitosamente: {OUTPUT_PNG} ({OUTPUT_PNG.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    generar_muestra_hd()
