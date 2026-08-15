#!/usr/bin/env python3
"""
generar_short_diario.py — Fábrica de Shorts Automáticos de Video Vertical (1080x1920 MP4)
Formateo y empaquetado visual limpio sin textos cortados ni superpuestos.
"""

import os
import sys
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_BIN = os.path.abspath(os.path.join(BASE_DIR, "..", "backup_2026_proyectos_viejos", "fabrica_magica", "ffmpeg"))
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "shorts")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_short_video(word_topic: str = "PRESUPUESTO Y TARIFAS", poll_question: str = "¿El rumbo fiscal vale la pena o el costo social es excesivo?") -> str:
    """Genera un Short vertical (1080x1920) de 10s listo para YouTube Shorts/TikTok."""
    img_path = os.path.join(OUTPUT_DIR, "frame_short.png")
    output_path = os.path.join(OUTPUT_DIR, "short_del_dia.mp4")

    clean_word = word_topic.upper()
    
    # Formatear la pregunta en 2 líneas cortas para evitar cortes visuales
    words_q = poll_question.split()
    mid = len(words_q) // 2
    q_line1 = " ".join(words_q[:mid])
    q_line2 = " ".join(words_q[mid:])

    convert_cmd = [
        "convert",
        "-size", "1080x1920",
        "xc:#0b0f19",
        "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        "-fill", "#3b82f6", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+260", "TEMA MAS HABLADO DEL DIA",
        
        "-fill", "#ffffff", "-pointsize", "85",
        "-gravity", "north", "-annotate", "+0+380", clean_word,
        
        "-fill", "#9ca3af", "-pointsize", "36",
        "-gravity", "north", "-annotate", "+0+620", q_line1,
        "-gravity", "north", "-annotate", "+0+680", q_line2,
        
        "-fill", "#10b981", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+1300", "🔥 VOTA EN EL TERMOMETRO SOCIAL",
        
        "-fill", "#f59e0b", "-pointsize", "40",
        "-gravity", "north", "-annotate", "+0+1410", "http://localhost:8001/",
        
        img_path
    ]

    print(f"🎬 Generando imagen base (1080x1920) formateada para Short...", file=sys.stderr)
    try:
        res_img = subprocess.run(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_img.returncode != 0 or not os.path.exists(img_path):
            print(f"⚠️ Error ImageMagick: {res_img.stderr}", file=sys.stderr)
            return ""
            
        ffmpeg_cmd = [
            FFMPEG_BIN if os.path.exists(FFMPEG_BIN) else "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", img_path,
            "-c:v", "libx264",
            "-t", "10",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1920",
            "-r", "30",
            output_path
        ]
        
        res_vid = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_vid.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Video Short limpio generado en: {output_path}", file=sys.stderr)
            return output_path
        else:
            print(f"⚠️ Error FFmpeg: {res_vid.stderr[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Excepción en generación de Short: {e}", file=sys.stderr)
        
    return ""

if __name__ == "__main__":
    path = generate_short_video()
    if path:
        print(json.dumps({"status": "success", "video_path": path}))
