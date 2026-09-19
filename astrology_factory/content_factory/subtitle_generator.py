"""
subtitle_generator.py
─────────────────────
Genera un archivo .ass perfectamente cronometrado usando
Whisper local (openai-whisper). Produce formato ASS (Advanced SubStation Alpha)
con PlayResX/Y correctos para que el FontSize se calcule relativo
al canvas de 1080x1920 y no quede gigante.

Uso:
    from subtitle_generator import generate_ass
    ass_path = generate_ass("/ruta/al/audio.mp3", modelo="small")
"""

import os
import json
import whisper


# ── Helpers de formato de tiempo ─────────────────────────────────────────────

def _segundos_a_ass(seg: float) -> str:
    """Convierte segundos (float) al formato ASS: H:MM:SS.cc (centisegundos)"""
    h  = int(seg // 3600)
    m  = int((seg % 3600) // 60)
    s  = int(seg % 60)
    cc = int(round((seg - int(seg)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cc:02d}"


def _segundos_a_srt(seg: float) -> str:
    """Convierte segundos (float) al formato SRT: HH:MM:SS,mmm"""
    h  = int(seg // 3600)
    m  = int((seg % 3600) // 60)
    s  = int(seg % 60)
    ms = int(round((seg - int(seg)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ── Generador principal ───────────────────────────────────────────────────────

def generate_ass(
    mp3_path:     str,
    modelo:       str = "small",
    video_width:  int = 1080,
    video_height: int = 1920,
    font_size:    int = 52,
    margin_v:     int = 100,
) -> str:
    """
    Transcribe el MP3 con Whisper local y genera un .ass con PlayRes correcto.

    Con PlayResX=1080 y PlayResY=1920, un FontSize=52 renderiza en ~52px sobre
    el canvas real de 1920px — proporcional y legible en TikTok/Reels.

    Parámetros:
        mp3_path     – Ruta absoluta al .mp3
        modelo       – Modelo Whisper: tiny | base | small | medium | large
        video_width  – Ancho del canvas final (default 1080)
        video_height – Alto del canvas final (default 1920)
        font_size    – Tamaño de fuente en unidades ASS (relativo a PlayRes)
        margin_v     – Margen vertical inferior en px de PlayRes

    Retorna:
        Ruta del archivo .ass generado.
    """
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"Audio no encontrado: {mp3_path}")

    ass_path = mp3_path.replace(".mp3", ".ass")

    print(f"🎙️  Whisper ({modelo}) transcribiendo: {os.path.basename(mp3_path)}...")

    model  = whisper.load_model(modelo)
    result = model.transcribe(
        mp3_path,
        language="es",
        word_timestamps=True,
        verbose=False,
    )

    segments = result.get("segments", [])
    if not segments:
        raise RuntimeError("Whisper no produjo segmentos. El MP3 puede estar vacío.")

    # ── Header ASS ────────────────────────────────────────────────────────────
    # CRÍTICO: PlayResX/Y deben coincidir con el tamaño real del video.
    # Esto hace que FontSize sea relativo al canvas y no se escale 6x.
    #
    # Colores en formato ASS ABGR hex:
    #   &H00FFFFFF = blanco opaco
    #   &H00000000 = negro opaco
    #   &H80000000 = negro semi-transparente (background del borde)
    #
    # Alignment=2 = centro-inferior (estándar subtítulos)
    ass_header = (
        f"[Script Info]\n"
        f"ScriptType: v4.00+\n"
        f"PlayResX: {video_width}\n"
        f"PlayResY: {video_height}\n"
        f"ScaledBorderAndShadow: yes\n"
        f"\n"
        f"[V4+ Styles]\n"
        f"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        f"OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        f"ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        f"Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Arial,{font_size},&H00FFFFFF,&H000000FF,"
        f"&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,4,2,"
        f"2,40,40,{margin_v},1\n"
        f"\n"
        f"[Events]\n"
        f"Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    # ── Eventos ───────────────────────────────────────────────────────────────
    eventos = []
    for seg in segments:
        t_ini  = _segundos_a_ass(seg["start"])
        t_fin  = _segundos_a_ass(seg["end"])
        texto  = seg["text"].strip().replace("\n", " ")
        eventos.append(f"Dialogue: 0,{t_ini},{t_fin},Default,,0,0,0,,{texto}\n")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        f.writelines(eventos)

    # También escribir .srt de respaldo (para referencia, no lo usa FFmpeg)
    srt_path = mp3_path.replace(".mp3", ".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{_segundos_a_srt(seg['start'])} --> {_segundos_a_srt(seg['end'])}\n"
                    f"{seg['text'].strip()}\n\n")

    # Guardar archivo words.json para el diseño sonoro inteligente
    words_data = []
    for seg in segments:
        if "words" in seg:
            for w in seg["words"]:
                # Normalizar palabra: quitar signos y pasar a minúsculas
                w_norm = "".join(c for c in w["word"].lower() if c.isalnum())
                words_data.append({
                    "word": w_norm,
                    "raw": w["word"],
                    "start": w["start"],
                    "end": w["end"]
                })
    words_json_path = mp3_path.replace(".mp3", "_words.json")
    with open(words_json_path, "w", encoding="utf-8") as f:
        json.dump(words_data, f, ensure_ascii=False, indent=2)

    print(f"✅ ASS generado con {len(segments)} bloques → {ass_path}")
    return ass_path


# Alias para compatibilidad con código que llame generate_srt
def generate_srt(mp3_path: str, modelo: str = "small") -> str:
    """Wrapper de compatibilidad: genera ASS y retorna su ruta."""
    return generate_ass(mp3_path, modelo=modelo)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python subtitle_generator.py <ruta_audio.mp3> [modelo]")
        sys.exit(1)
    modelo = sys.argv[2] if len(sys.argv) > 2 else "small"
    generate_ass(sys.argv[1], modelo=modelo)
