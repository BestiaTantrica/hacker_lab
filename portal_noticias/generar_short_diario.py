#!/usr/bin/env python3
"""
generar_short_diario.py — Fábrica de Shorts Automáticos de Video Vertical (1080x1920 MP4)
Utiliza ImageMagick (convert) + FFmpeg para máxima calidad y 100% de compatibilidad.
"""

import os
import sys
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_BIN = os.path.abspath(os.path.join(BASE_DIR, "..", "backup_2026_proyectos_viejos", "fabrica_magica", "ffmpeg"))
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "shorts")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_short_video(word_topic: str = "TARIFAS Y DÓLAR", poll_question: str = "¿El ajuste vale la pena o el costo social es insostenible?") -> str:
    """Genera un Short vertical (1080x1920) de 10s listo para YouTube Shorts/TikTok."""
    img_path = os.path.join(OUTPUT_DIR, "frame_short.png")
    output_path = os.path.join(OUTPUT_DIR, "short_del_dia.mp4")

    clean_word = word_topic.upper()
    clean_question = poll_question[:60] + "..." if len(poll_question) > 60 else poll_question

    # 1. Crear el Frame Visual 1080x1920 con ImageMagick
    convert_cmd = [
        "convert",
        "-size", "1080x1920",
        "xc:#0b0f19",
        "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        "-fill", "#3b82f6", "-pointsize", "46",
        "-gravity", "north", "-annotate", "+0+280", "TEMA MAS HABLADO DEL DIA",
        
        "-fill", "#ffffff", "-pointsize", "95",
        "-gravity", "north", "-annotate", "+0+400", clean_word,
        
        "-fill", "#9ca3af", "-pointsize", "38",
        "-gravity", "north", "-annotate", "+0+650", clean_question,
        
        "-fill", "#10b981", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+1300", "🔥 VOTA EN EL TERMOMETRO SOCIAL",
        
        "-fill", "#f59e0b", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+1420", "http://localhost:8001/",
        
        img_path
    ]

    print(f"🎬 Generando imagen base (1080x1920) para Short...", file=sys.stderr)
    try:
        res_img = subprocess.run(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res_img.returncode != 0 or not os.path.exists(img_path):
            print(f"⚠️ Error ImageMagick: {res_img.stderr}", file=sys.stderr)
            return ""
            
        # 2. Convertir imagen PNG en MP4 de 10 segundos con FFmpeg
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
            print(f"✅ Video Short generado con éxito: {output_path}", file=sys.stderr)
            return output_path
        else:
            print(f"⚠️ Error FFmpeg: {res_vid.stderr[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Excepción en generación de Short: {e}", file=sys.stderr)
        
    return ""

if __name__ == "__main__":
    path = generate_short_video("JUBILACIONES Y TARIFAS", "¿El ajuste vale la pena o el costo social es insostenible?")
    if path:
        print(json.dumps({"status": "success", "video_path": path}))
