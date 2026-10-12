import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Importar motores astronómicos y graficador
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "carta_natal"))
from calculador_astronomico import CalculadorAstronomico
from adn_autor import INSTRUCCION_ADN_AUTOR
from base_teorica import MARCO_TEORICO

from calculador_revolucion_solar import CalculadorRevolucionSolar
from graficador_biwheel import GraficadorBiWheelAstrologica

class EnsambladorHandoffRS:
    """
    Compila el paquete integral de datos y construye el Super-Prompt de Handoff para Claude (Medium)
    para generar el Guion de Oro de la Revolución Solar en Video.
    Garantiza el emparejamiento perfecto entre la Carta Astral Escrita y el Video de la RS.
    """
    def __init__(self):
        self.calc_natal = CalculadorAstronomico()
        self.calc_rs = CalculadorRevolucionSolar()
        self.graficador = GraficadorBiWheelAstrologica()

    def procesar_paquete_rs(
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
    ) -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        slug = nombre.lower().replace(" ", "_")

        # 1. Cálculo de Carta Natal Base
        print(f"[{nombre}] 1. Calculando Carta Natal base...")
        carta_natal = self.calc_natal.calcular_carta(nombre, dt_natal_local, lat_natal, lon_natal, utc_offset_natal)

        # 2. Cálculo de Revolución Solar y Superposiciones
        print(f"[{nombre}] 2. Calculando Revolución Solar {anio_rs} y matriz de superposición...")
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

        # 3. Renderizado de la Rueda Bi-Wheel Espacial
        print(f"[{nombre}] 3. Renderizando Bi-Wheel espacial en alta definición...")
        biwheel_filename = f"biwheel_{slug}_{anio_rs}.png"
        biwheel_path = os.path.join(output_dir, biwheel_filename)
        self.graficador.generar_biwheel(carta_natal, carta_rs, biwheel_path)

        # 4. Generación del Super-Prompt de Handoff para Claude
        print(f"[{nombre}] 4. Compilando Super-Prompt de Handoff para Claude...")
        prompt_content = self._generar_prompt_claude(carta_natal, carta_rs, biwheel_filename)
        
        prompt_path = os.path.join(output_dir, f"handoff_claude_rs_{slug}_{anio_rs}.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_content)

        print(f"[{nombre}] ¡Paquete de Handoff listo en {output_dir}!")
        return {
            "json_datos": json_path,
            "biwheel_png": biwheel_path,
            "handoff_prompt": prompt_path
        }

    def _generar_prompt_claude(self, carta_natal: Dict[str, Any], carta_rs: Dict[str, Any], biwheel_filename: str) -> str:
        sujeto = carta_natal["sujeto"]
        rs_meta = carta_rs["revolucion_solar"]
        planetas_natal = carta_natal["planetas"]
        angulos_natal = carta_natal["angulos"]
        
        planetas_rs = carta_rs["planetas_rs"]
        angulos_rs = carta_rs["angulos_rs"]
        superposicion = carta_rs["superposicion_clave"]
        aspectos_act = carta_rs["aspectos_intercartas"]

        # Resumen formateado de Carta Natal
        natal_txt = "### 1. MATRIZ DE NACIMIENTO (CARTA NATAL BASE - EL INFORME ESCRITO):\n"
        natal_txt += f"- **Ascendente Natal**: {angulos_natal['Ascendente']['formato']}\n"
        natal_txt += f"- **Medio Cielo Natal**: {angulos_natal['Medio Cielo']['formato']}\n"
        for p, info in planetas_natal.items():
            natal_txt += f"- **{p} Natal**: {info['formato']} en Casa {info['casa']} ({info['elemento']}, {info['modalidad']})\n"

        # Resumen formateado de Revolución Solar
        rs_txt = f"\n### 2. CLIMA DEL AÑO (REVOLUCIÓN SOLAR {rs_meta['anio']} EN {rs_meta['ciudad_retorno'].upper()}):\n"
        rs_txt += f"- **Momento exacto del Retorno Solar**: {rs_meta['fecha_hora_exacta_local']} hs (Local)\n"
        rs_txt += f"- **Ascendente de la RS**: {angulos_rs['Ascendente_RS']['formato']} -> **¡Cae en tu Casa Natal {superposicion['ascendente_rs_en_casa_natal']['casa_natal']}!**\n"
        rs_txt += f"- **Medio Cielo de la RS**: {angulos_rs['Medio_Cielo_RS']['formato']} -> Cae en Casa Natal {angulos_rs['Medio_Cielo_RS']['casa_natal_superpuesta']}\n"
        for p, info in planetas_rs.items():
            rs_txt += f"- **{p} RS**: {info['formato']} (Casa {info['casa_rs']} de RS / **Casa {info['casa_natal']} Natal**)\n"

        # Matriz de Superposiciones Clave
        sup_txt = "\n### 3. LOS 5 EJES CLAVE DE ACTIVACIÓN ANUAL (EL PUENTE ENTRE EL VIDEO Y EL TEXTO):\n"
        sup_txt += f"1. **Ascendente del Año**: Cae en Casa Natal {superposicion['ascendente_rs_en_casa_natal']['casa_natal']} ({superposicion['ascendente_rs_en_casa_natal']['grado_formato']}). Este es el portal del año: el escenario de vida donde se sentirá la energía cardinal durante los 12 meses.\n"
        sup_txt += f"2. **Luna del Año**: {superposicion['luna_rs_en_casas']['formato']} en Casa {superposicion['luna_rs_en_casas']['casa_rs']} de RS y Casa Natal {superposicion['luna_rs_en_casas']['casa_natal']}. Muestra la necesidad emocional y dónde buscará refugio la persona este año.\n"
        sup_txt += f"3. **Marte del Año**: {superposicion['marte_rs_en_casas']['formato']} en Casa {superposicion['marte_rs_en_casas']['casa_rs']} de RS y Casa Natal {superposicion['marte_rs_en_casas']['casa_natal']}. Motor de acción, ambición o punto de fricción/conflicto.\n"
        sup_txt += f"4. **Júpiter del Año**: {superposicion['jupiter_rs_en_casas']['formato']} en Casa {superposicion['jupiter_rs_en_casas']['casa_rs']} de RS y Casa Natal {superposicion['jupiter_rs_en_casas']['casa_natal']}. El terreno de expansión, oportunidades y sentido.\n"
        sup_txt += f"5. **Saturno del Año**: {superposicion['saturno_rs_en_casas']['formato']} en Casa {superposicion['saturno_rs_en_casas']['casa_rs']} de RS y Casa Natal {superposicion['saturno_rs_en_casas']['casa_natal']}. La prueba de maduración, límites y exigencia estructural.\n"

        # Top 8 aspectos inter-cartas
        asp_txt = "\n### 4. ASPECTOS MAYORES DE ACTIVACIÓN (PLANETAS DEL AÑO TOCANDO TU CARTA NATAL):\n"
        for asp in aspectos_act[:8]:
            asp_txt += f"- **{asp['descripcion']}** ({asp['tipo'].upper()})\n"

        prompt = f"""# PAQUETE DE HANDOFF PARA CLAUDE: GUION DE ORO REVOLUCIÓN SOLAR (VIDEO PREMIUM)
**Destinatario**: Claude 3.7 / 3.5 Sonnet (Modo Normal / Medium)
**Objetivo**: Escribir el **Guion Maestro de Locución y Realización de Video** de la Revolución Solar {rs_meta['anio']} para **{sujeto['nombre']}**.
**Duración Estimada**: 10 a 14 minutos de video (aprox. 1.800 a 2.300 palabras de locución profunda).
**Imagen de Rueda Bi-Wheel**: `![Rueda Bi-Wheel]({biwheel_filename})`

---

## 1. TU IDENTIDAD COMO AUTOR (EL ADN DE TOMÁS)

{INSTRUCCION_ADN_AUTOR}

### REGLAS DE ORO MANDATORIAS PARA ESTE GUION:
1. **EL ENLACE OBLIGATORIO CON EL REPORTE ESCRITO**:
   - Este video se entrega **junto con la Carta Natal escrita de 10 páginas**. El consultante ya tiene su informe en la mano o lo va a leer en simultáneo.
   - Tu guion DEBE hacer referencias claras y pedagógicas a su carta natal base.
2. **CERO LENGUAJE DE COACHING CORPORATIVO O METÁFORAS DE SOFTWARE**:
   - Prohibido hablar de "recalibración de software", "hardware", "aceleradores/chasis", "mostrame los números" o tips de productividad.
   - Escribe con peso arquetípico, densidad existencial y filo literario.
3. **CERO PARÉNTESIS EN [VOZ / LOCUCIÓN]**:
   - El texto de locución debe ser limpio al 100% para el motor TTS. Ninguna acotación escénica entre paréntesis dentro de la voz.
4. **CAPÍTULO 6: PROHIBIDO ENUMERAR CON LISTAS O VIÑETAS**:
   - El Capítulo 6 debe ser un **MANIFIESTO CONTINUO**, un monólogo cinematográfico y filosófico que integre el año y despida al consultante con aplomo y autoridad serena.
5. **FIRMA DE CIERRE**:
   - La locución debe cerrar exactamente con *"Tomás. portaltarotmistico.com"*.
6. **FORMATO**:
   - El guion debe estar dividido exactamente en **6 Capítulos**.
   - Cada capítulo debe incluir:
     * **[VOZ / LOCUCIÓN]**: El texto exacto que pronunciará la voz de Tomás (sin anotaciones entremedio para que el TTS lo lea fluido).
     * **[INDICACIONES VISUALES]**: Cuándo enfocar la rueda Bi-Wheel, qué planeta resaltar, o qué tipo de clip de stock emocional/abstracto debe acompañar la toma.
     * **[CLIMA SONORO]**: Tono de la música o pausas dramáticas.
   - Total de palabras de locución entre 2.000 y 2.300 palabras. Voseo argentino sobrio y maduro.

---

## 2. DATOS MATEMÁTICOS DEL CONSULTANTE Y DE LA REVOLUCIÓN SOLAR

- **Consultante**: {sujeto['nombre']}
- **Nacimiento**: {sujeto['fecha_hora_local']} hs | Lat {sujeto['latitud']}, Lon {sujeto['longitud']}
- **Año de la Revolución Solar**: {rs_meta['anio']} (Cumpleaños en {rs_meta['ciudad_retorno']})
- **Retorno Solar Exacto**: {rs_meta['fecha_hora_exacta_local']} hs (Local)

{natal_txt}
{rs_txt}
{sup_txt}
{asp_txt}

---

## 3. ESTRUCTURA OBLIGATORIA DEL GUION DE VIDEO (6 CAPÍTULOS)

Redacta el guion completo siguiendo esta estructura capitulada:

### Capítulo 1: El Clima del Año y el Portal del Ascendente Anual (~320 - 400 palabras)
- Bienvenida de Tomás. Qué es una Revolución Solar: la descripción de qué zonas de tu vida quedan iluminadas y cuáles en penumbra durante doce meses, sin destinos cerrados ni sentencias.
- El Ascendente de la Revolución Solar: su signo y grado, pero fundamentalmente **en qué Casa Natal cae**. ¿Qué escenario de tu vida se convierte en el epicentro obligatorio de los próximos doce meses?

### Capítulo 2: La Trinidad Anual: El Sol y la Luna del Retorno (~350 - 420 palabras)
- El Sol en su retorno: el combustible de vitalidad y el área de la carta donde pide brillar este año.
- La Luna de la Revolución Solar: en qué signo y casa (anual y natal) se ubica. ¿Qué va a necesitar tu mundo emocional para no entrar en defensividad o desborde?

### Capítulo 3: El Vector de Acción y Vínculos: Marte y Venus del Año (~320 - 400 palabras)
- Marte de la RS: dónde está el motor de conquista, la ambición o el riesgo de frustración/enojo.
- Venus de la RS: qué tipo de armonía, finanzas y relaciones busca construir durante este ciclo.

### Capítulo 4: La Estructura y la Expansión: Saturno y Júpiter Anuales (~350 - 420 palabras)
- Saturno del año: la prueba de realidad, madurez, paciencia y límites indispensables.
- Júpiter del año: el respiro, la confianza, la ventana de oportunidad y la síntesis con la carta base.

### Capítulo 5: Puntos de Inflexión: Los Aspectos Mayores de Activación (~380 - 450 palabras)
- Analiza detalladamente los aspectos más exactos entre los planetas del año y tus planetas natales con profundidad psicológica implacable (sin autoayuda superficial). ¿Qué nudo arquetípico se enciende este año?

### Capítulo 6: Manifiesto de Navegación y Cierre del Astrólogo (~300 - 380 palabras)
- MANIFIESTO CONTINUO: Prohibido enumerar "1, 2, 3, 4, 5".
- Síntesis integradora de Tomás: cómo conectar este año con la totalidad de tu Carta Natal que tenés por escrito.
- Despedida con peso filosófico, gravedad y calidez austera.
- Cierre y firma: *Tomás. portaltarotmistico.com*.

---

¡ADELANTE CLAUDE! Escribe el guion completo ahora en Markdown con modo High / Thinking activado, entregando una obra maestra de calibre internacional.
"""
        return prompt

if __name__ == "__main__":
    ensamblador = EnsambladorHandoffRS()
    print("Ensamblador de Handoff para Revolución Solar listo.")
