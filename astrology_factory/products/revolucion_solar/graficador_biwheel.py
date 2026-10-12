import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List

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

    def generar_biwheel(self, carta_natal: Dict[str, Any], carta_rs: Dict[str, Any], output_path: str):
        fig, ax = plt.subplots(figsize=(13, 13), subplot_kw={'projection': 'polar'})
        
        # Fondo Espacial Profundo
        bg_color = "#080b12"
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.axis('off')

        # Semilla fija para estrellas de fondo
        np.random.seed(42)
        n_stars = 180
        star_r = np.random.uniform(0.08, 0.98, n_stars)
        star_theta = np.random.uniform(0, 2 * np.pi, n_stars)
        star_alpha = np.random.uniform(0.15, 0.6, n_stars)
        star_sizes = np.random.uniform(2, 10, n_stars)
        ax.scatter(star_theta, star_r, c='#ffffff', alpha=star_alpha, s=star_sizes, zorder=1)

        # Grado del Ascendente Natal: Fijo a 180° (Horizonte Izquierdo)
        asc_natal_deg = carta_natal["angulos"]["Ascendente"]["grado_absoluto"]
        
        def to_wheel_rad(deg: float) -> float:
            """Convierte grado zodiacal (0-360) a radianes rotados con Asc Natal en 180°."""
            wheel_deg = (deg - asc_natal_deg + 180.0) % 360.0
            return np.radians(wheel_deg)

        # 1. Anillo Exterior: Signos del Zodiaco (0.86 a 1.0)
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
                
            ax.fill_between(rads, 0.86, 1.0, color=color, alpha=0.35, edgecolor='#d4af37', linewidth=1.2, zorder=2)
            
            mid_deg = deg_start + 15.0
            mid_rad = to_wheel_rad(mid_deg)
            ax.text(mid_rad, 0.93, f"{glyph}\n{sign_name}", ha='center', va='center', 
                    color='#ffffff', fontsize=9.5, fontweight='bold', zorder=3)

        # Círculos concéntricos de demarcación
        theta_full = np.linspace(0, 2 * np.pi, 250)
        ax.plot(theta_full, [1.0] * 250, color='#d4af37', linewidth=1.5, zorder=4)
        ax.plot(theta_full, [0.86] * 250, color='#d4af37', linewidth=1.2, zorder=4)
        ax.plot(theta_full, [0.72] * 250, color='#00d2ff', linewidth=1.0, linestyle='--', alpha=0.7, zorder=4) # Límite RS vs Natal
        ax.plot(theta_full, [0.56] * 250, color='#d4af37', linewidth=1.0, zorder=4) # Demarcación planetas natales
        ax.plot(theta_full, [0.42] * 250, color='#4a5568', linewidth=0.8, linestyle=':', zorder=4) # Límite casas natales
        ax.plot(theta_full, [0.30] * 250, color='#2d3748', linewidth=0.8, zorder=4) # Centro de aspectos

        # 2. Casas Natales (Cúspides y números 1 a 12)
        cuspides_natal = carta_natal["cuspides_grados"]
        for h in range(12):
            c_deg = cuspides_natal[h]
            c_next = cuspides_natal[(h + 1) % 12]
            rad_cusp = to_wheel_rad(c_deg)
            
            # Líneas de cúspides natales (desde r=0.30 hasta r=0.86)
            is_ang = (h in [0, 3, 6, 9])
            lw = 1.6 if is_ang else 0.7
            ls = '-' if is_ang else '--'
            c_line = '#f39c12' if is_ang else '#4a5568'
            ax.plot([rad_cusp, rad_cusp], [0.30, 0.86], color=c_line, linewidth=lw, linestyle=ls, zorder=5)

            # Número de Casa Natal centrado en su sector (r=0.36)
            diff_h = (c_next - c_deg) % 360.0
            mid_c_deg = (c_deg + diff_h / 2.0) % 360.0
            mid_rad = to_wheel_rad(mid_c_deg)
            ax.text(mid_rad, 0.36, str(h + 1), ha='center', va='center', 
                    color='#cbd5e0', fontsize=8.5, fontweight='bold', zorder=6)

        # 3. Planetas de la Carta Natal (Anillo Interior: r = 0.48)
        natal_planets = carta_natal["planetas"]
        # Agrupar para evitar solapamientos leves
        sorted_natal = sorted(natal_planets.items(), key=lambda x: x[1]["grado_absoluto"])
        for p_name, p_info in sorted_natal:
            deg = p_info["grado_absoluto"]
            rad = to_wheel_rad(deg)
            glyph = self.PLANET_GLYPHS.get(p_name, p_name[:2])
            
            # Punto de posición exacta natal
            ax.scatter([rad], [0.56], color='#f1c40f', s=16, zorder=7)
            # Glifo y grado
            ax.text(rad, 0.49, f"{glyph}\n{p_info['grado_en_signo']}°", ha='center', va='center',
                    color='#ffffff', fontsize=8, fontweight='bold', zorder=8)

        # 4. Planetas de la Revolución Solar (Anillo Exterior: r = 0.79)
        rs_planets = carta_rs["planetas_rs"]
        sorted_rs = sorted(rs_planets.items(), key=lambda x: x[1]["grado_absoluto"])
        for p_name, p_info in sorted_rs:
            deg = p_info["grado_absoluto"]
            rad = to_wheel_rad(deg)
            glyph = self.PLANET_GLYPHS.get(p_name, p_name[:2])
            
            # Punto de posición de RS (destacado en Cian / Azul Eléctrico)
            ax.scatter([rad], [0.72], color='#00f2fe', s=20, zorder=7)
            # Glifo y grado anual
            ax.text(rad, 0.79, f"{glyph}\n{p_info['grado_en_signo']}°", ha='center', va='center',
                    color='#00f2fe', fontsize=8.5, fontweight='bold', zorder=8)

        # 5. Marcador Especial: Ascendente de la Revolución Solar (¿Dónde cae en el natal?)
        asc_rs_deg = carta_rs["angulos_rs"]["Ascendente_RS"]["grado_absoluto"]
        asc_rs_rad = to_wheel_rad(asc_rs_deg)
        # Flecha o línea marcadora destacada
        ax.plot([asc_rs_rad, asc_rs_rad], [0.30, 0.86], color='#00f2fe', linewidth=2.2, linestyle='-', zorder=9)
        ax.text(asc_rs_rad, 0.83, "AC_RS", ha='center', va='center',
                color='#00f2fe', fontsize=7.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#080b12', edgecolor='#00f2fe', alpha=0.8), zorder=10)

        # 6. Aspectos de Activación Anual (Cuerdas en el núcleo r <= 0.30)
        # Dibujamos los 8 aspectos más exactos entre planetas de RS y planetas Natales
        aspectos_act = carta_rs["aspectos_intercartas"][:8]
        for asp in aspectos_act:
            p_rs_name = asp["cuerpo_rs"]
            p_nat_name = asp["cuerpo_natal"]
            
            if p_rs_name in rs_planets and p_nat_name in natal_planets:
                deg_rs = rs_planets[p_rs_name]["grado_absoluto"]
                deg_nat = natal_planets[p_nat_name]["grado_absoluto"]
                
                rad_rs = to_wheel_rad(deg_rs)
                rad_nat = to_wheel_rad(deg_nat)
                
                # Curva interior uniendo ambos puntos
                c_points = 25
                curve_r = np.linspace(0.30, 0.30, c_points)
                # Crear arco que pasa cerca del centro
                t_interp = np.linspace(0, 1, c_points)
                curve_rads = rad_rs + t_interp * (rad_nat - rad_rs)
                # Modulación de radio para arquear hacia el centro
                curve_r = 0.30 * (1 - 0.75 * np.sin(np.pi * t_interp))
                
                ax.plot(curve_rads, curve_r, color=asp["color"], alpha=0.65, linewidth=1.2, zorder=4)

        # Título y Leyenda Integrada
        sujeto = carta_natal["sujeto"]["nombre"]
        anio_rs = carta_rs["revolucion_solar"]["anio"]
        ciudad_rs = carta_rs["revolucion_solar"]["ciudad_retorno"]
        fecha_rs = carta_rs["revolucion_solar"]["fecha_hora_exacta_local"]
        
        fig.text(0.5, 0.04, 
                 f"REVOLUCIÓN SOLAR {anio_rs} · {sujeto.upper()}\n"
                 f"Retorno Solar: {fecha_rs} hs ({ciudad_rs}) | AC RS en {carta_rs['angulos_rs']['Ascendente_RS']['formato']} (Casa {carta_rs['superposicion_clave']['ascendente_rs_en_casa_natal']['casa_natal']} Natal)\n"
                 f"Anillo Interior (Amarillo): Carta Natal · Anillo Exterior (Cian): Revolución Solar · Centro: Aspectos de Activación",
                 ha='center', va='center', color='#e2e8f0', fontsize=9.5, linespacing=1.4)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200, facecolor=bg_color, edgecolor='none')
        plt.close(fig)
        return output_path
