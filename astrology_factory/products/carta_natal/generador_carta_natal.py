import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from calculador_astronomico import CalculadorAstronomico
from graficador_rueda import GraficadorRuedaAstrologica
from adn_autor import INSTRUCCION_ADN_AUTOR
from base_teorica import MARCO_TEORICO

from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv

# Cargar variables de entorno del proyecto
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

class GeneradorCartaNatalProduccion:
    """
    Motor de Producción para Carta Astral Premium (Fase 1).
    Utiliza:
    1. Swiss Ephemeris para cálculo matemático exacto (costo $0).
    2. Matplotlib para renderizado de la rueda gráfica espacial (costo $0).
    3. APIs de alta velocidad (Gemini 3.8 Flash / Groq 120B) condicionadas por
       los Ejemplos de Oro creados por Claude (Few-Shot Prompting).
    """
    def __init__(self):
        self.calculador = CalculadorAstronomico()
        self.graficador = GraficadorRuedaAstrologica()

        # Cargar llaves
        self.gemini_keys = [v for k, v in os.environ.items() if k.startswith("GEMINI_API_KEY") and v]
        self.groq_keys = [v for k, v in os.environ.items() if k.startswith("GROQ_API_KEY") and v]

        # Modelos recomendados vigentes
        self.gemini_models = ["gemini-3.8-flash", "gemini-3.5-flash"]
        self.groq_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]

        # Cargar fragmento de ejemplo de oro para Few-Shot
        self.few_shot_context = self._cargar_ejemplo_referencia()

    def _cargar_ejemplo_referencia(self) -> str:
        ejemplo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplos_oro", "ejemplo_oro_tomas.md")
        if os.path.exists(ejemplo_path):
            with open(ejemplo_path, "r", encoding="utf-8") as f:
                contenido = f.read()
                # Extraer los primeros 120 renglones (guía de lectura + estilo) como guía de tono
                lineas = contenido.splitlines()[:130]
                return "\n".join(lineas)
        return ""

    def _llamar_ia(self, prompt_usuario: str, system_prompt: str) -> str:
        # Intentar con Gemini primero
        for key in self.gemini_keys:
            for model in self.gemini_models:
                try:
                    client = genai.Client(api_key=key)
                    config = types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.75,
                    )
                    res = client.models.generate_content(
                        model=model,
                        contents=prompt_usuario,
                        config=config
                    )
                    if res.text:
                        return res.text
                except Exception as e:
                    print(f"[Generador-Gemini] Error con {model}: {str(e)[:80]}. Reintentando...")
                    time.sleep(2)
                    continue

        # Fallback con Groq
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
                        temperature=0.75
                    )
                    if res.choices and res.choices[0].message.content:
                        return res.choices[0].message.content
                except Exception as e:
                    print(f"[Generador-Groq] Error con {model}: {str(e)[:80]}. Reintentando...")
                    time.sleep(2)
                    continue

        raise RuntimeError("No se pudo obtener respuesta de ninguna API configurada.")

    def generar_reporte(self, nombre: str, dt_local: datetime, lat: float, lon: float, utc_offset: float, output_path: str):
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        slug = nombre.lower().replace(" ", "_")

        # 1. Cálculo Matemático
        print(f"[{nombre}] 1. Calculando posiciones astronómicas...")
        carta = self.calculador.calcular_carta(nombre, dt_local, lat, lon, utc_offset)

        # 2. Rueda Gráfica (Ruta absoluta para evitar bugs de visualización)
        rueda_path = os.path.join(output_dir, f"rueda_{slug}.png")
        print(f"[{nombre}] 2. Generando rueda astrológica en {rueda_path}...")
        self.graficador.generar_rueda(carta, rueda_path)

        # 3. Compilación por Bloques (Chunking Guiado por Estándar de Oro)
        print(f"[{nombre}] 3. Redactando informe en base al Estándar de Oro...")

        system_prompt = f"""
{INSTRUCCION_ADN_AUTOR}

MARCO TEÓRICO PEDAGÓGICO:
{json.dumps(MARCO_TEORICO, indent=2, ensure_ascii=False)}

ESTÁNDAR DE ORO Y GUÍA DE ESTILO (REFERENCIA DE ORO CREADA POR CLAUDE):
\"\"\"
{self.few_shot_context}
\"\"\"
REGLAS:
- Redacta con el mismo estilo, tono adulto, pedagógico y directo del estándar de oro.
- Utiliza la estructura: Qué es -> Cómo funciona -> En tu carta (signo/casa/aspectos) -> En la práctica (punto ciego y recurso).
- Cero cursilerías, cero predicciones baratas, cero sinastría con el autor.
"""

        # Resumen de datos para los prompts
        sujeto = carta["sujeto"]
        planetas = carta["planetas"]
        angulos = carta["angulos"]
        aspectos = carta["aspectos"]
        balances = carta["balances"]

        resumen_datos = f"""
CONSULTANTE: {sujeto['nombre']} ({sujeto['fecha_hora_local']} hs, Lat {sujeto['latitud']}, Lon {sujeto['longitud']})
POSICIONES:
"""
        for p, info in planetas.items():
            resumen_datos += f"- {p}: {info['formato']} en Casa {info['casa']} ({info['elemento']}, {info['modalidad']})\n"
        resumen_datos += f"- Ascendente: {angulos['Ascendente']['formato']}\n"
        resumen_datos += f"- Medio Cielo: {angulos['Medio Cielo']['formato']}\n"
        resumen_datos += f"- Balances: Elementos {json.dumps(balances['elementos'])}, Modalidades {json.dumps(balances['modalidades'])}\n"
        resumen_datos += f"- Aspectos principales: " + ", ".join([f"{a['cuerpo1']} {a['aspecto']} {a['cuerpo2']} ({a['orbe']}°)" for a in aspectos[:8]])

        # Encabezado del documento
        doc_final = f"""# Carta Astral Profunda: {nombre}
*Mapa de Navegación Psicológica y Geometría del Destino*

![Rueda Astrológica - {nombre}]({rueda_path})

**Datos de nacimiento:** {dt_local.strftime('%d de %B de %Y · %H:%M hs')}
**Sistema de cálculo:** zodíaco tropical, casas Placidus, efemérides Swiss Ephemeris

---

"""
        # Bloques de redacción en 6 etapas modulares (Garantiza 10 páginas sin cortes ni degradación)
        bloques = [
            ("1/6: Preliminares y Mapa de un Vistazo", 
             "Redacta las secciones iniciales:\n"
             "1. '## Bienvenida: qué tenés en las manos' (explicar que no es un horóscopo, precisión astronómica, mapa no sentencia, la tríada qué/cómo/por qué).\n"
             "2. '## Cómo leer este mapa en cinco minutos' (Planeta=Qué, Signo=Cómo, Casa=Dónde; tabla markdown con las 12 casas y su terreno; La rueda paso a paso con Ascendente a la izquierda a 180° y lectura antihoraria).\n"
             "3. '## Tu mapa de un vistazo' (tabla markdown completa con todos los planetas, grados y casas calculados; desglose de Elementos con conteo e interpretación de excesos/carencias; desglose de Modalidades; y análisis de Dónde se concentra la energía / eje conductor)."),

            ("2/6: Capítulo 1 — La Trinidad de la Identidad", 
             "Redacta completo el '## Capítulo 1 — La trinidad de la identidad: Sol, Luna y Ascendente':\n"
             "- Introducción a las 3 capas fundamentales.\n"
             "- '### El Sol en [Signo], Casa [X]': Qué es, Cómo funciona, En tu carta (signo y casa), En la práctica (recurso y punto ciego).\n"
             "- '### La Luna en [Signo], Casa [X]': Qué es, Cómo funciona, En tu carta (signo y casa), En la práctica (recurso y mecanismo defensivo).\n"
             "- '### El Ascendente en [Signo] (y su Regente)': Qué es, Cómo funciona, En tu carta (signo, grado y dónde opera su planeta regente), En la práctica.\n"
             "- Síntesis de integración de la trinidad."),

            ("3/6: Capítulo 2 — Mente, Vínculos y Acción", 
             "Redacta completo el '## Capítulo 2 — Mente, vínculos y acción: Mercurio, Venus y Marte':\n"
             "- '### Mercurio en [Signo], Casa [X]': Función mental, comunicación, estilo de razonamiento (Qué es, Cómo funciona, En tu carta, En la práctica).\n"
             "- '### Venus en [Signo], Casa [X]': Lo que valorás, estilo afectivo, goce y magnetismo (Qué es, Cómo funciona, En tu carta, En la práctica).\n"
             "- '### Marte en [Signo], Casa [X]': Motor de acción, asertividad, impulso y manejo del conflicto (Qué es, Cómo funciona, En tu carta, En la práctica)."),

            ("4/6: Capítulos 3 y 4 — Estructura Social y Mapa Evolutivo", 
             "Redacta los Capítulos 3 y 4:\n"
             "- '## Capítulo 3 — Expansión y estructura: Júpiter y Saturno':\n"
             "  * Júpiter (sentido, confianza, expansión vs desborde).\n"
             "  * Saturno (límite, maduración, frustración formativa y maestría).\n"
             "- '## Capítulo 4 — Mapa evolutivo y sombra: Quirón, Lilith y los Nodos':\n"
             "  * Quirón (la herida nuclear y el talento de resiliencia).\n"
             "  * Lilith (el instinto no domesticado, la sombra y el poder rebelde).\n"
             "  * Eje Nodal: Nodo Norte (dirección de crecimiento) vs Nodo Sur (zona de confort e inercia)."),

            ("5/6: Capítulos 5 y 6 — Generacionales y Vocación", 
             "Redacta los Capítulos 5 y 6:\n"
             "- '## Capítulo 5 — Los planetas generacionales: Urano, Neptuno y Plutón': Explicar su función de fondo y aterrizarlos a la vida cotidiana según la casa que ocupa cada uno en esta carta.\n"
             "- '## Capítulo 6 — Vocación y legado: el Medio Cielo': Analizar el Medio Cielo (MC) y el Fondo del Cielo (IC), la huella pública, vocación y el equilibrio entre vida profesional y raíces íntimas."),

            ("6/6: Capítulo 7 y Cierre — Diálogos Centrales y Despedida", 
             "Redacta el tramo final:\n"
             "- '## Capítulo 7 — Los diálogos centrales: aspectos planetarios': Analizar detalladamente los 4 a 6 aspectos mayores más tensos y armónicos con menor orbe, explicando el diálogo psicológico entre ambos planetas.\n"
             "- '## Cierre del astrólogo': Síntesis integradora sobre cómo opera este mapa como una totalidad, consejos concretos de maduración y despedida con la firma del autor (Tomás).\n"
             "- '### Ficha técnica': Tabla resumen final de efemérides y datos.")
        ]

        for i, (nombre_b, instruccion) in enumerate(bloques):
            print(f"[{nombre}] Generando bloque {nombre_b}...")
            prompt = f"""
DATOS MATEMÁTICOS DEL CONSULTANTE:
{resumen_datos}

TAREA A REDACTAR AHORA:
{instruccion}

REGLAS DE FORMATO:
- Escribe directamente en Markdown impecable.
- NO repitas el título principal de la carta ni la imagen de la rueda (ya están incluidos en el encabezado).
- Mantén el tono pedagógico riguroso, directo, adulto, sin cursilerías ni oráculos abstractos, fiel al Estándar de Oro.
"""
            texto_bloque = self._llamar_ia(prompt, system_prompt)
            doc_final += texto_bloque.strip() + "\n\n---\n\n"


        # Guardar resultado final
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(doc_final)

        print(f"[{nombre}] ¡Carta Astral Premium generada exitosamente en {output_path}!")
        return output_path

if __name__ == "__main__":
    generador = GeneradorCartaNatalProduccion()
    print("Motor de producción listo para generar cartas automatizadas.")
