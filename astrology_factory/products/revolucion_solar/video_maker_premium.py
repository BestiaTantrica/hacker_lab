#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video_maker_premium.py — Motor de Renderizado Audiovisual de Revolución Solar (16:9 Widescreen)
───────────────────────────────────────────────────────────────────────────────────────────────
Fase 6 del Paquete Premium de Astrology Factory:
  - Input: Guion en Markdown (6 capítulos) + Rueda Bi-Wheel (PNG).
  - Audio: Síntesis vocal neural (Edge-TTS Tomás / Fallback Piper) + Colchón espacial a -24dB.
  - Visual: Placas de capítulo, Bi-Wheel con encuadre pedagógico focalizado (Regla 8) y B-Roll de Bóveda.
  - Render: Arquitectura modular por capítulos en 1080p @ 25fps con FFmpeg Single-Pass.
  - Ensamble: Fusión final sin recodificación con concat demuxer (-c copy) a costo cero.
"""

import argparse
import asyncio
import glob
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# ── Constantes y Rutas Maestras ───────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
VAULT_VIDEOS_DIR = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Videos")
VAULT_IMAGES_DIR = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Imagenes")
VAULT_AUDIO_DIR  = Path("/home/tomas2/MediaContingencia/Privada/Astrology_Vault/Assets_Auditados/Stock_Sonoro")
PIPER_MODEL_PATH = PROJECT_ROOT / "v2" / "modelos_piper" / "es_ES-davefx-medium.onnx"
PIPER_BIN_PATH   = PROJECT_ROOT / "venv" / "bin" / "piper"

COLOR_BG_SPACE = (8, 11, 18)         # #080b12
COLOR_GOLD     = (212, 175, 55)       # #d4af37
COLOR_GOLD_LT  = (240, 215, 120)      # #f0d778
COLOR_WHITE    = (230, 235, 245)      # #e6ebf5
COLOR_CYAN     = (40, 190, 210)       # #28bed2
COLOR_MUTED    = (140, 150, 170)      # #8c96aa

FONT_TITLE_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_BODY_PATH  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ─────────────────────────────────────────────────────────────────────────────
# 1. PARSER DEL GUION EN MARKDOWN
# ─────────────────────────────────────────────────────────────────────────────

def parsear_guion_rs(markdown_path: Path) -> Tuple[Dict[str, str], List[Dict]]:
    """
    Parsea el archivo Markdown del guion de Revolución Solar en sus 6 capítulos canónicos.
    """
    if not markdown_path.exists():
        raise FileNotFoundError(f"No se encontró el guion en: {markdown_path}")

    contenido = markdown_path.read_text(encoding="utf-8")

    # Extraer metadatos del encabezado
    metadata = {
        "titulo_general": "Revolución Solar 2026",
        "consultante": "Consultante",
        "año": "2026",
    }
    m_h1 = re.search(r"^#\s*(.+)$", contenido, re.MULTILINE)
    if m_h1:
        metadata["titulo_general"] = m_h1.group(1).strip()
        # Intentar extraer nombre
        partes = [p.strip() for p in metadata["titulo_general"].split("·")]
        if len(partes) > 1:
            metadata["consultante"] = partes[-1]

    # Dividir por capítulos
    patron_cap = re.compile(
        r"##\s*CAP[ÍI]TULO\s*(\d+)\s*[-—–]\s*([^\n]+)\n(.*?)(?=\n##\s*CAP[ÍI]TULO|\Z)",
        re.DOTALL | re.IGNORECASE
    )

    capitulos = []
    matches = list(patron_cap.finditer(contenido))

    if not matches:
        raise ValueError(f"No se detectaron capítulos con formato '## CAPÍTULO N — ...' en {markdown_path}")

    for m in matches:
        num = int(m.group(1))
        titulo = m.group(2).strip()
        cuerpo = m.group(3)

        # Extraer [VOZ / LOCUCIÓN]
        locucion = ""
        m_voz = re.search(r"\*\*\[VOZ\s*/\s*LOCUCI[ÓO]N\]\*\*\s*\n+(.*?)(?=\n+\*\*\[|\Z)", cuerpo, re.DOTALL)
        if m_voz:
            locucion = m_voz.group(1).strip()
        else:
            # Fallback si no está el tag
            lineas = [l for l in cuerpo.split("\n") if not l.startswith("**[")]
            locucion = "\n".join(lineas).strip()

        # Limpiar texto de locución para TTS (eliminar markdown y caracteres conflictivos)
        locucion_limpia = re.sub(r"\[.*?\]", "", locucion)            # quitar corchetes
        locucion_limpia = re.sub(r"[*_#`]", "", locucion_limpia)        # quitar formato md
        locucion_limpia = re.sub(r"\s+", " ", locucion_limpia).strip()

        # Extraer [INDICACIONES VISUALES]
        visuales = ""
        m_vis = re.search(r"\*\*\[INDICACIONES\s*VISUALES\]\*\*\s*\n+(.*?)(?=\n+\*\*\[|\Z)", cuerpo, re.DOTALL)
        if m_vis:
            visuales = m_vis.group(1).strip()

        # Extraer [CLIMA SONORO]
        clima = ""
        m_son = re.search(r"\*\*\[CLIMA\s*SONORO\]\*\*\s*\n+(.*?)(?=\n+\*\*\[|\Z)", cuerpo, re.DOTALL)
        if m_son:
            clima = m_son.group(1).strip()

        capitulos.append({
            "num": num,
            "titulo": titulo,
            "locucion": locucion_limpia,
            "visuales": visuales,
            "clima": clima,
        })

    print(f"📖 Guion parseado con éxito: {len(capitulos)} capítulos detectados.")
    return metadata, capitulos


# ─────────────────────────────────────────────────────────────────────────────
# 2. MOTOR DE SÍNTESIS DE AUDIO (EDGE-TTS / PIPER FALLBACK)
# ─────────────────────────────────────────────────────────────────────────────

def _probe_duration(media_path: Path) -> float:
    """Retorna la duración en segundos usando ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(media_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


async def _edge_tts_async(text: str, voice: str, output_path: Path, rate: str = "+0%"):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))


def sintetizar_voz_capitulo(
    texto: str,
    output_mp3: Path,
    voice: str = "es-AR-TomasNeural",
    rate: str = "+0%"
) -> float:
    """
    Sintetiza la voz del capítulo.
    Intenta Edge-TTS y si la API devuelve error (ej. 403 o red), usa Piper TTS local.
    """
    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    temp_wav = output_mp3.with_suffix(".temp.wav")

    # 1. Intento con Edge-TTS
    edge_exitoso = False
    try:
        print(f"   🎙️  [Edge-TTS] Sintetizando con voz {voice}...")
        asyncio.run(_edge_tts_async(texto, voice, output_mp3, rate=rate))
        dur = _probe_duration(output_mp3)
        if dur > 1.0:
            edge_exitoso = True
            print(f"   ✅ Voz Edge-TTS generada: {dur:.1f}s")
            return dur
    except Exception as e:
        print(f"   ⚠️  Edge-TTS no disponible ({e}). Activando fallback local...")

    # 2. Fallback a Piper TTS (Offline, Determinístico)
    if not edge_exitoso:
        print(f"   🎙️  [Piper TTS] Sintetizando localmente con {PIPER_MODEL_PATH.name}...")
        if not PIPER_MODEL_PATH.exists() or not PIPER_BIN_PATH.exists():
            raise RuntimeError(f"Piper TTS o modelo faltante: {PIPER_MODEL_PATH}")

        # Sintetizar WAV con Piper
        p = subprocess.Popen(
            [str(PIPER_BIN_PATH), "--model", str(PIPER_MODEL_PATH), "--output_file", str(temp_wav), "--length-scale", "1.02"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        p.communicate(input=texto)
        if p.returncode != 0:
            raise RuntimeError("Fallo crítico en Piper TTS")

        # Convertir WAV a MP3
        cmd_conv = [
            "ffmpeg", "-y", "-i", str(temp_wav),
            "-c:a", "libmp3lame", "-b:a", "192k", str(output_mp3)
        ]
        subprocess.run(cmd_conv, capture_output=True, check=True)
        if temp_wav.exists():
            temp_wav.unlink()

        dur = _probe_duration(output_mp3)
        print(f"   ✅ Voz Piper generada exitosamente: {dur:.1f}s")
        return dur

    return _probe_duration(output_mp3)


def mezclar_audio_con_ambiente(
    voz_mp3: Path,
    output_mp3: Path,
    duracion_objetivo: float
) -> Path:
    """
    Mezcla la voz principal con un colchón sonoro espacial sutil a -24dB y fades suaves.
    """
    # Buscar colchón sonoro en Vault
    candidatos_pad = list(VAULT_AUDIO_DIR.glob("stock_ambient_space_biosphere_raw_*.mp3"))
    pad_file = candidatos_pad[0] if candidatos_pad else None

    if pad_file and pad_file.exists():
        cmd = [
            "ffmpeg", "-y",
            "-i", str(voz_mp3),
            "-stream_loop", "-1", "-i", str(pad_file),
            "-filter_complex",
            (
                f"[1:a]atrim=0:{duracion_objetivo:.2f},"
                f"afade=t=in:d=2.0,afade=t=out:st={max(0, duracion_objetivo - 2.5):.2f}:d=2.5,"
                f"volume=-24dB[amb];"
                f"[0:a][amb]amix=inputs=2:duration=first:dropout_transition=2[outa]"
            ),
            "-map", "[outa]",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(output_mp3)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_mp3
    else:
        # Fallback sin archivo externo: generar atmósfera armónica senoidal muy suave a 108Hz
        cmd = [
            "ffmpeg", "-y",
            "-i", str(voz_mp3),
            "-f", "lavfi", "-i", f"sine=frequency=108:sample_rate=44100:duration={duracion_objetivo:.2f}",
            "-filter_complex",
            (
                f"[1:a]afade=t=in:d=2.0,afade=t=out:st={max(0, duracion_objetivo - 2.5):.2f}:d=2.5,"
                f"volume=-32dB[amb];"
                f"[0:a][amb]amix=inputs=2:duration=first[outa]"
            ),
            "-map", "[outa]",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(output_mp3)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_mp3


# ─────────────────────────────────────────────────────────────────────────────
# 3. GENERADOR DE ELEMENTOS VISUALES PEDAGÓGICOS (REGLA 8)
# ─────────────────────────────────────────────────────────────────────────────

def _crear_fondo_estelar(w: int = 1920, h: int = 1080) -> Image.Image:
    """Genera un fondo espacial oscuro elegante #080b12 con estrellas sutiles."""
    img = Image.new("RGB", (w, h), color=COLOR_BG_SPACE)
    draw = ImageDraw.Draw(img)
    rng = random.Random(137)
    for _ in range(250):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        bright = rng.randint(40, 200)
        c = (bright, bright, min(255, bright + rng.randint(10, 40)))
        draw.point((x, y), fill=c)
        if bright > 170:
            draw.point((x + 1, y), fill=(bright // 2, bright // 2, bright // 2))
    return img


def generar_placa_capitulo(
    cap_num: int,
    titulo: str,
    consultante: str,
    output_path: Path
) -> Path:
    """
    Genera la tarjeta de inicio del capítulo (1920x1080) en tipografía dorada/ámbar.
    """
    img = _crear_fondo_estelar(1920, 1080)
    draw = ImageDraw.Draw(img)

    try:
        f_badge = ImageFont.truetype(FONT_BODY_PATH, 24)
        f_cap   = ImageFont.truetype(FONT_TITLE_PATH, 56)
        f_tit   = ImageFont.truetype(FONT_BODY_PATH, 32)
        f_name  = ImageFont.truetype(FONT_BODY_PATH, 22)
    except Exception:
        f_badge = f_cap = f_tit = f_name = ImageFont.load_default()

    # Badge superior
    draw.text((960, 360), "PORTAL TAROT MÍSTICO · REVOLUCIÓN SOLAR 2026", fill=COLOR_GOLD, font=f_badge, anchor="mm")

    # Línea decorativa dorada
    draw.line([(810, 400), (1110, 400)], fill=COLOR_GOLD, width=2)

    # Título principal del capítulo
    draw.text((960, 470), f"CAPÍTULO {cap_num}", fill=COLOR_WHITE, font=f_cap, anchor="mm")

    # Subtítulo explicativo
    # Cortar en dos líneas si es muy largo
    if len(titulo) > 50:
        palabras = titulo.split(" ")
        mitad = len(palabras) // 2
        linea1 = " ".join(palabras[:mitad])
        linea2 = " ".join(palabras[mitad:])
        draw.text((960, 560), linea1, fill=COLOR_GOLD_LT, font=f_tit, anchor="mm")
        draw.text((960, 605), linea2, fill=COLOR_GOLD_LT, font=f_tit, anchor="mm")
    else:
        draw.text((960, 570), titulo, fill=COLOR_GOLD_LT, font=f_tit, anchor="mm")

    # Consultante al pie
    draw.text((960, 720), f"INFORME PERSONALIZADO PARA: {consultante.upper()}", fill=COLOR_MUTED, font=f_name, anchor="mm")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")
    return output_path


def generar_marco_biwheel_pedagogico(
    biwheel_path: Path,
    cap_num: int,
    titulo: str,
    consultante: str,
    output_path: Path
) -> Path:
    """
    Enmarca la rueda Bi-Wheel (2600x2600) en un lienzo 1920x1080 con bandas pedagógicas
    laterales que explican el foco del capítulo (Regla 8 de PROJECT_RULES.md).
    """
    canvas = _crear_fondo_estelar(1920, 1080)

    # Cargar y redimensionar rueda Bi-Wheel a 1040x1040 para centrarla en 1080 de alto
    if biwheel_path.exists():
        rueda_raw = Image.open(biwheel_path).convert("RGBA")
        rueda_resized = rueda_raw.resize((1040, 1040), Image.Resampling.LANCZOS)
        # Posición centrada horizontalmente: x = (1920 - 1040) / 2 = 440, y = 20
        canvas.paste(rueda_resized, (440, 20), rueda_resized)
    else:
        # Placeholder si no existe
        draw_temp = ImageDraw.Draw(canvas)
        draw_temp.rectangle([440, 20, 1480, 1060], outline=COLOR_GOLD, width=3)

    draw = ImageDraw.Draw(canvas)

    try:
        f_sec_title = ImageFont.truetype(FONT_TITLE_PATH, 24)
        f_sec_text  = ImageFont.truetype(FONT_BODY_PATH, 18)
        f_sec_val   = ImageFont.truetype(FONT_BODY_PATH, 16)
    except Exception:
        f_sec_title = f_sec_text = f_sec_val = ImageFont.load_default()

    # Contenido temático según capítulo (Regla 8)
    focos_por_cap = {
        1: {
            "izq_tag": "PORTAL DEL AÑO",
            "izq_val": "Ascendente RS\ny Casas Base",
            "der_tag": "TERRITORIO",
            "der_val": "Interior: Natal\nExterior: RS 2026\nFlecha: Entrada"
        },
        2: {
            "izq_tag": "TRINIDAD ANUAL",
            "izq_val": "Sol (Consciente)\nLuna (Instinto)",
            "der_tag": "VIBRACIÓN",
            "der_val": "Propósito Solar\nvs Demanda Emocional\nen Casas Activas"
        },
        3: {
            "izq_tag": "ACCIÓN Y DESEO",
            "izq_val": "Marte (Impulso)\nVenus (Atracción)",
            "der_tag": "TERRENO",
            "der_val": "Conquista Material\nPactos y Vínculos\nEnergía Disponible"
        },
        4: {
            "izq_tag": "LEYES Y PRUEBAS",
            "izq_val": "Saturno (Frontera)\nJúpiter (Expansión)",
            "der_tag": "ARQUITECTURA",
            "der_val": "Maduración Kármica\nLímites Reales\nCrecimiento Firme"
        },
        5: {
            "izq_tag": "PUNTOS DE TENSIÓN",
            "izq_val": "Aspectos Mayores\nCuerdas Activas",
            "der_tag": "DINÁMICA",
            "der_val": "Rojo: Fricción Creativa\nAzul: Fluidez y Puente\nDorado: Conjunción"
        },
        6: {
            "izq_tag": "SÍNTESIS GLOBAL",
            "izq_val": "Maduración 2026\nEl Mapa Completo",
            "der_tag": "INTEGRACIÓN",
            "der_val": "Soberanía Personal\nportaltarotmistico.com\nTomás"
        },
    }

    info = focos_por_cap.get(cap_num, focos_por_cap[1])

    # ── PANEL LATERAL IZQUIERDO (x: 40 a 400) ─────────────────────────────────
    # Barra dorada
    draw.line([(40, 380), (40, 700)], fill=COLOR_GOLD, width=3)

    draw.text((60, 400), f"CAPÍTULO {cap_num}", fill=COLOR_GOLD, font=f_sec_title)
    draw.text((60, 440), info["izq_tag"], fill=COLOR_CYAN, font=f_sec_text)

    # Texto descriptivo
    y_pos = 490
    for linea in info["izq_val"].split("\n"):
        draw.text((60, y_pos), linea, fill=COLOR_WHITE, font=f_sec_val)
        y_pos += 26

    draw.text((60, y_pos + 20), f"Consultante: {consultante}", fill=COLOR_MUTED, font=f_sec_val)

    # ── PANEL LATERAL DERECHO (x: 1520 a 1880) ────────────────────────────────
    draw.line([(1520, 380), (1520, 700)], fill=COLOR_GOLD, width=3)

    draw.text((1540, 400), "ANÁLISIS BI-WHEEL", fill=COLOR_GOLD, font=f_sec_title)
    draw.text((1540, 440), info["der_tag"], fill=COLOR_CYAN, font=f_sec_text)

    y_pos = 490
    for linea in info["der_val"].split("\n"):
        draw.text((1540, y_pos), linea, fill=COLOR_WHITE, font=f_sec_val)
        y_pos += 26

    draw.text((1540, y_pos + 20), "Ascendente Natal a 180°", fill=COLOR_MUTED, font=f_sec_val)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(output_path), "PNG")
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# 4. SELECTOR DE ASSETS DE LA BÓVEDA (B-ROLL)
# ─────────────────────────────────────────────────────────────────────────────

def seleccionar_broll_para_capitulo(cap_num: int, cantidad_max: int = 4) -> List[Path]:
    """
    Selecciona clips de video o imágenes atmosféricas de la Bóveda para alternar
    con la rueda técnica.
    """
    mapa_carpetas = {
        1: ["07_Espacio_Galaxias", "11_Humanos_Emociones", "09_Geometria_Sagrada"],
        2: ["02_Planetas", "03_Elementos_Fuego", "04_Elementos_Agua"],
        3: ["03_Elementos_Fuego", "05_Elementos_Tierra", "18_General_B_Roll"],
        4: ["07_Espacio_Galaxias", "09_Geometria_Sagrada", "12_Rituales_Magia"],
        5: ["13_Abstracto_Fluidos", "03_Elementos_Fuego", "04_Elementos_Agua"],
        6: ["07_Espacio_Galaxias", "09_Geometria_Sagrada", "10_Naturaleza_Paisajes"],
    }

    carpetas = mapa_carpetas.get(cap_num, ["07_Espacio_Galaxias"])
    candidatos: List[Path] = []

    # 1. Buscar primero videos MP4
    for carpeta in carpetas:
        dir_v = VAULT_VIDEOS_DIR / carpeta
        if dir_v.exists():
            candidatos.extend(list(dir_v.glob("*.mp4")))

    # 2. Si hay pocos videos, complementar con imágenes JPG/PNG
    if len(candidatos) < cantidad_max:
        for carpeta in carpetas:
            dir_img = VAULT_IMAGES_DIR / carpeta
            if dir_img.exists():
                candidatos.extend(list(dir_img.glob("*.jpg")))
                candidatos.extend(list(dir_img.glob("*.png")))

    # Mezclar con semilla determinística por capítulo
    rng = random.Random(cap_num * 97)
    rng.shuffle(candidatos)

    seleccion = candidatos[:cantidad_max]
    return seleccion


# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPOSITOR DE TIMELINE Y RENDERIZADOR FFmpeg
# ─────────────────────────────────────────────────────────────────────────────

def renderizar_capitulo(
    cap_info: Dict,
    audio_mp3: Path,
    duracion_audio: float,
    placa_png: Path,
    biwheel_frame_png: Path,
    output_mp4: Path,
    preview: bool = False
) -> Path:
    """
    Renderiza un capítulo individual en MP4 (1080p @ 25fps) coordinado con el audio.
    Alterna rítmicamente: Placa (3.5s) → Bi-Wheel (14s) → B-Roll (10s) → Bi-Wheel (14s)...
    """
    duracion_real = min(15.0, duracion_audio) if preview else duracion_audio
    print(f"🎬 Renderizando Capítulo {cap_info['num']}: {cap_info['titulo']} ({duracion_real:.1f}s)...")

    # Seleccionar B-Roll
    brolls = seleccionar_broll_para_capitulo(cap_info["num"], cantidad_max=4)

    # Construir lista de escenas visuales
    # Escena 0: Placa del capítulo (3.5s)
    # Escenas subsecuentes: Bi-Wheel (12-14s) alternando con B-Roll (8-10s)
    escenas: List[Dict] = []
    tiempo_acumulado = 0.0

    # 1. Placa inicial
    dur_placa = min(3.5, duracion_real)
    escenas.append({"tipo": "imagen", "path": placa_png, "duracion": dur_placa})
    tiempo_acumulado += dur_placa

    broll_idx = 0
    foco_rueda = True

    while tiempo_acumulado < duracion_real:
        tiempo_restante = duracion_real - tiempo_acumulado
        if foco_rueda or not brolls:
            dur_escena = min(14.0, tiempo_restante)
            escenas.append({"tipo": "imagen", "path": biwheel_frame_png, "duracion": dur_escena})
            tiempo_acumulado += dur_escena
            foco_rueda = False
        else:
            asset = brolls[broll_idx % len(brolls)]
            dur_escena = min(10.0, tiempo_restante)
            es_video = asset.suffix.lower() == ".mp4"
            escenas.append({
                "tipo": "video" if es_video else "imagen",
                "path": asset,
                "duracion": dur_escena
            })
            tiempo_acumulado += dur_escena
            broll_idx += 1
            foco_rueda = True

    # Renderizar cada micro-escena en un fragmento TS temporal (evita saturación de RAM)
    temp_dir = output_mp4.parent / f"temp_cap_{cap_info['num']}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    ts_files = []

    for i, esc in enumerate(escenas):
        ts_out = temp_dir / f"scene_{i:02d}.ts"
        ts_files.append(ts_out)
        d = esc["duracion"]
        p = str(esc["path"])

        if esc["tipo"] == "imagen":
            cmd_scene = [
                "ffmpeg", "-y",
                "-loop", "1", "-t", f"{d:.3f}", "-i", p,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x080b12,fps=25",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                str(ts_out)
            ]
        else:
            cmd_scene = [
                "ffmpeg", "-y",
                "-t", f"{d:.3f}", "-i", p,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                "-an",
                str(ts_out)
            ]

        r = subprocess.run(cmd_scene, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Error renderizando micro-escena {i}:\n{r.stderr[-400:]}")

    # Concatenar todos los fragmentos TS y muxear con el audio final
    concat_list_txt = temp_dir / "scenes_list.txt"
    with open(concat_list_txt, "w", encoding="utf-8") as f:
        for ts in ts_files:
            f.write(f"file '{ts.resolve()}'\n")

    cmd_mux = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list_txt),
        "-t", f"{duracion_real:.3f}", "-i", str(audio_mp3),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_mp4)
    ]

    r = subprocess.run(cmd_mux, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg falló al compilar capítulo {cap_info['num']}:\n{r.stderr[-600:]}")

    # Limpiar fragmentos temporales
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"   ✅ Capítulo {cap_info['num']} generado: {output_mp4.name} ({_probe_duration(output_mp4):.1f}s)")
    return output_mp4


# ─────────────────────────────────────────────────────────────────────────────
# 6. CONCATENACIÓN LOSSLESS FINAL (CONCAT DEMUXER)
# ─────────────────────────────────────────────────────────────────────────────

def concatenar_capitulos(lista_mp4s: List[Path], output_final_mp4: Path) -> Path:
    """
    Fusiona los 6 capítulos generados sin recodificación (-c copy) en segundos.
    """
    print(f"🔗 Fusionando {len(lista_mp4s)} capítulos en video maestro final...")
    concat_txt = output_final_mp4.parent / "concat_chapters.txt"

    with open(concat_txt, "w", encoding="utf-8") as f:
        for mp4 in lista_mp4s:
            f.write(f"file '{mp4.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(output_final_mp4)
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg concat falló:\n{r.stderr[-500:]}")

    if concat_txt.exists():
        concat_txt.unlink()

    dur_total = _probe_duration(output_final_mp4)
    print(f"🏆 ¡VIDEO FINAL RENDERIZADO CON ÉXITO!")
    print(f"   📍 Ruta: {output_final_mp4}")
    print(f"   ⏱️  Duración total: {dur_total:.1f}s ({dur_total / 60:.1f} min)")
    return output_final_mp4


# ─────────────────────────────────────────────────────────────────────────────
# 7. ORQUESTADOR PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def procesar_video_revolucion_solar(
    guion_path: Path,
    biwheel_path: Path,
    output_dir: Optional[Path] = None,
    preview: bool = False,
    capitulo_especifico: Optional[int] = None
) -> Path:
    """
    Ejecuta el pipeline completo de renderizado de video para una Revolución Solar.
    """
    if output_dir is None:
        output_dir = guion_path.parent / "video_render"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parsear guion
    metadata, capitulos = parsear_guion_rs(guion_path)
    consultante = metadata.get("consultante", "Consultante")
    año = metadata.get("año", "2026")

    print("\n" + "═" * 70)
    print(f"🚀 INICIANDO RENDERIZADOR PREMIUM DE REVOLUCIÓN SOLAR ({año})")
    print(f"   Consultante: {consultante}")
    print(f"   Modo: {'PREVIEW RÁPIDO (15s por cap)' if preview else 'PRODUCCIÓN COMPLETA'}")
    print(f"   Directorio de trabajo: {output_dir}")
    print("═" * 70 + "\n")

    # Filtrar capítulos si se solicitó uno específico
    if capitulo_especifico:
        capitulos = [c for c in capitulos if c["num"] == capitulo_especifico]
        if not capitulos:
            raise ValueError(f"No se encontró el capítulo {capitulo_especifico} en el guion.")

    mp4_capitulos = []

    for cap in capitulos:
        c_num = cap["num"]
        print(f"\n▶️  Procesando Capítulo {c_num}: {cap['titulo']}")

        # Rutas de trabajo del capítulo
        voz_raw_mp3    = output_dir / f"cap_{c_num}_voz_raw.mp3"
        audio_mixed_mp3 = output_dir / f"cap_{c_num}_audio.mp3"
        placa_png      = output_dir / f"cap_{c_num}_placa.png"
        biwheel_png    = output_dir / f"cap_{c_num}_biwheel_foco.png"
        cap_mp4        = output_dir / f"capitulo_{c_num}.mp4"

        # A. Síntesis de voz (reutiliza si ya fue sintetizado)
        if voz_raw_mp3.exists() and voz_raw_mp3.stat().st_size > 1000 and _probe_duration(voz_raw_mp3) > 1.0:
            dur_voz = _probe_duration(voz_raw_mp3)
            print(f"   ℹ️  Reutilizando voz existente: {voz_raw_mp3.name} ({dur_voz:.1f}s)")
        else:
            dur_voz = sintetizar_voz_capitulo(cap["locucion"], voz_raw_mp3)

        # B. Mezcla de ambiente sonoro
        if audio_mixed_mp3.exists() and audio_mixed_mp3.stat().st_size > 1000 and _probe_duration(audio_mixed_mp3) > 1.0:
            print(f"   ℹ️  Reutilizando audio mezclado existente: {audio_mixed_mp3.name}")
        else:
            mezclar_audio_con_ambiente(voz_raw_mp3, audio_mixed_mp3, dur_voz)

        # C. Generación de placa de inicio
        generar_placa_capitulo(c_num, cap["titulo"], consultante, placa_png)

        # D. Generación de marco Bi-Wheel focalizado (Regla 8)
        generar_marco_biwheel_pedagogico(biwheel_path, c_num, cap["titulo"], consultante, biwheel_png)

        # E. Compilación FFmpeg del capítulo
        renderizar_capitulo(
            cap_info=cap,
            audio_mp3=audio_mixed_mp3,
            duracion_audio=dur_voz,
            placa_png=placa_png,
            biwheel_frame_png=biwheel_png,
            output_mp4=cap_mp4,
            preview=preview
        )

        mp4_capitulos.append(cap_mp4)

    # Si se procesaron varios capítulos, fusionar en video maestro
    nombre_limpio = re.sub(r"[^\w]", "_", consultante).upper()
    video_final_mp4 = output_dir / f"REVOLUCION_SOLAR_{nombre_limpio}_{año}.mp4"

    if len(mp4_capitulos) > 1:
        concatenar_capitulos(mp4_capitulos, video_final_mp4)
        return video_final_mp4
    else:
        return mp4_capitulos[0]


# ─────────────────────────────────────────────────────────────────────────────
# CLI ENTRY-POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Motor de renderizado de video cinematográfico de Revolución Solar (16:9 Widescreen)."
    )
    parser.add_argument("--guion", required=True, type=Path, help="Ruta al archivo Markdown del guion.")
    parser.add_argument("--biwheel", required=True, type=Path, help="Ruta al archivo PNG de la rueda Bi-Wheel.")
    parser.add_argument("--output_dir", type=Path, default=None, help="Directorio de salida para los renders.")
    parser.add_argument("--preview", action="store_true", help="Modo preview rápido (15s por capítulo).")
    parser.add_argument("--capitulo", type=int, default=None, choices=range(1, 7), help="Renderizar solo el capítulo N (1-6).")

    args = parser.parse_args()

    try:
        procesar_video_revolucion_solar(
            guion_path=args.guion,
            biwheel_path=args.biwheel,
            output_dir=args.output_dir,
            preview=args.preview,
            capitulo_especifico=args.capitulo
        )
    except Exception as e:
        print(f"\n❌ ERROR EN RENDERIZADO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
