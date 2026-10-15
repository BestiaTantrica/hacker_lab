#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generador_ruedas_vibrantes.py
─────────────────────────────────────────────────────────────────────────────
Generador de Cartas Astrológicas Vibrantes de Alta Calidad para Video.
- Carta Natal Completa: Con líneas de aspectos coloreadas (azul, rojo, oro),
  planetas como joyas cromáticas diferenciadas, casas y signos nítidos.
- Bi-Wheel Completa: Superposición cósmica con aspectos intercartas,
  anillo anual de RS en cian y el rayo del Ascendente en Libra hacia Casa 9.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Paleta cromática personalizada para cada planeta (Joyas Cósmicas)
PLANET_STYLES = {
    'Sol': {'glyph': '☉', 'color': '#ffb703', 'glow': '#fb8500', 'size': 18, 'name': 'Sol'},
    'Luna': {'glyph': '☽', 'color': '#e0f2fe', 'glow': '#38bdf8', 'size': 17, 'name': 'Luna'},
    'Mercurio': {'glyph': '☿', 'color': '#06b6d4', 'glow': '#22d3ee', 'size': 16, 'name': 'Mercurio'},
    'Venus': {'glyph': '♀', 'color': '#10b981', 'glow': '#34d399', 'size': 17, 'name': 'Venus'},
    'Marte': {'glyph': '♂', 'color': '#ef4444', 'glow': '#f87171', 'size': 17, 'name': 'Marte'},
    'Júpiter': {'glyph': '♃', 'color': '#c084fc', 'glow': '#a855f7', 'size': 18, 'name': 'Júpiter'},
    'Saturno': {'glyph': '♄', 'color': '#f59e0b', 'glow': '#d97706', 'size': 17, 'name': 'Saturno'},
    'Urano': {'glyph': '♅', 'color': '#00f2fe', 'glow': '#38bdf8', 'size': 16, 'name': 'Urano'},
    'Neptuno': {'glyph': '♆', 'color': '#3b82f6', 'glow': '#60a5fa', 'size': 16, 'name': 'Neptuno'},
    'Plutón': {'glyph': '♇', 'color': '#ec4899', 'glow': '#f43f5e', 'size': 16, 'name': 'Plutón'},
    'Nodo Norte': {'glyph': '☊', 'color': '#e2e8f0', 'glow': '#94a3b8', 'size': 15, 'name': 'Nodo'},
    'Quirón': {'glyph': '⚷', 'color': '#a3e635', 'glow': '#84cc16', 'size': 15, 'name': 'Quirón'},
    'Lilith': {'glyph': '⚸', 'color': '#9333ea', 'glow': '#7e22ce', 'size': 15, 'name': 'Lilith'}
}

ZODIAC_SIGNS = [
    {"name": "Aries", "glyph": "♈", "color": "#dc2626", "elem": "Fuego"},
    {"name": "Tauro", "glyph": "♉", "color": "#16a34a", "elem": "Tierra"},
    {"name": "Géminis", "glyph": "♊", "color": "#ea580c", "elem": "Aire"},
    {"name": "Cáncer", "glyph": "♋", "color": "#0284c7", "elem": "Agua"},
    {"name": "Leo", "glyph": "♌", "color": "#e11d48", "elem": "Fuego"},
    {"name": "Virgo", "glyph": "♍", "color": "#059669", "elem": "Tierra"},
    {"name": "Libra", "glyph": "♎", "color": "#d97706", "elem": "Aire"},
    {"name": "Escorpio", "glyph": "♏", "color": "#2563eb", "elem": "Agua"},
    {"name": "Sagitario", "glyph": "♐", "color": "#b91c1c", "elem": "Fuego"},
    {"name": "Capricornio", "glyph": "♑", "color": "#047857", "elem": "Tierra"},
    {"name": "Acuario", "glyph": "♒", "color": "#b45309", "elem": "Aire"},
    {"name": "Piscis", "glyph": "♓", "color": "#1d4ed8", "elem": "Agua"}
]


def renderizar_carta_natal_vibrante(datos: Dict[str, Any], output_path: str):
    """Renderiza la Carta Natal completa con aspectos interiores, colores y máxima nitidez."""
    natal = datos["carta_natal"]
    sujeto = natal["sujeto"]["nombre"]
    asc_deg = natal["angulos"]["Ascendente"]["grado_absoluto"]

    fig, ax = plt.subplots(figsize=(14, 14), subplot_kw={'projection': 'polar'})
    bg_color = "#040711"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.axis('off')

    def to_rad(deg: float) -> float:
        """Convierte grado zodiacal a radianes con Ascendente fijo a 180° (horizonte izquierdo)."""
        rel = (deg - asc_deg + 180.0) % 360.0
        return np.radians(rel)

    # 1. Estrellas de fondo
    np.random.seed(42)
    n_stars = 240
    s_r = np.random.uniform(0.10, 0.98, n_stars)
    s_th = np.random.uniform(0, 2 * np.pi, n_stars)
    s_al = np.random.uniform(0.12, 0.65, n_stars)
    s_sz = np.random.uniform(3, 14, n_stars)
    ax.scatter(s_th, s_r, c='#ffffff', alpha=s_al, s=s_sz, zorder=1)

    # 2. Anillo de Signos del Zodiaco (0.84 a 1.0)
    for i, s in enumerate(ZODIAC_SIGNS):
        deg_s = i * 30.0
        deg_e = (i + 1) * 30.0
        degs = np.linspace(deg_s, deg_e, 35)
        rads = np.array([to_rad(d) for d in degs])
        if rads[-1] < rads[0]:
            rads = np.unwrap(rads)

        ax.fill_between(rads, 0.84, 1.0, color=s["color"], alpha=0.32, edgecolor='#d4af37', linewidth=1.4, zorder=2)
        mid_rad = to_rad(deg_s + 15.0)
        ax.text(mid_rad, 0.92, f"{s['glyph']}\n{s['name']}", ha='center', va='center',
                color='#ffffff', fontsize=10.5, fontweight='bold', zorder=3)

    # Círculos delimitadores dorados
    theta_f = np.linspace(0, 2 * np.pi, 300)
    ax.plot(theta_f, [1.0] * 300, color='#d4af37', linewidth=1.6, zorder=4)
    ax.plot(theta_f, [0.84] * 300, color='#d4af37', linewidth=1.4, zorder=4)
    ax.plot(theta_f, [0.60] * 300, color='#ffd700', linewidth=1.2, alpha=0.7, zorder=4)
    ax.plot(theta_f, [0.42] * 300, color='#718096', linewidth=0.8, linestyle=':', alpha=0.8, zorder=4)

    # 3. Líneas de Aspectos Natales en el centro (0.0 a 0.42)
    aspectos = natal.get("aspectos", [])
    planetas = natal["planetas"]
    for asp in aspectos:
        c1, c2 = asp["cuerpo1"], asp["cuerpo2"]
        if c1 in planetas and c2 in planetas:
            d1 = planetas[c1]["grado_absoluto"]
            d2 = planetas[c2]["grado_absoluto"]
            r1, r2 = to_rad(d1), to_rad(d2)

            t_int = np.linspace(0, 1, 30)
            c_rads = r1 + t_int * (r2 - r1)
            c_r = 0.42 * (1.0 - 0.70 * np.sin(np.pi * t_int))

            tipo = asp.get("tipo", "")
            if "tension" in tipo:
                c_line = "#ef4444" # Rojo rubí para cuadraturas y oposiciones
                lw = 2.0
                alpha = 0.65
            elif "fluidez" in tipo or "armonico" in tipo:
                c_line = "#38bdf8" # Azul zafiro brillante para trígonos y sextiles
                lw = 2.0
                alpha = 0.65
            else:
                c_line = "#fbbf24" # Oro
                lw = 1.6
                alpha = 0.50

            # Resplandor de la cuerda de aspecto
            ax.plot(c_rads, c_r, color=c_line, alpha=alpha * 0.4, linewidth=lw * 3.5, zorder=3)
            ax.plot(c_rads, c_r, color=c_line, alpha=alpha, linewidth=lw, zorder=4)

    # 4. Casas Natales (Cúspides 1 a 12)
    casas_deg = natal.get("casas_grados", [i * 30.0 for i in range(12)])
    for h in range(12):
        c_deg = casas_deg[h]
        c_next = casas_deg[(h + 1) % 12]
        r_c = to_rad(c_deg)

        es_eje = (h in [0, 3, 6, 9])
        col_c = "#ffd700" if es_eje else "#4a5568"
        lw_c = 2.6 if es_eje else 0.9
        ls_c = "-" if es_eje else "--"

        ax.plot([r_c, r_c], [0.42, 0.84], color=col_c, linewidth=lw_c, linestyle=ls_c, zorder=5)

        # Número de casa
        diff = (c_next - c_deg) % 360.0
        m_deg = (c_deg + diff / 2.0) % 360.0
        m_rad = to_rad(m_deg)
        ax.text(m_rad, 0.48, str(h + 1), ha='center', va='center',
                color='#f8fafc', fontsize=10.5, fontweight='bold',
                bbox=dict(boxstyle='circle,pad=0.25', facecolor='#090d18', edgecolor='#d4af37', linewidth=1.0, alpha=0.9),
                zorder=6)

    # 5. Planetas Natales como Joyas Celestiales
    p_sorted = sorted(planetas.items(), key=lambda x: x[1]["grado_absoluto"])
    for idx, (p_name, p_info) in enumerate(p_sorted):
        deg = p_info["grado_absoluto"]
        rad = to_rad(deg)
        style = PLANET_STYLES.get(p_name, {'glyph': p_name[:2], 'color': '#ffd700', 'glow': '#fbbf24', 'size': 16})

        # Alternar radio para evitar superposiciones si están muy pegados
        prev_deg = p_sorted[idx - 1][1]["grado_absoluto"] if idx > 0 else -999.0
        r_p = 0.65 if ((deg - prev_deg) % 360.0 < 12.0 and idx % 2 == 1) else 0.73

        # Resplandor exterior (glow)
        ax.scatter([rad], [r_p], color=style['glow'], s=380, alpha=0.35, zorder=7)
        ax.scatter([rad], [r_p], color=style['glow'], s=160, alpha=0.70, zorder=8)
        # Orbe central
        ax.scatter([rad], [r_p], color=style['color'], s=50, zorder=9)

        # Glifo grande y legible + grado
        ax.text(rad, r_p - 0.08, f"{style['glyph']} {p_info['grado_en_signo']}°", ha='center', va='center',
                color='#ffffff', fontsize=10.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.28', facecolor='#060a14', edgecolor=style['color'], linewidth=1.5, alpha=0.95),
                zorder=10)

    # 6. Marcador del Ascendente Natal (Izquierda a 180°)
    rad_asc = np.pi
    ax.plot([rad_asc, rad_asc], [0.42, 0.98], color='#ffd700', linewidth=3.5, zorder=11)
    ax.text(rad_asc, 1.04, "✦ ASC NATAL · ACUARIO ✦", ha='center', va='center',
            color='#ffd700', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#090d18', edgecolor='#ffd700', linewidth=1.8), zorder=12)

    # Título superior cinematográfico
    fig.text(0.5, 0.96, f"✦ CARTA NATAL · {sujeto.upper()} ✦",
             ha='center', va='center', color='#ffd700', fontsize=16, fontweight='bold')
    fig.text(0.5, 0.935, "Matriz Arquetípica Permanente · Aspectos y Planetas de Nacimiento",
             ha='center', va='center', color='#94a3b8', fontsize=11, fontweight='medium')

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor=bg_color, edgecolor='none')
    plt.close(fig)
    print(f"✅ Carta Natal Vibrante lista: {output_path}")


def renderizar_biwheel_vibrante(datos: Dict[str, Any], output_path: str, resaltar_portal: bool = False):
    """Renderiza la Bi-Wheel completa con anillo interior natal, anillo exterior de RS y aspectos anuales."""
    natal = datos["carta_natal"]
    rs = datos["revolucion_solar"]
    sujeto = natal["sujeto"]["nombre"]
    asc_deg = natal["angulos"]["Ascendente"]["grado_absoluto"]
    asc_rs_deg = rs["angulos_rs"]["Ascendente_RS"]["grado_absoluto"]

    fig, ax = plt.subplots(figsize=(14, 14), subplot_kw={'projection': 'polar'})
    bg_color = "#040711"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.axis('off')

    def to_rad(deg: float) -> float:
        rel = (deg - asc_deg + 180.0) % 360.0
        return np.radians(rel)

    # 1. Estrellas de fondo
    np.random.seed(42)
    n_stars = 260
    s_r = np.random.uniform(0.10, 0.98, n_stars)
    s_th = np.random.uniform(0, 2 * np.pi, n_stars)
    s_al = np.random.uniform(0.12, 0.65, n_stars)
    s_sz = np.random.uniform(3, 14, n_stars)
    ax.scatter(s_th, s_r, c='#ffffff', alpha=s_al, s=s_sz, zorder=1)

    # 2. Anillo de Signos (0.68 a 0.82)
    for i, s in enumerate(ZODIAC_SIGNS):
        deg_s = i * 30.0
        deg_e = (i + 1) * 30.0
        degs = np.linspace(deg_s, deg_e, 35)
        rads = np.array([to_rad(d) for d in degs])
        if rads[-1] < rads[0]:
            rads = np.unwrap(rads)

        ax.fill_between(rads, 0.68, 0.82, color=s["color"], alpha=0.30, edgecolor='#d4af37', linewidth=1.2, zorder=2)
        mid_rad = to_rad(deg_s + 15.0)
        ax.text(mid_rad, 0.75, f"{s['glyph']}", ha='center', va='center',
                color='#ffffff', fontsize=12, fontweight='bold', zorder=3)

    # Delimitadores de anillos
    theta_f = np.linspace(0, 2 * np.pi, 300)
    ax.plot(theta_f, [0.98] * 300, color='#00f2fe', linewidth=2.0, alpha=0.9, zorder=4) # Exterior RS
    ax.plot(theta_f, [0.82] * 300, color='#00f2fe', linewidth=1.2, linestyle='--', alpha=0.7, zorder=4)
    ax.plot(theta_f, [0.68] * 300, color='#ffd700', linewidth=1.5, zorder=4) # Anillo Natal
    ax.plot(theta_f, [0.46] * 300, color='#ffd700', linewidth=1.0, linestyle=':', alpha=0.6, zorder=4)
    ax.plot(theta_f, [0.30] * 300, color='#334155', linewidth=0.8, zorder=4)

    # 3. Resaltar Sector de Casa 9 Natal si resaltar_portal=True
    casas_deg = natal.get("casas_grados", [i * 30.0 for i in range(12)])
    c9_s = casas_deg[8]
    c9_e = casas_deg[9]
    diff_c9 = (c9_e - c9_s) % 360.0
    degs_c9 = np.linspace(c9_s, c9_s + diff_c9, 30)
    rads_c9 = np.array([to_rad(d) for d in degs_c9])
    if rads_c9[-1] < rads_c9[0]:
        rads_c9 = np.unwrap(rads_c9)

    if resaltar_portal:
        # Iluminar Casa 9 completa con resplandor dorado / cian
        ax.fill_between(rads_c9, 0.30, 0.98, color='#00f2fe', alpha=0.22, zorder=3)
        ax.fill_between(rads_c9, 0.30, 0.68, color='#ffd700', alpha=0.20, zorder=3)

    # 4. Aspectos Intercartas en el centro (0.0 a 0.30)
    aspectos_inter = rs.get("aspectos_intercartas", [])[:12]
    p_natal = natal["planetas"]
    p_rs = rs["planetas_rs"]

    for asp in aspectos_inter:
        c_rs = asp["cuerpo_rs"]
        c_nat = asp["cuerpo_natal"]
        if c_rs in p_rs and c_nat in p_natal:
            d_rs = p_rs[c_rs]["grado_absoluto"]
            d_nat = p_natal[c_nat]["grado_absoluto"]
            r_rs = to_rad(d_rs)
            r_nat = to_rad(d_nat)

            t_int = np.linspace(0, 1, 30)
            c_rads = r_rs + t_int * (r_nat - r_rs)
            c_r = 0.30 * (1.0 - 0.70 * np.sin(np.pi * t_int))

            c_line = asp.get("color", "#38bdf8")
            ax.plot(c_rads, c_r, color=c_line, alpha=0.25, linewidth=4.0, zorder=3)
            ax.plot(c_rads, c_r, color=c_line, alpha=0.85, linewidth=1.6, zorder=4)

    # 5. Cúspides y Números de Casa Natal
    for h in range(12):
        c_deg = casas_deg[h]
        c_next = casas_deg[(h + 1) % 12]
        r_c = to_rad(c_deg)
        es_c9 = (h == 8)
        col_c = '#00f2fe' if (es_c9 and resaltar_portal) else ('#ffd700' if h in [0, 3, 6, 9] else '#4a5568')
        lw_c = 3.2 if (es_c9 and resaltar_portal) else (2.0 if h in [0, 3, 6, 9] else 0.8)

        ax.plot([r_c, r_c], [0.30, 0.68], color=col_c, linewidth=lw_c, zorder=5)

        diff = (c_next - c_deg) % 360.0
        m_rad = to_rad((c_deg + diff / 2.0) % 360.0)
        c_num = '#00f2fe' if (es_c9 and resaltar_portal) else '#f8fafc'
        ax.text(m_rad, 0.38, str(h + 1), ha='center', va='center',
                color=c_num, fontsize=9.5, fontweight='bold',
                bbox=dict(boxstyle='circle,pad=0.2', facecolor='#090d18', edgecolor=col_c, linewidth=1.2, alpha=0.9),
                zorder=6)

    # 6. Planetas Natales (Anillo Interior: r = 0.54 / 0.62)
    p_nat_sorted = sorted(p_natal.items(), key=lambda x: x[1]["grado_absoluto"])
    for idx, (p_name, p_info) in enumerate(p_nat_sorted):
        deg = p_info["grado_absoluto"]
        rad = to_rad(deg)
        style = PLANET_STYLES.get(p_name, {'glyph': p_name[:2], 'color': '#ffd700', 'glow': '#fbbf24'})
        prev_deg = p_nat_sorted[idx - 1][1]["grado_absoluto"] if idx > 0 else -999.0
        r_p = 0.50 if ((deg - prev_deg) % 360.0 < 12.0 and idx % 2 == 1) else 0.58

        # Halos y orbe
        ax.scatter([rad], [r_p], color=style['glow'], s=220, alpha=0.35, zorder=7)
        ax.scatter([rad], [r_p], color=style['color'], s=40, zorder=8)
        ax.text(rad, r_p - 0.065, f"{style['glyph']} {p_info['grado_en_signo']}°", ha='center', va='center',
                color='#ffffff', fontsize=8.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#060a14', edgecolor=style['color'], linewidth=1.2, alpha=0.92),
                zorder=9)

    # 7. Planetas RS (Anillo Exterior: r = 0.90) en Cian Eléctrico
    p_rs_sorted = sorted(p_rs.items(), key=lambda x: x[1]["grado_absoluto"])
    for idx, (p_name, p_info) in enumerate(p_rs_sorted):
        deg = p_info["grado_absoluto"]
        rad = to_rad(deg)
        style = PLANET_STYLES.get(p_name, {'glyph': p_name[:2], 'color': '#00f2fe', 'glow': '#38bdf8'})
        prev_deg = p_rs_sorted[idx - 1][1]["grado_absoluto"] if idx > 0 else -999.0
        r_p = 0.86 if ((deg - prev_deg) % 360.0 < 12.0 and idx % 2 == 1) else 0.92

        ax.scatter([rad], [r_p], color='#00f2fe', s=260, alpha=0.35, zorder=7)
        ax.scatter([rad], [r_p], color='#00f2fe', s=45, zorder=8)
        ax.text(rad, r_p + 0.06, f"{style['glyph']} {p_info['grado_en_signo']}°", ha='center', va='center',
                color='#00f2fe', fontsize=8.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#060a14', edgecolor='#00f2fe', linewidth=1.4, alpha=0.92),
                zorder=9)

    # 8. Rayo Láser del Ascendente RS en Libra 14°21' aterrizando en Casa 9
    rad_asc_rs = to_rad(asc_rs_deg)
    ax.plot([rad_asc_rs, rad_asc_rs], [0.30, 0.98], color='#00f2fe', linewidth=3.5, zorder=10)
    ax.plot([rad_asc_rs, rad_asc_rs], [0.30, 0.98], color='#00f2fe', linewidth=12.0, alpha=0.30, zorder=9)
    ax.scatter([rad_asc_rs], [0.98], color='#ffffff', s=120, zorder=11)
    ax.text(rad_asc_rs, 1.04, "✦ ASC RS · LIBRA 14°21' ✦", ha='center', va='center',
            color='#00f2fe', fontsize=11.5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#090d18', edgecolor='#00f2fe', linewidth=1.8), zorder=12)

    # Título superior
    fig.text(0.5, 0.96, f"✦ RETORNO SOLAR 2026 · {sujeto.upper()} ✦",
             ha='center', va='center', color='#00f2fe', fontsize=16, fontweight='bold')
    fig.text(0.5, 0.935, "Bi-Wheel Cósmica · Anillo Natal Interior (Oro) ⟷ Tránsitos Anuales Exteriores (Cian)",
             ha='center', va='center', color='#94a3b8', fontsize=11, fontweight='medium')

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, facecolor=bg_color, edgecolor='none')
    plt.close(fig)
    print(f"✅ Bi-Wheel Vibrante lista: {output_path}")


if __name__ == "__main__":
    datos_path = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/datos_rs_tomás_2026.json")
    with open(datos_path, "r", encoding="utf-8") as f:
        datos = json.load(f)

    out_dir = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/ruedas_vibrantes")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("🎨 Renderizando Carta Natal Vibrante...")
    renderizar_carta_natal_vibrante(datos, str(out_dir / "carta_natal_vibrante.png"))

    print("🎨 Renderizando Bi-Wheel Vibrante...")
    renderizar_biwheel_vibrante(datos, str(out_dir / "biwheel_vibrante.png"), resaltar_portal=False)

    print("🎨 Renderizando Bi-Wheel con Portal Iluminado...")
    renderizar_biwheel_vibrante(datos, str(out_dir / "biwheel_portal_casa9.png"), resaltar_portal=True)
