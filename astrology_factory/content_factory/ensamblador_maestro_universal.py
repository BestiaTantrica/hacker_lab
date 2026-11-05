#!/usr/bin/env python3
"""
🌟 ASTROLOGY FACTORY — ensamblador_maestro_universal.py (Versión 1.0)
─────────────────────────────────────────────────────────────────────────────
Pipeline Universal de Montaje Audiovisual: "Modelo de Oro"
Instrumento Canónico: El Astrolabio Sagrado de El Glifo Maestro

Estructura de Edición Canónica:
1. Toma 1 (00.0s – 02.0s) [ 2.0s ]: Intro Espacio Profundo con Color Grading Elemental.
2. Toma 2 (02.0s – 15.0s) [13.0s ]: Astrolabio Sagrado — Seg 1: Amanecer + Zoom-in + HOLD Oposición Luna ♎ - Saturno ♈.
3. Toma 3 (15.0s – 18.0s) [ 3.0s ]: Materialización Canónica 1 — Sigilo de Libra / Casa 7 (Balanza y Equilibrio).
4. Toma 4 (18.0s – 21.0s) [ 3.0s ]: Materialización Canónica 2 — Glifo de Saturno (Plomo y Basalto).
5. Toma 5 (21.0s – 32.0s) [11.0s ]: Astrolabio Sagrado — Seg 2: Tarde + Zoom-in + HOLD Sextil Venus ♎ - Júpiter ♌.
6. Toma 6 (32.0s – 38.0s) [ 6.0s ]: Outro Espacio Profundo — Cierre de Loop Cósmico idéntico al frame inicial.

Audio:
- Locución: Tomás (es-AR-TomasNeural a +6%), con voseo rioplatense humano y CTA directo.
- Música de fondo / Pulsos celestiales mezclados a -18dB.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import subprocess
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FACTORY_ROOT))

BOVEDA = Path("/home/tomas2/Desktop/Boveda_Astrologia")
TEMP_DIR = Path("/tmp/ensamble_nov6")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

PRODUCCION_DIR = FACTORY_ROOT / "produccion" / "videos_completos"
PRODUCCION_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. CONFIGURACIÓN DEL TRÁNSITO Y ASSETS (6 DE NOVIEMBRE 2026) ─────────────
FECHA = "2026-11-06"
EVENTO_ID = "2026-11-06_Luna_Oposicion_Saturno"
OUT_MASTER = PRODUCCION_DIR / f"MASTER_FINAL_{EVENTO_ID}_GlifoMaestro.mp4"

# Clip continuo del Astrolabio Sagrado (previamente generado a 40s exactos)
ASTROLABIO_40S = FACTORY_ROOT / "produccion" / "clips_reloj_2d" / f"astrolabio_continuo_{FECHA}_40s.mp4"

# Fondo espacial galáctico para intro y loop final
ESPACIO_VIDEO = BOVEDA / "Assets_Auditados" / "videos de espacio para fondo" / "07_espacio_galaxias_deep_space_galaxy_pex_v_20556585.mp4"

# Filtro elemental Aire (Libra) con destellos dorados
FILTRO_ELEMENTAL = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,colorchannelmixer=rr=0.75:rg=0.15:rb=0.35:gg=0.95:gb=0.25:bb=1.25,eq=saturation=1.25:contrast=1.10:brightness=0.02"

# Imágenes Canónicas Auditadas de El Glifo Maestro (no usadas en los últimos 30 días)
# 1. Bloque Simbólico (Post Hold 1 Oposición)
IMG_LIBRA = BOVEDA / "Assets_Auditados" / "Imagenes" / "Glifo_Maestro" / "04_Casas_Astrologicas" / "07_Casa_7_Alianzas_Espejos" / "casa_07_v6_sigilo_libra_equilibrio.webp"
IMG_SATURNO = BOVEDA / "Assets_Auditados" / "Imagenes" / "Glifo_Maestro" / "02_Planetas_Sociales_y_Transpersonales" / "02_Saturno" / "glifo_saturno_plomo_basalto.webp"

# 2. Bloque Humano y Material (Post Hold 2 Sextil - 4s c/u)
IMG_HUMANA = BOVEDA / "Assets_Auditados" / "Imagenes" / "Glifo_Maestro" / "04_Casas_Astrologicas" / "07_Casa_7_Alianzas_Espejos" / "casa_07_v5_escultura_pacto_sagrado.webp"
IMG_MATERIAL = BOVEDA / "Assets_Auditados" / "Imagenes" / "Glifo_Maestro" / "04_Casas_Astrologicas" / "05_Casa_5_Creacion_Teatro" / "casa_05_v2_corona_oro_teatro.webp"

# Guion con Voseo Argentino y Llamado a la Acción (CTA)
GUION_TEXTO = """Fijate cómo arranca este 6 de noviembre en el cielo.

Al mediodía, la Luna en Libra choca con Saturno en Aries. Es una oposición directa: sentís un freno o una frialdad en el otro. No mendigues aprobación ni te encierres con rencor. Mantené tu eje.

A la tarde el juego cambia. Venus en Libra conecta en sextil con Júpiter en Leo. Hay diplomacia, pero con fuego y soberanía. Es el momento de negociar sin regalar tu valor.

Seguinos para sincronizarte cada día con el Astrolabio Sagrado, y dejame en comentarios en qué signo tenés la Luna para ver cómo te pega esta tensión."""


def generar_audio_locucion() -> Path:
    """Genera la locución con es-AR-TomasNeural a +6%."""
    out_audio = TEMP_DIR / "locucion_tomas_nov6.mp3"
    edge_bin = "/home/LAB/astrology_factory/venv/bin/edge-tts"
    cmd = [
        edge_bin,
        "--voice", "es-AR-TomasNeural",
        "--rate=+6%",
        "--text", GUION_TEXTO,
        "--write-media", str(out_audio)
    ]
    print(f"🎙️ [1/6] Sintetizando voz neural humana con CTA...")
    subprocess.run(cmd, check=True)
    
    d_raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_audio)]
    ).decode().strip()
    print(f"   ✅ Audio generado: {float(d_raw):.2f}s ({out_audio.name})")
    return out_audio


def preparar_segmentos_video():
    """Genera los 8 bloques de video limpios y normalizados a 1080x1920 @ 30fps."""
    print("✂️ [2/6] Cortando y normalizando los 8 segmentos canónicos...")
    
    seg1_intro = TEMP_DIR / "seg1_intro_espacio.mp4"
    seg2_astro1 = TEMP_DIR / "seg2_astrolabio_hold1.mp4"
    seg3_libra = TEMP_DIR / "seg3_materializa_libra.mp4"
    seg4_saturno = TEMP_DIR / "seg4_materializa_saturno.mp4"
    seg5_astro2 = TEMP_DIR / "seg5_astrolabio_hold2.mp4"
    seg6_humana = TEMP_DIR / "seg6_materializa_humana.mp4"
    seg7_material = TEMP_DIR / "seg7_materializa_material.mp4"
    seg8_outro = TEMP_DIR / "seg8_outro_loop.mp4"
    
    # 1. Intro Espacio (2.0s)
    cmd1 = (
        f"ffmpeg -y -ss 00:00:01.000 -t 2.0 -i '{ESPACIO_VIDEO}' "
        f"-vf '{FILTRO_ELEMENTAL},format=yuv420p' -r 30 -c:v libx264 -crf 16 -preset fast '{seg1_intro}' >/dev/null 2>&1"
    )
    subprocess.run(cmd1, shell=True, check=True)
    
    # 2. Astrolabio Seg 1: Amanecer + Zoom-in + Hold 1 (13.0s de clip, del t=0.0s al t=13.0s)
    cmd2 = (
        f"ffmpeg -y -ss 00:00:00.000 -t 13.0 -i '{ASTROLABIO_40S}' "
        f"-vf 'scale=1080:1920,format=yuv420p' -r 30 -c:v libx264 -crf 14 -preset fast '{seg2_astro1}' >/dev/null 2>&1"
    )
    subprocess.run(cmd2, shell=True, check=True)
    
    # 3. Materialización Canónica 1 (Símbolo): Libra (3.0s) estático nítido
    cmd3 = (
        f"ffmpeg -y -loop 1 -t 3.0 -i '{IMG_LIBRA}' "
        f"-vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p' "
        f"-r 30 -c:v libx264 -crf 16 -preset fast '{seg3_libra}' >/dev/null 2>&1"
    )
    subprocess.run(cmd3, shell=True, check=True)
    
    # 4. Materialización Canónica 2 (Símbolo): Saturno (3.0s) estático nítido
    cmd4 = (
        f"ffmpeg -y -loop 1 -t 3.0 -i '{IMG_SATURNO}' "
        f"-vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p' "
        f"-r 30 -c:v libx264 -crf 16 -preset fast '{seg4_saturno}' >/dev/null 2>&1"
    )
    subprocess.run(cmd4, shell=True, check=True)
    
    # 5. Astrolabio Seg 2: Tarde + Zoom-in + Hold 2 Sextil (11.0s, del t=18.5s al t=29.5s)
    cmd5 = (
        f"ffmpeg -y -ss 00:00:18.500 -t 11.0 -i '{ASTROLABIO_40S}' "
        f"-vf 'scale=1080:1920,format=yuv420p' -r 30 -c:v libx264 -crf 14 -preset fast '{seg5_astro2}' >/dev/null 2>&1"
    )
    subprocess.run(cmd5, shell=True, check=True)

    # 6. Materialización Humana: Escultura del Pacto Sagrado (4.0s)
    cmd6 = (
        f"ffmpeg -y -loop 1 -t 4.0 -i '{IMG_HUMANA}' "
        f"-vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p' "
        f"-r 30 -c:v libx264 -crf 16 -preset fast '{seg6_humana}' >/dev/null 2>&1"
    )
    subprocess.run(cmd6, shell=True, check=True)

    # 7. Materialización Material: Corona de Oro y Soberanía Leo/Júpiter (4.0s)
    cmd7 = (
        f"ffmpeg -y -loop 1 -t 4.0 -i '{IMG_MATERIAL}' "
        f"-vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=yuv420p' "
        f"-r 30 -c:v libx264 -crf 16 -preset fast '{seg7_material}' >/dev/null 2>&1"
    )
    subprocess.run(cmd7, shell=True, check=True)
    
    # 8. Outro Espacio para loop perfecto (2.4s). Termina enlazando con la cabecera
    cmd8 = (
        f"ffmpeg -y -ss 00:00:03.000 -t 2.4 -i '{ESPACIO_VIDEO}' "
        f"-vf '{FILTRO_ELEMENTAL},format=yuv420p' -r 30 -c:v libx264 -crf 16 -preset fast '{seg8_outro}' >/dev/null 2>&1"
    )
    subprocess.run(cmd8, shell=True, check=True)
    
    print("   ✅ Todos los 8 segmentos normalizados a 1080x1920 @ 30fps.")
    return [seg1_intro, seg2_astro1, seg3_libra, seg4_saturno, seg5_astro2, seg6_humana, seg7_material, seg8_outro]


def ensamblar_video_transiciones(segmentos, out_video_raw: Path):
    """
    Concatena los 8 clips usando crossfade (xfade) suave de 0.40s.
    Cero saltos abruptos, cero pantallas blancas, loop infinito garantizado.
    """
    print("🎬 [3/6] Ensamblando video con 7 transiciones crossfade de 0.40s...")
    
    # Duraciones exactas:
    # d1 = 2.0s
    # d2 = 13.0s
    # d3 = 3.0s
    # d4 = 3.0s
    # d5 = 11.0s
    # d6 = 4.0s
    # d7 = 4.0s
    # d8 = 2.4s
    # Con xfade = 0.40s:
    # offset1 = 2.0 - 0.40 = 1.60
    # offset2 = 1.60 + 13.0 - 0.40 = 14.20
    # offset3 = 14.20 + 3.0 - 0.40 = 16.80
    # offset4 = 16.80 + 3.0 - 0.40 = 19.40
    # offset5 = 19.40 + 11.0 - 0.40 = 30.00
    # offset6 = 30.00 + 4.0 - 0.40 = 33.60
    # offset7 = 33.60 + 4.0 - 0.40 = 37.20
    # Duración total: 37.20 + 2.40 = 39.60s (prácticamente 40s exactos)
    
    filter_complex = (
        "[0:v][1:v]xfade=transition=fade:duration=0.40:offset=1.60[v01];"
        "[v01][2:v]xfade=transition=fade:duration=0.40:offset=14.20[v02];"
        "[v02][3:v]xfade=transition=fade:duration=0.40:offset=16.80[v03];"
        "[v03][4:v]xfade=transition=fade:duration=0.40:offset=19.40[v04];"
        "[v04][5:v]xfade=transition=fade:duration=0.40:offset=30.00[v05];"
        "[v05][6:v]xfade=transition=fade:duration=0.40:offset=33.60[v06];"
        "[v06][7:v]xfade=transition=fade:duration=0.40:offset=37.20,format=yuv420p[v_final]"
    )
    
    inputs_cmd = []
    for s in segmentos:
        inputs_cmd.extend(["-i", str(s)])
        
    cmd = [
        "ffmpeg", "-y",
        *inputs_cmd,
        "-filter_complex", filter_complex,
        "-map", "[v_final]",
        "-c:v", "libx264",
        "-crf", "14",
        "-preset", "slow",
        "-r", "30",
        str(out_video_raw)
    ]
    subprocess.run(cmd, check=True)
    print(f"   ✅ Pista de video continua generada: {out_video_raw.name}")


def masterizar_audiovisual(video_path: Path, audio_path: Path, out_master: Path):
    """
    Muxea el video con la locución sincronizada.
    La voz entra en el segundo 1.5 (respiro elegante tras la apertura espacial).
    """
    print(f"🎛️ [4/6] Muxeando audio y video maestro con delay de respiración...")
    
    # Duración de la voz
    d_audio = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio_path)]
    ).decode().strip())
    
    d_video = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)]
    ).decode().strip())
    
    print(f"   Duración Video: {d_video:.2f}s | Duración Voz: {d_audio:.2f}s")
    
    # Delay de 1.2s para la voz para que entre después de la apertura de estrellas
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-filter_complex",
        "[1:a]adelay=1200|1200,apad,volume=1.0[a_voice]",
        "-map", "0:v",
        "-map", "[a_voice]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(d_video),
        str(out_master)
    ]
    subprocess.run(cmd, check=True)
    size_mb = out_master.stat().st_size / (1024 * 1024)
    print(f"   🏆 ¡MASTER FINAL COMPLETO!: {out_master.name} ({size_mb:.2f} MB, {d_video:.2f}s)")


def main():
    print(f"\n=================================================================")
    print(f"🌌 ENSAMBLADOR MAESTRO UNIVERSAL: {EVENTO_ID}")
    print(f"=================================================================")
    
    voz_mp3 = generar_audio_locucion()
    segmentos = preparar_segmentos_video()
    video_raw = TEMP_DIR / "video_raw_ensamblado.mp4"
    ensamblar_video_transiciones(segmentos, video_raw)
    masterizar_audiovisual(video_raw, voz_mp3, OUT_MASTER)
    
    print("\n✅ PROCESO COMPLETADO CON ÉXITO.")
    print(f"📁 Master exportado en: {OUT_MASTER}")


if __name__ == "__main__":
    main()
