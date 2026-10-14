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
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# ── Constantes y Rutas Maestras ───────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from products.revolucion_solar.graficador_biwheel import GraficadorBiWheelAstrologica

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
    output_path: Path,
    foco_info: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Enmarca la rueda Bi-Wheel (2600x2600) en un lienzo 1920x1080 con bandas pedagógicas
    laterales que explican el foco del capítulo (Regla 8 y 11 de PROJECT_RULES.md).
    """
    canvas = _crear_fondo_estelar(1920, 1080)

    # Cargar y redimensionar rueda Bi-Wheel a 1040x1040 para centrarla en 1080 de alto
    if biwheel_path.exists():
        rueda_raw = Image.open(biwheel_path).convert("RGBA")
        rueda_resized = rueda_raw.resize((1040, 1040), Image.Resampling.LANCZOS)
        # Posición centrada horizontalmente: x = (1920 - 1040) / 2 = 440, y = 20
        canvas.paste(rueda_resized, (440, 20), rueda_resized)
    else:
        draw_temp = ImageDraw.Draw(canvas)
        draw_temp.rectangle([440, 20, 1480, 1060], outline=COLOR_GOLD, width=3)

    draw = ImageDraw.Draw(canvas)

    try:
        f_sec_title = ImageFont.truetype(FONT_TITLE_PATH, 24)
        f_sec_text  = ImageFont.truetype(FONT_BODY_PATH, 18)
        f_sec_val   = ImageFont.truetype(FONT_BODY_PATH, 16)
    except Exception:
        f_sec_title = f_sec_text = f_sec_val = ImageFont.load_default()

    izq_tag = foco_info.get("izq_tag", f"CAPÍTULO {cap_num}") if foco_info else f"CAPÍTULO {cap_num}"
    izq_val = foco_info.get("izq_val", titulo) if foco_info else titulo
    der_tag = foco_info.get("der_tag", "ANÁLISIS BI-WHEEL") if foco_info else "ANÁLISIS BI-WHEEL"
    der_val = foco_info.get("der_val", "Interior: Natal\nExterior: RS 2026") if foco_info else "Interior: Natal\nExterior: RS 2026"

    # ── PANEL LATERAL IZQUIERDO (x: 40 a 400) ─────────────────────────────────
    draw.line([(40, 380), (40, 700)], fill=COLOR_GOLD, width=3)
    draw.text((60, 400), f"CAPÍTULO {cap_num}", fill=COLOR_GOLD, font=f_sec_title)
    draw.text((60, 440), izq_tag, fill=COLOR_CYAN, font=f_sec_text)

    y_pos = 490
    for linea in izq_val.split("\n"):
        draw.text((60, y_pos), linea, fill=COLOR_WHITE, font=f_sec_val)
        y_pos += 26

    draw.text((60, y_pos + 20), f"Consultante: {consultante}", fill=COLOR_MUTED, font=f_sec_val)

    # ── PANEL LATERAL DERECHO (x: 1520 a 1880) ────────────────────────────────
    draw.line([(1520, 380), (1520, 700)], fill=COLOR_GOLD, width=3)
    draw.text((1540, 400), "ANÁLISIS BI-WHEEL", fill=COLOR_GOLD, font=f_sec_title)
    draw.text((1540, 440), der_tag, fill=COLOR_CYAN, font=f_sec_text)

    y_pos = 490
    for linea in der_val.split("\n"):
        draw.text((1540, y_pos), linea, fill=COLOR_WHITE, font=f_sec_val)
        y_pos += 26

    draw.text((1540, y_pos + 20), "Ascendente Natal a 180°", fill=COLOR_MUTED, font=f_sec_val)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(output_path), "PNG")
    return output_path


def obtener_focos_capitulo(cap_num: int, cap_info: Dict, datos_rs: Optional[Dict]) -> List[Dict[str, Any]]:
    """
    Retorna la lista de focos temáticos y planetarios para un capítulo según sus datos astrológicos.
    Permite alternar entre los puntos de mayor relieve mencionados por la locución.
    """
    if not datos_rs or "revolucion_solar" not in datos_rs or "carta_natal" not in datos_rs:
        return [{
            "tipo": "general", "titulo": "CARTA BI-WHEEL", "subtitulo": "Mapa Anual Completo",
            "izq_tag": "MAPA DEL AÑO", "izq_val": "Interior: Natal\nExterior: RS",
            "der_tag": "TERRITORIO", "der_val": "Ciclo Anual"
        }]

    natal = datos_rs["carta_natal"]
    rs = datos_rs["revolucion_solar"]
    planetas_rs = rs.get("planetas_rs", {})
    angulos_rs = rs.get("angulos_rs", {})
    casa_portal = rs.get("superposicion_clave", {}).get("ascendente_rs_en_casa_natal", {}).get("casa_natal", 1)
    asc_rs_signo = angulos_rs.get("Ascendente_RS", {}).get("signo", "Aries")
    asc_rs_fmt = angulos_rs.get("Ascendente_RS", {}).get("formato", "")

    if cap_num == 1:
        return [
            {
                "tipo": "portal",
                "nombre": "AC_RS",
                "titulo": f"EL PORTAL: ASCENDENTE ANUAL EN {asc_rs_signo.upper()}",
                "subtitulo": f"Aterriza en tu Casa {casa_portal} Natal · {asc_rs_fmt}",
                "izq_tag": "PORTAL DEL AÑO",
                "izq_val": f"Ascendente RS en {asc_rs_signo}\nGrado: {asc_rs_fmt}",
                "der_tag": "ESCENARIO PROTAGONISTA",
                "der_val": f"Casa Natal {casa_portal}\nDemanda Concreta\nFoco y Presencia"
            },
            {
                "tipo": "casa",
                "casa": casa_portal,
                "titulo": f"ESCENARIO PROTAGONISTA: CASA {casa_portal} NATAL",
                "subtitulo": "El gran taller de manifestación y aprendizaje del año",
                "izq_tag": "ESCENARIO ACTIVO",
                "izq_val": f"Casa {casa_portal} Natal\nFuerzas Concentradas\nOrden y Soberanía",
                "der_tag": "DESAFÍO ANUAL",
                "der_val": "Poner el cuerpo\nSin abstracciones\nMaduración real"
            }
        ]
    elif cap_num == 2:
        sol_info = planetas_rs.get("Sol", {})
        luna_info = planetas_rs.get("Luna", {})
        return [
            {
                "tipo": "planeta",
                "nombre": "Sol",
                "titulo": f"SOL RS EN {sol_info.get('formato', 'Sol RS')}",
                "subtitulo": f"Propósito consciente del ciclo · Casa {sol_info.get('casa', '')} RS",
                "izq_tag": "PROPÓSITO CONSCIENTE",
                "izq_val": f"Sol en {sol_info.get('signo', '')} {sol_info.get('grado_en_signo', '')}°\nCasa {sol_info.get('casa', '')} Anual",
                "der_tag": "DIRECCIÓN SOLAR",
                "der_val": "Voluntad y lucidez\nExpresión de verdad\nSin concesiones"
            },
            {
                "tipo": "planeta",
                "nombre": "Luna",
                "titulo": f"LUNA RS EN {luna_info.get('formato', 'Luna RS')}",
                "subtitulo": f"El pulso emocional y reactivo del año · Casa {luna_info.get('casa', '')} RS",
                "izq_tag": "PULSO EMOCIONAL",
                "izq_val": f"Luna en {luna_info.get('signo', '')} {luna_info.get('grado_en_signo', '')}°\nCasa {luna_info.get('casa', '')} Anual",
                "der_tag": "NECESIDAD VISCERAL",
                "der_val": "Respuesta inmediata\nDrenaje de tensión\nLímites claros"
            }
        ]
    elif cap_num == 3:
        marte_info = planetas_rs.get("Marte", {})
        venus_info = planetas_rs.get("Venus", {})
        return [
            {
                "tipo": "planeta",
                "nombre": "Marte",
                "titulo": f"MARTE RS EN {marte_info.get('formato', 'Marte RS')}",
                "subtitulo": f"Vector de conquista, empuje y asertividad · Casa {marte_info.get('casa', '')} RS",
                "izq_tag": "IMPULSO Y ACCIÓN",
                "izq_val": f"Marte en {marte_info.get('signo', '')} {marte_info.get('grado_en_signo', '')}°\nCasa {marte_info.get('casa', '')} Anual",
                "der_tag": "MOTOR DE COMBATE",
                "der_val": "Iniciativa y coraje\nEnergía disponible\nSin postergaciones"
            },
            {
                "tipo": "planeta",
                "nombre": "Venus",
                "titulo": f"VENUS RS EN {venus_info.get('formato', 'Venus RS')}",
                "subtitulo": f"Pactos, valor personal y vínculos estratégicos · Casa {venus_info.get('casa', '')} RS",
                "izq_tag": "DESEO Y VÍNCULOS",
                "izq_val": f"Venus en {venus_info.get('signo', '')} {venus_info.get('grado_en_signo', '')}°\nCasa {venus_info.get('casa', '')} Anual",
                "der_tag": "ARMONÍA Y PACTOS",
                "der_val": "Negociación lúcida\nMagnetismo personal\nCuidado del valor"
            }
        ]
    elif cap_num == 4:
        saturno_info = planetas_rs.get("Saturno", {})
        jupiter_info = planetas_rs.get("Júpiter", {})
        return [
            {
                "tipo": "planeta",
                "nombre": "Saturno",
                "titulo": f"SATURNO RS EN {saturno_info.get('formato', 'Saturno RS')}",
                "subtitulo": f"Frontera de realidad, disciplina y maduración · Casa {saturno_info.get('casa', '')} RS",
                "izq_tag": "LEYES Y LÍMITES",
                "izq_val": f"Saturno en {saturno_info.get('signo', '')} {saturno_info.get('grado_en_signo', '')}°\nCasa {saturno_info.get('casa', '')} Anual",
                "der_tag": "ARQUITECTURA KÁRMICA",
                "der_val": "Construcción sólida\nPaciencia estratégica\nPago de peajes"
            },
            {
                "tipo": "planeta",
                "nombre": "Júpiter",
                "titulo": f"JÚPITER RS EN {jupiter_info.get('formato', 'Júpiter RS')}",
                "subtitulo": f"Expansión fértil, confianza y nuevos horizontes · Casa {jupiter_info.get('casa', '')} RS",
                "izq_tag": "HORIZONTE FÉRTIL",
                "izq_val": f"Júpiter en {jupiter_info.get('signo', '')} {jupiter_info.get('grado_en_signo', '')}°\nCasa {jupiter_info.get('casa', '')} Anual",
                "der_tag": "CRECIMIENTO REAL",
                "der_val": "Oportunidades vivas\nSentido de avance\nMultiplicación"
            }
        ]
    elif cap_num == 5:
        aspectos = rs.get("aspectos_intercartas", [])
        asp1 = aspectos[0] if len(aspectos) > 0 else {"aspecto": "Tensión", "cuerpo_rs": "Saturno", "cuerpo_natal": "Sol", "color": "#e74c3c"}
        asp2 = aspectos[1] if len(aspectos) > 1 else {"aspecto": "Fluidez", "cuerpo_rs": "Júpiter", "cuerpo_natal": "Luna", "color": "#2980b9"}
        return [
            {
                "tipo": "aspecto",
                "nombre": asp1.get("cuerpo_rs", ""),
                "titulo": f"ACTIVACIÓN ANUAL: {asp1.get('aspecto', '').upper()} {asp1.get('cuerpo_rs', '')} - {asp1.get('cuerpo_natal', '')}",
                "subtitulo": "Punto de fricción que cataliza maduración y enfoque",
                "izq_tag": "CABLE DE TENSIÓN",
                "izq_val": f"{asp1.get('cuerpo_rs', '')} RS ↔ {asp1.get('cuerpo_natal', '')} Natal\n{asp1.get('aspecto', '')}",
                "der_tag": "TRANSFORMACIÓN",
                "der_val": "Presión constructiva\nNo evadir el conflicto\nTemplar el carácter"
            },
            {
                "tipo": "aspecto",
                "nombre": asp2.get("cuerpo_rs", ""),
                "titulo": f"PUENTE ARMÓNICO: {asp2.get('aspecto', '').upper()} {asp2.get('cuerpo_rs', '')} - {asp2.get('cuerpo_natal', '')}",
                "subtitulo": "Vía de escape y fluidez disponible para destrabar el ciclo",
                "izq_tag": "CANAL DESPEJADO",
                "izq_val": f"{asp2.get('cuerpo_rs', '')} RS ↔ {asp2.get('cuerpo_natal', '')} Natal\n{asp2.get('aspecto', '')}",
                "der_tag": "RECURSO ACTIVO",
                "der_val": "Fluidez natural\nIntegración ágil\nRespira el mapa"
            }
        ]
    else:
        anio = rs.get("revolucion_solar", {}).get("anio", 2026)
        return [
            {
                "tipo": "general",
                "titulo": f"SÍNTESIS MAESTRA · REVOLUCIÓN SOLAR {anio}",
                "subtitulo": "Integración del mapa completo · Soberanía y madurez personal",
                "izq_tag": "MAPA COMPLETO",
                "izq_val": f"Revolución Solar {anio}\n12 Meses de Ciclo\nADN y Retorno",
                "der_tag": "SOBERANÍA",
                "der_val": "Las cartas marcan el suelo\nTu voluntad construye\nportaltarotmistico.com"
            }
        ]


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
# 5. COMPOSITOR DE TIMELINE Y RENDERIZADOR FFmpeg CON KEN BURNS DINÁMICO
# ─────────────────────────────────────────────────────────────────────────────

def renderizar_capitulo(
    cap_info: Dict,
    audio_mp3: Path,
    duracion_audio: float,
    placa_png: Path,
    biwheel_focos: List[Dict],
    output_mp4: Path,
    preview: bool = False
) -> Path:
    """
    Renderiza un capítulo individual en MP4 (1080p @ 25fps) coordinado con el audio.
    Alterna rítmicamente: Placa (3.5s) → Bi-Wheel con zoom focal (13s) → B-Roll (10s) → Bi-Wheel Foco 2 (13s)...
    Aplica efecto Ken Burns cinemático dirigido hacia las coordenadas calculadas de cada astro o casa.
    """
    duracion_real = min(20.0, duracion_audio) if preview else duracion_audio
    print(f"🎬 Renderizando Capítulo {cap_info['num']}: {cap_info['titulo']} ({duracion_real:.1f}s)...")

    # Seleccionar B-Roll
    brolls = seleccionar_broll_para_capitulo(cap_info["num"], cantidad_max=4)

    escenas: List[Dict] = []
    tiempo_acumulado = 0.0

    # 1. Placa inicial
    dur_placa = min(2.5 if preview else 3.5, duracion_real)
    escenas.append({"tipo": "placa", "path": placa_png, "duracion": dur_placa})
    tiempo_acumulado += dur_placa

    broll_idx = 0
    foco_idx = 0
    foco_rueda = True

    while tiempo_acumulado < duracion_real:
        tiempo_restante = duracion_real - tiempo_acumulado
        if foco_rueda or not brolls:
            dur_escena = min(8.0 if preview else 14.0, tiempo_restante)
            foco_item = biwheel_focos[foco_idx % len(biwheel_focos)]
            escenas.append({
                "tipo": "biwheel",
                "path_base": foco_item.get("path_base", foco_item.get("path")),
                "path_foco": foco_item.get("path_foco", foco_item.get("path")),
                "coords": foco_item.get("coords", {"x": 960, "y": 540}),
                "duracion": dur_escena
            })
            tiempo_acumulado += dur_escena
            foco_idx += 1
            foco_rueda = False
        else:
            asset = brolls[broll_idx % len(brolls)]
            dur_escena = min(6.0 if preview else 10.0, tiempo_restante)
            es_video = asset.suffix.lower() == ".mp4"
            escenas.append({
                "tipo": "video" if es_video else "imagen",
                "path": asset,
                "duracion": dur_escena
            })
            tiempo_acumulado += dur_escena
            broll_idx += 1
            foco_rueda = True

    # Renderizar cada micro-escena en un fragmento TS temporal
    temp_dir = output_mp4.parent / f"temp_cap_{cap_info['num']}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    ts_files = []

    for i, esc in enumerate(escenas):
        ts_out = temp_dir / f"scene_{i:02d}.ts"
        ts_files.append(ts_out)
        d = esc["duracion"]
        total_frames = max(25, int(d * 25))

        if esc["tipo"] == "biwheel":
            cx = esc["coords"].get("x", 960)
            cy = esc["coords"].get("y", 540)
            p_base = str(esc.get("path_base", esc.get("path_foco")))
            p_foco = str(esc.get("path_foco", esc.get("path_base")))

            # Curvas cinematográficas: zoom profundo a 1.75x con 5s de deslizamiento y aparición de efectos
            max_zoom = 1.75
            t_fade_start = 1.0
            t_fade_dur = 3.5 if not preview else 2.5
            t_zoom_start = 1.0
            t_zoom_dur = 5.0 if not preview else 3.8

            f_zoom_start = int(t_zoom_start * 25)
            f_zoom_dur = max(25, int(t_zoom_dur * 25))

            if p_base != p_foco and Path(p_base).exists() and Path(p_foco).exists():
                # Transición progresiva: comienza el mandala base y los efectos se encienden al acercarse la cámara
                fc = (
                    f"[0:v][1:v]blend=all_expr='A*(1-min(max((T-{t_fade_start})/{t_fade_dur},0),1))+B*min(max((T-{t_fade_start})/{t_fade_dur},0),1)'[merged];"
                    f"[merged]zoompan=z='1.0+{max_zoom - 1.0:.2f}*min(max((on-{f_zoom_start})/{f_zoom_dur},0),1)':"
                    f"x='(iw/2-(iw/zoom/2))+(( {cx} - iw/2)*(1-1/zoom))':"
                    f"y='(ih/2-(ih/zoom/2))+(( {cy} - ih/2)*(1-1/zoom))':"
                    f"d=1:s=1920x1080:fps=25[v]"
                )
                cmd_scene = [
                    "ffmpeg", "-y",
                    "-loop", "1", "-t", f"{d:.3f}", "-i", p_base,
                    "-loop", "1", "-t", f"{d:.3f}", "-i", p_foco,
                    "-filter_complex", fc,
                    "-map", "[v]",
                    "-frames:v", str(total_frames),
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    str(ts_out)
                ]
            else:
                vf = (
                    f"zoompan=z='1.0+{max_zoom - 1.0:.2f}*min(max((on-{f_zoom_start})/{f_zoom_dur},0),1)':"
                    f"x='(iw/2-(iw/zoom/2))+(( {cx} - iw/2)*(1-1/zoom))':"
                    f"y='(ih/2-(ih/zoom/2))+(( {cy} - ih/2)*(1-1/zoom))':"
                    f"d={total_frames}:s=1920x1080:fps=25"
                )
                cmd_scene = [
                    "ffmpeg", "-y",
                    "-i", p_foco,
                    "-vf", vf,
                    "-frames:v", str(total_frames),
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    str(ts_out)
                ]
        elif esc["tipo"] in ["imagen", "placa"]:
            p = str(esc["path"])
            # Ken Burns sutil para placas y fotos fijas de B-Roll (elimina tomas estáticas muertas)
            zoom_step = 0.05 / float(total_frames)
            vf = (
                f"zoompan=z='min(zoom+{zoom_step:.6f},1.05)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={total_frames}:s=1920x1080:fps=25"
            )
            cmd_scene = [
                "ffmpeg", "-y",
                "-i", p,
                "-vf", vf,
                "-frames:v", str(total_frames),
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                str(ts_out)
            ]
        else: # video
            p = str(esc["path"])
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
    datos_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    preview: bool = False,
    capitulo_especifico: Optional[int] = None
) -> Path:
    """
    Ejecuta el pipeline completo de renderizado de video para una Revolución Solar.
    Genera variantes de rueda Bi-Wheel con zoom dinámico Ken Burns y resaltado selectivo.
    """
    if output_dir is None:
        output_dir = guion_path.parent / "video_render"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parsear guion
    metadata, capitulos = parsear_guion_rs(guion_path)
    consultante = metadata.get("consultante", "Consultante")
    año = metadata.get("año", "2026")

    # 2. Cargar datos astrológicos si existen para activar los focos dinámicos
    datos_rs = None
    if datos_path and datos_path.exists():
        with open(datos_path, "r", encoding="utf-8") as f:
            datos_rs = json.load(f)
            print(f"📊 Datos astrológicos cargados desde: {datos_path.name}")
    else:
        candidatos_json = list(guion_path.parent.glob("datos_rs_*.json"))
        if candidatos_json:
            with open(candidatos_json[0], "r", encoding="utf-8") as f:
                datos_rs = json.load(f)
                print(f"📊 Datos astrológicos detectados automáticamente: {candidatos_json[0].name}")

    graficador = GraficadorBiWheelAstrologica() if (datos_rs and "carta_natal" in datos_rs and "revolucion_solar" in datos_rs) else None

    print("\n" + "═" * 70)
    print(f"🚀 INICIANDO RENDERIZADOR PREMIUM DE REVOLUCIÓN SOLAR ({año})")
    print(f"   Consultante: {consultante}")
    print(f"   Focos Dinámicos & Ken Burns: {'ACTIVADO (NASA Ephemeris)' if graficador else 'DESACTIVADO (Modo Fallback Estático)'}")
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
        voz_raw_mp3     = output_dir / f"cap_{c_num}_voz_raw.mp3"
        audio_mixed_mp3 = output_dir / f"cap_{c_num}_audio.mp3"
        placa_png       = output_dir / f"cap_{c_num}_placa.png"
        cap_mp4         = output_dir / f"capitulo_{c_num}.mp4"

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

        # D. Generación de marcos Bi-Wheel focalizados dinámicos (Regla 8 y 11)
        focos_cap = obtener_focos_capitulo(c_num, cap, datos_rs)
        biwheel_focos = []

        for f_idx, foco in enumerate(focos_cap):
            raw_base_png = output_dir / f"cap_{c_num}_rueda_base_{f_idx+1}.png"
            frame_base_png = output_dir / f"cap_{c_num}_biwheel_base_{f_idx+1}.png"
            raw_foco_png = output_dir / f"cap_{c_num}_rueda_raw_{f_idx+1}.png"
            frame_foco_png = output_dir / f"cap_{c_num}_biwheel_foco_{f_idx+1}.png"

            if graficador:
                # 1. Rueda base limpia (todo el mandala cósmico completo sin retícula de foco)
                graficador.generar_biwheel_con_foco(
                    carta_natal=datos_rs["carta_natal"],
                    carta_rs=datos_rs["revolucion_solar"],
                    output_path=str(raw_base_png),
                    foco=foco,
                    solo_base=True
                )
                # 2. Rueda con foco neón (resaltado aditivo con mira telescópica y aura)
                _, coords = graficador.generar_biwheel_con_foco(
                    carta_natal=datos_rs["carta_natal"],
                    carta_rs=datos_rs["revolucion_solar"],
                    output_path=str(raw_foco_png),
                    foco=foco
                )
            else:
                raw_base_png = biwheel_path
                raw_foco_png = biwheel_path
                coords = {"x": 960, "y": 540}

            # Marco pedagógico para la base
            generar_marco_biwheel_pedagogico(
                biwheel_path=raw_base_png,
                cap_num=c_num,
                titulo=cap["titulo"],
                consultante=consultante,
                output_path=frame_base_png,
                foco_info=foco
            )
            # Marco pedagógico para el foco
            generar_marco_biwheel_pedagogico(
                biwheel_path=raw_foco_png,
                cap_num=c_num,
                titulo=cap["titulo"],
                consultante=consultante,
                output_path=frame_foco_png,
                foco_info=foco
            )

            biwheel_focos.append({
                "path_base": frame_base_png,
                "path_foco": frame_foco_png,
                "coords": coords,
                "foco_info": foco
            })

        # E. Compilación FFmpeg del capítulo con Ken Burns dinámico
        renderizar_capitulo(
            cap_info=cap,
            audio_mp3=audio_mixed_mp3,
            duracion_audio=dur_voz,
            placa_png=placa_png,
            biwheel_focos=biwheel_focos,
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
    parser.add_argument("--datos", type=Path, default=None, help="Ruta al archivo JSON con los datos astrológicos (opcional, auto-detectado).")
    parser.add_argument("--output_dir", type=Path, default=None, help="Directorio de salida para los renders.")
    parser.add_argument("--preview", action="store_true", help="Modo preview rápido (15s por capítulo).")
    parser.add_argument("--capitulo", type=int, default=None, choices=range(1, 7), help="Renderizar solo el capítulo N (1-6).")

    args = parser.parse_args()

    try:
        procesar_video_revolucion_solar(
            guion_path=args.guion,
            biwheel_path=args.biwheel,
            datos_path=args.datos,
            output_dir=args.output_dir,
            preview=args.preview,
            capitulo_especifico=args.capitulo
        )
    except Exception as e:
        print(f"\n❌ ERROR EN RENDERIZADO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

