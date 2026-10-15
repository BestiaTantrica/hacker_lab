#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
motor_vectorial_rs.py
─────────────────────────────────────────────────────────────────────────────
Motor de Renderizado Vectorial (SVG / HTML5 + FFmpeg) para Revolución Solar.
Diseñado bajo la Arquitectura de 3 Actos:
  - ACTO 1: Carta Natal Base (Tu Origen, nítido y grande).
  - ACTO 2: El Acoplamiento del Retorno Solar (Bi-Wheel Cósmico).
  - ACTO 3: Enfoques Quirúrgicos Ampliados (Zooms nítidos con HUD holográfico).
Cero costo ($0), vectorial puro, 1080p nativo y sin pixelación.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import math
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


ZODIAC_SIGNS = [
    {"nombre": "Aries", "simbolo": "♈", "elemento": "Fuego", "color": "#e74c3c"},
    {"nombre": "Tauro", "simbolo": "♉", "elemento": "Tierra", "color": "#27ae60"},
    {"nombre": "Géminis", "simbolo": "♊", "elemento": "Aire", "color": "#f39c12"},
    {"nombre": "Cáncer", "simbolo": "♋", "elemento": "Agua", "color": "#2980b9"},
    {"nombre": "Leo", "simbolo": "♌", "elemento": "Fuego", "color": "#d35400"},
    {"nombre": "Virgo", "simbolo": "♍", "elemento": "Tierra", "color": "#229954"},
    {"nombre": "Libra", "simbolo": "♎", "elemento": "Aire", "color": "#d4ac0d"},
    {"nombre": "Escorpio", "simbolo": "♏", "elemento": "Agua", "color": "#2471a3"},
    {"nombre": "Sagitario", "simbolo": "♐", "elemento": "Fuego", "color": "#b03a2e"},
    {"nombre": "Capricornio", "simbolo": "♑", "elemento": "Tierra", "color": "#1e8449"},
    {"nombre": "Acuario", "simbolo": "♒", "elemento": "Aire", "color": "#b7950b"},
    {"nombre": "Piscis", "simbolo": "♓", "elemento": "Agua", "color": "#1f618d"},
]

PLANET_GLYPHS = {
    'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂',
    'Júpiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Plutón': '♇',
    'Quirón': '⚷', 'Nodo Norte': '☊', 'Lilith': '⚸'
}


class GeneradorVectorialAstrologico:
    """Genera representaciones vectoriales en SVG de alta fidelidad estética (1920x1080)."""

    def __init__(self, cx: float = 960.0, cy: float = 540.0):
        self.cx = cx
        self.cy = cy

    def deg_to_rad(self, deg: float, asc_deg: float) -> float:
        """Convierte grado zodiacal a radianes con Ascendente a 180° (izquierda) y avance antihorario."""
        rel_deg = (deg - asc_deg) % 360.0
        # En coordenadas SVG (Y hacia abajo), 180° + rel_deg avanza en sentido antihorario:
        # 180° (izq/Asc) -> 270° (abajo/FC) -> 0°/360° (der/Desc) -> 90° (arriba/MC)
        return math.radians(180.0 + rel_deg)

    def polar_to_xy(self, rad: float, r: float) -> Tuple[float, float]:
        """Convierte coordenadas polares a coordenadas cartesianas (X, Y) de pantalla."""
        x = self.cx + r * math.cos(rad)
        y = self.cy - r * math.sin(rad)
        return x, y

    def _generar_filtros_svg(self) -> str:
        """Filtros SVG para resplandores neón y glassmorphism."""
        return """
        <defs>
            <radialGradient id="spaceGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#141c30" stop-opacity="0.8"/>
                <stop offset="60%" stop-color="#080b14" stop-opacity="0.95"/>
                <stop offset="100%" stop-color="#04060a" stop-opacity="1"/>
            </radialGradient>
            <radialGradient id="portalGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.45"/>
                <stop offset="100%" stop-color="#00f2fe" stop-opacity="0"/>
            </radialGradient>
            <filter id="glowGold" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="5" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="glowCyan" x="-30%" y="-30%" width="160%" height="160%">
                <feGaussianBlur stdDeviation="7" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffe270"/>
                <stop offset="100%" stop-color="#d4af37"/>
            </linearGradient>
            <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#70f3ff"/>
                <stop offset="100%" stop-color="#00b4d8"/>
            </linearGradient>
        </defs>
        """

    def generar_svg_acto1_natal(self, datos_rs: Dict[str, Any]) -> str:
        """
        ACTO 1: Carta Natal Base limpia, amplia y de máxima claridad visual.
        Ocupa el protagonismo central con orientación astrológica canónica (antihoraria, Asc a las 9hs).
        """
        natal = datos_rs["carta_natal"]
        sujeto = natal["sujeto"]["nombre"]
        fecha_natal = natal["sujeto"]["fecha_hora_local"]
        planetas = natal["planetas"]
        asc_deg = natal["angulos"]["Ascendente"]["grado_absoluto"]
        asc_fmt = natal["angulos"]["Ascendente"]["formato"]
        sol_fmt = planetas["Sol"]["formato"]
        luna_fmt = planetas["Luna"]["formato"]

        r_out = 450.0
        r_zodiac = 405.0
        r_houses = 345.0
        r_planets_base = 270.0
        r_core = 160.0

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#05070d; font-family:\'Cinzel\', \'Segoe UI\', sans-serif;">',
            self._generar_filtros_svg(),
            f'<circle cx="{self.cx}" cy="{self.cy}" r="520" fill="url(#spaceGlow)"/>'
        ]

        # 1. Anillo Zodiacal (Sentido Antihorario Canónico)
        for i, sign in enumerate(ZODIAC_SIGNS):
            deg_start = i * 30.0
            deg_end = (i + 1) * 30.0
            rad_s = self.deg_to_rad(deg_start, asc_deg)
            rad_e = self.deg_to_rad(deg_end, asc_deg)
            rad_mid = (rad_s + rad_e) / 2.0

            x1_o, y1_o = self.polar_to_xy(rad_s, r_out)
            x2_o, y2_o = self.polar_to_xy(rad_e, r_out)
            x1_i, y1_i = self.polar_to_xy(rad_s, r_zodiac)
            x2_i, y2_i = self.polar_to_xy(rad_e, r_zodiac)

            # Segmento del signo (arco SVG)
            d_path = f"M {x1_o} {y1_o} A {r_out} {r_out} 0 0 0 {x2_o} {y2_o} L {x2_i} {y2_i} A {r_zodiac} {r_zodiac} 0 0 1 {x1_i} {y1_i} Z"
            svg.append(f'<path d="{d_path}" fill="{sign["color"]}" fill-opacity="0.22" stroke="#d4af37" stroke-width="1.2" stroke-opacity="0.4"/>')

            # Glifo del signo
            x_txt, y_txt = self.polar_to_xy(rad_mid, (r_out + r_zodiac) / 2.0)
            svg.append(f'<text x="{x_txt}" y="{y_txt + 7}" text-anchor="middle" fill="#ffffff" font-size="20" font-weight="bold" fill-opacity="0.9">{sign["simbolo"]}</text>')

        # 2. Cúspides y Casas Natales (12 Casas)
        casas_deg = natal.get("casas_grados", [i * 30.0 for i in range(12)])
        for h in range(12):
            c_deg = casas_deg[h]
            c_next = casas_deg[(h + 1) % 12]
            rad_c = self.deg_to_rad(c_deg, asc_deg)
            rad_next = self.deg_to_rad(c_next, asc_deg)

            x_in, y_in = self.polar_to_xy(rad_c, r_core)
            x_out, y_out = self.polar_to_xy(rad_c, r_zodiac)

            es_eje = (h in [0, 3, 6, 9]) # AC, FC, DC, MC
            stroke_c = "#ffd700" if es_eje else "#718096"
            stroke_w = "2.8" if es_eje else "1.0"
            stroke_op = "0.95" if es_eje else "0.35"
            svg.append(f'<line x1="{x_in}" y1="{y_in}" x2="{x_out}" y2="{y_out}" stroke="{stroke_c}" stroke-width="{stroke_w}" stroke-opacity="{stroke_op}"/>')

            # Número de Casa
            diff_deg = (c_next - c_deg) % 360.0
            mid_house_deg = (c_deg + diff_deg / 2.0) % 360.0
            rad_mid = self.deg_to_rad(mid_house_deg, asc_deg)
            x_num, y_num = self.polar_to_xy(rad_mid, (r_core + r_houses) / 2.0)
            svg.append(f'<circle cx="{x_num}" cy="{y_num}" r="14" fill="#080b14" stroke="#d4af37" stroke-width="1" stroke-opacity="0.5"/>')
            svg.append(f'<text x="{x_num}" y="{y_num + 5}" text-anchor="middle" fill="#d4af37" font-size="12" font-weight="bold">{h + 1}</text>')

        # 3. Planetas Natales con Desfase Radial Anticolisión (Staggering)
        # Ordenamos planetas por grado para detectar aglomeraciones
        p_items = sorted(planetas.items(), key=lambda it: it[1]["grado_absoluto"])
        stagger_radii = [r_planets_base, r_planets_base - 45.0, r_planets_base + 38.0]
        
        for idx, (p_name, p_info) in enumerate(p_items):
            p_deg = p_info["grado_absoluto"]
            rad_p = self.deg_to_rad(p_deg, asc_deg)
            glyph = PLANET_GLYPHS.get(p_name, p_name[:2])

            # Detectar si está cerca del anterior para alternar radio
            prev_deg = p_items[idx - 1][1]["grado_absoluto"] if idx > 0 else -999.0
            dist_prev = (p_deg - prev_deg) % 360.0
            r_cur = stagger_radii[idx % 2] if dist_prev < 14.0 else r_planets_base

            px, py = self.polar_to_xy(rad_p, r_cur)

            # Orbe de luz y Badge de planeta
            svg.append(f'<circle cx="{px}" cy="{py}" r="20" fill="#ffd700" fill-opacity="0.18" filter="url(#glowGold)"/>')
            svg.append(f'<circle cx="{px}" cy="{py}" r="14" fill="#0c111e" stroke="#ffd700" stroke-width="1.8"/>')
            svg.append(f'<text x="{px}" y="{py + 6}" text-anchor="middle" fill="#ffe270" font-size="15" font-weight="bold">{glyph}</text>')

            # Grado en signo
            g_txt, g_ytxt = self.polar_to_xy(rad_p, r_cur + (24.0 if r_cur <= r_planets_base else -24.0))
            svg.append(f'<text x="{g_txt}" y="{g_ytxt + 4}" text-anchor="middle" fill="#ffffff" font-size="11" font-weight="600">{p_info["grado_en_signo"]}°</text>')

        # 4. Marcador Especial: Ascendente Natal (180° = izquierda absoluta / 9hs)
        ax_in, ay_in = self.polar_to_xy(math.pi, r_core)
        ax_out, ay_out = self.polar_to_xy(math.pi, r_out + 25.0)
        svg.append(f'<line x1="{ax_in}" y1="{ay_in}" x2="{ax_out}" y2="{ay_out}" stroke="#ffd700" stroke-width="3.5" filter="url(#glowGold)"/>')
        svg.append(f'<rect x="{ax_out - 130}" y="{ay_out - 18}" width="125" height="36" rx="6" fill="#0c111e" stroke="#ffd700" stroke-width="1.8"/>')
        svg.append(f'<text x="{ax_out - 67}" y="{ay_out + 5}" text-anchor="middle" fill="#ffd700" font-size="13" font-weight="bold">ASC NATAL</text>')

        # 5. Encabezado y Ficha de Presentación
        svg.append(f"""
        <g id="header">
            <rect x="560" y="30" width="800" height="74" rx="10" fill="#090d18" fill-opacity="0.9" stroke="#d4af37" stroke-width="1.4"/>
            <text x="960" y="60" text-anchor="middle" fill="#ffd700" font-size="20" font-weight="bold" letter-spacing="3">✦ CARTA NATAL BASE · {sujeto.upper()} ✦</text>
            <text x="960" y="86" text-anchor="middle" fill="#94a3b8" font-size="13">Fecha: {fecha_natal} · Sol: {sol_fmt} · Luna: {luna_fmt} · Ascendente: {asc_fmt}</text>
        </g>
        <g id="footer_badge">
            <rect x="680" y="990" width="560" height="50" rx="8" fill="#090d18" fill-opacity="0.9" stroke="#d4af37" stroke-width="1"/>
            <text x="960" y="1021" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="500">ACTO 1: Tu Matriz Psicológica Permanente (La Raíz del Retorno)</text>
        </g>
        """)

        svg.append('</svg>')
        return "\n".join(svg)

    def generar_svg_acto2_biwheel(self, datos_rs: Dict[str, Any]) -> str:
        """
        ACTO 2: El Acoplamiento Bi-Wheel (Natal Interior Dorado + RS Exterior Cian).
        Muestra la sincronización exacta del Retorno Solar acoplándose sobre la matriz natal.
        """
        natal = datos_rs["carta_natal"]
        rs = datos_rs["revolucion_solar"]
        sujeto = natal["sujeto"]["nombre"]
        asc_deg = natal["angulos"]["Ascendente"]["grado_absoluto"]
        fecha_rs = rs.get("retorno_solar", {}).get("fecha_hora_local", "11 de Abril 2026, 18:10 hs")

        planetas_nat = natal["planetas"]
        planetas_rs = rs["planetas_rs"]

        r_out_rs = 485.0
        r_rs_band = 425.0
        r_zodiac = 385.0
        r_nat_band = 295.0
        r_core = 160.0

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#05070d; font-family:\'Cinzel\', \'Segoe UI\', sans-serif;">',
            self._generar_filtros_svg(),
            f'<circle cx="{self.cx}" cy="{self.cy}" r="520" fill="url(#spaceGlow)"/>',
            # Halo exterior del Retorno Solar
            f'<circle cx="{self.cx}" cy="{self.cy}" r="{r_out_rs}" fill="none" stroke="#00f2fe" stroke-width="2.5" filter="url(#glowCyan)"/>',
            f'<circle cx="{self.cx}" cy="{self.cy}" r="{r_rs_band}" fill="none" stroke="#00f2fe" stroke-width="1.2" stroke-dasharray="4,4" stroke-opacity="0.6"/>',
            f'<circle cx="{self.cx}" cy="{self.cy}" r="{r_zodiac}" fill="none" stroke="#ffd700" stroke-width="2.0" stroke-opacity="0.8"/>',
            f'<circle cx="{self.cx}" cy="{self.cy}" r="{r_core}" fill="#080b14" stroke="#d4af37" stroke-width="1.2"/>'
        ]

        # 1. Anillo Zodiacal Central
        for i, sign in enumerate(ZODIAC_SIGNS):
            deg_start = i * 30.0
            deg_end = (i + 1) * 30.0
            rad_s = self.deg_to_rad(deg_start, asc_deg)
            rad_e = self.deg_to_rad(deg_end, asc_deg)
            rad_mid = (rad_s + rad_e) / 2.0

            x1_o, y1_o = self.polar_to_xy(rad_s, r_zodiac)
            x2_o, y2_o = self.polar_to_xy(rad_e, r_zodiac)
            x1_i, y1_i = self.polar_to_xy(rad_s, r_nat_band)
            x2_i, y2_i = self.polar_to_xy(rad_e, r_nat_band)

            d_path = f"M {x1_o} {y1_o} A {r_zodiac} {r_zodiac} 0 0 0 {x2_o} {y2_o} L {x2_i} {y2_i} A {r_nat_band} {r_nat_band} 0 0 1 {x1_i} {y1_i} Z"
            svg.append(f'<path d="{d_path}" fill="{sign["color"]}" fill-opacity="0.20" stroke="#d4af37" stroke-width="1" stroke-opacity="0.3"/>')
            x_txt, y_txt = self.polar_to_xy(rad_mid, (r_zodiac + r_nat_band) / 2.0)
            svg.append(f'<text x="{x_txt}" y="{y_txt + 6}" text-anchor="middle" fill="#ffffff" font-size="18" font-weight="bold">{sign["simbolo"]}</text>')

        # 2. Planetas Natales (Anillo Interior - Oro)
        r_p_nat = 230.0
        p_nat_items = sorted(planetas_nat.items(), key=lambda it: it[1]["grado_absoluto"])
        for idx, (p_name, p_info) in enumerate(p_nat_items):
            p_deg = p_info["grado_absoluto"]
            rad_p = self.deg_to_rad(p_deg, asc_deg)
            gl = PLANET_GLYPHS.get(p_name, p_name[:2])
            prev_deg = p_nat_items[idx - 1][1]["grado_absoluto"] if idx > 0 else -999.0
            r_cur = (r_p_nat - 30.0) if ((p_deg - prev_deg) % 360.0 < 14.0 and idx % 2 == 1) else r_p_nat
            px, py = self.polar_to_xy(rad_p, r_cur)
            svg.append(f'<circle cx="{px}" cy="{py}" r="12" fill="#080b14" stroke="#ffd700" stroke-width="1.6"/>')
            svg.append(f'<text x="{px}" y="{py + 5}" text-anchor="middle" fill="#ffe270" font-size="13" font-weight="bold">{gl}</text>')

        # 3. Planetas RS (Anillo Exterior - Cian Neón)
        r_p_rs = 455.0
        p_rs_items = sorted(planetas_rs.items(), key=lambda it: it[1]["grado_absoluto"])
        for idx, (p_name, p_info) in enumerate(p_rs_items):
            p_deg = p_info["grado_absoluto"]
            rad_p = self.deg_to_rad(p_deg, asc_deg)
            gl = PLANET_GLYPHS.get(p_name, p_name[:2])
            prev_deg = p_rs_items[idx - 1][1]["grado_absoluto"] if idx > 0 else -999.0
            r_cur = (r_p_rs - 26.0) if ((p_deg - prev_deg) % 360.0 < 14.0 and idx % 2 == 1) else r_p_rs
            px, py = self.polar_to_xy(rad_p, r_cur)
            svg.append(f'<circle cx="{px}" cy="{py}" r="15" fill="#00f2fe" fill-opacity="0.22" filter="url(#glowCyan)"/>')
            svg.append(f'<circle cx="{px}" cy="{py}" r="12" fill="#06121e" stroke="#00f2fe" stroke-width="1.6"/>')
            svg.append(f'<text x="{px}" y="{py + 5}" text-anchor="middle" fill="#70f3ff" font-size="13" font-weight="bold">{gl}</text>')

        # 4. Rayo del Ascendente RS aterrizando en la Carta Natal
        asc_rs_deg = rs["angulos_rs"]["Ascendente_RS"]["grado_absoluto"]
        rad_asc_rs = self.deg_to_rad(asc_rs_deg, asc_deg)
        x_ray_in, y_ray_in = self.polar_to_xy(rad_asc_rs, r_core)
        x_ray_out, y_ray_out = self.polar_to_xy(rad_asc_rs, r_out_rs + 25.0)
        svg.append(f'<line x1="{x_ray_in}" y1="{y_ray_in}" x2="{x_ray_out}" y2="{y_ray_out}" stroke="#00f2fe" stroke-width="3.5" filter="url(#glowCyan)"/>')
        svg.append(f'<rect x="{x_ray_out - 15}" y="{y_ray_out - 16}" width="160" height="32" rx="6" fill="#08101e" stroke="#00f2fe" stroke-width="1.6"/>')
        svg.append(f'<text x="{x_ray_out + 65}" y="{y_ray_out + 5}" text-anchor="middle" fill="#00f2fe" font-size="12" font-weight="bold">ASC RS: LIBRA 14°</text>')

        # 5. Encabezado y Leyenda
        svg.append(f"""
        <g id="header_biwheel">
            <rect x="520" y="30" width="880" height="74" rx="10" fill="#090d18" fill-opacity="0.92" stroke="#00f2fe" stroke-width="1.6" filter="url(#glowCyan)"/>
            <text x="960" y="60" text-anchor="middle" fill="#00f2fe" font-size="20" font-weight="bold" letter-spacing="3">✦ ACOPLAMIENTO CÓSMICO · RETORNO SOLAR 2026 ✦</text>
            <text x="960" y="86" text-anchor="middle" fill="#94a3b8" font-size="13">Retorno Exacto: {fecha_rs} · Natal (Oro) ⟷ Tránsito Anual (Cian)</text>
        </g>
        <g id="footer_biwheel">
            <rect x="640" y="990" width="640" height="50" rx="8" fill="#090d18" fill-opacity="0.9" stroke="#d4af37" stroke-width="1"/>
            <text x="960" y="1021" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="500">ACTO 2: El Anillo Anual sincroniza su pulso sobre tus posiciones de origen</text>
        </g>
        """)

        svg.append('</svg>')
        return "\n".join(svg)

    def generar_svg_acto3_portal(self, datos_rs: Dict[str, Any]) -> str:
        """
        ACTO 3: Enfoque Quirúrgico en el Portal del Año (Ascendente RS en Libra / Casa 9 Natal).
        Zoom óptico centrado en el cuadrante del Portal con tarjeta holográfica explicativa lateral.
        """
        natal = datos_rs["carta_natal"]
        rs = datos_rs["revolucion_solar"]
        sujeto = natal["sujeto"]["nombre"]
        asc_natal_deg = natal["angulos"]["Ascendente"]["grado_absoluto"]
        asc_rs = rs["angulos_rs"]["Ascendente_RS"]
        asc_rs_deg = asc_rs["grado_absoluto"]
        casa_portal = asc_rs["casa_natal_superpuesta"]

        cx_zoom = 600.0
        cy_zoom = 540.0
        r_out = 640.0
        r_rs = 530.0
        r_nat = 410.0
        r_core = 230.0

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" style="background:#05070d; font-family:\'Cinzel\', \'Segoe UI\', sans-serif;">',
            self._generar_filtros_svg(),
            f'<circle cx="{cx_zoom}" cy="{cy_zoom}" r="750" fill="url(#spaceGlow)"/>'
        ]

        # Resplandor de fondo en la zona del Portal (Libra / Casa 9)
        rad_portal = self.deg_to_rad(asc_rs_deg, asc_natal_deg)
        x_p_glow, y_p_glow = (cx_zoom + 460 * math.cos(rad_portal)), (cy_zoom - 460 * math.sin(rad_portal))
        svg.append(f'<circle cx="{x_p_glow}" cy="{y_p_glow}" r="240" fill="url(#portalGlow)"/>')

        # Círculos delimitadores
        svg.append(f'<circle cx="{cx_zoom}" cy="{cy_zoom}" r="{r_out}" fill="none" stroke="#00f2fe" stroke-width="1.8" stroke-opacity="0.4"/>')
        svg.append(f'<circle cx="{cx_zoom}" cy="{cy_zoom}" r="{r_rs}" fill="none" stroke="#00f2fe" stroke-width="1.2" stroke-dasharray="4,4" stroke-opacity="0.6"/>')
        svg.append(f'<circle cx="{cx_zoom}" cy="{cy_zoom}" r="{r_nat}" fill="none" stroke="#ffd700" stroke-width="2.0" stroke-opacity="0.8"/>')
        svg.append(f'<circle cx="{cx_zoom}" cy="{cy_zoom}" r="{r_core}" fill="#080b14" stroke="#d4af37" stroke-width="1.2"/>')

        # 1. Sector Destacado: Casa 9 Natal (Enriquecida en Oro Cálido)
        # Casa 9 de Tomás empieza en aprox 194° y va hasta 230°
        casas_deg = natal.get("casas_grados", [i * 30.0 for i in range(12)])
        c9_start = casas_deg[8] # Cúspide Casa 9 (índice 8)
        c9_end = casas_deg[9]   # Cúspide Casa 10 / MC (índice 9)
        rad_c9_start = self.deg_to_rad(c9_start, asc_natal_deg)
        rad_c9_end = self.deg_to_rad(c9_end, asc_natal_deg)

        x1, y1 = cx_zoom + r_core * math.cos(rad_c9_start), cy_zoom - r_core * math.sin(rad_c9_start)
        x2, y2 = cx_zoom + r_rs * math.cos(rad_c9_start), cy_zoom - r_rs * math.sin(rad_c9_start)
        x3, y3 = cx_zoom + r_rs * math.cos(rad_c9_end), cy_zoom - r_rs * math.sin(rad_c9_end)
        x4, y4 = cx_zoom + r_core * math.cos(rad_c9_end), cy_zoom - r_core * math.sin(rad_c9_end)

        svg.append(f'<polygon points="{x1},{y1} {x2},{y2} {x3},{y3} {x4},{y4}" fill="#ffd700" fill-opacity="0.18"/>')

        # 2. El Rayo Láser del Portal (Ascendente RS en Libra 14°21')
        px_in, py_in = cx_zoom + r_core * math.cos(rad_portal), cy_zoom - r_core * math.sin(rad_portal)
        px_out, py_out = cx_zoom + (r_out + 30) * math.cos(rad_portal), cy_zoom - (r_out + 30) * math.sin(rad_portal)
        svg.append(f'<line x1="{px_in}" y1="{py_in}" x2="{px_out}" y2="{py_out}" stroke="#00f2fe" stroke-width="4.5" filter="url(#glowCyan)"/>')

        # Reticle Lock en el punto exacto
        svg.append(f'<circle cx="{px_out}" cy="{py_out}" r="26" fill="none" stroke="#00f2fe" stroke-width="2.5" stroke-dasharray="6,4" filter="url(#glowCyan)"/>')
        svg.append(f'<circle cx="{px_out}" cy="{py_out}" r="6" fill="#ffffff"/>')

        # 3. Planetas natales en Casa 9: Saturno, Plutón y Júpiter con posiciones limpias
        planetas_c9 = [
            ("Saturno", natal["planetas"]["Saturno"], r_nat - 20.0, 32.0, 0.0),
            ("Plutón", natal["planetas"]["Plutón"], r_nat - 75.0, -28.0, 0.0),
            ("Júpiter", natal["planetas"]["Júpiter"], r_nat - 130.0, 32.0, 0.0)
        ]
        for p_name, p_info, r_offset, txt_offset, dx in planetas_c9:
            deg = p_info["grado_absoluto"]
            rad = self.deg_to_rad(deg, asc_natal_deg)
            x_p, y_p = cx_zoom + r_offset * math.cos(rad) + dx, cy_zoom - r_offset * math.sin(rad)
            gl = PLANET_GLYPHS.get(p_name, p_name[:2])
            svg.append(f'<circle cx="{x_p}" cy="{y_p}" r="24" fill="#ffd700" fill-opacity="0.25" filter="url(#glowGold)"/>')
            svg.append(f'<circle cx="{x_p}" cy="{y_p}" r="17" fill="#080b14" stroke="#ffd700" stroke-width="2"/>')
            svg.append(f'<text x="{x_p}" y="{y_p + 6}" text-anchor="middle" fill="#ffe270" font-size="17" font-weight="bold">{gl}</text>')
            svg.append(f'<text x="{x_p}" y="{y_p + txt_offset}" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="bold">{p_name} {p_info["grado_en_signo"]}°</text>')

        # 4. TARJETA HOLOGRÁFICA LATERAL DERECHA (HUD Cinemático 45% pantalla)
        card_x = 1220
        card_y = 120
        card_w = 640
        card_h = 840

        svg.append(f"""
        <g id="hud_card">
            <!-- Marco de Cristal Holográfico -->
            <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="16"
                  fill="#0a0f1d" fill-opacity="0.94" stroke="#00f2fe" stroke-width="2.0" filter="url(#glowCyan)"/>
            
            <!-- Cabecera de la Tarjeta -->
            <rect x="{card_x}" y="{card_y}" width="{card_w}" height="80" rx="16" fill="#0e172a"/>
            <text x="{card_x + 32}" y="{card_y + 48}" fill="#00f2fe" font-size="22" font-weight="bold" letter-spacing="2">✦ EL PORTAL DEL AÑO 2026 ✦</text>

            <!-- Bloque 1: Coordenada Astronómica -->
            <g transform="translate({card_x + 32}, {card_y + 120})">
                <text x="0" y="0" fill="#94a3b8" font-size="13" font-weight="600">PUNTO DE ENTRADA ANUAL</text>
                <text x="0" y="32" fill="#ffffff" font-size="26" font-weight="bold">Ascendente RS en Libra 14° 21'</text>
                <rect x="0" y="48" width="576" height="1" fill="#1e293b"/>
            </g>

            <!-- Bloque 2: Territorio Natal Conquistado -->
            <g transform="translate({card_x + 32}, {card_y + 220})">
                <text x="0" y="0" fill="#ffd700" font-size="13" font-weight="bold">ESCENARIO PROTAGONISTA</text>
                <text x="0" y="34" fill="#ffe270" font-size="28" font-weight="bold">Casa 9 Natal (La Ley y el Horizonte)</text>
                <text x="0" y="66" fill="#cbd5e1" font-size="15" font-weight="normal">Ahí habitan tus nudos fundacionales:</text>
                <text x="0" y="94" fill="#ffffff" font-size="16" font-weight="600">♄ Saturno 18° · ♇ Plutón 25° · ♃ Júpiter 7°</text>
                <rect x="0" y="116" width="576" height="1" fill="#1e293b"/>
            </g>

            <!-- Bloque 3: Mensaje Pedagógico del Guion de Tomás -->
            <g transform="translate({card_x + 32}, {card_y + 400})">
                <text x="0" y="0" fill="#00f2fe" font-size="14" font-weight="bold">DIAGNÓSTICO DEL RETORNO</text>
                
                <text x="0" y="36" fill="#e2e8f0" font-size="16" font-weight="500">"El Ascendente natal está en Acuario: mirar desde</text>
                <text x="0" y="62" fill="#e2e8f0" font-size="16" font-weight="500">afuera, resolver solo y desconfiar de pertenecer.</text>
                
                <text x="0" y="105" fill="#f8fafc" font-size="16" font-weight="bold">Este año esa postura queda desplazada.</text>
                <text x="0" y="132" fill="#e2e8f0" font-size="16" font-weight="500">La puerta es Libra: el pacto, el socio, la balanza.</text>
                
                <text x="0" y="175" fill="#ffd700" font-size="16" font-weight="bold">Que aterrice en tu Casa 9 es una exigencia:</text>
                <text x="0" y="202" fill="#e2e8f0" font-size="16" font-weight="500">Te toca negociar, poner firma y ceder terreno."</text>
            </g>

            <!-- Pie de Tarjeta -->
            <g transform="translate({card_x + 32}, {card_y + 760})">
                <rect x="0" y="0" width="576" height="44" rx="8" fill="#1e293b" fill-opacity="0.6"/>
                <text x="288" y="27" text-anchor="middle" fill="#00f2fe" font-size="13" font-weight="bold">CAPÍTULO 1 · REVOLUCIÓN SOLAR 2026</text>
            </g>
        </g>
        """)

        svg.append('</svg>')
        return "\n".join(svg)


def exportar_svg_a_png(svg_content: str, output_png: str) -> str:
    """Renderiza el código SVG a un PNG de 1920x1080 utilizando Google Chrome / Chromium headless."""
    out_p = Path(output_png)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    temp_svg = out_p.with_suffix(".svg")

    with open(temp_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)

    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--default-background-color=000000",
        "--window-size=1920,1080",
        f"--screenshot={str(out_p)}",
        str(temp_svg)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Error renderizando SVG con Chrome:\n{res.stderr}")

    if temp_svg.exists():
        temp_svg.unlink()

    return str(out_p)


if __name__ == "__main__":
    datos_tomas_path = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/datos_rs_tomás_2026.json")
    if not datos_tomas_path.exists():
        print(f"Error: No se encontró {datos_tomas_path}")
        sys.exit(1)

    with open(datos_tomas_path, "r", encoding="utf-8") as f:
        datos = json.load(f)

    gen = GeneradorVectorialAstrologico()
    out_dir = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/vectorial_preview")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("🎨 Renderizando Acto 1: Carta Natal de Tomás...")
    svg_acto1 = gen.generar_svg_acto1_natal(datos)
    png_acto1 = exportar_svg_a_png(svg_acto1, str(out_dir / "acto1_carta_natal_tomas.png"))
    print(f"✅ Acto 1 listo: {png_acto1}")

    print("🎨 Renderizando Acto 2: Acoplamiento Bi-Wheel Retorno Solar 2026...")
    svg_acto2 = gen.generar_svg_acto2_biwheel(datos)
    png_acto2 = exportar_svg_a_png(svg_acto2, str(out_dir / "acto2_acoplamiento_biwheel.png"))
    print(f"✅ Acto 2 listo: {png_acto2}")

    print("🎨 Renderizando Acto 3: Enfoque Portal en Libra / Casa 9...")
    svg_acto3 = gen.generar_svg_acto3_portal(datos)
    png_acto3 = exportar_svg_a_png(svg_acto3, str(out_dir / "acto3_portal_libra_casa9.png"))
    print(f"✅ Acto 3 listo: {png_acto3}")
