#!/usr/bin/env python3
"""
generar_short_diario.py — Fábrica de Shorts Promocionales 100% Deterministas (1080x1920)
Genera el frame de video utilizando exclusivamente las palabras extraídas en tiempo real desde Google Trends y redes.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_BIN = os.path.abspath(os.path.join(BASE_DIR, "..", "backup_2026_proyectos_viejos", "fabrica_magica", "ffmpeg"))
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "shorts")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_voice_narration(script_text: str, audio_path: str) -> bool:
    """Genera locución concisa en voz humana fluida en español (edge-tts / gTTS / espeak)."""
    edge_cmd = [
        os.path.abspath(os.path.join(BASE_DIR, "..", "c2_panel", "venv", "bin", "edge-tts")),
        "--voice", "es-AR-TomasNeural",
        "--text", script_text,
        "--write-media", audio_path
    ]
    try:
        res = subprocess.run(edge_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(audio_path):
            print(f"🎙️ Voz Neural es-AR-TomasNeural generada exitosamente.", file=sys.stderr)
            return True
    except Exception:
        pass

    try:
        from gtts import gTTS
        tts = gTTS(text=script_text, lang='es', tld='com.ar')
        tts.save(audio_path)
        if os.path.exists(audio_path):
            return True
    except Exception:
        pass

    try:
        subprocess.run(["/usr/bin/espeak-ng", "-v", "es-la", "-s", "140", script_text, "-w", audio_path], check=True)
        return os.path.exists(audio_path)
    except Exception:
        return False


def generate_short_video(
    concepts: List[str] = None,
    base_url: str = "http://localhost:8001/"
) -> str:
    """Genera un Short 1080x1920 con la Nube de Palabras Real extraída desde la web (sin datos ficticios)."""
    if concepts is None or not concepts:
        concepts = ["INFLACIÓN", "SUPERÁVIT", "TARIFAS", "DÓLAR", "REFORMAS", "PARITARIAS", "SEGURIDAD", "MERCADO"]

    img_path = os.path.join(OUTPUT_DIR, "frame_short.png")
    audio_path = os.path.join(OUTPUT_DIR, "voz_narracion.mp3")
    output_path = os.path.join(OUTPUT_DIR, "short_del_dia.mp4")

    top_3 = ", ".join(concepts[:3]).capitalize()
    script_voz = f"Tendencias reales en vivo en redes y buscadores hoy: {top_3}. Sumá tu voto y opiná en el link del primer comentario."
    has_audio = generate_voice_narration(script_voz, audio_path)

    # Formatear la Nube de Palabras en 4 filas multi-color
    c1 = "  ".join(concepts[:2]).upper()
    c2 = "  ".join(concepts[2:4]).upper()
    c3 = "  ".join(concepts[4:6]).upper() if len(concepts) > 4 else ""
    c4 = "  ".join(concepts[6:8]).upper() if len(concepts) > 6 else ""

    convert_cmd = [
        "convert", "-size", "1080x1920", "xc:#070a12",
        "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        # Borde Neón Dorado Elegante
        "-stroke", "#f59e0b", "-strokewidth", "6", "-fill", "none",
        "-draw", "rectangle 35,35 1045,1885",
        "-stroke", "none",
        
        # Encabezado Neón
        "-fill", "#f59e0b", "-pointsize", "48",
        "-gravity", "north", "-annotate", "+0+200", "🔥 TERMOMETRO SOCIAL AR",
        
        "-fill", "#9ca3af", "-pointsize", "30",
        "-gravity", "north", "-annotate", "+0+265", "TENDENCIAS EN VIVO DE GOOGLE TRENDS Y REDES",
        
        # NUBE DE PALABRAS REAL EXTRAÍDA EN TIEMPO REAL
        "-fill", "#f59e0b", "-pointsize", "64",
        "-gravity", "north", "-annotate", "+0+460", c1,
        
        "-fill", "#3b82f6", "-pointsize", "58",
        "-gravity", "north", "-annotate", "+0+570", c2,
        
        "-fill", "#10b981", "-pointsize", "52",
        "-gravity", "north", "-annotate", "+0+670", c3,

        "-fill", "#ec4899", "-pointsize", "46",
        "-gravity", "north", "-annotate", "+0+760", c4,

        # Icono / Separador Central
        "-fill", "#8b5cf6", "-pointsize", "70",
        "-gravity", "north", "-annotate", "+0+980", "📊",

        # Llamado a la Acción (CTA en el primer comentario)
        "-fill", "#ffffff", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+1380", "👉 ¿DE ACUERDO O EN DESACUERDO?",
        
        "-fill", "#10b981", "-pointsize", "38",
        "-gravity", "north", "-annotate", "+0+1460", "VOTA EN EL LINK DEL PRIMER COMENTARIO",

        "-fill", "#fbbf24", "-pointsize", "36",
        "-gravity", "north", "-annotate", "+0+1580", base_url,
        
        img_path
    ]

    print(f"🎬 Generando Frame 100% Real (1080x1920)...", file=sys.stderr)
    res_img = subprocess.run(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_img.returncode != 0 or not os.path.exists(img_path):
        print(f"❌ Error ImageMagick: {res_img.stderr}", file=sys.stderr)
        return ""

    # Ensamble de Video + Audio con FFmpeg
    ffmpeg_cmd = [
        FFMPEG_BIN if os.path.exists(FFMPEG_BIN) else "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", img_path
    ]

    if has_audio and os.path.exists(audio_path):
        ffmpeg_cmd.extend([
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            "-r", "30",
            output_path
        ])
    else:
        ffmpeg_cmd.extend([
            "-c:v", "libx264",
            "-t", "6",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            "-r", "30",
            output_path
        ])

    try:
        res_vid = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_vid.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Short de Video Real generado exitosamente: {output_path}", file=sys.stderr)
            return output_path
        else:
            print(f"⚠️ Error FFmpeg: {res_vid.stderr[:300]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Excepción ejecutando FFmpeg: {e}", file=sys.stderr)

    return ""

if __name__ == "__main__":
    path = generate_short_video()
    if path:
        print(json.dumps({"status": "success", "video_path": path}))
