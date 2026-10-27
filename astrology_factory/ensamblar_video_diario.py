#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ensamblar_video_diario.py
─────────────────────────────────────────────────────────────────────────────
ORQUESTADOR MAESTRO DE PRODUCCIÓN DE VIDEO DIARIO — EL GLIFO MAESTRO

Ejecuta el pipeline end-to-end de forma 100% automatizada:
  1. Guion Editorial con Gemini (ROLE_SCRIPTWRITER.md · Tono lúcido/clínico)
  2. Locución Neural con Edge-TTS (es-AR-ElenaNeural / es-MX-JorgeNeural)
  3. Subtitulado ASS Karaoke sincronizado con Whisper local
  4. Selección de Assets con La Nodriza Visual (Filtrado estricto anti-baneo)
  5. Ensamblaje FFmpeg Single-Pass con Marca de Agua del Reloj Astrológico

Uso:
  python3 ensamblar_video_diario.py
  python3 ensamblar_video_diario.py --fecha 2026-10-27
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import time
import argparse
import asyncio
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

import google.genai as genai
import edge_tts
import whisper

# Módulos internos
from content_factory.subtitle_generator import generate_ass
from content_factory.video_maker import create_video

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
ROLE_PATH = FACTORY_ROOT / "content_factory" / "ROLE_SCRIPTWRITER.md"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; BOLD = "\033[1m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")
def ok(msg): log(f"✅ {msg}", VERDE)
def info(msg): log(f"ℹ️  {msg}", CYAN)
def warn(msg): log(f"⚠️  {msg}", AMARILLO)
def err(msg): log(f"❌ {msg}", ROJO)


def cargar_adn():
    with open(ADN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generar_guion_editorial(adn: dict) -> dict:
    """Genera el guion estructurado de 5 tomas usando Gemini y ROLE_SCRIPTWRITER.md"""
    info("Generando guion con Gemini bajo rol editorial clínico y visceral...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no encontrada en .env")

    client = genai.Client(api_key=api_key)

    with open(ROLE_PATH, "r", encoding="utf-8") as f:
        role_prompt = f.read()

    transito = adn["transito"]
    prompt = f"""
{role_prompt}

DATOS DEL TRÁNSITO ACTIVO PARA EL GUION:
- Evento: {adn['produccion']['evento_titulo']} ({adn['produccion']['fecha_publicacion']})
- Planetas: {transito['planeta']} ({transito['simbolo_planetario']})
- Signos: {transito['signo_destino']} ({transito['simbolo_signo']})
- Aspecto: {transito['tipo_aspecto']}
- Descripción Clave: {transito['descripcion_breve']}
- Arquetipos: {adn['arquetipos']['primario']} / {adn['arquetipos']['secundario']}

REQUERIMIENTO:
Redacta un guion de EXACTAMENTE 5 tomas para un video vertical de ~38-40 segundos.

REGLA CRÍTICA PARA TOMA 5 (CTA COMERCIAL DE VENTA DIRECTA):
- PROHIBIDO divagar con preguntas existenciales o poéticas (CERO "¿dónde te duele?", CERO "mira tu carta" sin dirección).
- DEBES VENDER DIRECTAMENTE: Indica al espectador que vaya al enlace del perfil, ingrese fecha y hora exacta, y calcule o descargue su mapa astral completo.
- Ejemplo obligado de referencia: "Andá al link de mi perfil, ingresá tu fecha y hora exacta, y descubrí qué casa te activa este tránsito hoy."

Formato de respuesta: ÚNICAMENTE un bloque JSON válido con esta estructura:
{{
  "tomas": [
    {{ "num": 1, "rol": "gancho", "duracion_max_s": 7, "texto": "..." }},
    {{ "num": 2, "rol": "efecto_cuerpo_emocion", "duracion_max_s": 9, "texto": "..." }},
    {{ "num": 3, "rol": "mecanica_astrologica", "duracion_max_s": 9, "texto": "..." }},
    {{ "num": 4, "rol": "afrontarlo_constructivamente", "duracion_max_s": 9, "texto": "..." }},
    {{ "num": 5, "rol": "cta", "duracion_max_s": 6, "texto": "..." }}
  ]
}}
"""

    modelos_candidatos = [
        adn.get("gemini_vision", {}).get("modelo", "gemini-3.5-flash-lite"),
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite"
    ]

    resp = None
    for mod in modelos_candidatos:
        try:
            resp = client.models.generate_content(
                model=mod,
                contents=prompt
            )
            break
        except Exception as ex:
            warn(f"Modelo {mod} falló: {ex}. Probando siguiente...")

    if resp is None:
        raise RuntimeError("No se pudo generar el guion con ninguno de los modelos de Gemini.")

    clean_text = resp.text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]

    guion_data = json.loads(clean_text.strip())
    ok(f"Guion generado con {len(guion_data.get('tomas', []))} tomas.")
    return guion_data


async def sintetizar_audio_async(texto_completo: str, voz: str, output_path: Path):
    communicate = edge_tts.Communicate(texto_completo, voz, rate="+6%")
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])


def generar_audio_y_subtitulos(adn: dict, guion: dict) -> tuple[Path, Path, Path]:
    """Sintetiza la narración y genera el timeline y subtítulos ASS con Whisper."""
    info("Sintetizando locución con Edge-TTS...")
    evento_id = adn["produccion"]["evento_id"]
    voz = adn["audio"]["voz_tts"]["voz"]

    tomas = guion["tomas"]
    texto_completo = " ".join(t["texto"].strip() for t in tomas)

    paths = adn["assets"]["paths"]
    audio_dir = Path(paths["audio_master"])
    sub_dir = Path(paths["subtitulos"])
    timeline_dir = Path(paths["timeline_huecos"])
    guiones_dir = Path(paths["guiones"])

    for d in [audio_dir, sub_dir, timeline_dir, guiones_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Guardar guion en disco
    guion_json = guiones_dir / f"{evento_id}.json"
    with open(guion_json, "w", encoding="utf-8") as f:
        json.dump(guion, f, indent=2, ensure_ascii=False)

    # 2. Generar MP3
    mp3_path = audio_dir / f"{evento_id}.mp3"
    asyncio.run(sintetizar_audio_async(texto_completo, voz, mp3_path))
    ok(f"Audio sintetizado: {mp3_path.name}")

    # 3. Transcribir con Whisper y generar subtítulos ASS
    info("Transcribiendo audio y alineando subtítulos karaoke con Whisper...")
    model_name = adn["audio"].get("whisper", {}).get("modelo", "base")
    model = whisper.load_model(model_name)
    result = model.transcribe(str(mp3_path), language="es", word_timestamps=True)

    ass_path = sub_dir / f"{evento_id}.ass"
    generate_ass(str(mp3_path), modelo=model_name)
    ok(f"Subtítulos generados: {ass_path.name}")

    # 4. Crear timeline_huecos con timestamps reales
    dur_total = result.get("segments", [{}])[-1].get("end", 38.0)
    dur_por_toma = dur_total / len(tomas)

    timeline_tomas = []
    acumulado = 0.0
    for i, t in enumerate(tomas):
        dur = dur_por_toma
        fin = acumulado + dur
        timeline_tomas.append({
            "num": t["num"],
            "num_toma": t["num"],
            "rol": t["rol"],
            "inicio_ms": int(acumulado * 1000),
            "fin_ms": int(fin * 1000),
            "duracion_ms": int(dur * 1000),
            "duracion_s": round(dur, 2),
            "texto": t["texto"],
            "etiqueta_visual": None,
            "emocion": adn["arquetipos"]["emocion_dominante"]
        })
        acumulado = fin

    timeline_data = {
        "evento_id": evento_id,
        "semana": adn["produccion"]["semana_prefijo"],
        "duracion_total_s": round(dur_total, 2),
        "tomas": timeline_tomas
    }

    timeline_path = timeline_dir / f"{evento_id}.json"
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)
    ok(f"Timeline sincronizado: {timeline_path.name} ({dur_total:.1f}s)")

    return mp3_path, ass_path, timeline_path


def ejecutar_nodriza_y_validador(adn: dict):
    """Ejecuta Célula 2: Nodriza Visual y Validador de Ensamble"""
    info("Lanzando La Nodriza Visual (Selección en base de datos visual)...")
    nodriza_script = FACTORY_ROOT / "v2" / "celula_2" / "nodriza_visual.py"
    validador_script = FACTORY_ROOT / "v2" / "celula_2" / "validador_de_ensamble.py"

    import subprocess
    cmd_nodriza = [sys.executable, str(nodriza_script)]
    r = subprocess.run(cmd_nodriza, capture_output=True, text=True)
    if r.returncode != 0:
        err(f"Fallo en nodriza_visual.py: {r.stderr}")
        sys.exit(1)
    ok("Nodriza Visual completó la asignación de cortes sin errores.")

    info("Validando lista de cortes y gapless slots...")
    cmd_val = [sys.executable, str(validador_script), "--opcion", "3"]
    r_val = subprocess.run(cmd_val, capture_output=True, text=True)
    if r_val.returncode != 0:
        err(f"Fallo en validador_de_ensamble.py: {r_val.stderr}")
        sys.exit(1)
    ok("Lista de corte validada lista para FFmpeg single-pass.")


def main():
    parser = argparse.ArgumentParser(description="Ensamblador Maestro de Video Diario")
    parser.add_argument("--fecha", help="Fecha del video (AAAA-MM-DD)")
    args = parser.parse_args()

    print(f"\n{BOLD}{MAGENTA}╔════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{MAGENTA}║      EL GLIFO MAESTRO — ENSAMBLADOR DE VIDEO DIARIO V2        ║{RESET}")
    print(f"{BOLD}{MAGENTA}╚════════════════════════════════════════════════════════════════╝{RESET}\n")

    adn = cargar_adn()
    if args.fecha:
        adn["produccion"]["fecha_publicacion"] = args.fecha
        adn["produccion"]["evento_id"] = f"{args.fecha}_Transito_Diario"

    evento = adn["produccion"]["evento_id"]
    titulo = adn["produccion"]["evento_titulo"]
    fecha = adn["produccion"]["fecha_publicacion"]

    info(f"Producción activa: {BOLD}{titulo}{RESET} (ID: {evento} · Fecha: {fecha})")

    # Paso 1: Guion
    guion = generar_guion_editorial(adn)

    # Paso 2: Audio & Whisper
    generar_audio_y_subtitulos(adn, guion)

    # Paso 3: Nodriza Visual & Validador
    ejecutar_nodriza_y_validador(adn)

    # Paso 4: Renderizado FFmpeg Single-Pass con Watermark del Reloj
    info("Ensamblando video final con FFmpeg single-pass y sello de marca...")
    video_final = create_video(evento)

    if video_final and Path(video_final).is_file():
        size_mb = Path(video_final).stat().st_size / (1024 * 1024)
        print(f"\n{BOLD}{VERDE}🎉 VIDEO GENERADO CON ÉXITO:{RESET}")
        print(f"📁 Ruta: {BOLD}{video_final}{RESET}")
        print(f"📦 Tamaño: {size_mb:.2f} MB")
        print(f"⏱  Sello de Marca: Reloj Astrológico Activo en Esquina Superior")
    else:
        err("El proceso de ensamble final falló.")
        sys.exit(1)


if __name__ == "__main__":
    main()
