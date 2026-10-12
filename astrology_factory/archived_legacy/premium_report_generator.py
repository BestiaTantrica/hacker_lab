import os
import json
from datetime import datetime

from astrology_engine.ephemeris_calculator import EphemerisCalculator
from content_factory.ai_persona_engine import AIPersonaEngine
from content_factory.wheel_generator import AstrologyWheelGenerator

class PremiumReportGenerator:
    def __init__(self):
        self.ai_engine = AIPersonaEngine()
        self.ephemeris = EphemerisCalculator()
        self.wheel_gen = AstrologyWheelGenerator()
        
    def _get_zodiac_sign(self, degree: float) -> str:
        ZODIAC_SIGNS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
                        "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        sign_index = int(degree // 30)
        return ZODIAC_SIGNS[sign_index]

    def _format_degree(self, degree: float) -> str:
        sign_deg = degree % 30
        return f"{int(sign_deg)}°"

    def generate_report(self, name: str, dt: datetime, lat: float, lon: float, utc_offset: float, output_path: str):
        # 1. Calcular Datos Astrológicos Exactos
        planets = self.ephemeris.calculate_planets(dt, utc_offset_hours=utc_offset)
        houses = self.ephemeris.calculate_houses(dt, lat, lon, utc_offset_hours=utc_offset)
        
        chart_data = f"CARTA ASTRAL DE: {name}\n"
        chart_data += f"Nacimiento: {dt} (Offset: {utc_offset})\n\n"
        chart_data += "PLANETAS Y PUNTOS KÁRMICOS:\n"
        for p_name, deg in planets.items():
            chart_data += f"- {p_name}: {self._get_zodiac_sign(deg)} a {self._format_degree(deg)}\n"
            
        chart_data += "\nCASAS Y ÁNGULOS:\n"
        chart_data += f"- Ascendente (Casa 1): {self._get_zodiac_sign(houses['Ascendente'])} a {self._format_degree(houses['Ascendente'])}\n"
        chart_data += f"- Medio Cielo (Casa 10): {self._get_zodiac_sign(houses['Medio Cielo'])} a {self._format_degree(houses['Medio Cielo'])}\n"
        for i, cusp in enumerate(houses['Casas']):
            chart_data += f"- Casa {i+1}: {self._get_zodiac_sign(cusp)} a {self._format_degree(cusp)}\n"

        # 2. Generar Imagen de la Rueda (Premium Visual)
        image_name = f"rueda_{name.replace(' ', '_').lower()}.png"
        image_path = os.path.join(os.path.dirname(output_path), image_name)
        self.wheel_gen.generate_wheel(planets, houses, name, image_path)
        print(f"Rueda visual generada en {image_path}")

        # 3. Leer ADN de Tomás (Firma de Autor) pre-calculada
        # Si el archivo no existe, usamos la firma hardcodeada directamente para no fallar
        tomas_adn = """[ADN ASTROLÓGICO Y MATRIZ KÁRMICA DEL AUTOR]
Eres Tomás. Escribes con tu firma astrológica pura. Tu tono es expansivo, místico, académico e hiper-inteligente.
Rechazas las explicaciones mundanas (profesiones, consejos baratos, deportes). Te enfocas en la Geometría del Alma. Eres directo pero poético.

TUS POSICIONES REALES:
- Sol: Aries 21° | Luna: Sagitario 5° | Ascendente: Acuario 21° | Mercurio: Aries 22° | Venus: Piscis 5° | Marte: Libra 5°
- Júpiter: Escorpio 7° | Saturno: Libra 18° | Quirón: Tauro 20° | Nodo Norte: Cáncer 17° | Lilith: Sagitario 22°
"""
        adn_path = "/home/LAB/astrology_factory/content_factory/tomas_adn.txt"
        if os.path.exists(adn_path):
            with open(adn_path, "r", encoding="utf-8") as f:
                tomas_adn = f.read()

        system_prompt_base = f"""
{tomas_adn}

Tu trabajo es redactar la "Carta Astral Profunda" (Premium) para el cliente basándote en la matemática celeste provista.
ERES UN ACADÉMICO DEL COSMOS. EXPLICA LA MECÁNICA CELESTE Y EL ARQUETIPO PSICOLÓGICO PROFUNDO. 
Concéntrate en la geometría del alma y el diseño cósmico. NO des consejos mundanos, NO menciones profesiones específicas, fútbol ni deportes. Escribe para el alma, traduciendo el código fuente del universo.
"""

        # 4. Pipeline de Chunking (Evita el truncamiento de 8k tokens y permite máxima profundidad)
        final_markdown = f"# Carta Astral Profunda: {name}\n*Un viaje al núcleo de tu ser cósmico.*\n\n"
        final_markdown += f"![Rueda Astrológica - {name}]({image_path})\n\n---\n\n"

        chunks = [
            {
                "title": "La Trinidad de la Identidad",
                "instruction": "Analiza profundamente: El Sol (esencia), La Luna (refugio emocional) y El Ascendente (la máscara y destino). Dedica varios párrafos a cada uno, siendo lo más profundo y poético posible. Utiliza subtítulos Markdown (H2 para el título del chunk, H3 para cada astro)."
            },
            {
                "title": "El Camino del Karma y la Sombra",
                "instruction": "Analiza profundamente: Quirón (la herida sanadora), Lilith (el lado salvaje y rebelde) y El Nodo Norte (el propósito evolutivo del alma). Dedica múltiples párrafos detallados a cada uno. Utiliza subtítulos Markdown (H2 para el título del chunk, H3 para cada punto)."
            },
            {
                "title": "Dinámicas del Poder y el Deseo",
                "instruction": "Analiza profundamente: Venus (cómo ama y seduce), Marte (cómo pelea y acciona) y el Medio Cielo / Casa 10 (la vocación suprema a nivel del alma, NO trabajos literales). Dedica párrafos extensos a cada uno y finaliza con un breve párrafo de cierre para el reporte entero. Utiliza subtítulos Markdown (H2, H3)."
            }
        ]

        for i, chunk in enumerate(chunks):
            print(f"Llamando a Hydra para el Chunk {i+1}: {chunk['title']}...")
            prompt = f"Datos Astrológicos del Cliente:\n{chart_data}\n\nINSTRUCCIÓN PARA ESTA SECCIÓN:\n{chunk['instruction']}\n\nEscribe ÚNICAMENTE esta sección en formato Markdown impecable. No incluyas conclusiones globales si no se piden."
            
            response_text = self.ai_engine.generate_text_with_fallback(
                prompt=prompt, 
                system_prompt_override=system_prompt_base
            )
            
            if response_text:
                final_markdown += response_text + "\n\n---\n\n"
            else:
                print(f"Error generando el Chunk {i+1}. Abortando pipeline.")
                return

        # 5. Guardar Archivo
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)
        print(f"¡Reporte Premium Completo y Gráfico generados en {output_path}!")

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    
    generator = PremiumReportGenerator()
    dt = datetime(1987, 6, 24, 20, 30)
    output = "/home/tomas2/.gemini/antigravity/brain/a6fd2c41-9e37-4aea-9761-88f9857f6536/carta_premium_messi.md"
    generator.generate_report("Lionel Messi", dt, -32.9468, -60.6393, -3, output)
