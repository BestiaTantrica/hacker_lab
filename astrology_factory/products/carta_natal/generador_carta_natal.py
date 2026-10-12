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
        # Bloques de redacción
        bloques = [
            ("Introducción y Trinidad", "Escribe la bienvenida pedagógica (qué tenés en las manos, cómo leer este mapa con la tabla de casas y el resumen de elementos/modalidades) y el Capítulo 1 completo: La Trinidad de la Identidad (Sol, Luna y Ascendente explicados a fondo con qué es, cómo funciona y en la práctica)."),
            ("Mente, Vínculos y Acción", "Escribe el Capítulo 2 (Mercurio, Venus y Marte) y el Capítulo 3 (Júpiter y Saturno: expansión y estructura), analizando cada astro en su signo, casa y aspectos según los datos provistos."),
            ("Karma, Vocación y Aspectos", "Escribe el Capítulo 4 (Quirón, Lilith y Nodos Lunares), el Capítulo 5 (Planetas generacionales), el Capítulo 6 (Medio Cielo y vocación), el Capítulo 7 (Los diálogos centrales / aspectos mayores) y el Cierre del astrólogo firmado por Tomás.")
        ]

        for i, (nombre_b, instruccion) in enumerate(bloques):
            print(f"[{nombre}] Generando bloque {i+1}/3: {nombre_b}...")
            prompt = f"""
DATOS MATEMÁTICOS DEL CONSULTANTE:
{resumen_datos}

TAREA A REDACTAR AHORA:
{instruccion}

Escribe directamente en formato Markdown impecable, siguiendo rigurosamente el tono y nivel de detalle del Estándar de Oro.
"""
            texto_bloque = self._llamar_ia(prompt, system_prompt)
            doc_final += texto_bloque + "\n\n---\n\n"

        # Guardar resultado final
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(doc_final)

        print(f"[{nombre}] ¡Carta Astral Premium generada exitosamente en {output_path}!")
        return output_path

if __name__ == "__main__":
    generador = GeneradorCartaNatalProduccion()
    print("Motor de producción listo para generar cartas automatizadas.")
