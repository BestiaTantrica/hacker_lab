#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
produccion_batch_semana.py
─────────────────────────────────────────────────────────────────────────────
Orquestador Batch para Ensamblar los Videos Diarios de la Semana:
- 2026-10-30: Mercurio Retrógrado en Cuadratura Partil con Marte
- 2026-10-31: Noche de Samhain: Luna en Cáncer Trígono Mercurio Retrógrado
- 2026-11-01: Luna en Leo en Oposición a Plutón en Acuario (Cuarto Menguante)

Flujo por cada día:
1. Actualiza contexto_astrologico.json (ADN) con el tránsito específico.
2. Copia guión, audio y metadata a las carpetas maestras del Vault.
3. Transcribe con Whisper local y genera timeline_huecos + subtítulos ASS.
4. Ejecuta Nodriza Visual (selección DB-first) y Validador de Ensamble.
5. Renderiza con create_video (FFmpeg single-pass con marca de agua).
6. Copia el FINAL_{evento_id}.mp4 a produccion/semana_29oct_01nov/.
7. Actualiza produccion/registro_publicaciones.json.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

import whisper
from content_factory.subtitle_generator import generate_ass
from content_factory.video_maker import create_video

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
OUTPUT_DIR = FACTORY_ROOT / "produccion" / "semana_29oct_01nov"
REGISTRO_PATH = FACTORY_ROOT / "produccion" / "registro_publicaciones.json"

RESET = "\033[0m"; VERDE = "\033[92m"; ROJO = "\033[91m"
CYAN = "\033[96m"; AMARILLO = "\033[93m"; MAGENTA = "\033[95m"; BOLD = "\033[1m"

def log(msg, color=RESET): print(f"{color}{msg}{RESET}")
def ok(msg): log(f"✅ {msg}", VERDE)
def info(msg): log(f"ℹ️  {msg}", CYAN)
def warn(msg): log(f"⚠️  {msg}", AMARILLO)
def err(msg): log(f"❌ {msg}", ROJO)

DIAS_PRODUCCION = [
    {
        "fecha": "2026-10-30",
        "evento_id": "2026-10-30_Mercurio_Cuadratura_Partil_Marte",
        "titulo": "Clímax de Tensión: Mercurio Retrógrado en Cuadratura Partil Exacta a Marte",
        "planeta": "Mercurio/Marte",
        "simbolos": "☿(R)/♂",
        "signos": "Escorpio/Leo",
        "aspecto": "cuadratura",
        "intensidad": "alta",
        "orbe": "0.32°",
        "arquetipo_primario": "La Navaja Mental",
        "arquetipo_secundario": "Purga de la Sombra",
        "emocion": "tension",
        "elemento": "Agua/Fuego",
        "modalidad": "Fija",
        "planeta_regente": "Pluton/Sol",
        "simbolo_regente": "♇/☉",
        "descripcion": "El ángulo de tensión entre la mente escorpiana y el impulso leonino alcanza su orbe exacto de 0.32 grados. El Sol en Escorpio hace trígono a la Luna en Cáncer: lo que reprimías durante meses sale a la superficie. Si no lo verbalizas con conciencia, estalla en impulsos.",
        "palabras_clave": ["tension", "climax", "mente", "veneno", "escorpio", "fuego", "partil", "sombra"]
    },
    {
        "fecha": "2026-10-31",
        "evento_id": "2026-10-31_Samhain_Luna_Trigono_Mercurio",
        "titulo": "Noche de Samhain: Luna en Cáncer en Trígono con Mercurio Retrógrado en Escorpio",
        "planeta": "Luna/Mercurio",
        "simbolos": "☽/☿(R)",
        "signos": "Cáncer/Escorpio",
        "aspecto": "trigono",
        "intensidad": "alta",
        "orbe": "3.17°",
        "arquetipo_primario": "El Desgarro del Velo Psíquico",
        "arquetipo_secundario": "Memoria Ancestral",
        "emocion": "misterio",
        "elemento": "Agua",
        "modalidad": "Cardinal/Fija",
        "planeta_regente": "Luna/Pluton",
        "simbolo_regente": "☽/♇",
        "descripcion": "En la noche sagrada de Samhain, la Luna en Cáncer conecta en trígono fluido con Mercurio retrógrado en Escorpio. Se rasga el velo: emergen memorias del linaje, pactos tácitos y certezas que no necesitan palabras. Noche de transmutación y silencio consciente.",
        "palabras_clave": ["samhain", "agua", "luna", "escorpio", "velo", "linaje", "silencio", "ancestros"]
    },
    {
        "fecha": "2026-11-01",
        "evento_id": "2026-11-01_Luna_Oposicion_Pluton_Cuarto_Menguante",
        "titulo": "Luna en Leo en Oposición a Plutón en Acuario (Cuarto Menguante)",
        "planeta": "Luna/Pluton",
        "simbolos": "☽/♇",
        "signos": "Leo/Acuario",
        "aspecto": "oposicion",
        "intensidad": "alta",
        "orbe": "1.37°",
        "arquetipo_primario": "El Trono Personal",
        "arquetipo_secundario": "La Colmena Colectiva",
        "emocion": "desapego",
        "elemento": "Fuego/Aire",
        "modalidad": "Fija",
        "planeta_regente": "Sol/Urano",
        "simbolo_regente": "☉/♅",
        "descripcion": "La Luna entra en Leo y choca en oposición directa con Plutón en Acuario mientras cuadra al Sol. El Cuarto Menguante exige soltar la necesidad de validación y aplauso externo. Se desmorona el personaje para dar lugar a una soberanía real y despojada.",
        "palabras_clave": ["menguante", "pluton", "soberania", "trono", "fuego", "aire", "aplauso", "personaje"]
    }
]


def actualizar_adn_para_evento(dia: dict) -> dict:
    """Actualiza contexto_astrologico.json con los datos del día."""
    with open(ADN_PATH, "r", encoding="utf-8") as f:
        adn = json.load(f)

    adn["produccion"]["evento_id"] = dia["evento_id"]
    adn["produccion"]["evento_titulo"] = dia["titulo"]
    adn["produccion"]["fecha_publicacion"] = dia["fecha"]
    adn["produccion"]["semana_prefijo"] = "Oct_W4"

    adn["transito"]["planeta"] = dia["planeta"]
    adn["transito"]["simbolo_planetario"] = dia["simbolos"]
    adn["transito"]["signo_destino"] = dia["signos"]
    adn["transito"]["simbolo_signo"] = dia["signos"]
    adn["transito"]["tipo_aspecto"] = dia["aspecto"]
    adn["transito"]["intensidad"] = dia["intensidad"]
    adn["transito"]["fecha_exacta"] = dia["fecha"]
    adn["transito"]["descripcion_breve"] = dia["descripcion"]
    adn["transito"]["palabras_clave"] = dia["palabras_clave"]

    adn["arquetipos"]["primario"] = dia["arquetipo_primario"]
    adn["arquetipos"]["secundario"] = dia["arquetipo_secundario"]
    adn["arquetipos"]["emocion_dominante"] = dia["emocion"]
    adn["arquetipos"]["elemento"] = dia["elemento"]
    adn["arquetipos"]["modalidad"] = dia["modalidad"]
    adn["arquetipos"]["planeta_regente"] = dia["planeta_regente"]
    adn["arquetipos"]["simbolo_regente"] = dia["simbolo_regente"]

    with open(ADN_PATH, "w", encoding="utf-8") as f:
        json.dump(adn, f, indent=2, ensure_ascii=False)

    ok(f"ADN actualizado para {dia['evento_id']}")
    return adn


def procesar_audio_subtitulos_y_timeline(adn: dict, dia: dict):
    """Copia audios y genera timeline con Whisper + subtítulos ASS."""
    evento_id = dia["evento_id"]
    paths = adn["assets"]["paths"]

    audio_dir = Path(paths["audio_master"])
    sub_dir = Path(paths["subtitulos"])
    timeline_dir = Path(paths["timeline_huecos"])
    guiones_dir = Path(paths["guiones"])
    meta_dir = Path(adn["assets"]["boveda_base"]) / "Metadata_Redes"

    for d in [audio_dir, sub_dir, timeline_dir, guiones_dir, meta_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Copiar audio MP3 ya existente
    src_mp3 = OUTPUT_DIR / f"audio_{evento_id}.mp3"
    dst_mp3 = audio_dir / f"{evento_id}.mp3"
    shutil.copy2(src_mp3, dst_mp3)
    ok(f"Audio copiado a {dst_mp3.name}")

    # 2. Copiar guion JSON
    src_guion = OUTPUT_DIR / f"guion_{evento_id}.json"
    dst_guion = guiones_dir / f"{evento_id}.json"
    shutil.copy2(src_guion, dst_guion)

    with open(src_guion, "r", encoding="utf-8") as f:
        guion_data = json.load(f)

    # 3. Formatear y copiar metadata redes
    src_meta = OUTPUT_DIR / f"metadata_redes_{evento_id}.json"
    if src_meta.exists():
        with open(src_meta, "r", encoding="utf-8") as f:
            raw_meta = json.load(f)
        meta_formatted = {
            "titulo_youtube": raw_meta.get("titulo_redes", dia["titulo"]),
            "descripcion": raw_meta.get("descripcion_post", dia["descripcion"]),
            "tags_cortos": ["#Astrologia", f"#{dia['aspecto'].capitalize()}", "#Transitos", "#Shorts"],
            "tags_largos": dia["palabras_clave"] + ["portal tarot mistico", "carta natal"]
        }
        dst_meta = meta_dir / f"{evento_id}_metadata.json"
        with open(dst_meta, "w", encoding="utf-8") as f:
            json.dump(meta_formatted, f, indent=2, ensure_ascii=False)
        ok(f"Metadata copiada a {dst_meta.name}")

    # 4. Transcribir con Whisper y generar subtítulos ASS
    info(f"Transcribiendo con Whisper ({dst_mp3.name})...")
    model_name = adn["audio"].get("whisper", {}).get("modelo", "base")
    model = whisper.load_model(model_name)
    result = model.transcribe(str(dst_mp3), language="es", word_timestamps=True)

    # Generar ASS en subtitulos/
    generate_ass(str(dst_mp3), modelo=model_name)
    generated_ass = dst_mp3.with_suffix(".ass")
    dst_ass = sub_dir / f"{evento_id}.ass"
    if generated_ass.exists() and generated_ass != dst_ass:
        shutil.move(generated_ass, dst_ass)
    ok(f"Subtítulos generados: {dst_ass.name}")

    # 5. Crear timeline_huecos con timestamps reales
    tomas = guion_data.get("tomas", [])
    dur_total = result.get("segments", [{}])[-1].get("end", 34.0)
    dur_por_toma = dur_total / len(tomas)

    timeline_tomas = []
    acumulado = 0.0
    for i, t in enumerate(tomas):
        dur = dur_por_toma
        fin = acumulado + dur
        timeline_tomas.append({
            "num": t["num"],
            "num_toma": t["num"],
            "rol": t.get("rol", f"toma_{t['num']}"),
            "inicio_ms": int(acumulado * 1000),
            "fin_ms": int(fin * 1000),
            "duracion_ms": int(dur * 1000),
            "duracion_s": round(dur, 2),
            "texto": t["texto"],
            "etiqueta_visual": None,
            "emocion": dia["emocion"]
        })
        acumulado = fin

    timeline_data = {
        "evento_id": evento_id,
        "semana": "Oct_W4",
        "duracion_total_s": round(dur_total, 2),
        "tomas": timeline_tomas
    }

    timeline_path = timeline_dir / f"{evento_id}.json"
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)
    ok(f"Timeline sincronizado: {timeline_path.name} ({dur_total:.1f}s)")


def ejecutar_nodriza_y_validador():
    """Ejecuta Nodriza Visual y Validador de Ensamble."""
    nodriza_script = FACTORY_ROOT / "v2" / "celula_2" / "nodriza_visual.py"
    validador_script = FACTORY_ROOT / "v2" / "celula_2" / "validador_de_ensamble.py"

    info("Lanzando La Nodriza Visual...")
    r = subprocess.run([sys.executable, str(nodriza_script)], capture_output=True, text=True)
    if r.returncode != 0:
        err(f"Fallo en nodriza_visual.py: {r.stderr}")
        sys.exit(1)
    ok("Nodriza Visual completó la asignación de cortes.")

    info("Ejecutando Validador de Ensamble...")
    r_val = subprocess.run([sys.executable, str(validador_script), "--opcion", "3"], capture_output=True, text=True)
    if r_val.returncode != 0:
        err(f"Fallo en validador_de_ensamble.py: {r_val.stderr}")
        sys.exit(1)
    ok("Lista de corte validada lista para renderizado.")


def actualizar_registro_publicaciones(fecha: str, video_path: str):
    """Actualiza produccion/registro_publicaciones.json marcando video generado."""
    if not REGISTRO_PATH.exists():
        return
    with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)

    if fecha in reg.get("publicaciones", {}):
        reg["publicaciones"][fecha]["video_generado"] = True
        reg["publicaciones"][fecha]["path_video"] = video_path
        reg["publicaciones"][fecha]["estado_render"] = "COMPLETADO"
        if reg["publicaciones"][fecha]["estado_youtube"] == "PENDIENTE_RENDER":
            reg["publicaciones"][fecha]["estado_youtube"] = "LISTO_PARA_SUBIR"
        if reg["publicaciones"][fecha]["estado_tiktok"] == "PENDIENTE_RENDER":
            reg["publicaciones"][fecha]["estado_tiktok"] = "LISTO_PARA_SUBIR"

    with open(REGISTRO_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
    ok(f"Registro maestro actualizado para {fecha}")


def ensamblar_dia(dia: dict):
    evento_id = dia["evento_id"]
    fecha = dia["fecha"]
    print(f"\n{BOLD}{MAGENTA}════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{MAGENTA}🎬 PROCESANDO: {dia['titulo']} ({fecha}){RESET}")
    print(f"{BOLD}{MAGENTA}════════════════════════════════════════════════════════════════{RESET}\n")

    # 1. Actualizar ADN
    adn = actualizar_adn_para_evento(dia)

    # 2. Audio, Whisper, Subtítulos, Timeline
    procesar_audio_subtitulos_y_timeline(adn, dia)

    # 3. Nodriza & Validador
    ejecutar_nodriza_y_validador()

    # 4. Render con create_video
    info(f"Ensamblando video final con FFmpeg single-pass para {evento_id}...")
    video_final = create_video(evento_id)

    if video_final and Path(video_final).is_file():
        size_mb = Path(video_final).stat().st_size / (1024 * 1024)
        ok(f"Video final renderizado: {video_final} ({size_mb:.2f} MB)")

        # 5. Copiar a carpeta de semana
        dest_local = OUTPUT_DIR / f"FINAL_{evento_id}.mp4"
        shutil.copy2(video_final, dest_local)
        ok(f"Copiado a {dest_local}")

        # 6. Actualizar registro
        actualizar_registro_publicaciones(fecha, str(dest_local))
    else:
        err(f"Fallo al renderizar el video para {evento_id}")
        sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch Ensamblador de Videos Semanales")
    parser.add_argument("--fecha", help="Fecha específica a ensamblar (ej: 2026-10-30)")
    args = parser.parse_args()

    if args.fecha:
        dias = [d for d in DIAS_PRODUCCION if d["fecha"] == args.fecha]
        if not dias:
            err(f"Fecha {args.fecha} no encontrada en DIAS_PRODUCCION.")
            sys.exit(1)
    else:
        dias = DIAS_PRODUCCION

    for dia in dias:
        ensamblar_dia(dia)

    print(f"\n{BOLD}{VERDE}✨ ¡PROCESAMIENTO BATCH COMPLETADO CON ÉXITO! ✨{RESET}\n")


if __name__ == "__main__":
    main()
