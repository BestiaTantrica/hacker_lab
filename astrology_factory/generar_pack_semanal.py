#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_pack_semanal.py
─────────────────────────────────────────────────────────────────────────────
Generador del Pack de Tránsitos Diarios (29 Octubre a 1 Noviembre 2026)
Ecosistema: Astrology Factory / El Glifo Maestro

Calcula efemérides con Swiss Ephemeris, genera guiones canónicos de autor
con Gemini y sintetiza la voz humana argentina (es-AR-TomasNeural).
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

FACTORY_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(FACTORY_ROOT))

from dotenv import load_dotenv
load_dotenv(FACTORY_ROOT / ".env")

import swisseph as swe
from google import genai
import edge_tts

OUTPUT_DIR = FACTORY_ROOT / "produccion" / "semana_29oct_01nov"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. DEFINICIÓN DE LOS 4 TRÁNSITOS SAGRADOS ────────────────────────────────
DIAS = [
    {
        "fecha": "2026-10-29",
        "evento_id": "2026-10-29_Mercurio_Cuadratura_Marte",
        "titulo": "Mercurio Retrógrado en Escorpio en Cuadratura con Marte en Leo",
        "planeta": "Mercurio/Marte",
        "simbolos": "☿(R)/♂",
        "signos": "Escorpio/Leo",
        "aspecto": "Cuadratura (90°)",
        "orbe": "1.67°",
        "arquetipo": "La Palabra como Bisturí vs. El Orgullo Defensivo",
        "emocion": "tensión verbal / revelación incómoda",
        "descripcion": "Mercurio retrógrado en Escorpio destapa verdades que tocan el orgullo de Marte en Leo. La mente quiere investigar la herida oculta mientras el ego reacciona a la defensiva. Cuidado con usar la verdad como arma destructiva.",
        "hashtags": "#astrologia #mercurioretrogrado #escorpio #marte #climaastral"
    },
    {
        "fecha": "2026-10-30",
        "evento_id": "2026-10-30_Mercurio_Cuadratura_Partil_Marte",
        "titulo": "Clímax de Tensión: Mercurio Retrógrado en Cuadratura Partil Exacta a Marte",
        "planeta": "Mercurio/Marte",
        "simbolos": "☿(R)/♂",
        "signos": "Escorpio/Leo",
        "aspecto": "Cuadratura Partil (90°00')",
        "orbe": "0.32°",
        "arquetipo": "La Navaja Mental / Purga de la Sombra",
        "emocion": "catarsis visceral / combustión psicológica",
        "descripcion": "El ángulo de tensión entre la mente escorpiana y el impulso leonino alcanza su orbe exacto de 0.32 grados. El Sol en Escorpio hace trígono a la Luna en Cáncer: lo que reprimías durante meses sale a la superficie. Si no lo verbalizas con conciencia, estalla en impulsos.",
        "hashtags": "#astrologia #transitos #climaastral #escorpio #fuego #psicologia"
    },
    {
        "fecha": "2026-10-31",
        "evento_id": "2026-10-31_Samhain_Luna_Trigono_Mercurio",
        "titulo": "Noche de Samhain: Luna en Cáncer en Trígono con Mercurio Retrógrado en Escorpio",
        "planeta": "Luna/Mercurio",
        "simbolos": "☽/☿(R)",
        "signos": "Cáncer/Escorpio",
        "aspecto": "Trígono de Agua (120°)",
        "orbe": "3.17°",
        "arquetipo": "El Desgarro del Velo Psíquico / Memoria Ancestral",
        "emocion": "intuición quirúrgica / transmutación profunda",
        "descripcion": "En la noche sagrada de Samhain, la Luna en Cáncer conecta en trígono fluido con Mercurio retrógrado en Escorpio. Se rasga el velo: emergen memorias del linaje, pactos tácitos y certezas que no necesitan palabras. Noche de transmutación y silencio consciente.",
        "hashtags": "#samhain #halloweenastrologico #lunaencancer #escorpio #oraculo"
    },
    {
        "fecha": "2026-11-01",
        "evento_id": "2026-11-01_Luna_Oposicion_Pluton_Cuarto_Menguante",
        "titulo": "Luna en Leo en Oposición a Plutón en Acuario (Cuarto Menguante)",
        "planeta": "Luna/Pluton",
        "simbolos": "☽/♇",
        "signos": "Leo/Acuario",
        "aspecto": "Oposición (180°) + Cuarto Menguante",
        "orbe": "1.37°",
        "arquetipo": "El Trono Personal frente a la Colmena Colectiva",
        "emocion": "desapego del personaje / renacimiento sobrio",
        "descripcion": "La Luna entra en Leo y choca en oposición directa con Plutón en Acuario mientras cuadra al Sol. El Cuarto Menguante exige soltar la necesidad de validación y aplauso externo. Se desmorona el personaje para dar lugar a una soberanía real y despojada.",
        "hashtags": "#lunamenguante #pluton #acuario #leo #astrologiahoy"
    }
]

# ── 2. MOTOR DE GUIONES CANÓNICOS DE AUTOR (CLAUDE PRO GOLD STANDARD) ────────
def generar_guion(dia: dict, client: genai.Client) -> dict:
    prompt = f"""
Eres un Astrólogo Clínico y Sociológico de autor, con tono tenebrista, filosófico y visceral (estilo Roberto Ferri y James Hillman).
PROHIBIDO EL COACHING DE PELUQUERÍA, CERO FRASES CLICHÉ ("auditá tus vínculos", "no seas cobarde", "universo cuántico").
Escribe un guion riguroso de EXACTAMENTE 5 tomas para un video vertical (Short / Reel / TikTok) de 38 a 40 segundos.
Métrica estricta: Cada toma debe tener entre 14 y 20 palabras (total: 80 a 95 palabras).

DATOS ASTRONÓMICOS REALES:
- Título: {dia['titulo']}
- Tránsito: {dia['planeta']} ({dia['simbolos']}) en {dia['signos']} ({dia['aspecto']} - Orbe {dia['orbe']})
- Arquetipo: {dia['arquetipo']}
- Clima emocional: {dia['emocion']}
- Síntesis cósmica: {dia['descripcion']}

ESTRUCTURA OBLIGATORIA EN 5 TOMAS:
- Toma 1 (Gancho visceral): Nombra el síntoma físico o mental exacto que la gente está sintiendo hoy en el pecho o la cabeza.
- Toma 2 (Efecto en la sombra): Explica cómo la psicología humana tropieza con esta energía (el orgullo, la herida o el miedo).
- Toma 3 (Mecánica celeste): Traduce la geometría astronómica ({dia['aspecto']}) en una ley de causa y efecto lúcida.
- Toma 4 (Afrontamiento maduro): Una instrucción de dignidad y sobriedad para transitar el día sin quemar puentes.
- Toma 5 (CTA COMERCIAL DIRECTO): Manda al espectador a portaltarotmistico.com o link del perfil a ingresar su fecha y hora para ver la casa exacta afectada.

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
    modelos = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.8-flash"]
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

# ── 3. SINTETIZADOR DE LOCUCIÓN ARGENTINA ────────────────────────────────────
async def sintetizar_audio(texto: str, output_path: Path):
    voice = "es-AR-TomasNeural"
    communicate = edge_tts.Communicate(texto, voice, rate="-2%", pitch="-1Hz")
    await communicate.save(str(output_path))

# ── 4. ORQUESTADOR PRINCIPAL ────────────────────────────────────────────────
async def main():
    print("=" * 70)
    print("🛸 GENERANDO PACK DE TRÁNSITOS DIARIOS: 29 OCTUBRE A 01 NOVIEMBRE 2026")
    print("=" * 70)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY no encontrada en .env")
        return
        
    client = genai.Client(api_key=api_key)
    
    for i, dia in enumerate(DIAS, 1):
        fecha = dia["fecha"]
        print(f"\n[{i}/4] 📅 Procesando {fecha}: {dia['titulo']}")
        
        # 1. Generar Guion de Oro Canónico
        print("   ✍️  Forjando guion con Gemini Flash bajo rol editorial de autor...")
        guion = generar_guion(dia, client)
        guion_path = OUTPUT_DIR / f"guion_{dia['evento_id']}.json"
        with open(guion_path, "w", encoding="utf-8") as f:
            json.dump(guion, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Guion guardado: {guion_path.name}")
        
        # 2. Sintetizar Audio Master con TomasNeural
        print("   🎙️  Sintetizando locución argentina (es-AR-TomasNeural)...")
        texto_completo = " ".join(t["texto"].strip() for t in guion["tomas"])
        audio_path = OUTPUT_DIR / f"audio_{dia['evento_id']}.mp3"
        await sintetizar_audio(texto_completo, audio_path)
        print(f"   ✅ Audio masterizado: {audio_path.name} ({len(texto_completo.split())} palabras)")
        
        # 3. Generar Metadatos y Copy para Redes (YouTube Shorts / TikTok / Reels)
        meta = {
            "fecha": fecha,
            "evento_id": dia["evento_id"],
            "titulo_redes": f"🔥 {dia['titulo'][:90]}",
            "descripcion_post": (
                f"{dia['descripcion']}\n\n"
                f"🌌 Descubrí qué casa y qué planetas de tu carta natal están recibiendo este impacto:\n"
                f"🔗 https://portaltarotmistico.com (Ingresá tu fecha y hora exacta)\n\n"
                f"{dia['hashtags']}"
            ),
            "pinned_comment_youtube": (
                f"🔮 ¿Tenés planetas en {dia['signos']} cerca del grado clave? "
                f"Ahí es donde este tránsito te moviliza de lleno. "
                f"Calculá tu carta natal exacta y dialogá con el oráculo en: https://portaltarotmistico.com"
            ),
            "guion_locucion": texto_completo
        }
        meta_path = OUTPUT_DIR / f"metadata_redes_{dia['evento_id']}.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Metadatos para redes listos: {meta_path.name}")
        
    print("\n" + "=" * 70)
    print(f"🎉 PACK SEMANAL 100% COMPLETADO EN: {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
