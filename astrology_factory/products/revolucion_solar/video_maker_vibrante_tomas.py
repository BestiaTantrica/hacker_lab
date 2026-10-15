#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video_maker_vibrante_tomas.py
─────────────────────────────────────────────────────────────────────────────
Generador Maestro del Video Capítulo 1 para Tomás:
  - Acto 1: Carta Natal Vibrante (Cromática, aspectos visibles en el centro, cámara lenta).
  - Transición Cósmica: Vórtice / Espiral 3D del tiempo (1982 -> 2026).
  - Acto 2: Acoplamiento Bi-Wheel (Rueda doble, aspectos de activación, rayo en Libra).
  - Acto 3: Zoom Dinámico Continuo sobre Casa 9 (Sin borrar la carta, badges flotantes minimalistas).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path("/home/LAB/astrology_factory/products/revolucion_solar")
RUEDAS_DIR = BASE_DIR / "output_tomas" / "ruedas_vibrantes"
OUTPUT_DIR = BASE_DIR / "output_tomas" / "capitulo_1_vibrante"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AUDIO_DIR = BASE_DIR / "output_tomas" / "capitulo_1_produccion"
AUDIO1 = str(AUDIO_DIR / "audio_acto1.mp3")
AUDIO2 = str(AUDIO_DIR / "audio_acto2.mp3")
AUDIO3 = str(AUDIO_DIR / "audio_acto3.mp3")

IMG_NATAL = str(RUEDAS_DIR / "carta_natal_vibrante.png")
IMG_BIWHEEL = str(RUEDAS_DIR / "biwheel_vibrante.png")
IMG_PORTAL = str(RUEDAS_DIR / "biwheel_portal_casa9.png")
VIDEO_ESPIRAL = str(BASE_DIR / "test_camila" / "video_test_zoom" / "espiral_3d_test.mp4")


def obtener_duracion(media_path: str) -> float:
    """Obtiene la duración exacta en segundos."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        media_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def generar_clip_acto1(duracion: float, out_path: str):
    """
    Acto 1: Carta Natal Vibrante en 1920x1080 con sutil cámara lenta (zoom 1.0 a 1.08).
    Mantiene la carta fija y majestuosa para que el consultante reconozca su mapa.
    """
    # Escalar imagen cuadrada 2800x2800 a 1080p centrada con fondo oscuro y zoom sutil
    vf = (
        f"scale=1080:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#040711,"
        f"zoompan=z='min(zoom+0.0003,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=25*{duracion}:s=1920x1080:fps=25"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMG_NATAL,
        "-i", AUDIO1,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duracion),
        out_path
    ]
    subprocess.run(cmd, check=True)


def generar_clip_espiral(duracion_audio2: float, out_path: str):
    """
    Transición Cósmica + Acto 2:
    Usa el espiral 3D durante los primeros 4 segundos (como puente temporal),
    y luego funde a la Bi-Wheel acoplada durante el resto del audio 2.
    """
    t_espiral = 4.0
    t_biwheel = max(1.0, duracion_audio2 - t_espiral)

    # 1. Segmento Espiral (4s)
    seg_espiral = str(OUTPUT_DIR / "temp_espiral.mp4")
    cmd_esp = [
        "ffmpeg", "-y",
        "-i", VIDEO_ESPIRAL,
        "-t", str(t_espiral),
        "-vf", "scale=1920:1080",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an",
        seg_espiral
    ]
    subprocess.run(cmd_esp, check=True)

    # 2. Segmento Bi-Wheel Acoplada (resto del audio)
    seg_biw = str(OUTPUT_DIR / "temp_biwheel.mp4")
    vf_biw = (
        f"scale=1080:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#040711,"
        f"zoompan=z='min(zoom+0.0003,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=25*{t_biwheel}:s=1920x1080:fps=25"
    )
    cmd_biw = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMG_BIWHEEL,
        "-vf", vf_biw,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-t", str(t_biwheel),
        seg_biw
    ]
    subprocess.run(cmd_biw, check=True)

    # 3. Concatenar y montar Audio 2
    concat_list = OUTPUT_DIR / "temp_list_acto2.txt"
    with open(concat_list, "w") as f:
        f.write(f"file '{seg_espiral}'\n")
        f.write(f"file '{seg_biw}'\n")

    cmd_merge = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-i", AUDIO2,
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(duracion_audio2),
        out_path
    ]
    subprocess.run(cmd_merge, check=True)


def generar_clip_acto3_zoom(duracion: float, out_path: str):
    """
    Acto 3: Zoom continuo y fluido hacia Casa 9 y el Ascendente en Libra.
    ¡LA CARTA NO SE BORRA! La cámara se acerca suavemente de 1.0x a 1.9x enfocando Casa 9.
    Badges flotantes animados con subtítulos ASS profesionales y fade-in/out.
    """
    ass_path = OUTPUT_DIR / "badges_acto3.ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleCyan, DejaVu Sans, 26, &H00FEF200, &H00000000, &H00000000, &H95060A14, 1, 0, 0, 0, 100, 100, 1, 0, 3, 6, 0, 2, 40, 40, 95, 1
Style: SubtitleWhite, DejaVu Sans, 17, &H00F0E8E2, &H00000000, &H00000000, &H95060A14, 0, 0, 0, 0, 100, 100, 0, 0, 3, 5, 0, 2, 40, 40, 58, 1
Style: TitleGold, DejaVu Sans, 26, &H0000D7FF, &H00000000, &H00000000, &H95060A14, 1, 0, 0, 0, 100, 100, 1, 0, 3, 6, 0, 2, 40, 40, 95, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:02.00,0:00:18.00,TitleCyan,,0,0,0,,{\\fad(400,400)}✦ ASCENDENTE ANUAL: LIBRA 14° 21' ✦
Dialogue: 0,0:00:02.00,0:00:18.00,SubtitleWhite,,0,0,0,,{\\fad(400,400)}El portal del año: el signo del otro, del pacto y la balanza
Dialogue: 0,0:00:19.00,0:00:42.00,TitleGold,,0,0,0,,{\\fad(400,400)}✦ CASA 9 NATAL: LA LEY Y EL HORIZONTE ✦
Dialogue: 0,0:00:19.00,0:00:42.00,SubtitleWhite,,0,0,0,,{\\fad(400,400)}Nudos fundacionales activos: Saturno 18° · Plutón 25° · Júpiter 7°
Dialogue: 0,0:00:43.00,0:01:12.00,TitleCyan,,0,0,0,,{\\fad(400,400)}✦ LA EXIGENCIA DEL RETORNO ✦
Dialogue: 0,0:00:43.00,0:01:12.00,SubtitleWhite,,0,0,0,,{\\fad(400,400)}Poner firma, negociar y ceder terreno · El horizonte se alcanza acompañado
""")

    # Zoom hacia Casa 9 (cuadrante superior derecho)
    zoom_expr = "min(1.0 + 0.9 * (on/(25*12)), 1.9)"
    x_expr = "iw/2 - (iw/zoom/2) + (zoom-1.0)/0.9 * (1180 - iw/2)"
    y_expr = "ih/2 - (ih/zoom/2) + (zoom-1.0)/0.9 * (340 - ih/2)"

    vf = (
        f"scale=1080:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#040711,"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d=25*{duracion}:s=1920x1080:fps=25,"
        f"subtitles={str(ass_path)}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", IMG_PORTAL,
        "-i", AUDIO3,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duracion),
        out_path
    ]
    subprocess.run(cmd, check=True)


def ensamblar_video_maestro():
    print("🚀 Ensamblando Video Maestro Vibrante para Tomás...")

    d1 = obtener_duracion(AUDIO1)
    d2 = obtener_duracion(AUDIO2)
    d3 = obtener_duracion(AUDIO3)

    v1 = str(OUTPUT_DIR / "clip1_natal.mp4")
    v2 = str(OUTPUT_DIR / "clip2_espiral_biwheel.mp4")
    v3 = str(OUTPUT_DIR / "clip3_zoom_casa9.mp4")

    print(f"🎬 Generando Clip 1 (Carta Natal Base con Aspectos Vibrantes)... {d1:.1f}s")
    generar_clip_acto1(d1, v1)

    print(f"🎬 Generando Clip 2 (Espiral Temporal 3D + Bi-Wheel)... {d2:.1f}s")
    generar_clip_espiral(d2, v2)

    print(f"🎬 Generando Clip 3 (Zoom Continuo a Casa 9 + Badges Animados)... {d3:.1f}s")
    generar_clip_acto3_zoom(d3, v3)

    # Concatenación final
    concat_list = OUTPUT_DIR / "master_concat_list.txt"
    with open(concat_list, "w") as f:
        f.write(f"file '{v1}'\n")
        f.write(f"file '{v2}'\n")
        f.write(f"file '{v3}'\n")

    master_final = OUTPUT_DIR / "capitulo_1_vibrante_tomas.mp4"
    print(f"🎞️ Concatenando Video Maestro: {master_final}...")
    cmd_cat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(master_final)
    ]
    subprocess.run(cmd_cat, check=True)

    print("\n" + "=" * 60)
    print(f"✨ ¡VIDEO MAESTRO VIBRANTE GENERADO EXITOSAMENTE!")
    print(f"📁 Archivo: {master_final}")
    print("=" * 60)


if __name__ == "__main__":
    ensamblar_video_maestro()
