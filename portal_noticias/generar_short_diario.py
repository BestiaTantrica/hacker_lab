#!/usr/bin/env python3
"""
generar_short_diario.py — Fábrica de Shorts Automáticos con Narración de Voz en Español (TTS) y Video Vertical 1080x1920
Renderiza videos virales con voz en off automatizada e imagen de alto impacto.
"""

import os
import sys
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_BIN = os.path.abspath(os.path.join(BASE_DIR, "..", "backup_2026_proyectos_viejos", "fabrica_magica", "ffmpeg"))
ESPEAK_BIN = "/usr/bin/espeak-ng"
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "shorts")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_short_video(word_topic: str = "PRESUPUESTO", poll_question: str = "¿El rumbo fiscal vale la pena o el costo social es excesivo?") -> str:
    """Genera un Short vertical (1080x1920) de 8-10s con narración en voz en español y audio AAC."""
    img_path = os.path.join(OUTPUT_DIR, "frame_short.png")
    audio_path = os.path.join(OUTPUT_DIR, "voz_narracion.wav")
    output_path = os.path.join(OUTPUT_DIR, "short_del_dia.mp4")

    clean_word = word_topic.upper()
    
    # 1. Narración en Voz con espeak-ng (Español)
    script_voz = f"Atención Argentina. El tema más hablado del día es {clean_word}. Entrá ya a votar en el termómetro social."
    
    print(f"🎙️ Generando narración de voz en español...", file=sys.stderr)
    try:
        subprocess.run([ESPEAK_BIN, "-v", "es", "-s", "150", script_voz, "-w", audio_path], check=True)
    except Exception as e:
        print(f"⚠️ Warning generando voz: {e}", file=sys.stderr)
        audio_path = ""

    # 2. Formatear la pregunta en 2-3 líneas cortas para legibilidad total
    words = poll_question.split()
    line1 = " ".join(words[:4]) if len(words) >= 4 else poll_question
    line2 = " ".join(words[4:9]) if len(words) >= 9 else (" ".join(words[4:]) if len(words) > 4 else "")
    line3 = " ".join(words[9:]) if len(words) > 9 else ""

    # 3. Crear Frame de Alto Impacto con ImageMagick (1080x1920)
    convert_cmd = [
        "convert",
        "-size", "1080x1920",
        "xc:#070a12",
        "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        # Encabezado
        "-fill", "#3b82f6", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+220", "🔥 TEMA MAS HABLADO DEL DIA",
        
        # Tema Principal (Gigante Neón)
        "-fill", "#ffffff", "-pointsize", "95",
        "-gravity", "north", "-annotate", "+0+340", clean_word,
        
        # Consigna / Pregunta en Líneas Limpias
        "-fill", "#f3f4f6", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+620", line1,
        "-gravity", "north", "-annotate", "+0+690", line2,
        "-gravity", "north", "-annotate", "+0+760", line3,
        
        # Llamado a la Acción (CTA)
        "-fill", "#10b981", "-pointsize", "46",
        "-gravity", "north", "-annotate", "+0+1280", "📊 VOTA EN EL TERMOMETRO SOCIAL",
        
        "-fill", "#f59e0b", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+1400", "http://localhost:8001/",
        
        img_path
    ]

    print(f"🎬 Renders de imagen (1080x1920)...", file=sys.stderr)
    res_img = subprocess.run(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_img.returncode != 0 or not os.path.exists(img_path):
        print(f"❌ Error ImageMagick: {res_img.stderr}", file=sys.stderr)
        return ""

    # 4. Ensamble de Video + Audio de Voz con FFmpeg
    ffmpeg_cmd = [
        FFMPEG_BIN if os.path.exists(FFMPEG_BIN) else "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", img_path
    ]

    if audio_path and os.path.exists(audio_path):
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
            print(f"✅ Short de Video con Voz Narrada generado exitosamente: {output_path}", file=sys.stderr)
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
