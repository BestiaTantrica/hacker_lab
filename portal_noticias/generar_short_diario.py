#!/usr/bin/env python3
"""
generar_short_diario.py — Fábrica de Shorts Promocionales para Redes (1080x1920 con Voz Neural)
Diseño gráfico de alto impacto para viralizar encuestas y atraer tráfico a la plataforma.
"""

import os
import sys
import json
import subprocess

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


def generate_short_video(word_topic: str = "SUPERAVIT Y TARIFAS", poll_question: str = "¿Estás de acuerdo con el rumbo económico y las reformas de mercado?", base_url: str = "http://localhost:8001/") -> str:
    """Genera un Short promocional vertical (1080x1920) de alto impacto con voz neural y gráfica de encuesta."""
    img_path = os.path.join(OUTPUT_DIR, "frame_short.png")
    audio_path = os.path.join(OUTPUT_DIR, "voz_narracion.mp3")
    output_path = os.path.join(OUTPUT_DIR, "short_del_dia.mp4")

    clean_word = word_topic.upper()
    
    # Narración optimizada para llamada a la acción
    script_voz = f"¡Medición en tiempo real! La conversación social en redes hoy gira en torno a {clean_word}. ¿Querés sumar tu voto al termómetro directo sin intermediarios? Entrá ya a {base_url} y votá en vivo."
    has_audio = generate_voice_narration(script_voz, audio_path)

    # Formatear la consigna en líneas limpias
    words = poll_question.split()
    line1 = " ".join(words[:5]) if len(words) >= 5 else poll_question
    line2 = " ".join(words[5:10]) if len(words) >= 10 else (" ".join(words[5:]) if len(words) > 5 else "")
    line3 = " ".join(words[10:]) if len(words) > 10 else ""

    # Crear imagen vertical 1080x1920 con ImageMagick
    convert_cmd = [
        "convert",
        "-size", "1080x1920",
        "xc:#0a0d14",
        "-font", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        
        # Borde / Marco Neón Dorado
        "-stroke", "#f59e0b", "-strokewidth", "8", "-fill", "none",
        "-draw", "rectangle 40,40 1040,1880",
        "-stroke", "none",
        
        # Encabezado Comercial
        "-fill", "#f59e0b", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+180", "🔥 TERMOMETRO SOCIAL & MEDIDA REAL",
        
        "-fill", "#9ca3af", "-pointsize", "32",
        "-gravity", "north", "-annotate", "+0+240", "CONCEPTOS Y DEBATES CANDENTES EN REDES",
        
        # Concepto Central Gigante
        "-fill", "#ffffff", "-pointsize", "75",
        "-gravity", "north", "-annotate", "+0+380", clean_word,
        
        # Caja de la Pregunta / Encuesta
        "-fill", "#3b82f6", "-pointsize", "36",
        "-gravity", "north", "-annotate", "+0+620", "📊 ENCUESTA INTERACTIVA DEL DIA:",
        
        "-fill", "#f3f4f6", "-pointsize", "42",
        "-gravity", "north", "-annotate", "+0+720", line1,
        "-gravity", "north", "-annotate", "+0+790", line2,
        "-gravity", "north", "-annotate", "+0+860", line3,
        
        # Opciones de Voto Visuales
        "-fill", "#10b981", "-pointsize", "36",
        "-gravity", "north", "-annotate", "+0+1050", "[ 1 ] Apoyo total al rumbo economico",
        
        "-fill", "#f59e0b", "-pointsize", "36",
        "-gravity", "north", "-annotate", "+0+1130", "[ 2 ] Apoyo critico / Atento a tarifas",
        
        "-fill", "#f43f5e", "-pointsize", "36",
        "-gravity", "north", "-annotate", "+0+1210", "[ 3 ] Desacuerdo / Mayor gradualidad",
        
        # Llamado a la Acción (CTA)
        "-fill", "#ffffff", "-pointsize", "44",
        "-gravity", "north", "-annotate", "+0+1480", "👇 SUMA TU VOTO ANÓNIMO EN VIVO:",
        
        "-fill", "#fbbf24", "-pointsize", "46",
        "-gravity", "north", "-annotate", "+0+1580", base_url,
        
        img_path
    ]

    print(f"🎬 Generando Frame Promocional (1080x1920)...", file=sys.stderr)
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
            print(f"✅ Short de Video Promocional generado exitosamente: {output_path}", file=sys.stderr)
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
