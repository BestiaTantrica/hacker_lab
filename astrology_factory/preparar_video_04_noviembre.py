#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparar_video_04_noviembre.py
─────────────────────────────────────────────────────────────────────────────
Pipeline Canónico de Producción: 4 de Noviembre de 2026
- Tránsito: Mercurio entra en el Corazón del Sol (Cazimi Partil a 12° Escorpio, orbe 0.06°)
            + Luna en Virgo (17° Virgo) en Sextil armónico exacto.
- Tono: Psicología conductual madura, voseo argentino Tomás, sin tecnicismos árabes.
- Cadena narrativa: Enlaza con el orden de Virgo del día 3. Lucidez sin filtro ni drama.
- Innovación: Doble Reloj 2D Cinemático (Apertura 00h-06h + Cierre 18h-24h con destello dorado).
- Safe Zone: Carteles tácticos en y=1280 a 1510; franja inferior y=1580 a 1920 100% limpia para subtítulos.
- Transiciones: Disolvencias suaves y esfumadas (xfade 0.75s).
- Anti-shadowban: Cero .com ("Entrá al link de mi perfil").
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import shutil
import asyncio
import subprocess
from pathlib import Path

FACTORY_ROOT = Path("/home/LAB/astrology_factory")
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

import google.genai as genai
import edge_tts
import whisper
from content_factory.subtitle_generator import generate_ass
from content_factory.video_maker import create_video

ADN_PATH = FACTORY_ROOT / "contexto_astrologico.json"
OUTPUT_DIR = FACTORY_ROOT / "produccion" / "semana_02nov_08nov"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REGISTRO_PATH = FACTORY_ROOT / "produccion" / "registro_publicaciones.json"

DIA_04_NOV = {
    "fecha": "2026-11-04",
    "evento_id": "2026-11-04_Mercurio_Cazimi_Escorpio",
    "titulo": "4 de Noviembre | Mercurio en el corazón del Sol: Ver la verdad sin filtro",
    "planeta": "Mercurio",
    "simbolos": "☿",
    "signos": "Escorpio",
    "aspecto": "conjunción cazimi y sextil",
    "intensidad": "muy alta",
    "orbe": "0.06°",
    "arquetipo_primario": "La Lucidez Quirúrgica",
    "arquetipo_secundario": "El Discernimiento contra la Negación",
    "emocion": "caen las caretas / ver la verdad oculta sin filtro ni drama",
    "elemento": "Agua/Tierra",
    "modalidad": "Fija/Mutable",
    "planeta_regente": "Plutón/Marte",
    "simbolo_regente": "♇/♂",
    "descripcion": "El 4 de Noviembre Mercurio entra en el corazón del Sol a 12° de Escorpio en conjunción partil (Cazimi). El intelecto se fusiona con la fuente de luz: lo que estaba bajo siete llaves sale a la superficie. La Luna en Virgo aporta el método y el orden para no quemarse en la intensidad emocional.",
    "palabras_clave": ["mercurio", "sol", "cazimi", "escorpio", "virgo", "luna", "verdad", "lucidez", "discernimiento"]
}

GUION_CANONICO_04_NOV = {
  "titulo": DIA_04_NOV["titulo"],
  "evento_id": DIA_04_NOV["evento_id"],
  "fecha": DIA_04_NOV["fecha"],
  "tomas": [
    {
      "num": 1,
      "rol": "gancho_reloj2d_apertura",
      "duracion_s": 7.5,
      "texto": "4 de noviembre. Mercurio entra en el corazón del Sol en Escorpio."
    },
    {
      "num": 2,
      "rol": "mecanica_psicologica",
      "duracion_s": 8.0,
      "texto": "Cuando la mente se funde con la verdad, las caretas caen solas... Lo que estaba bajo siete llaves sale a la superficie."
    },
    {
      "num": 3,
      "rol": "mecanica_celeste_tension",
      "duracion_s": 8.0,
      "texto": "La Luna en Virgo aporta el método: no te ahogues en la intensidad, ordená los datos con precisión quirúrgica."
    },
    {
      "num": 4,
      "rol": "brujula_lucida",
      "duracion_s": 8.5,
      "texto": "No intentes tapar el sol con las manos... Mirá lo que hay, asumí la realidad y decidí con cabeza fría."
    },
    {
      "num": 5,
      "rol": "cta_reloj2d_loop",
      "duracion_s": 6.5,
      "texto": "Para ver en qué casa te cae esta revelación, entrá al link de mi perfil."
    }
  ]
}

def generar_guion_tomas(dia: dict, client: genai.Client) -> dict:
    return GUION_CANONICO_04_NOV

async def sintetizar_audio(texto: str, output_path: Path):
    voice = "es-AR-TomasNeural"
    communicate = edge_tts.Communicate(texto, voice, rate="-2%", pitch="-1Hz")
    await communicate.save(str(output_path))

def actualizar_adn(dia: dict) -> dict:
    with open(ADN_PATH, "r", encoding="utf-8") as f:
        adn = json.load(f)

    adn["produccion"]["evento_id"] = dia["evento_id"]
    adn["produccion"]["evento_titulo"] = dia["titulo"]
    adn["produccion"]["fecha_publicacion"] = dia["fecha"]
    adn["produccion"]["semana_prefijo"] = "Nov_W1"

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

    # Transiciones suaves de 0.75s para esfumar y mezclar sin cortes tajantes
    adn["render"]["xfade_duracion_s"] = 0.75

    with open(ADN_PATH, "w", encoding="utf-8") as f:
        json.dump(adn, f, indent=2, ensure_ascii=False)
    return adn

def procesar_timeline_y_subtitulos(adn: dict, dia: dict, guion_data: dict, audio_path: Path):
    evento_id = dia["evento_id"]
    paths = adn["assets"]["paths"]

    audio_dir = Path(paths["audio_master"])
    sub_dir = Path(paths["subtitulos"])
    timeline_dir = Path(paths["timeline_huecos"])
    guiones_dir = Path(paths["guiones"])
    meta_dir = Path(adn["assets"]["boveda_base"]) / "Metadata_Redes"

    for d in [audio_dir, sub_dir, timeline_dir, guiones_dir, meta_dir]:
        d.mkdir(parents=True, exist_ok=True)

    dst_mp3 = audio_dir / f"{evento_id}.mp3"
    shutil.copy2(audio_path, dst_mp3)

    dst_guion = guiones_dir / f"{evento_id}.json"
    with open(dst_guion, "w", encoding="utf-8") as f:
        json.dump(guion_data, f, indent=2, ensure_ascii=False)

    print(f"🎙️  Transcribiendo con Whisper ({dst_mp3.name})...")
    model_name = adn["audio"].get("whisper", {}).get("modelo", "small")
    model = whisper.load_model(model_name)
    result = model.transcribe(str(dst_mp3), language="es", word_timestamps=True)

    # Margen vertical 220px: los subtítulos quedan en y=1700, 100% en la zona limpia
    generate_ass(str(dst_mp3), modelo=model_name, margin_v=220)
    generated_ass = dst_mp3.with_suffix(".ass")
    dst_ass = sub_dir / f"{evento_id}.ass"
    if generated_ass.exists() and generated_ass != dst_ass:
        shutil.move(generated_ass, dst_ass)
    print(f"✅ Subtítulos sincronizados: {dst_ass.name}")

    tomas = guion_data.get("tomas", [])
    dur_total = result.get("segments", [{}])[-1].get("end", 38.5)
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
        "semana": "Nov_W1",
        "duracion_total_s": round(dur_total, 2),
        "tomas": timeline_tomas
    }

    timeline_path = timeline_dir / f"{evento_id}.json"
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Timeline sincronizado: {timeline_path.name} ({dur_total:.1f}s)")

async def main():
    print("=" * 70)
    print("🔥 PREPARANDO VIDEO CANÓNICO: 4 DE NOVIEMBRE 2026")
    print("=" * 70)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # 1. Guion Editorial
    print("✍️  Generando guion editorial Tomás (Mercurio en el Corazón del Sol)...")
    guion = generar_guion_tomas(DIA_04_NOV, client)
    guion_local = OUTPUT_DIR / f"guion_{DIA_04_NOV['evento_id']}.json"
    with open(guion_local, "w", encoding="utf-8") as f:
        json.dump(guion, f, indent=2, ensure_ascii=False)
    print(f"✅ Guion forjado con éxito ({len(guion['tomas'])} tomas)")
    for t in guion["tomas"]:
        print(f"   [{t['num']}] {t['rol'].upper()}: {t['texto']}")

    # 2. Audio Master con prosodia pausada y natural
    texto_completo = " \n\n ".join(t["texto"].strip() for t in guion["tomas"])
    audio_local = OUTPUT_DIR / f"audio_{DIA_04_NOV['evento_id']}.mp3"
    print("\n🎙️  Sintetizando locución argentina con prosodia natural (es-AR-TomasNeural)...")
    await sintetizar_audio(texto_completo, audio_local)
    print(f"✅ Audio generado: {audio_local.name}")

    # 3. Actualizar ADN y procesar Timeline/Subtítulos
    adn = actualizar_adn(DIA_04_NOV)
    procesar_timeline_y_subtitulos(adn, DIA_04_NOV, guion, audio_local)

    # 4. Nodriza Visual (Doble Reloj 2D en Toma 1 y Toma 5 + Arte Tenebrista)
    print("\n📦 Ejecutando Nodriza Visual V2 (Dual Clock Loop)...")
    py_exec = sys.executable
    res_nodriza = subprocess.run([py_exec, str(FACTORY_ROOT / "v2" / "celula_2" / "nodriza_visual.py")], capture_output=True, text=True)
    if res_nodriza.returncode != 0:
        print("❌ Error en Nodriza Visual:\n", res_nodriza.stderr)
        return
    print("✅ Nodriza Visual completada.")

    # 5. Validador de Ensamble
    print("🔍 Validando ensamble con validador_de_ensamble.py...")
    res_val = subprocess.run([py_exec, str(FACTORY_ROOT / "v2" / "celula_2" / "validador_de_ensamble.py"), "--opcion", "3"], capture_output=True, text=True)
    if res_val.returncode != 0:
        print("❌ Error en Validador de Ensamble:\n", res_val.stderr)
        return
    print("✅ Plan de corte validado.")

    # 6. Renderizar Video Final Single-Pass
    print("\n🎬 Renderizando video con FFmpeg Single-Pass (Dissolve 0.75s + Safe Zone)...")
    video_final = create_video(DIA_04_NOV["evento_id"])
    if video_final and Path(video_final).is_file():
        dest_video = OUTPUT_DIR / f"FINAL_{DIA_04_NOV['evento_id']}.mp4"
        shutil.copy2(video_final, dest_video)
        size_mb = dest_video.stat().st_size / (1024 * 1024)
        print("=" * 70)
        print(f"🎉 VIDEO DEL 4 DE NOVIEMBRE LISTO PARA AUDITORÍA:")
        print(f"📁 Ruta: {dest_video}")
        print(f"📊 Peso: {size_mb:.2f} MB")
        print("⚠️  ESTADO: GENERADO LOCALMENTE (NO SUBIDO A REDES AÚN)")
        print("=" * 70)

        # Actualizar registro maestro como LISTO_AUDITORIA
        if REGISTRO_PATH.exists():
            with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
                reg = json.load(f)
            reg.setdefault("publicaciones", {})[DIA_04_NOV["fecha"]] = {
                "evento_id": DIA_04_NOV["evento_id"],
                "titulo": DIA_04_NOV["titulo"],
                "youtube_video_id": None,
                "youtube_url": None,
                "tiktok_url": None,
                "estado_youtube": "LISTO_AUDITORIA",
                "estado_tiktok": "LISTO_AUDITORIA",
                "fecha_publicacion": DIA_04_NOV["fecha"],
                "video_generado": True,
                "path_video": str(dest_video),
                "estado_render": "COMPLETADO",
                "notas": "Doble Reloj 2D (Apertura 00-06h + Cierre 18-24h destello) · Safe Subtitle Zone · Xfade 0.75s"
            }
            with open(REGISTRO_PATH, "w", encoding="utf-8") as f:
                json.dump(reg, f, indent=2, ensure_ascii=False)
            print("📝 Registro maestro actualizado con éxito.")
    else:
        print("❌ Error al generar el video final.")

if __name__ == "__main__":
    asyncio.run(main())
