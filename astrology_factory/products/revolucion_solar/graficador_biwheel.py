import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple

class GraficadorBiWheelAstrologica:
    """
    Graficador de Rueda Doble (Bi-Wheel) Espacial Profesional.
    Superpone la Carta Natal (anillo interior) con la Revolución Solar (anillo exterior).
    - Ascendente Natal fijo en el horizonte izquierdo (180° / 9 en punto).
    - Cúspides y planetas natales en el círculo interior.
    - Planetas de la Revolución Solar en el anillo exterior.
    - Cuerdas de aspectos de activación anual en el centro con código de color.
    - Fondo de Espacio Profundo con estética de alta gama.
    """
    def __init__(self):
        self.ZODIAC_SIGNS = [
            "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
        ]
        
        self.ZODIAC_GLYPHS = [
            "♈", "♉", "♊", "♋", "♌", "♍",
            "♎", "♏", "♐", "♑", "♒", "♓"
        ]
        
        # Colores por elemento
        self.ELEMENT_COLORS = {
            "Aries": "#c0392b", "Leo": "#d35400", "Sagitario": "#b03a2e",      # Fuego
            "Tauro": "#27ae60", "Virgo": "#229954", "Capricornio": "#1e8449",  # Tierra
            "Géminis": "#f39c12", "Libra": "#d4ac0d", "Acuario": "#b7950b",    # Aire
            "Cáncer": "#2980b9", "Escorpio": "#2471a3", "Piscis": "#1f618d"    # Agua
        }

        self.PLANET_GLYPHS = {
            'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂',
            'Júpiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Plutón': '♇',
            'Quirón': '⚷', 'Nodo Norte': '☊', 'Lilith': '⚸'
        }

    def to_canvas_xy(self, rad: float, r: float) -> Dict[str, int]:
        """Convierte coordenadas polares (rad, r) a coordenadas pixel (X, Y) en canvas 1920x1080."""
        cx, cy = 960, 540
        r_px = r * 485.0
        x = int(round(cx + r_px * np.cos(rad)))
        y = int(round(cy - r_px * np.sin(rad)))
        x = max(180, min(1740, x))
        y = max(120, min(960, y))
        return {"x": x, "y": y}

    def generar_biwheel(
        self,
        carta_natal: Dict[str, Any],
        carta_rs: Dict[str, Any],
        output_path: str,
        foco: Optional[Dict[str, Any]] = None
    ) -> str:
        """Genera la rueda Bi-Wheel estándar o enfocada, retornando la ruta del archivo generado."""
        out, _ = self.generar_biwheel_con_foco(carta_natal, carta_rs, output_path, foco=foco)
        return out

    def generar_biwheel_con_foco(
        self,
        carta_natal: Dict[str, Any],
        carta_rs: Dict[str, Any],
        output_path: str,
        foco: Optional[Dict[str, Any]] = None,
        solo_base: bool = False
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Grafica la rueda Bi-Wheel con soporte de Enfoque Pedagógico Dinámico (Regla 8 y 11).
        Retorna (output_path, coords_foco) donde coords_foco = {'x': int, 'y': int} en el canvas 1920x1080.
        Si solo_base=True, grafica la rueda limpia con todo el detalle cósmico pero sin la retícula de foco,
        manteniendo idénticos los títulos y badges superiores para una transición de zoom perfecta.
        """
        fig, ax = plt.subplots(figsize=(13, 13), subplot_kw={'projection': 'polar'})
        
        # Fondo Espacial Profundo
        bg_color = "#080b12"
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.axis('off')

        # Configuración de Foco
        foco_activo = (foco is not None and foco.get("tipo", "general") != "general") and not solo_base
        foco_tipo = foco.get("tipo", "general") if (foco and not solo_base) else "general"
        foco_nombre = foco.get("nombre", "").strip() if (foco and not solo_base) else ""
        foco_casa = foco.get("casa", None) if (foco and not solo_base) else None
        coords_foco = {"x": 960, "y": 540} # Por defecto al centro

        # Semilla fija para estrellas de fondo
        np.random.seed(42)
        n_stars = 180
        star_r = np.random.uniform(0.08, 0.98, n_stars)
        star_theta = np.random.uniform(0, 2 * np.pi, n_stars)
        star_alpha = np.random.uniform(0.10 if foco_activo else 0.15, 0.4 if foco_activo else 0.6, n_stars)
        star_sizes = np.random.uniform(2, 10, n_stars)
        ax.scatter(star_theta, star_r, c='#ffffff', alpha=star_alpha, s=star_sizes, zorder=1)

        # Grado del Ascendente Natal: Fijo a 180° (Horizonte Izquierdo)
        asc_natal_deg = carta_natal["angulos"]["Ascendente"]["grado_absoluto"]
        
        def to_wheel_rad(deg: float) -> float:
            """Convierte grado zodiacal (0-360) a radianes rotados con Asc Natal en 180°."""
            wheel_deg = (deg - asc_natal_deg + 180.0) % 360.0
            return np.radians(wheel_deg)

        # 1. Anillo Exterior: Signos del Zodiaco (0.86 a 1.0)
        alpha_signos = 0.38
        for i in range(12):
            sign_name = self.ZODIAC_SIGNS[i]
            glyph = self.ZODIAC_GLYPHS[i]
            color = self.ELEMENT_COLORS[sign_name]
            
            deg_start = i * 30.0
            deg_end = (i + 1) * 30.0
            degs = np.linspace(deg_start, deg_end, 30)
            rads = np.array([to_wheel_rad(d) for d in degs])
            if rads[-1] < rads[0]:
                rads = np.unwrap(rads)
                
            ax.fill_between(rads, 0.86, 1.0, color=color, alpha=alpha_signos, edgecolor='#d4af37', linewidth=1.2, zorder=2)
            
            mid_deg = deg_start + 15.0
            mid_rad = to_wheel_rad(mid_deg)
            ax.text(mid_rad, 0.93, f"{glyph}\n{sign_name}", ha='center', va='center', 
                    color='#ffffff', fontsize=9.2, fontweight='bold', zorder=3)

        # Círculos concéntricos de demarcación
        theta_full = np.linspace(0, 2 * np.pi, 250)
        ax.plot(theta_full, [1.0] * 250, color='#d4af37', linewidth=1.2, alpha=0.9, zorder=4)
        ax.plot(theta_full, [0.86] * 250, color='#d4af37', linewidth=1.0, alpha=0.9, zorder=4)
        ax.plot(theta_full, [0.72] * 250, color='#00d2ff', linewidth=0.8, linestyle='--', alpha=0.75, zorder=4)
        ax.plot(theta_full, [0.56] * 250, color='#d4af37', linewidth=0.8, alpha=0.85, zorder=4)
        ax.plot(theta_full, [0.42] * 250, color='#4a5568', linewidth=0.6, linestyle=':', alpha=0.8, zorder=4)
        ax.plot(theta_full, [0.30] * 250, color='#2d3748', linewidth=0.6, alpha=0.8, zorder=4)

        # 2. Casas Natales (Cúspides y números 1 a 12)
        cuspides_natal = carta_natal["cuspides_grados"]
        casa_natal_portal = carta_rs['superposicion_clave']['ascendente_rs_en_casa_natal']['casa_natal']

        for h in range(12):
            c_deg = cuspides_natal[h]
            c_next = cuspides_natal[(h + 1) % 12]
            rad_cusp = to_wheel_rad(c_deg)
            
            diff_h = (c_next - c_deg) % 360.0
            mid_c_deg = (c_deg + diff_h / 2.0) % 360.0
            mid_rad = to_wheel_rad(mid_c_deg)

            es_casa_enfocada = (foco_tipo == "casa" and foco_casa == (h + 1))
            es_casa_portal = (foco_tipo == "portal" and (h + 1) == casa_natal_portal)

            # Relleno del sector enfocado (iluminación dinámica de casa con borde luminoso)
            if es_casa_enfocada or es_casa_portal:
                degs_sec = np.linspace(c_deg, c_deg + diff_h, 30)
                rads_sec = np.array([to_wheel_rad(d) for d in degs_sec])
                if rads_sec[-1] < rads_sec[0]:
                    rads_sec = np.unwrap(rads_sec)
                glow_color = '#00f2fe' if es_casa_portal else '#ffd700'
                ax.fill_between(rads_sec, 0.30, 0.86, color=glow_color, alpha=0.28, zorder=3)
                coords_foco = self.to_canvas_xy(mid_rad, 0.45)

            # Líneas de cúspides natales
            is_ang = (h in [0, 3, 6, 9])
            if es_casa_enfocada or es_casa_portal:
                c_line = '#00f2fe' if es_casa_portal else '#ffd700'
                ax.plot([rad_cusp, rad_cusp], [0.30, 0.86], color=c_line, linewidth=3.2, zorder=6)
                ax.plot([rad_cusp, rad_cusp], [0.30, 0.86], color=c_line, linewidth=10.0, alpha=0.35, zorder=5)
            else:
                lw = 1.4 if is_ang else 0.7
                ls = '-' if is_ang else '--'
                c_line = '#f39c12' if is_ang else '#4a5568'
                ax.plot([rad_cusp, rad_cusp], [0.30, 0.86], color=c_line, linewidth=lw, linestyle=ls, zorder=5)

            # Número de Casa Natal
            if es_casa_enfocada or es_casa_portal:
                color_num = '#00f2fe' if es_casa_portal else '#ffd700'
                ax.text(mid_rad, 0.36, str(h + 1), ha='center', va='center', 
                        color=color_num, fontsize=12, fontweight='bold', zorder=7,
                        bbox=dict(boxstyle='circle,pad=0.25', facecolor='#080b12', edgecolor=color_num, linewidth=1.6, alpha=0.95))
            else:
                ax.text(mid_rad, 0.36, str(h + 1), ha='center', va='center', 
                        color='#cbd5e0', fontsize=8.5, fontweight='bold', zorder=6)

        # 3. Planetas de la Carta Natal (Anillo Interior: r = 0.48 / 0.56)
        natal_planets = carta_natal["planetas"]
        sorted_natal = sorted(natal_planets.items(), key=lambda x: x[1]["grado_absoluto"])
        for p_name, p_info in sorted_natal:
            deg = p_info["grado_absoluto"]
            rad = to_wheel_rad(deg)
            glyph = self.PLANET_GLYPHS.get(p_name, p_name[:2])
            
            es_planeta_foco = (foco_tipo == "planeta" and foco_nombre.lower() == p_name.lower() and foco.get("es_natal", False))
            
            if es_planeta_foco:
                coords_foco = self.to_canvas_xy(rad, 0.56)
                # Halos concéntricos neón oro
                for s_glow, a_glow in [(450, 0.12), (280, 0.25), (150, 0.45), (60, 0.80)]:
                    ax.scatter([rad], [0.56], color='#ffd700', s=s_glow, alpha=a_glow, zorder=8)
                ax.scatter([rad], [0.56], facecolors='none', edgecolors='#ffd700', s=550, linewidth=2.2, linestyle='--', zorder=9)
                # Mira cruzada (crosshair ticks)
                dt = 0.04
                dr = 0.05
                ax.plot([rad - dt, rad + dt], [0.56, 0.56], color='#ffd700', linewidth=1.5, zorder=9)
                ax.plot([rad, rad], [0.56 - dr, 0.56 + dr], color='#ffd700', linewidth=1.5, zorder=9)
                ax.text(rad, 0.48, f"{glyph}\n{p_info['grado_en_signo']}°", ha='center', va='center',
                        color='#ffd700', fontsize=12, fontweight='bold', zorder=10,
                        bbox=dict(boxstyle='circle,pad=0.32', facecolor='#080b12', edgecolor='#ffd700', linewidth=1.8, alpha=0.98))
                # HUD callout
                ax.text(rad, 0.38, f"✦ {p_name.upper()} {p_info['grado_en_signo']}° ✦", ha='center', va='center',
                        color='#ffd700', fontsize=9.0, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='#080b12', edgecolor='#ffd700', linewidth=1.2, alpha=0.9), zorder=11)
            else:
                # Planeta natal estándar: orbe radiante con halo y glifo nítido
                ax.scatter([rad], [0.56], color='#ffd700', s=70, alpha=0.25, zorder=6)
                ax.scatter([rad], [0.56], color='#f1c40f', s=24, zorder=7)
                ax.text(rad, 0.49, f"{glyph}\n{p_info['grado_en_signo']}°", ha='center', va='center',
                        color='#ffffff', fontsize=8.2, fontweight='bold', zorder=8,
                        bbox=dict(boxstyle='circle,pad=0.18', facecolor='#080b12', edgecolor='#d4af37', linewidth=0.7, alpha=0.85))

        # 4. Planetas de la Revolución Solar (Anillo Exterior: r = 0.72 / 0.79)
        rs_planets = carta_rs["planetas_rs"]
        sorted_rs = sorted(rs_planets.items(), key=lambda x: x[1]["grado_absoluto"])
        for p_name, p_info in sorted_rs:
            deg = p_info["grado_absoluto"]
            rad = to_wheel_rad(deg)
            glyph = self.PLANET_GLYPHS.get(p_name, p_name[:2])
            
            es_planeta_foco = (foco_tipo == "planeta" and foco_nombre.lower() == p_name.lower() and not foco.get("es_natal", False))
            
            if es_planeta_foco:
                coords_foco = self.to_canvas_xy(rad, 0.72)
                # Halos concéntricos neón cian
                for s_glow, a_glow in [(500, 0.12), (300, 0.28), (160, 0.50), (70, 0.85)]:
                    ax.scatter([rad], [0.72], color='#00f2fe', s=s_glow, alpha=a_glow, zorder=8)
                ax.scatter([rad], [0.72], facecolors='none', edgecolors='#00f2fe', s=600, linewidth=2.4, linestyle='--', zorder=9)
                # Mira cruzada (crosshair ticks)
                dt = 0.04
                dr = 0.05
                ax.plot([rad - dt, rad + dt], [0.72, 0.72], color='#00f2fe', linewidth=1.6, zorder=9)
                ax.plot([rad, rad], [0.72 - dr, 0.72 + dr], color='#00f2fe', linewidth=1.6, zorder=9)
                ax.text(rad, 0.79, f"{glyph}\n{p_info['grado_en_signo']}°", ha='center', va='center',
                        color='#00f2fe', fontsize=12.5, fontweight='bold', zorder=10,
                        bbox=dict(boxstyle='circle,pad=0.35', facecolor='#080b12', edgecolor='#00f2fe', linewidth=2.0, alpha=0.98))
                # HUD callout
                ax.text(rad, 0.65, f"✦ {p_name.upper()} {p_info['grado_en_signo']}° ✦", ha='center', va='center',
                        color='#00f2fe', fontsize=9.2, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='#080b12', edgecolor='#00f2fe', linewidth=1.2, alpha=0.9), zorder=11)
            else:
                # Planeta RS estándar: orbe radiante con halo cian y glifo nítido
                ax.scatter([rad], [0.72], color='#00f2fe', s=75, alpha=0.28, zorder=6)
                ax.scatter([rad], [0.72], color='#00f2fe', s=26, zorder=7)
                ax.text(rad, 0.79, f"{glyph}\n{p_info['grado_en_signo']}°", ha='center', va='center',
                        color='#00f2fe', fontsize=8.8, fontweight='bold', zorder=8,
                        bbox=dict(boxstyle='circle,pad=0.18', facecolor='#080b12', edgecolor='#00f2fe', linewidth=0.7, alpha=0.85))

        # 5. Marcador Especial: Ascendente de la Revolución Solar
        asc_rs_deg = carta_rs["angulos_rs"]["Ascendente_RS"]["grado_absoluto"]
        asc_rs_rad = to_wheel_rad(asc_rs_deg)
        es_portal_foco = (foco_tipo == "portal" or foco_nombre.upper() in ["AC_RS", "ASCENDENTE_RS", "PORTAL", "ASCENDENTE"])

        if es_portal_foco:
            coords_foco = self.to_canvas_xy(asc_rs_rad, 0.80)
            ax.plot([asc_rs_rad, asc_rs_rad], [0.30, 0.88], color='#00ffff', linewidth=4.0, zorder=10)
            ax.plot([asc_rs_rad, asc_rs_rad], [0.30, 0.88], color='#00ffff', linewidth=16, alpha=0.35, zorder=9)
            ax.text(asc_rs_rad, 0.85, "✦ PORTAL AC_RS ✦", ha='center', va='center',
                    color='#00ffff', fontsize=10.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.35', facecolor='#080b12', edgecolor='#00ffff', linewidth=2.2), zorder=11)
        else:
            ax.plot([asc_rs_rad, asc_rs_rad], [0.30, 0.86], color='#00f2fe', linewidth=2.0, linestyle='-', zorder=9)
            ax.text(asc_rs_rad, 0.83, "AC_RS", ha='center', va='center',
                    color='#00f2fe', fontsize=7.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#080b12', edgecolor='#00f2fe', alpha=0.85), zorder=10)

        # 6. Aspectos de Activación Anual (Cuerdas en el núcleo r <= 0.30)
        aspectos_act = carta_rs["aspectos_intercartas"][:10]
        for asp in aspectos_act:
            p_rs_name = asp["cuerpo_rs"]
            p_nat_name = asp["cuerpo_natal"]
            
            if p_rs_name in rs_planets and p_nat_name in natal_planets:
                deg_rs = rs_planets[p_rs_name]["grado_absoluto"]
                deg_nat = natal_planets[p_nat_name]["grado_absoluto"]
                
                rad_rs = to_wheel_rad(deg_rs)
                rad_nat = to_wheel_rad(deg_nat)
                
                c_points = 30
                t_interp = np.linspace(0, 1, c_points)
                curve_rads = rad_rs + t_interp * (rad_nat - rad_rs)
                curve_r = 0.30 * (1 - 0.75 * np.sin(np.pi * t_interp))
                
                es_aspecto_foco = (
                    foco_tipo == "aspecto" and (
                        foco_nombre.lower() in [p_rs_name.lower(), p_nat_name.lower(), asp.get("aspecto", "").lower()]
                    )
                )

                if es_aspecto_foco:
                    mid_rad = (rad_rs + rad_nat) / 2.0
                    coords_foco = self.to_canvas_xy(mid_rad, 0.20)
                    ax.plot(curve_rads, curve_r, color=asp["color"], alpha=0.40, linewidth=16, zorder=5)
                    ax.plot(curve_rads, curve_r, color=asp["color"], alpha=1.0, linewidth=4.0, zorder=6)
                    # Halos en los dos planetas conectados
                    ax.scatter([rad_rs], [0.72], color=asp["color"], s=280, alpha=0.4, zorder=8)
                    ax.scatter([rad_nat], [0.56], color=asp["color"], s=280, alpha=0.4, zorder=8)
                    # Badge central del aspecto
                    nom_asp = asp.get("aspecto", "").upper()
                    ax.text(mid_rad, 0.18, f"✦ {nom_asp} ✦", ha='center', va='center',
                            color='#ffffff', fontsize=8.5, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.25', facecolor='#080b12', edgecolor=asp["color"], linewidth=1.5, alpha=0.95), zorder=7)
                else:
                    # Todos los demás aspectos con aura sutil para mayor profundidad espacial
                    ax.plot(curve_rads, curve_r, color=asp["color"], alpha=0.18, linewidth=3.5, zorder=3)
                    ax.plot(curve_rads, curve_r, color=asp["color"], alpha=0.60, linewidth=1.4, zorder=4)

        # 7. Título y Leyenda Integrada Pedagógica
        sujeto = carta_natal["sujeto"]["nombre"]
        anio_rs = carta_rs["revolucion_solar"]["anio"]
        ciudad_rs = carta_rs["revolucion_solar"]["ciudad_retorno"]
        fecha_rs = carta_rs["revolucion_solar"]["fecha_hora_exacta_local"]
        asc_rs_fmt = carta_rs['angulos_rs']['Ascendente_RS']['formato']
        
        if foco and foco.get("titulo"):
            tit_foco = foco["titulo"]
            sub_foco = foco.get("subtitulo", "")
            fig.text(0.5, 0.965, f"✦ {tit_foco.upper()} ✦",
                     ha='center', va='center', color='#00f2fe' if 'RS' in tit_foco else '#ffd700',
                     fontsize=13, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.4', facecolor='#0b111e', edgecolor='#00f2fe', linewidth=1.2, alpha=0.92))
            if sub_foco:
                fig.text(0.5, 0.935, sub_foco,
                         ha='center', va='center', color='#e2e8f0', fontsize=9.5, fontweight='medium')
        else:
            fig.text(0.5, 0.96, f"REVOLUCIÓN SOLAR {anio_rs} · {sujeto.upper()}",
                     ha='center', va='center', color='#d4af37', fontsize=13, fontweight='bold')
            fig.text(0.5, 0.935, f"Retorno Solar Exacto: {fecha_rs} hs ({ciudad_rs}) · Ascendente RS: {asc_rs_fmt}",
                     ha='center', va='center', color='#00f2fe', fontsize=10, fontweight='medium')

        # Caja de Leyenda Pedagógica Inferior
        leyenda_biwheel = (
            "GUÍA RÁPIDA DE LA RUEDA DOBLE (CÓMO LEER EL MAPA DEL AÑO)\n"
            "• ANILLO INTERIOR (Dorado): Tu Carta Natal de nacimiento = Tu ADN psicológico permanente.\n"
            "• ANILLO EXTERIOR (Cian Eléctrico): La Revolución Solar = El cielo y los tránsitos durante estos 12 meses.\n"
            f"• MARCADOR 'AC_RS' (Cian): El Portal del Año = Cae en tu Casa Natal {casa_natal_portal} (el gran escenario protagonista del ciclo).\n"
            "• LÍNEAS CENTRALES: Cables de activación anual ( Rojo: Fricción que madura ·  Azul: Oportunidad y fluidez ·  Dorado: Conjunción directa)."
        )
        fig.text(0.5, 0.04, leyenda_biwheel, ha='center', va='center',
                 color='#e2e8f0', fontsize=8.8, fontweight='medium', linespacing=1.5,
                 bbox=dict(boxstyle='round,pad=0.6', facecolor='#101626', edgecolor='#00f2fe', linewidth=1.0, alpha=0.9))

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200, facecolor=bg_color, edgecolor='none')
        plt.close(fig)
        return output_path, coords_foco

