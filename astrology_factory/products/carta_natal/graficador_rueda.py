import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List

class GraficadorRuedaAstrologica:
    def __init__(self):
        self.ZODIAC_SIGNS = [
            "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
        ]
        
        self.ZODIAC_GLYPHS = [
            "♈", "♉", "♊", "♋", "♌", "♍",
            "♎", "♏", "♐", "♑", "♒", "♓"
        ]
        
        # Colores elegantes por elemento (Armoniosos y sutiles)
        self.ELEMENT_COLORS = {
            "Aries": "#c0392b", "Leo": "#d35400", "Sagitario": "#b03a2e",      # Fuego (Rojos cálidos)
            "Tauro": "#27ae60", "Virgo": "#229954", "Capricornio": "#1e8449",  # Tierra (Verdes profundos)
            "Géminis": "#f39c12", "Libra": "#d4ac0d", "Acuario": "#b7950b",    # Aire (Dorados/Ámbar)
            "Cáncer": "#2980b9", "Escorpio": "#2471a3", "Piscis": "#1f618d"    # Agua (Azules celestes)
        }

        self.PLANET_GLYPHS = {
            'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂',
            'Júpiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Plutón': '♇',
            'Quirón': '⚷', 'Nodo Norte': '☊', 'Lilith': '⚸'
        }

    def generar_rueda(self, carta_data: Dict[str, Any], output_path: str):
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': 'polar'})
        
        # Color de fondo de la figura y del eje (Espacio Profundo)
        bg_color = "#080b12"
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.axis('off')

        # Semilla fija para estrellas de fondo sutiles
        np.random.seed(42)
        n_stars = 150
        star_r = np.random.uniform(0.1, 0.98, n_stars)
        star_theta = np.random.uniform(0, 2 * np.pi, n_stars)
        star_alpha = np.random.uniform(0.15, 0.6, n_stars)
        star_sizes = np.random.uniform(2, 12, n_stars)
        ax.scatter(star_theta, star_r, c='#ffffff', alpha=star_alpha, s=star_sizes, zorder=1)

        # Grado del Ascendente para rotar la rueda: Ascendente siempre en 180° (Horizonte Izquierdo)
        asc_deg = carta_data["angulos"]["Ascendente"]["grado_absoluto"]
        
        def to_wheel_rad(deg: float) -> float:
            """Convierte grado zodiacal (0-360) a radianes rotados con Asc en 180° (pi rad)."""
            wheel_deg = (deg - asc_deg + 180.0) % 360.0
            return np.radians(wheel_deg)

        # 1. Anillo Exterior: Signos del Zodiaco (0.85 a 1.0)
        for i in range(12):
            sign_name = self.ZODIAC_SIGNS[i]
            glyph = self.ZODIAC_GLYPHS[i]
            color = self.ELEMENT_COLORS[sign_name]
            
            # Arco de 30 grados para cada signo
            deg_start = i * 30.0
            deg_end = (i + 1) * 30.0
            
            # Generar puntos del sector
            degs = np.linspace(deg_start, deg_end, 30)
            rads = np.array([to_wheel_rad(d) for d in degs])
            
            # Ordenar radianes para fill_between correcto
            if rads[-1] < rads[0]: # Si cruza 0
                rads = np.unwrap(rads)
                
            ax.fill_between(rads, 0.85, 1.0, color=color, alpha=0.35, edgecolor='#d4af37', linewidth=1.2, zorder=2)
            
            # Etiqueta del signo (Glifo + Nombre)
            mid_deg = deg_start + 15.0
            mid_rad = to_wheel_rad(mid_deg)
            ax.text(mid_rad, 0.92, f"{glyph}\n{sign_name}", ha='center', va='center', 
                    color='#ffffff', fontsize=10, fontweight='bold', zorder=3)

        # Círculos concéntricos de demarcación
        theta_full = np.linspace(0, 2 * np.pi, 200)
        ax.plot(theta_full, [1.0] * 200, color='#d4af37', linewidth=1.5, zorder=4)
        ax.plot(theta_full, [0.85] * 200, color='#d4af37', linewidth=1.0, zorder=4)
        ax.plot(theta_full, [0.70] * 200, color='#4a5568', linewidth=0.8, linestyle=':', zorder=4)
        ax.plot(theta_full, [0.55] * 200, color='#d4af37', linewidth=1.0, zorder=4)
        ax.plot(theta_full, [0.42] * 200, color='#2d3748', linewidth=0.8, zorder=4)

        # 2. Casas Astrológicas (Cúspides y Números)
        cuspides = carta_data["cuspides_grados"]
        for h in range(12):
            c_deg = cuspides[h]
            c_next = cuspides[(h + 1) % 12]
            rad_cusp = to_wheel_rad(c_deg)
            
            # Línea de la cúspide (desde el círculo interior hasta el anillo de signos)
            # Resaltar los 4 ángulos mayores (Casas 1, 4, 7, 10)
            if h in [0, 6]: # Eje Ascendente - Descendente
                ax.plot([rad_cusp, rad_cusp], [0.42, 0.85], color='#e74c3c', linewidth=2.0, zorder=5)
            elif h in [3, 9]: # Eje MC - IC
                ax.plot([rad_cusp, rad_cusp], [0.42, 0.85], color='#3498db', linewidth=2.0, zorder=5)
            else:
                ax.plot([rad_cusp, rad_cusp], [0.42, 0.85], color='#718096', linewidth=0.9, linestyle='--', zorder=5)

            # Punto medio de la casa para poner el número adentro del sector
            diff = (c_next - c_deg) % 360.0
            mid_house_deg = (c_deg + diff / 2.0) % 360.0
            mid_house_rad = to_wheel_rad(mid_house_deg)
            
            # Número de la casa centrado dentro de su sector
            ax.text(mid_house_rad, 0.48, str(h + 1), ha='center', va='center',
                    color='#e2e8f0', fontsize=10, fontweight='bold', zorder=6)

        # Etiquetas de los ángulos mayores
        ax.text(to_wheel_rad(cuspides[0]), 0.82, "AC", ha='center', va='center', color='#e74c3c', fontsize=11, fontweight='black', zorder=7)
        ax.text(to_wheel_rad(cuspides[6]), 0.82, "DC", ha='center', va='center', color='#e74c3c', fontsize=11, fontweight='black', zorder=7)
        ax.text(to_wheel_rad(cuspides[9]), 0.82, "MC", ha='center', va='center', color='#3498db', fontsize=11, fontweight='black', zorder=7)
        ax.text(to_wheel_rad(cuspides[3]), 0.82, "IC", ha='center', va='center', color='#3498db', fontsize=11, fontweight='black', zorder=7)

        # 3. Planetas y Puntos Kármicos
        # Distribuir radialmente para evitar solapamientos si están muy juntos
        planetas = carta_data["planetas"]
        sorted_planets = sorted(planetas.items(), key=lambda x: x[1]["grado_absoluto"])
        
        # Algoritmo de dispersión de radios entre 0.60 y 0.76
        planet_radii = {}
        prev_deg = -999
        current_layer = 0
        layers = [0.62, 0.74, 0.68]
        
        for p_name, p_info in sorted_planets:
            deg = p_info["grado_absoluto"]
            if abs(deg - prev_deg) < 7.0:
                current_layer = (current_layer + 1) % len(layers)
            else:
                current_layer = 0
            planet_radii[p_name] = layers[current_layer]
            prev_deg = deg

        planet_wheel_coords = {}
        for p_name, p_info in planetas.items():
            rad = to_wheel_rad(p_info["grado_absoluto"])
            r_pos = planet_radii[p_name]
            planet_wheel_coords[p_name] = (rad, r_pos)
            
            glyph = self.PLANET_GLYPHS.get(p_name, '•')
            deg_text = f"{p_info['grado_en_signo']}°"
            
            # Punto en el gráfico
            ax.scatter(rad, r_pos, color='#d4af37', s=45, edgecolor='#ffffff', linewidth=0.8, zorder=8)
            # Glifo y etiqueta
            label = f"{glyph} {p_name[:3]} {deg_text}"
            ax.text(rad, r_pos + 0.045, label, ha='center', va='center',
                    color='#ffffff', fontsize=8, fontweight='medium', zorder=9,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a202c', edgecolor='#4a5568', alpha=0.85))

        # 4. Líneas de Aspectos en el Centro (radio < 0.42)
        center_r = 0.40
        for asp in carta_data["aspectos"]:
            p1, p2 = asp["cuerpo1"], asp["cuerpo2"]
            if p1 in planetas and p2 in planetas:
                rad1 = to_wheel_rad(planetas[p1]["grado_absoluto"])
                rad2 = to_wheel_rad(planetas[p2]["grado_absoluto"])
                
                # Coordenadas polares para trazar la cuerda recta entre (rad1, center_r) y (rad2, center_r)
                # En coordenadas polares de matplotlib, un plot([r1, r2], [theta1, theta2]) traza línea curva polar.
                # Para trazar una línea recta real, interpolamos en cartesiano y volvemos a polar:
                x1, y1 = center_r * np.cos(rad1), center_r * np.sin(rad1)
                x2, y2 = center_r * np.cos(rad2), center_r * np.sin(rad2)
                
                xs = np.linspace(x1, x2, 20)
                ys = np.linspace(y1, y2, 20)
                
                line_thetas = np.arctan2(ys, xs)
                line_rs = np.sqrt(xs**2 + ys**2)
                
                alpha_val = max(0.3, 0.85 - (asp["orbe"] / 10.0))
                ax.plot(line_thetas, line_rs, color=asp["color"], alpha=alpha_val, linewidth=1.2, zorder=4)

        # 5. Título y Detalles
        sujeto = carta_data["sujeto"]
        title_text = f"CARTA ASTRAL: {sujeto['nombre'].upper()}\n{sujeto['fecha_hora_local']} hs | Lat: {sujeto['latitud']}° Lon: {sujeto['longitud']}°"
        plt.title(title_text, color='#d4af37', fontsize=13, fontweight='bold', pad=30, y=1.02)
        
        # Guardar en alta resolución
        plt.savefig(output_path, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=180)
        plt.close()
        return output_path

if __name__ == "__main__":
    from calculador_astronomico import CalculadorAstronomico
    from datetime import datetime
    
    calc = CalculadorAstronomico()
    dt = datetime(1987, 6, 24, 20, 30)
    data = calc.calcular_carta("Lionel Messi", dt, -32.9468, -60.6393, -3)
    
    graficador = GraficadorRuedaAstrologica()
    out = "/home/LAB/astrology_factory/products/carta_natal/test_rueda_messi.png"
    graficador.generar_rueda(data, out)
    print("Rueda profesional generada con éxito en:", out)
