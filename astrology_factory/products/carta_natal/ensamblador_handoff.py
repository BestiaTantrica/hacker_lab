import os
import json
from datetime import datetime
from typing import Dict, Any

from calculador_astronomico import CalculadorAstronomico
from graficador_rueda import GraficadorRuedaAstrologica
from adn_autor import INSTRUCCION_ADN_AUTOR, TOMAS_NATAL_DATA
from base_teorica import MARCO_TEORICO

class EnsambladorHandoff:
    def __init__(self):
        self.calculador = CalculadorAstronomico()
        self.graficador = GraficadorRuedaAstrologica()

    def procesar_carta(self, nombre: str, dt_local: datetime, lat: float, lon: float, utc_offset: float, output_dir: str) -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        slug = nombre.lower().replace(" ", "_")

        # 1. Cálculo Astronómico Determinístico (0 llamadas a API)
        print(f"[{nombre}] 1. Calculando posiciones astronómicas y aspectos...")
        carta_data = self.calculador.calcular_carta(nombre, dt_local, lat, lon, utc_offset)

        # Guardar JSON de datos puros
        json_path = os.path.join(output_dir, f"datos_{slug}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(carta_data, f, indent=2, ensure_ascii=False)

        # 2. Renderizado de la Rueda Astrológica Profesional (0 llamadas a API)
        print(f"[{nombre}] 2. Generando rueda astrológica en alta resolución...")
        rueda_filename = f"rueda_{slug}.png"
        rueda_path = os.path.join(output_dir, rueda_filename)
        self.graficador.generar_rueda(carta_data, rueda_path)

        # 3. Construcción del Prompt Maestro de Handoff para Claude
        print(f"[{nombre}] 3. Compilando paquete de handoff para Claude...")
        prompt_content = self._generar_prompt_claude(carta_data, rueda_filename)
        
        prompt_path = os.path.join(output_dir, f"handoff_claude_{slug}.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_content)

        print(f"[{nombre}] ¡Listo! Archivos generados en: {output_dir}")
        return {
            "json_datos": json_path,
            "rueda_png": rueda_path,
            "handoff_prompt": prompt_path
        }

    def _generar_prompt_claude(self, carta: Dict[str, Any], rueda_filename: str) -> str:
        sujeto = carta["sujeto"]
        planetas = carta["planetas"]
        angulos = carta["angulos"]
        casas = carta["casas"]
        aspectos = carta["aspectos"]
        balances = carta["balances"]

        # Resumen formateado de posiciones
        posiciones_txt = "### TABLA DE POSICIONES EXACTAS (SWISS EPHEMERIS):\n"
        for p_name, p_info in planetas.items():
            posiciones_txt += f"- **{p_name}**: {p_info['formato']} en **Casa {p_info['casa']}** (Elemento: {p_info['elemento']}, Modalidad: {p_info['modalidad']})\n"
        
        posiciones_txt += "\n### ÁNGULOS Y CASAS CLAVE:\n"
        posiciones_txt += f"- **Ascendente (Casa 1)**: {angulos['Ascendente']['formato']}\n"
        posiciones_txt += f"- **Medio Cielo (Casa 10)**: {angulos['Medio Cielo']['formato']}\n"
        posiciones_txt += f"- **Descendente (Casa 7)**: {angulos['Descendente']['formato']}\n"
        posiciones_txt += f"- **Fondo Cielo (Casa 4)**: {angulos['Fondo Cielo']['formato']}\n"

        posiciones_txt += "\n### BALANCE ELEMENTAL Y MODAL:\n"
        posiciones_txt += f"- **Elementos**: Fuego: {balances['elementos']['Fuego']} | Tierra: {balances['elementos']['Tierra']} | Aire: {balances['elementos']['Aire']} | Agua: {balances['elementos']['Agua']}\n"
        posiciones_txt += f"- **Modalidades**: Cardinal: {balances['modalidades']['Cardinal']} | Fijo: {balances['modalidades']['Fijo']} | Mutable: {balances['modalidades']['Mutable']}\n"

        # Aspectos significativos (ordenados por orbe)
        aspectos_txt = "\n### ASPECTOS INTERPLANETARIOS EXACTOS (Ordenados por menor orbe):\n"
        aspectos_ordenados = sorted(aspectos, key=lambda x: x["orbe"])[:12] # Los 12 más exactos
        for asp in aspectos_ordenados:
            aspectos_txt += f"- **{asp['cuerpo1']}** en {asp['aspecto']} a **{asp['cuerpo2']}** (Ángulo: {asp['diferencia']}°, Orbe: {asp['orbe']}° - {asp['tipo'].upper()})\n"

        prompt = f"""# PAQUETE DE HANDOFF PARA CLAUDE: CARTA ASTRAL PREMIUM
**Destinatario**: Claude (o modelo de lenguaje superior)
**Objetivo**: Redactar el informe definitivo de Carta Astral para **{sujeto['nombre']}** con la máxima calidad literaria, psicológica y pedagógica.

---

## 1. TU IDENTIDAD COMO AUTOR (EL ADN DE TOMÁS)

{INSTRUCCION_ADN_AUTOR}

---

## 2. DATOS MATEMÁTICOS DEL CONSULTANTE

- **Nombre**: {sujeto['nombre']}
- **Nacimiento**: {sujeto['fecha_hora_local']} (Hora Local) | Coordenadas: {sujeto['latitud']}° Lat, {sujeto['longitud']}° Lon
- **Imagen de la Rueda**: `![Rueda Astrológica]({rueda_filename})`

{posiciones_txt}
{aspectos_txt}

---

## 3. MARCO TEÓRICO PEDAGÓGICO DE REFERENCIA

Utiliza las siguientes definiciones conceptuales para estructurar las explicaciones de cada astro (sin copiarlas textualmente, úsalas como brújula para explicar 'qué es, cómo funciona y por qué'):

```json
{json.dumps(MARCO_TEORICO, indent=2, ensure_ascii=False)}
```

---

## 4. ESTRUCTURA OBLIGATORIA DEL REPORTE FINAL

Redacta el informe en Markdown pulcro, extenso, generoso y profundo, siguiendo este índice:

### Portada y Gráfico
- Título principal: `# Carta Astral Profunda: {sujeto['nombre']}`
- Subtítulo: `*Mapa de Navegación Psicológica y Geometría del Destino*`
- Incrustación de la rueda: `![Rueda Astrológica - {sujeto['nombre']}]({rueda_filename})`
- Breve introducción de bienvenida: qué es una carta astral (la foto del cielo en tu primer respiro como mapa de potencialidades vivas, no como condena fatalista).

### Capítulo 1: La Trinidad de la Identidad (El Núcleo del Ser)
- **El Sol**: Explica qué es el Sol en astrología (tu centro consciente, tu vitalidad). Analiza el Sol de {sujeto['nombre']} en su signo y casa específicos. ¿Cómo busca autorrealizarse? ¿Cuáles son sus trampas de ego?
- **La Luna**: Explica qué es la Luna (el sistema emocional automático, el refugio instintivo). Analiza la Luna en su signo y casa. ¿Qué necesita para sentirse a salvo? ¿Cómo reacciona bajo estrés?
- **El Ascendente**: Explica qué es el Ascendente (el horizonte de entrada, la interfaz con el mundo y el camino de aprendizaje). Analiza su signo ascendente. ¿Cómo lo perciben los demás y cómo encara los comienzos?

### Capítulo 2: Dinámicas de Deseo, Vínculos y Acción
- **Venus**: El principio de valoración, goce y amor. En qué signo y casa está, qué le atrae y cómo construye puentes afectivos.
- **Marte**: El motor de arranque, la conquista y el manejo de la asertividad y la rabia. Cómo acciona en su signo y casa.

### Capítulo 3: El Mapa Kármico y la Maestría de la Sombra
- **Quirón**: La herida que deviene en maestría. En qué área duele y cómo se transmuta en sabiduría.
- **Lilith**: La fuerza salvaje y el límite visceral no negociable. Dónde reclama soberanía absoluta.
- **Los Nodos Lunares**: El eje evolutivo. De dónde viene (Nodo Sur: zona de confort) y hacia dónde empuja el crecimiento (Nodo Norte).

### Capítulo 4: Vocación y Legado (Medio Cielo)
- Análisis del Medio Cielo en su signo y casa 10: qué tipo de autoridad, reputación y aporte al mundo está llamado a construir.

### Capítulo 5: Los Diálogos Centrales (Aspectos Planetarios Mayores)
- Interpreta los 3 o 4 aspectos más tensos o armónicos de la carta (ej. cuadraturas, trígonos, conjunciones). Explica cómo esas dos fuerzas internas dialogan o tiranonean en la psique cotidiana.

### Cierre del Astrólogo
- Mensaje final sobrio, empoderador y reflexivo que invite a la integración de todas estas partes, firmado como:
  *Tomás — Laboratorio de Astrología*

---
¡ADELANTE CLAUDE! Escribe el reporte completo ahora en Markdown, sin censuras, sin rodeos, con la madurez, la agudeza y la riqueza que este consultante espera recibir.
"""
        return prompt

if __name__ == "__main__":
    ensamblador = EnsambladorHandoff()
    dt = datetime(1987, 6, 24, 20, 30)
    res = ensamblador.procesar_carta(
        nombre="Lionel Messi",
        dt_local=dt,
        lat=-32.9468,
        lon=-60.6393,
        utc_offset=-3.0,
        output_dir="/home/LAB/astrology_factory/products/carta_natal/output_messi"
    )
    print("Resultado del pipeline:", res)
