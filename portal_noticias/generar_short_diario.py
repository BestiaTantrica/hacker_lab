#!/usr/bin/env python3
"""
generar_short_diario.py — Fábrica de Shorts Promocionales con NUBE DE PALABRAS ENTERA + MINI-ENCUESTA
Genera un video vertical 1080x1920 con la nube completa de conceptos, la encuesta interactiva y voz neural.
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
    """Genera locución en voz humana fluida en español (edge-tts / gTTS / espeak)."""
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
    poll_question: str = "¿Cuál es tu prioridad principal ante el nuevo rumbo económico?",
    poll_options: List[str] = None,
    base_url: str = "http://localhost:8001/"
) -> str:
    """Genera un Short promocional 1080x1920 con la NUBE DE PALABRAS ENTERA y MINI-ENCUESTA."""
    if concepts is None or not concepts:
        concepts = ["LIBERTAD", "SUPERÁVIT", "TARIFAS", "INFLACIÓN", "DÓLAR", "PROPIEDAD", "PARITARIAS", "DESREGULACIÓN"]
    
    if poll_options is None or not poll_options:
        poll_options = [
            "1. Apoyar el superávit y fin de la inflación",
            "2. Controlar tarifas y costo de servicios",
            "3. Reducir impuestos y promover empleo"
        ]

    img_path = os.path.join(OUTPUT_DIR, "frame_short.png")
    audio_path = os.path.join(OUTPUT_DIR, "voz_narracion.mp3")
    output_path = os.path.join(OUTPUT_DIR, "short_del_dia.mp4")

    # Script de locución relatando la nube de palabras y la encuesta
    concepts_str = ", ".join(concepts[:5])
    script_voz = f"¡Medición en tiempo real! Esta es la nube de palabras del día en redes: {concepts_str}. Entrá a votar en la encuesta interactiva en {base_url} y sumá tu voto al termómetro directo."
    has_audio = generate_voice_narration(script_voz, audio_path)

    # Formatear la consigna en líneas limpias
    words = poll_question.split()
    line1 = " ".join(words[:5]) if len(words) >= 5 else poll_question
    line2 = " ".join(words[5:10]) if len(words) >= 10 else (" ".join(words[5:]) if len(words) > 5 else "")
    line3 = " ".join(words[10:]) if len(words) > 10 else ""

    # Formatear la Nube de Palabras en 3 filas visuales con ImageMagick
    c_row1 = "  ".join(concepts[:3]).upper()
    c_row2 = "  ".join(concepts[3:6]).upper()
    c_row3 = "  ".join(concepts[6:9]).upper() if len(concepts) > 6 else ""

    opt1 = poll_options[0] if len(poll_options) > 0 else "1. Apoyo al rumbo económico"
    opt2 = poll_options[1] if len(poll_options) > 1 else "2. Foco en tarifas y servicios"
    opt3 = poll_options[2] if len(poll_options) > 2 else "3. Reducción impositiva"

    convert_cmd = [
        "convert",
        "-size", "1080x1920",
        "xc:#0a0d14",
        "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        # Borde Neón Dorado
        "-stroke", "#f59e0b", "-strokewidth", "8", "-fill", "none",
        "-draw", "rectangle 40,40 1040,1880",
        "-stroke", "none",
        
        # Encabezado Comercial
        "-fill", "#f59e0b", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+120", "🔥 TERMOMETRO SOCIAL & NUBE DEL DIA",
        
        "-fill", "#9ca3af", "-pointsize", "30",
        "-gravity", "north", "-annotate", "+0+175", "CONCEPTOS MAS REPETIDOS EN REDES HOY",
        
        # NUBE DE PALABRAS ENTERA EN 3 FILAS MULTI-COLOR
        "-fill", "#f59e0b", "-pointsize", "56",
        "-gravity", "north", "-annotate", "+0+260", c_row1,
        
        "-fill", "#3b82f6", "-pointsize", "52",
        "-gravity", "north", "-annotate", "+0+330", c_row2,
        
        "-fill", "#10b981", "-pointsize", "48",
        "-gravity", "north", "-annotate", "+0+400", c_row3,
        
        # Línea divisoria
        "-stroke", "#ffffff", "-strokewidth", "2",
        "-draw", "line 100,480 980,480",
        "-stroke", "none",

        # Caja de la Pregunta / Encuesta
        "-fill", "#ec4899", "-pointsize", "38",
        "-gravity", "north", "-annotate", "+0+530", "📊 MINI ENCUESTA INTERACTIVA:",
        
        "-fill", "#ffffff", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+610", line1,
        "-gravity", "north", "-annotate", "+0+670", line2,
        "-gravity", "north", "-annotate", "+0+730", line3,
        
        # Opciones de Voto Visuales
        "-fill", "#10b981", "-pointsize", "34",
        "-gravity", "north", "-annotate", "+0+880", opt1[:55],
        
        "-fill", "#f59e0b", "-pointsize", "34",
        "-gravity", "north", "-annotate", "+0+960", opt2[:55],
        
        "-fill", "#f43f5e", "-pointsize", "34",
        "-gravity", "north", "-annotate", "+0+1040", opt3[:55],
        
        # Llamado a la Acción (CTA y Redirección a la Web)
        "-fill", "#ffffff", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+1420", "👇 SUMA TU VOTO Y VISTA RESULTADOS:",
        
        "-fill", "#fbbf24", "-pointsize", "48",
        "-gravity", "north", "-annotate", "+0+1520", base_url,
        
        img_path
    ]

    print(f"🎬 Generando Frame con Nube de Palabras Completa (1080x1920)...", file=sys.stderr)
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
            "-t", "10",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            "-r", "30",
            output_path
        ])

    try:
        res_vid = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_vid.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Short de Video con Nube Completa generado: {output_path}", file=sys.stderr)
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
