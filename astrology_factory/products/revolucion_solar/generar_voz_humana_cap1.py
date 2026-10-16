#!/usr/bin/env python3
"""
generar_voz_humana_cap1.py
─────────────────────────────────────────────────────────────────────────────
Genera la locución del Capítulo 1 para Tomás usando edge-tts con la voz
argentina de alta fidelidad 'es-AR-TomasNeural', con cadencia humana,
pausas respirables y modulación solemne.
─────────────────────────────────────────────────────────────────────────────
"""

import asyncio
import os
import subprocess
from pathlib import Path

BASE_DIR = Path("/home/LAB/astrology_factory/products/revolucion_solar")
VISOR_DIR = BASE_DIR / "visor_cinematico"
OUTPUT_DIR = BASE_DIR / "output_tomas" / "capitulo_1_produccion"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

EDGE_TTS_BIN = "/home/LAB/astrology_factory/venv/bin/edge-tts"
VOICE = "es-AR-TomasNeural"
RATE = "-3%"  # Cadencia solemne y reflexiva

def sintetizar_segmento(texto: str, out_file: Path):
    cmd = [
        EDGE_TTS_BIN,
        "--voice", VOICE,
        f"--rate={RATE}",
        "--pitch=-1Hz",
        "--text", texto,
        "--write-media", str(out_file)
    ]
    subprocess.run(cmd, check=True)

def medir_duracion(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def main():
    print(f"🎙️ Sintetizando con voz argentina humana: {VOICE} ({RATE})...")
    tmp_a1 = OUTPUT_DIR / "acto1_tomas.mp3"
    tmp_a2 = OUTPUT_DIR / "acto2_tomas.mp3"
    tmp_a3 = OUTPUT_DIR / "acto3_tomas.mp3"

    sintetizar_segmento(TEXTO_ACTO1, tmp_a1)
    d1 = medir_duracion(tmp_a1)
    print(f"  ✅ Acto 1 listo: {d1:.2f}s")

    sintetizar_segmento(TEXTO_ACTO2, tmp_a2)
    d2 = medir_duracion(tmp_a2)
    print(f"  ✅ Acto 2 listo: {d2:.2f}s")

    sintetizar_segmento(TEXTO_ACTO3, tmp_a3)
    d3 = medir_duracion(tmp_a3)
    print(f"  ✅ Acto 3 listo: {d3:.2f}s")

    # Crear silencios naturales de respiración (0.8s) entre actos
    silencio_path = OUTPUT_DIR / "silence_08.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", "0.8", "-q:a", "2", str(silencio_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Concat demuxer
    concat_list = OUTPUT_DIR / "concat_audio.txt"
    with open(concat_list, "w") as f:
        f.write(f"file '{tmp_a1.name}'\n")
        f.write(f"file '{silencio_path.name}'\n")
        f.write(f"file '{tmp_a2.name}'\n")
        f.write(f"file '{silencio_path.name}'\n")
        f.write(f"file '{tmp_a3.name}'\n")

    master_audio = OUTPUT_DIR / "audio_capitulo1_humano.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:a", "libmp3lame", "-q:a", "2",
        str(master_audio)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_d = medir_duracion(master_audio)
    print(f"🎉 Master Audio Humano Generado Exitosamente: {master_audio}")
    print(f"   Duración Total: {total_d:.2f}s (Acto 1: 0.0s - {d1:.2f}s | Acto 2: {d1+0.8:.2f}s - {d1+0.8+d2:.2f}s | Acto 3: {d1+1.6+d2:.2f}s - {total_d:.2f}s)")

    # Copiar a visor_cinematico
    dest_visor = VISOR_DIR / "audio_capitulo1.mp3"
    subprocess.run(["cp", str(master_audio), str(dest_visor)], check=True)
    print(f"   Copiado a {dest_visor}")

if __name__ == "__main__":
    main()
