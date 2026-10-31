#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparar_video_02_noviembre.py
─────────────────────────────────────────────────────────────────────────────
Pipeline de Preparación y Ensamble para el Tránsito del 2 de Noviembre de 2026:
- Tránsito: Luna en Conjunción Exacta con Marte en Leo a 18° y Cuadratura a Mercurio Retrógrado en Escorpio
- Voz de Autor: Tomás (Sol/Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5°)
- Cero morbo, cero escabroso, cero clichés paganos.
- Tomas estables (3.5s - 5.0s), Reloj 2D en Toma 3, cero duplicados visuales.
- Renderiza el video local para auditoría sin subir a redes.
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

DIA_02_NOV = {
    "fecha": "2026-11-02",
    "evento_id": "2026-11-02_Luna_Conjuncion_Marte_Leo",
    "titulo": "2 de Noviembre: Luna y Marte en Conjunción en Leo en Cuadratura a Mercurio Retrógrado",
    "planeta": "Luna/Marte",
    "simbolos": "☽/♂",
    "signos": "Leo/Escorpio",
    "aspecto": "conjunción y cuadratura",
    "intensidad": "alta",
    "orbe": "0.80°",
    "arquetipo_primario": "El Fuego del Corazón",
    "arquetipo_secundario": "La Alquimia del Orgullo",
    "emocion": "impulso visceral / maestría sobre la reactividad",
    "elemento": "Fuego/Agua",
    "modalidad": "Fija",
    "planeta_regente": "Sol/Pluton",
    "simbolo_regente": "☉/♇",
    "descripcion": "El 2 de Noviembre la Luna se une a Marte a los 18 grados de Leo, encendiendo un impulso emocional ardiente que choca en cuadratura con Mercurio retrógrado en Escorpio. No reacciones por orgullo ni te quemes en discusiones estériles: usá este voltaje para crear y afirmarte en tu centro.",
    "palabras_clave": ["luna", "marte", "leo", "mercurio", "escorpio", "fuego", "voluntad", "transmutacion", "astrolabio"]
}

def generar_guion_tomas(dia: dict, client: genai.Client) -> dict:
    prompt = f"""
Eres Tomás: creador de 'Portal Tarot Místico' con ADN astral de fuego y aire (Sol y Mercurio en Aries 22°, Ascendente Acuario 22°, Luna en Sagitario 5°).
Tu voz es: DIRECTA AL HUESO, LÚCIDA, ENÉRGICA, PEDAGÓGICA Y CON VOSEO ARGENTINO MADURO (mirá, fijate, tenés, no comas vidrio).

REGLAS INNEGOCIABLES DE PERSONALIDAD:
1. PROHIBIDO EL MORBO Y LO ESCABROSO: Cero referencias a autopsias, heridas sangrantes, podredumbre o muerte morbosa. El tenebrismo de Roberto Ferri es exclusivamente la estética visual pictórica de los cuadros en claroscuro; jamás debe contaminar el guion con pesimismo gótico.
2. PROHIBIDO EL HUMO NEW AGE O PAGANO: Cero palabras como 'Samhain', 'códices sagrados', 'portales de luz' o 'brujería'. Esto es astrología técnica, psicológica y viva.
3. DATOS PRECISOS: Menciona la fecha exacta ("2 de Noviembre") y los grados exactos ("18 grados de Leo").
4. TOMA 3 (EL RELOJ ASTROLÓGICO): La Toma 3 es donde se muestra en pantalla el Reloj Astrológico 2D y se traduce la geometría del cielo en una ley clara y práctica.

DATOS ASTRONÓMICOS REALES:
- Título: {dia['titulo']}
- Tránsito: {dia['planeta']} en {dia['signos']} ({dia['aspecto']} - Orbe {dia['orbe']})
- Arquetipo: {dia['arquetipo_primario']} vs {dia['arquetipo_secundario']}
- Clima psicológico: {dia['emocion']}
- Síntesis: {dia['descripcion']}

ESTRUCTURA DIDÁCTICA EN 5 TOMAS (38 a 40 segundos totales, 14 a 18 palabras por toma):
- Toma 1 (Gancho directo con fecha): "2 de Noviembre: la Luna y Marte se juntan a quemarropa en el signo de Leo..."
- Toma 2 (Mecánica psicológica / Fricción): Explica qué trampa de ego salta (el orgullo herido frente a lo que destapa Mercurio en Escorpio).
- Toma 3 (Mecánica celeste / Reloj 2D): Explica la conjunción partil a 18° y la cuadratura.
- Toma 4 (Acción soberana / Maestría): Acción constructiva ariana (no engancharse, dirigir la potencia a crear).
- Toma 5 (Llamado a la web): Invita a meter su mapa en el reloj interactivo de la bio (portaltarotmistico.com).

Responde ÚNICAMENTE en JSON con esta estructura exacta:
{{
  "titulo": "{dia['titulo']}",
  "evento_id": "{dia['evento_id']}",
  "fecha": "{dia['fecha']}",
  "tomas": [
    {{ "num": 1, "rol": "gancho", "duracion_s": 7, "texto": "..." }},
    {{ "num": 2, "rol": "efecto_sombra", "duracion_s": 8, "texto": "..." }},
    {{ "num": 3, "rol": "mecanica_astral", "duracion_s": 9, "texto": "..." }},
    {{ "num": 4, "rol": "afrontamiento", "duracion_s": 8, "texto": "..." }},
    {{ "num": 5, "rol": "cta_web", "duracion_s": 7, "texto": "..." }}
  ]
}}
"""
    modelos = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
    for m in modelos:
        try:
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config={"temperature": 0.7}
            )
            txt = res.text.strip()
            if txt.startswith("```json"): txt = txt[7:]
            if txt.startswith("```"): txt = txt[3:]
            if txt.endswith("```"): txt = txt[:-3]
            data = json.loads(txt.strip())
            return data
        except Exception as e:
            print(f"  [Warn] Falló {m}: {e}")
            continue
    raise RuntimeError("No se pudo generar guion con los modelos disponibles.")

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
    model_name = adn["audio"].get("whisper", {}).get("modelo", "base")
    model = whisper.load_model(model_name)
    result = model.transcribe(str(dst_mp3), language="es", word_timestamps=True)

    generate_ass(str(dst_mp3), modelo=model_name)
    generated_ass = dst_mp3.with_suffix(".ass")
    dst_ass = sub_dir / f"{evento_id}.ass"
    if generated_ass.exists() and generated_ass != dst_ass:
        shutil.move(generated_ass, dst_ass)
    print(f"✅ Subtítulos sincronizados: {dst_ass.name}")

    tomas = guion_data.get("tomas", [])
    dur_total = result.get("segments", [{}])[-1].get("end", 36.0)
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
    print("🔥 PREPARANDO VIDEO CANÓNICO: 2 DE NOVIEMBRE 2026")
    print("=" * 70)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # 1. Guion Editorial
    print("✍️  Generando guion con ADN de Tomás (Aries/Acuario/Sagitario)...")
    guion = generar_guion_tomas(DIA_02_NOV, client)
    guion_local = OUTPUT_DIR / f"guion_{DIA_02_NOV['evento_id']}.json"
    with open(guion_local, "w", encoding="utf-8") as f:
        json.dump(guion, f, indent=2, ensure_ascii=False)
    print(f"✅ Guion forjado con éxito ({len(guion['tomas'])} tomas)")
    for t in guion["tomas"]:
        print(f"   [{t['num']}] {t['rol'].upper()}: {t['texto']}")

    # 2. Audio Master con TomasNeural
    texto_completo = " ".join(t["texto"].strip() for t in guion["tomas"])
    audio_local = OUTPUT_DIR / f"audio_{DIA_02_NOV['evento_id']}.mp3"
    print("\n🎙️  Sintetizando locución argentina (es-AR-TomasNeural)...")
    await sintetizar_audio(texto_completo, audio_local)
    print(f"✅ Audio generado: {audio_local.name}")

    # 3. Actualizar ADN y procesar Timeline/Subtítulos
    adn = actualizar_adn(DIA_02_NOV)
    procesar_timeline_y_subtitulos(adn, DIA_02_NOV, guion, audio_local)

    # 4. Nodriza Visual (Stable Takes + Reloj en Toma 3 + Zero Duplicados)
    print("\n📦 Ejecutando Nodriza Visual V2...")
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
    print("\n🎬 Renderizando video con FFmpeg Single-Pass...")
    video_final = create_video(DIA_02_NOV["evento_id"])
    if video_final and Path(video_final).is_file():
        dest_video = OUTPUT_DIR / f"FINAL_{DIA_02_NOV['evento_id']}.mp4"
        shutil.copy2(video_final, dest_video)
        size_mb = dest_video.stat().st_size / (1024 * 1024)
        print("=" * 70)
        print(f"🎉 VIDEO DEL 2 DE NOVIEMBRE LISTO PARA AUDITORÍA:")
        print(f"📁 Ruta: {dest_video}")
        print(f"📊 Peso: {size_mb:.2f} MB")
        print("⚠️  ESTADO: GENERADO LOCALMENTE (NO SUBIDO A REDES AÚN)")
        print("=" * 70)

        # Actualizar registro maestro como LISTO_AUDITORIA
        if REGISTRO_PATH.exists():
            with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
                reg = json.load(f)
            reg.setdefault("publicaciones", {})[DIA_02_NOV["fecha"]] = {
                "evento_id": DIA_02_NOV["evento_id"],
                "titulo": DIA_02_NOV["titulo"],
                "youtube_video_id": None,
                "youtube_url": None,
                "tiktok_url": None,
                "estado_youtube": "LISTO_AUDITORIA",
                "estado_tiktok": "LISTO_AUDITORIA",
                "fecha_publicacion": DIA_02_NOV["fecha"],
                "video_generado": True,
                "path_video": str(dest_video),
                "estado_render": "COMPLETADO"
            }
            with open(REGISTRO_PATH, "w", encoding="utf-8") as f:
                json.dump(reg, f, indent=2, ensure_ascii=False)
            print("📝 Registro maestro actualizado con éxito.")
    else:
        print("❌ Error al generar el video final.")

if __name__ == "__main__":
    asyncio.run(main())
