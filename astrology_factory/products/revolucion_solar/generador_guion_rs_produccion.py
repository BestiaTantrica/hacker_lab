import os
import sys
import re
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Importar motores determinísticos locales ($0 costo)
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "carta_natal"))
from calculador_astronomico import CalculadorAstronomico
from adn_autor import INSTRUCCION_ADN_AUTOR
from base_teorica import MARCO_TEORICO

from calculador_revolucion_solar import CalculadorRevolucionSolar
from graficador_biwheel import GraficadorBiWheelAstrologica

from google import genai
from google.genai import types
from groq import Groq

# Cargar variables de entorno del proyecto (.env)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

class GeneradorGuionRSProduccion:
    """
    Motor de Producción Masiva a Costo $0 para Guiones de Revolución Solar en Video (10-15 min).
    Arquitectura Híbrida 'Gold Standard':
    1. Swiss Ephemeris (`swisseph`) para cálculo determinístico de retorno solar y matriz de superposición.
    2. Matplotlib para renderizado de la rueda Bi-Wheel espacial en alta definición.
    3. APIs gratuitas de alta velocidad (Gemini 3.8 Flash / Groq 120B) mediante Few-Shot prompting
       guiado por los moldes de oro canónicos creados por Claude High.
    4. Chunking en 6 capítulos independientes para garantizar profundidad psicológica y evitar truncamiento.
    """
    def __init__(self):
        self.calc_natal = CalculadorAstronomico()
        self.calc_rs = CalculadorRevolucionSolar()
        self.graficador = GraficadorBiWheelAstrologica()

        # Cargar llaves rotativas
        self.gemini_keys = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and v]
        self.groq_keys = [v for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v]

        # Modelos vigentes
        self.gemini_models = ["gemini-3.8-flash"]
        self.groq_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]

        # Cargar los dos guiones de oro para Few-Shot
        self.ejemplos_oro = self._cargar_ejemplos_oro()

    def _cargar_ejemplos_oro(self) -> Dict[str, Dict[int, str]]:
        """Carga y segmenta por capítulos los dos Guiones de Oro canónicos."""
        ejemplos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplos_oro")
        oro_data = {"tomas": {}, "messi": {}}

        archivos = {
            "tomas": os.path.join(ejemplos_dir, "guion_oro_rs_tomas.md"),
            "messi": os.path.join(ejemplos_dir, "guion_oro_rs_messi.md")
        }

        for clave, path in archivos.items():
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    contenido = f.read()
                # Separar por capítulos
                partes = re.split(r"## CAPÍTULO (\d)", contenido)
                for i in range(1, len(partes), 2):
                    num_cap = int(partes[i])
                    texto_cap = "## CAPÍTULO " + partes[i] + partes[i+1]
                    oro_data[clave][num_cap] = texto_cap.strip()
        return oro_data

    def _llamar_ia(self, prompt_usuario: str, system_prompt: str, temperature: float = 0.7) -> str:
        """Invoca Gemini 3.8 Flash con reintentos y fallback automático a Groq."""
        # 1. Intentar con Gemini Flash
        for key in self.gemini_keys:
            for model in self.gemini_models:
                try:
                    client = genai.Client(api_key=key)
                    config = types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                    )
                    res = client.models.generate_content(
                        model=model,
                        contents=prompt_usuario,
                        config=config
                    )
                    if res.text:
                        return res.text.strip()
                except Exception as e:
                    err_msg = str(e)
                    if "404" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                        continue
                    time.sleep(1)
                    continue

        # 2. Fallback con Groq
        for key in self.groq_keys:
            client = Groq(api_key=key)
            for model in self.groq_models:
                try:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt_usuario}
                    ]
                    res = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature
                    )
                    if res.choices and res.choices[0].message.content:
                        return res.choices[0].message.content.strip()
                except Exception as e:
                    time.sleep(1)
                    continue

        raise RuntimeError("No se pudo obtener respuesta de ninguna API de IA configurada (Gemini / Groq).")

    def _limpiar_bloque_locucion(self, texto: str) -> str:
        """Limpia paréntesis dentro del bloque [VOZ / LOCUCIÓN] para no romper el motor TTS."""
        def limpiar_parens(match):
            encabezado = match.group(1)
            cuerpo_voz = match.group(2)
            # Eliminar cualquier paréntesis o contenido dentro de paréntesis en la voz
            cuerpo_limpio = re.sub(r"\(.*?\)", "", cuerpo_voz)
            # Limpiar dobles espacios resultantes
            cuerpo_limpio = re.sub(r"  +", " ", cuerpo_limpio)
            return encabezado + cuerpo_limpio

        # Aplicar solo entre [VOZ / LOCUCIÓN] y el siguiente bloque de indicaciones
        patron = r"(\*\*\[VOZ / LOCUCIÓN\]\*\*\s*\n)(.*?)(?=\*\*\[INDICACIONES VISUALES\]\*\*|\Z)"
        return re.sub(patron, limpiar_parens, texto, flags=re.DOTALL)

    def generar_guion_completo(
        self,
        nombre: str,
        dt_natal_local: datetime,
        lat_natal: float,
        lon_natal: float,
        utc_offset_natal: float,
        anio_rs: int,
        lat_rs: float,
        lon_rs: float,
        utc_offset_rs: float,
        ciudad_rs: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Genera el paquete completo de Revolución Solar:
        1. Cálculo astronómico doble ($0)
        2. Rueda Bi-Wheel espacial en PNG ($0)
        3. Guion de locución en 6 capítulos vía Few-Shot prompting ($0)
        4. Validación métrica y exportación en Markdown y JSON
        """
        os.makedirs(output_dir, exist_ok=True)
        slug = nombre.lower().replace(" ", "_")

        # 1. Cálculo de Carta Natal Base
        print(f"[{nombre}] 1. Calculando Carta Natal base (Swiss Ephemeris)...")
        carta_natal = self.calc_natal.calcular_carta(nombre, dt_natal_local, lat_natal, lon_natal, utc_offset_natal)

        # 2. Cálculo de Retorno Solar con Doble Geocodificación Obligatoria
        print(f"[{nombre}] 2. Calculando Revolución Solar {anio_rs} en {ciudad_rs}...")
        carta_rs = self.calc_rs.calcular_revolucion_solar(
            carta_natal, anio_rs, lat_rs, lon_rs, utc_offset_rs, ciudad_rs
        )

        # Guardar JSON de datos puros
        json_path = os.path.join(output_dir, f"datos_rs_{slug}_{anio_rs}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "carta_natal": carta_natal,
                "revolucion_solar": carta_rs
            }, f, indent=2, ensure_ascii=False)

        # 3. Renderizado de la Rueda Bi-Wheel Espacial en PNG
        biwheel_filename = f"biwheel_{slug}_{anio_rs}.png"
        biwheel_path = os.path.join(output_dir, biwheel_filename)
        print(f"[{nombre}] 3. Renderizando Bi-Wheel espacial en {biwheel_path}...")
        self.graficador.generar_biwheel(carta_natal, carta_rs, biwheel_path)

        # 4. Preparación de Datos y Metadatos para el Pipeline de IA
        sujeto = carta_natal["sujeto"]
        rs_meta = carta_rs["revolucion_solar"]
        planetas_natal = carta_natal["planetas"]
        angulos_natal = carta_natal["angulos"]
        planetas_rs = carta_rs["planetas_rs"]
        angulos_rs = carta_rs["angulos_rs"]
        superposicion = carta_rs["superposicion_clave"]
        aspectos_act = carta_rs["aspectos_intercartas"]

        datos_contexto = f"""
CONSULTANTE: {sujeto['nombre']}
NACIMIENTO: {sujeto['fecha_hora_local']} hs | Lat {sujeto['latitud']}, Lon {sujeto['longitud']}
REVOLUCIÓN SOLAR: Año {rs_meta['anio']} en {rs_meta['ciudad_retorno']} (Retorno exacto local: {rs_meta['fecha_hora_exacta_local']} hs)

CARTA NATAL BASE (INFORME ESCRITO DE 10 PÁGINAS):
- Ascendente Natal: {angulos_natal['Ascendente']['formato']}
- Medio Cielo Natal: {angulos_natal['Medio Cielo']['formato']}
- Sol Natal: {planetas_natal['Sol']['formato']} en Casa {planetas_natal['Sol']['casa']}
- Luna Natal: {planetas_natal['Luna']['formato']} en Casa {planetas_natal['Luna']['casa']}
- Mercurio Natal: {planetas_natal['Mercurio']['formato']} en Casa {planetas_natal['Mercurio']['casa']}
- Venus Natal: {planetas_natal['Venus']['formato']} en Casa {planetas_natal['Venus']['casa']}
- Marte Natal: {planetas_natal['Marte']['formato']} en Casa {planetas_natal['Marte']['casa']}
- Júpiter Natal: {planetas_natal['Júpiter']['formato']} en Casa {planetas_natal['Júpiter']['casa']}
- Saturno Natal: {planetas_natal['Saturno']['formato']} en Casa {planetas_natal['Saturno']['casa']}
- Urano Natal: {planetas_natal['Urano']['formato']} en Casa {planetas_natal['Urano']['casa']}
- Neptuno Natal: {planetas_natal['Neptuno']['formato']} en Casa {planetas_natal['Neptuno']['casa']}
- Plutón Natal: {planetas_natal['Plutón']['formato']} en Casa {planetas_natal['Plutón']['casa']}
- Quirón Natal: {planetas_natal['Quirón']['formato']} en Casa {planetas_natal['Quirón']['casa']}
- Nodo Norte Natal: {planetas_natal['Nodo Norte']['formato']} en Casa {planetas_natal['Nodo Norte']['casa']}
- Lilith Natal: {planetas_natal['Lilith']['formato']} en Casa {planetas_natal['Lilith']['casa']}

REVOLUCIÓN SOLAR {rs_meta['anio']} (CIELO ANUAL):
- Ascendente RS: {angulos_rs['Ascendente_RS']['formato']} -> ¡Cae en Casa Natal {angulos_rs['Ascendente_RS']['casa_natal_superpuesta']}!
- Medio Cielo RS: {angulos_rs['Medio_Cielo_RS']['formato']} -> Cae en Casa Natal {angulos_rs['Medio_Cielo_RS']['casa_natal_superpuesta']}
- Sol RS: {planetas_rs['Sol']['formato']} (Casa {planetas_rs['Sol']['casa_rs']} RS / Casa Natal {planetas_rs['Sol']['casa_natal']})
- Luna RS: {planetas_rs['Luna']['formato']} (Casa {planetas_rs['Luna']['casa_rs']} RS / Casa Natal {planetas_rs['Luna']['casa_natal']})
- Mercurio RS: {planetas_rs['Mercurio']['formato']} (Casa {planetas_rs['Mercurio']['casa_rs']} RS / Casa Natal {planetas_rs['Mercurio']['casa_natal']})
- Venus RS: {planetas_rs['Venus']['formato']} (Casa {planetas_rs['Venus']['casa_rs']} RS / Casa Natal {planetas_rs['Venus']['casa_natal']})
- Marte RS: {planetas_rs['Marte']['formato']} (Casa {planetas_rs['Marte']['casa_rs']} RS / Casa Natal {planetas_rs['Marte']['casa_natal']})
- Júpiter RS: {planetas_rs['Júpiter']['formato']} (Casa {planetas_rs['Júpiter']['casa_rs']} RS / Casa Natal {planetas_rs['Júpiter']['casa_natal']})
- Saturno RS: {planetas_rs['Saturno']['formato']} (Casa {planetas_rs['Saturno']['casa_rs']} RS / Casa Natal {planetas_rs['Saturno']['casa_natal']})
- Urano RS: {planetas_rs['Urano']['formato']} (Casa {planetas_rs['Urano']['casa_rs']} RS / Casa Natal {planetas_rs['Urano']['casa_natal']})
- Neptuno RS: {planetas_rs['Neptuno']['formato']} (Casa {planetas_rs['Neptuno']['casa_rs']} RS / Casa Natal {planetas_rs['Neptuno']['casa_natal']})
- Plutón RS: {planetas_rs['Plutón']['formato']} (Casa {planetas_rs['Plutón']['casa_rs']} RS / Casa Natal {planetas_rs['Plutón']['casa_natal']})
- Quirón RS: {planetas_rs['Quirón']['formato']} (Casa {planetas_rs['Quirón']['casa_rs']} RS / Casa Natal {planetas_rs['Quirón']['casa_natal']})
- Nodo Norte RS: {planetas_rs['Nodo Norte']['formato']} (Casa {planetas_rs['Nodo Norte']['casa_rs']} RS / Casa Natal {planetas_rs['Nodo Norte']['casa_natal']})
- Lilith RS: {planetas_rs['Lilith']['formato']} (Casa {planetas_rs['Lilith']['casa_rs']} RS / Casa Natal {planetas_rs['Lilith']['casa_natal']})

ASPECTOS MAYORES INTER-CARTAS (ACTIVACIONES ANUALES):
"""
        for asp in aspectos_act[:8]:
            datos_contexto += f"- {asp['descripcion']} ({asp['tipo']})\n"

        # 5. Generación Modular por Capítulos (Chunking Guiado por Few-Shot)
        print(f"[{nombre}] 4. Generando guion modular en 6 capítulos con IA y Few-Shot...")

        guion_capitulos = []
        conteo_palabras = {}

        instrucciones_capitulos = [
            (1, "El clima del año y el portal del Ascendente anual",
             "Bienvenida de Tomás. Qué es una Revolución Solar: la descripción de qué zonas quedan iluminadas y cuáles en penumbra durante doce meses, sin destinos cerrados ni sentencias. El Ascendente de la RS, su signo, grado y fundamentalmente en qué Casa Natal cae, contrastando con el Ascendente natal del informe escrito.",
             320, 400),

            (2, "La trinidad anual: el Sol y la Luna del retorno",
             "El Sol en su retorno solar: vitalidad, foco y en qué casa de la RS y casa natal cae. La Luna de la RS: en qué signo y casas (anual y natal) vive, y qué necesita su mundo emocional para no entrar en defensividad o desborde.",
             350, 420),

            (3, "El vector de acción y vínculos: Marte y Venus del año",
             "Marte de la RS (motor de acción, ambición, riesgo de fricción o impaciencia en sus casas anual y natal). Venus de la RS (tipo de armonía, finanzas, qué exige en los pactos y cómo contrasta con el Venus natal).",
             320, 400),

            (4, "La estructura y la expansión: Saturno y Júpiter anuales",
             "Saturno del año (la prueba de realidad, límites, madurez y disciplina operativa en sus casas). Júpiter del año (la expansión, ventana de oportunidad, sentido y cómo se articula con Saturno para sostener el crecimiento).",
             350, 420),

            (5, "Puntos de inflexión: aspectos mayores de activación",
             "Analiza con profundidad psicológica implacable (sin autoayuda superficial) los aspectos más exactos entre los planetas del año y los planetas natales. Tocar los nervios vivos arquetípicos de esta persona.",
             380, 450),

            (6, "Manifiesto de navegación y cierre",
             "MANIFIESTO CONTINUO: Prohibido enumerar '1, 2, 3, 4, 5'. Síntesis integradora de Tomás articulando el clima del año con la Carta Natal escrita de 10 páginas. Consejos de autor con gravedad y calidez austera. La locución debe cerrar exactamente con 'Tomás. portaltarotmistico.com'.",
             300, 380)
        ]

        for num_cap, titulo_cap, directiva_cap, palabras_min, palabras_max in instrucciones_capitulos:
            print(f"[{nombre}] -> Generando Capítulo {num_cap}/6: {titulo_cap}...")

            # Inyectar el ejemplo canónico de Few-Shot para este capítulo específico
            ejemplo_tomas_cap = self.ejemplos_oro.get("tomas", {}).get(num_cap, "")
            ejemplo_messi_cap = self.ejemplos_oro.get("messi", {}).get(num_cap, "")

            system_prompt = f"""
{INSTRUCCION_ADN_AUTOR}

REGLAS DE ORO MANDATORIAS:
1. Escribes como Tomás (Aries/Acuario/Sagitario): directo al hueso, lúcido, maduro, voseo argentino sobrio.
2. CERO METÁFORAS DE SOFTWARE/HARDWARE O COACHING CORPORATIVO: Prohibido hablar de "recalibración de software", "aceleradores/chasis", "mostrame los números" o tips de productividad. Habla con densidad arquetípica y psicológica real.
3. CERO PARÉNTESIS EN [VOZ / LOCUCIÓN]: Todo texto de locución debe ser limpio al 100% para el motor TTS. Ninguna acotación entre paréntesis dentro de la voz.
4. ENLACE CON LA CARTA NATAL: Este video acompaña la Carta Natal escrita de 10 páginas. Remite a ella con naturalidad.
5. FORMATO OBLIGATORIO:
   - ## CAPÍTULO {num_cap} — {titulo_cap}
   - **[VOZ / LOCUCIÓN]**
   - **[INDICACIONES VISUALES]** (detallar cámara sobre la Bi-Wheel y clips abstractos/emocionales)
   - **[CLIMA SONORO]** (texturas sonoras y pausas)
6. EXTENSIÓN: La locución de este capítulo debe tener entre {palabras_min} y {palabras_max} palabras.

REFERENCIA DE ORO CANÓNICA (ESTILO Y CADENCIA EXACTA DE ESTE CAPÍTULO):
\"\"\"
{ejemplo_tomas_cap}
\"\"\"
"""
            user_prompt = f"""
DATOS MATEMÁTICOS DEL CONSULTANTE:
{datos_contexto}

TAREA:
Redacta el CAPÍTULO {num_cap}: "{titulo_cap}" para {nombre}.
Directiva específica: {directiva_cap}
Asegúrate de respetar el formato con [VOZ / LOCUCIÓN], [INDICACIONES VISUALES] y [CLIMA SONORO].
"""
            cap_generado = self._llamar_ia(user_prompt, system_prompt, temperature=0.7)
            cap_limpio = self._limpiar_bloque_locucion(cap_generado)

            # Contar palabras de locución
            voz_match = re.search(r"\*\*\[VOZ / LOCUCIÓN\]\*\*(.*?)(?=\*\*\[INDICACIONES VISUALES\]\*\*|\Z)", cap_limpio, re.DOTALL)
            palabras_cap = len(voz_match.group(1).split()) if voz_match else len(cap_limpio.split())
            conteo_palabras[num_cap] = palabras_cap

            guion_capitulos.append(cap_limpio)
            time.sleep(1)

        # 6. Ensamble del Documento Final
        total_palabras = sum(conteo_palabras.values())
        print(f"[{nombre}] ¡Guion completado! Locución total: {total_palabras} palabras.")

        encabezado = f"""# GUION MAESTRO — REVOLUCIÓN SOLAR {rs_meta['anio']} · {nombre.upper()}
**portaltarotmistico.com · Duración estimada: {round(total_palabras / 155, 1)} min ({total_palabras} palabras)**
Imagen de referencia: `![Rueda Bi-Wheel]({biwheel_filename})`

---

"""
        guion_final = encabezado + "\n\n---\n\n".join(guion_capitulos) + "\n"

        # Guardar en archivo Markdown
        guion_path = os.path.join(output_dir, f"guion_revolucion_solar_{slug}_{anio_rs}.md")
        with open(guion_path, "w", encoding="utf-8") as f:
            f.write(guion_final)

        return {
            "guion_md": guion_path,
            "biwheel_png": biwheel_path,
            "datos_json": json_path,
            "palabras_totales": total_palabras,
            "duracion_minutos": round(total_palabras / 155, 1),
            "desglose_capitulos": conteo_palabras
        }

if __name__ == "__main__":
    print("Motor de Producción de Revolución Solar listo.")
