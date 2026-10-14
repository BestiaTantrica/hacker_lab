#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
animador_espiral_3d.py
─────────────────────────────────────────────────────────────────────────────
Generador de la Espiral Temporal 3D ("Tirabuzón de Retornos Solares")
A costo cero ($0), puramente en Python con NumPy, Matplotlib 3D y FFmpeg.

Concepto Astrológico:
- Z = 0: Carta Natal (El origen, la raíz psicológica inmutable, en oro #ffd700).
- Eje Z ascendente: El paso del tiempo (hélice cósmica con anillos anuales).
- Z = Top: Revolución Solar del año actual (en cian eléctrico #00f2fe).
- Una estela de partículas y luz asciende en hiperlapso por la espiral,
  mostrando cómo el retorno solar de este año se apoya en toda la historia de vida.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image


def generar_espiral_temporal_3d(
    nombre_consultante: str,
    anio_nacimiento: int,
    anio_rs: int,
    output_mp4: str,
    fps: int = 25,
    duracion_seg: float = 4.5,
    signo_sol: str = "Aries",
    signo_asc_rs: str = "Leo"
) -> str:
    """
    Renderiza la secuencia cinemática 3D del tirabuzón temporal y la compila en MP4.
    """
    total_frames = int(duracion_seg * fps)
    edad_anios = max(1, anio_rs - anio_nacimiento)
    vueltas_espiral = min(8.0, max(3.5, edad_anios * 0.25))

    out_path = Path(output_mp4)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Coordenadas paramétricas de la espiral de tiempo
    t_vals = np.linspace(0, 1, 400)
    theta = 2.0 * np.pi * vueltas_espiral * t_vals
    radio = 1.0 + 0.15 * np.sin(np.pi * t_vals)
    x_helix = radio * np.cos(theta)
    y_helix = radio * np.sin(theta)
    z_helix = t_vals * 2.2 # Altura vertical

    # Anillos intermedios (cada retorno solar pasado)
    num_anillos = min(edad_anios, 12)
    t_rings = np.linspace(0.08, 0.92, num_anillos)
    ring_points = []
    ang_circ = np.linspace(0, 2 * np.pi, 80)
    for tr in t_rings:
        r_ring = 1.0 + 0.15 * np.sin(np.pi * tr)
        xr = r_ring * np.cos(ang_circ)
        yr = r_ring * np.sin(ang_circ)
        zr = np.full_like(ang_circ, tr * 2.2)
        ring_points.append((xr, yr, zr, tr))

    # Anillo Base Natal (Z = 0)
    x_natal = 1.05 * np.cos(ang_circ)
    y_natal = 1.05 * np.sin(ang_circ)
    z_natal = np.zeros_like(ang_circ)

    # Anillo Cúspide RS (Z = 2.2)
    x_rs = 1.08 * np.cos(ang_circ)
    y_rs = 1.08 * np.sin(ang_circ)
    z_rs = np.full_like(ang_circ, 2.2)

    # Estrellas de fondo 3D
    np.random.seed(42)
    n_stars = 250
    stars_x = np.random.uniform(-3.5, 3.5, n_stars)
    stars_y = np.random.uniform(-3.5, 3.5, n_stars)
    stars_z = np.random.uniform(-0.8, 3.0, n_stars)
    stars_s = np.random.uniform(0.5, 3.0, n_stars)
    stars_alpha = np.random.uniform(0.2, 0.75, n_stars)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        print(f"🌀 Renderizando Espiral 3D ({total_frames} frames)...")

        for f_idx in range(total_frames):
            prog = f_idx / float(total_frames - 1) # 0.0 a 1.0

            # Dinámica de Cámara:
            # Comienza en plano general angular, asciende y orbita hacia la cima
            elev = 26.0 + 32.0 * (prog ** 1.5)
            azim = -65.0 + 130.0 * (prog ** 0.85)

            fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
            ax = fig.add_subplot(111, projection='3d')
            bg_color = "#05070f"
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

            # Ocultar rejilla y ejes técnicos para estética pura de espacio
            ax.grid(False)
            ax.set_axis_off()
            ax.set_box_aspect([1.0, 1.0, 1.1])

            # 1. Fondo de Estrellas 3D
            ax.scatter(stars_x, stars_y, stars_z, s=stars_s, color="#ffffff", alpha=stars_alpha, depthshade=False)

            # 2. Base Natal (Z = 0)
            ax.plot(x_natal, y_natal, z_natal, color='#ffd700', linewidth=3.2, alpha=0.9, zorder=5)
            ax.plot(x_natal, y_natal, z_natal, color='#ffd700', linewidth=10.0, alpha=0.25, zorder=4)
            # Nodos planetarios dorados en la base
            for p_deg in [0, 60, 120, 180, 240, 300]:
                rad_p = np.radians(p_deg)
                ax.scatter([1.05 * np.cos(rad_p)], [1.05 * np.sin(rad_p)], [0.0],
                           color='#ffd700', s=45, alpha=0.95, zorder=6)

            # 3. Anillos Intermedios (Pasado / Tiempo acumulado)
            for xr, yr, zr, tr in ring_points:
                # Se iluminan a medida que el pulso asciende
                alpha_ring = 0.15 + 0.35 * max(0.0, 1.0 - abs(prog - tr) * 3.5)
                lw_ring = 1.0 if prog < tr else 1.5
                color_ring = "#3a4a6b" if prog < tr else "#60a5fa"
                ax.plot(xr, yr, zr, color=color_ring, linewidth=lw_ring, alpha=alpha_ring, zorder=3)

            # 4. Hélice del Tirabuzón (Curva de tiempo)
            # Dibujamos la espiral base en azul oscuro
            ax.plot(x_helix, y_helix, z_helix, color='#1e293b', linewidth=1.5, alpha=0.45, zorder=2)

            # Haz de luz activo (crece desde Z=0 hasta la posición actual según prog)
            idx_active = int(prog * (len(t_vals) - 1))
            if idx_active > 1:
                # Cola luminosa
                ax.plot(x_helix[:idx_active+1], y_helix[:idx_active+1], z_helix[:idx_active+1],
                        color='#00f2fe', linewidth=3.5, alpha=0.95, zorder=7)
                ax.plot(x_helix[:idx_active+1], y_helix[:idx_active+1], z_helix[:idx_active+1],
                        color='#00ffff', linewidth=9.0, alpha=0.35, zorder=6)

                # Cabeza de cometa / pulso cósmico
                head_x = x_helix[idx_active]
                head_y = y_helix[idx_active]
                head_z = z_helix[idx_active]
                ax.scatter([head_x], [head_y], [head_z], color='#ffffff', s=160, alpha=1.0, zorder=9)
                ax.scatter([head_x], [head_y], [head_z], color='#00f2fe', s=450, alpha=0.55, zorder=8)

            # 5. Cúspide de la Revolución Solar (Z = 2.2)
            # A medida que el pulso se acerca a la cima, el anillo RS se enciende intensamente
            alpha_rs = 0.25 + 0.75 * max(0.0, min(1.0, (prog - 0.4) * 1.8))
            lw_rs = 2.0 + 2.5 * max(0.0, min(1.0, (prog - 0.5) * 2.0))
            ax.plot(x_rs, y_rs, z_rs, color='#00f2fe', linewidth=lw_rs, alpha=alpha_rs, zorder=8)
            ax.plot(x_rs, y_rs, z_rs, color='#00ffff', linewidth=lw_rs * 3.2, alpha=alpha_rs * 0.35, zorder=7)

            # Nodos planetarios de la RS
            for p_deg in [30, 90, 150, 210, 270, 330]:
                rad_p = np.radians(p_deg)
                ax.scatter([1.08 * np.cos(rad_p)], [1.08 * np.sin(rad_p)], [2.2],
                           color='#00f2fe', s=55 * alpha_rs, alpha=alpha_rs, zorder=9)

            # 6. Eje Central de Alineación Cósmica
            ax.plot([0, 0], [0, 0], [-0.1, 2.3], color='#ffffff', linewidth=1.2, linestyle=':', alpha=0.25, zorder=1)

            # 7. Textos y Badges Flotantes en el Lienzo
            # Overlay 2D en pantalla
            fig.text(0.5, 0.94, f"✦ LÍNEA TEMPORAL: {anio_nacimiento} ➔ {anio_rs} ✦",
                     ha='center', va='center', color='#00f2fe', fontsize=16, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.4', facecolor='#090d1a', edgecolor='#00f2fe', linewidth=1.2, alpha=0.9))

            subt = f"{nombre_consultante.upper()} · DE LA RAÍZ NATAL AL RETORNO SOLAR ANUAL ({edad_anios} AÑOS DE CICLO)"
            fig.text(0.5, 0.895, subt, ha='center', va='center', color='#94a3b8', fontsize=11, fontweight='medium')

            # Badge inferior izquierdo: Semilla Natal
            fig.text(0.08, 0.12, f"● BASE: CARTA NATAL ({anio_nacimiento})\n  ADN y Matriz de Origen\n  Sol en {signo_sol}",
                     color='#ffd700', fontsize=10.5, fontweight='bold', linespacing=1.4,
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='#0b111e', edgecolor='#ffd700', linewidth=1.0, alpha=0.85))

            # Badge inferior derecho: Cima Revolución Solar
            fig.text(0.92, 0.12, f"● CIMA: REVOLUCIÓN SOLAR ({anio_rs})\n  El Retorno en {edad_anios} años\n  Ascendente en {signo_asc_rs}",
                     color='#00f2fe', fontsize=10.5, fontweight='bold', linespacing=1.4, ha='right',
                     bbox=dict(boxstyle='round,pad=0.5', facecolor='#0b111e', edgecolor='#00f2fe', linewidth=1.0, alpha=0.85))

            # Configurar límites y vista de cámara
            ax.set_xlim([-1.8, 1.8])
            ax.set_ylim([-1.8, 1.8])
            ax.set_zlim([-0.4, 2.5])
            ax.view_init(elev=elev, azim=azim)

            plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
            frame_file = temp_dir_path / f"frame_{f_idx:04d}.png"
            plt.savefig(str(frame_file), dpi=100, facecolor=bg_color, edgecolor='none')
            plt.close(fig)

        # Compilar en MP4 con FFmpeg ultrafast
        print(f"🎬 Compilando MP4 de la Espiral 3D con FFmpeg en {out_path.name}...")
        cmd_ffmpeg = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(temp_dir_path / "frame_%04d.png"),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            str(out_path)
        ]
        res = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Error compilando video de la espiral 3D:\n{res.stderr[-400:]}")

    print(f"✅ Espiral Temporal 3D generada con éxito: {out_path}")
    return str(out_path)


if __name__ == "__main__":
    test_out = "/home/LAB/astrology_factory/products/revolucion_solar/test_camila/video_test_zoom/espiral_3d_test.mp4"
    generar_espiral_temporal_3d(
        nombre_consultante="Camila",
        anio_nacimiento=1995,
        anio_rs=2026,
        output_mp4=test_out,
        fps=25,
        duracion_seg=4.0,
        signo_sol="Tauro",
        signo_asc_rs="Leo"
    )
