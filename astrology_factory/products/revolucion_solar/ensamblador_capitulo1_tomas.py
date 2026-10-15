#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ensamblador_capitulo1_tomas.py
─────────────────────────────────────────────────────────────────────────────
Ensambla el Capítulo 1 completo de la Revolución Solar 2026 de Tomás.
Arquitectura de 3 Actos:
  - ACTO 1: Carta Natal Base (Raíz Acuariana).
  - ACTO 2: Acoplamiento Bi-Wheel (Retorno Solar 2026 en Libra 14°).
  - ACTO 3: Enfoque Quirúrgico en el Portal (Casa 9 + HUD Explicativo).

Locución en audio Rioplatense auténtico con edge-tts (es-AR-TomasNeural).
Cero costo ($0), sincronización perfecta audio/visual y 1080p nativo.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
import edge_tts

OUTPUT_DIR = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/capitulo_1_produccion")
PREVIEW_DIR = Path("/home/LAB/astrology_factory/products/revolucion_solar/output_tomas/vectorial_preview")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "es-AR-TomasNeural"

TEXTO_ACTO1 = (
    "Bienvenido. Esto que vas a escuchar no funciona solo. Tenés en la mano el informe escrito de tu Carta Natal, "
    "diez páginas donde quedó dibujado el territorio de base, y este video trabaja encima de ese territorio. "
    "Volvé a él mientras escuchás: cada cosa que diga acá tiene su raíz en esas páginas. "
    "Una Revolución Solar es el instante exacto en que el Sol regresa al grado preciso donde estaba cuando naciste. "
    "No es una sentencia. Es la descripción de qué zonas de tu vida quedan iluminadas durante doce meses y cuáles quedan en penumbra. "
    "Lo que hagas con esa luz es asunto tuyo."
)

TEXTO_ACTO2 = (
    "Tu retorno ocurre el 11 de abril de 2026, a las 18:10 de Buenos Aires. "
    "Y lo primero que hay que mirar en esa carta es el Ascendente, porque marca la puerta por la que entra el año. "
    "Se ubica en Libra, 14 grados 21 minutos."
)

TEXTO_ACTO3 = (
    "Fijate lo que eso implica. En tu informe escrito, el Ascendente natal está en Acuario. "
    "Es una postura de toda la vida: mirar desde afuera, resolver solo, desconfiar de todo lo que exija pertenencia. "
    "Este año esa postura queda desplazada. La puerta de entrada es Libra, el signo del otro, del pacto, de la balanza que no se inclina sola. "
    "Y ese punto cae en tu Casa 9 natal. Ahí viven tu Saturno y tu Plutón, los dos en Libra, y también tu Júpiter en Escorpio. "
    "Es una de las zonas más cargadas de tu carta, donde lo que creés, lo que te enseñaron y lo que te cuesta soltar están atados con nudos viejos. "
    "Que el Ascendente anual aterrice justo ahí no es una invitación amable. Es una exigencia. "
    "Te toca negociar, acordar, poner firma, ceder terreno, y hacerlo desde una constitución que prefiere no deberle nada a nadie. "
    "Eso incomoda, y no vale disimularlo. No se trata de hacer amigos ni de volverte conciliador. "
    "Se trata de enfrentar la realidad de cualquier vínculo serio: que implica reglas, contratos, límites compartidos y la renuncia a decidir todo en soledad. "
    "Si lo atravesás con honestidad, vas a descubrir que ciertos horizontes, los de la Casa 9, solamente se alcanzan acompañado y con las condiciones escritas. "
    "Ese es el portal. Veamos qué hay del otro lado."
)


PIPER_BIN = Path("/home/LAB/astrology_factory/venv/bin/piper")
PIPER_MODEL = Path("/home/LAB/astrology_factory/v2/modelos_piper/es_ES-davefx-medium.onnx")


def generar_audio_piper(texto: str, output_path: str):
    """Genera audio localmente usando Piper TTS offline."""
    out_p = Path(output_path)
    wav_path = out_p.with_suffix(".wav")

    cmd_piper = [
        str(PIPER_BIN),
        "--model", str(PIPER_MODEL),
        "--output_file", str(wav_path),
        "--length-scale", "1.08" # Un poco más pausado y solemne
    ]
    proc = subprocess.run(
        cmd_piper,
        input=texto.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120
    )
    if proc.returncode != 0 or not wav_path.exists():
        raise RuntimeError(f"Error en Piper TTS:\n{proc.stderr.decode('utf-8')}")

    # Convertir a MP3
    cmd_ffmpeg = [
        "ffmpeg", "-y",
        "-i", str(wav_path),
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out_p)
    ]
    subprocess.run(cmd_ffmpeg, capture_output=True, text=True, check=True)
    if wav_path.exists():
        wav_path.unlink()


async def generar_audio(texto: str, output_path: str):
    """Genera audio MP3 usando Piper TTS local confiable."""
    generar_audio_piper(texto, output_path)


def obtener_duracion_audio(audio_path: str) -> float:
    """Obtiene la duración exacta en segundos de un archivo de audio con ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def renderizar_segmento(img_path: str, audio_path: str, out_segment: str, duracion: float):
    """Crea un segmento MP4 sincronizado con la imagen y el audio."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(duracion + 0.5),
        "-shortest",
        out_segment
    ]
    subprocess.run(cmd, capture_output=True, text=True, check=True)


async def main():
    print("🚀 Iniciando Ensamblado del Capítulo 1 para Tomás...")

    # 1. Rutas de Imágenes Vectoriales
    img_acto1 = str(PREVIEW_DIR / "acto1_carta_natal_tomas.png")
    img_acto2 = str(PREVIEW_DIR / "acto2_acoplamiento_biwheel.png")
    img_acto3 = str(PREVIEW_DIR / "acto3_portal_libra_casa9.png")

    for img in [img_acto1, img_acto2, img_acto3]:
        if not Path(img).exists():
            print(f"Error: No existe {img}")
            return

    # 2. Generar Audios
    a1_path = str(OUTPUT_DIR / "audio_acto1.mp3")
    a2_path = str(OUTPUT_DIR / "audio_acto2.mp3")
    a3_path = str(OUTPUT_DIR / "audio_acto3.mp3")

    print("🎙️ Generando locución Acto 1...")
    await generar_audio(TEXTO_ACTO1, a1_path)
    d1 = obtener_duracion_audio(a1_path)
    print(f"   Duración Acto 1: {d1:.2f}s")

    print("🎙️ Generando locución Acto 2...")
    await generar_audio(TEXTO_ACTO2, a2_path)
    d2 = obtener_duracion_audio(a2_path)
    print(f"   Duración Acto 2: {d2:.2f}s")

    print("🎙️ Generando locución Acto 3...")
    await generar_audio(TEXTO_ACTO3, a3_path)
    d3 = obtener_duracion_audio(a3_path)
    print(f"   Duración Acto 3: {d3:.2f}s")

    # 3. Renderizar Segmentos de Video
    v1_path = str(OUTPUT_DIR / "seg1_acto1.mp4")
    v2_path = str(OUTPUT_DIR / "seg2_acto2.mp4")
    v3_path = str(OUTPUT_DIR / "seg3_acto3.mp4")

    print("🎬 Renderizando Segmento 1 (Acto 1: Carta Natal Base)...")
    renderizar_segmento(img_acto1, a1_path, v1_path, d1)

    print("🎬 Renderizando Segmento 2 (Acto 2: Acoplamiento Bi-Wheel)...")
    renderizar_segmento(img_acto2, a2_path, v2_path, d2)

    print("🎬 Renderizando Segmento 3 (Acto 3: Portal Libra en Casa 9)...")
    renderizar_segmento(img_acto3, a3_path, v3_path, d3)

    # 4. Concatenación Final con FFmpeg
    concat_txt = OUTPUT_DIR / "concat_list.txt"
    with open(concat_txt, "w") as f:
        f.write(f"file '{v1_path}'\n")
        f.write(f"file '{v2_path}'\n")
        f.write(f"file '{v3_path}'\n")

    master_video = OUTPUT_DIR / "capitulo_1_revolucion_solar_tomas.mp4"
    print(f"🎞️ Concatenando Capítulo 1 Maestro: {master_video}...")

    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(master_video)
    ]
    subprocess.run(cmd_concat, capture_output=True, text=True, check=True)

    total_dur = d1 + d2 + d3 + 1.5
    print("\n" + "=" * 60)
    print(f"✅ ¡CAPÍTULO 1 MAESTRO GENERADO CON ÉXITO!")
    print(f"📁 Video Final: {master_video}")
    print(f"⏱️ Duración Total: {total_dur:.2f}s ({total_dur / 60:.1f} minutos)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
