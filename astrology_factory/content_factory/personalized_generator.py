import os
import json
from google import genai
from google.genai import types
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from astrology_engine.ephemeris_calculator import EphemerisCalculator

class PersonalizedGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
            
        self.system_prompt = """
        Eres un astrólogo experto, con humor ácido, crítico y muy humano. Tu empatía es real: dices las cosas como son, con profundidad psicológica.
        
        REGLA DE REDACCIÓN ASTRAL:
        No tires conclusiones al aire. Debes dar una brevísima referencia fácil de entender sobre QUÉ significa ese planeta ahí y QUÉ área de la vida afecta.
        Ejemplo correcto: "Venus, que rige cómo nos vinculamos y el amor, estaba en Libra, el signo de la armonía, cuando naciste. Por eso tienes la necesidad tóxica de complacer a todos para evitar el conflicto."
        Explica el 'por qué' astrológico (sin aburrir, de forma dinámica y empática) para que la gente aprenda mientras se emociona.
        
        Debes escribir una lectura personalizada directa al usuario en formato HTML (sin las etiquetas <html> o <body>, solo el contenido como <h1>, <p>, <strong>).
        Debe sonar a una carta íntima, que empiece saludando por su nombre.
        
        Al final, SIEMPRE INCLUYE ESTE PÁRRAFO EXACTO en HTML:
        <p><em>Espero que esta lectura haya sacudido tu universo. Hacemos esto gratis, así que si quieres recibir tu horóscopo semanal personalizado a partir de ahora, te pido un favor a cambio: ve a nuestro perfil de <a href="https://www.youtube.com/@portaltarotmistico">YouTube</a> o <a href="https://www.tiktok.com/@portaltarotmistico">TikTok</a> y déjanos un comentario en nuestro video más reciente. Luego, haz clic en el siguiente enlace mágico para activar tus envíos semanales automáticos: <br><br><strong><a href="http://143.47.115.34:8000/activar/{{EMAIL}}">💫 ACTIVAR MI HORÓSCOPO SEMANAL</a></strong></em></p>
        """

    def generate_welcome_email(self, name, email, birth_date):
        if not self.client:
            return f"<h1>Hola {name}</h1><p>Falta la GEMINI_API_KEY en el entorno.</p>"
            
        try:
            # Aproximamos la fecha para calcular los planetas
            bdate = datetime.strptime(birth_date, "%Y-%m-%d")
            calc = EphemerisCalculator()
            positions = calc.calculate_planets(bdate)
            
            prompt = f"El usuario se llama {name}. Sus posiciones planetarias al nacer fueron: {json.dumps(positions, indent=2)}. Redacta su Carta Astral Base. Recuerda incluir el enlace mágico al final asegurándote de reemplazar {{EMAIL}} por {email}."
            
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.8
                ),
            )
            html_content = response.text.replace('{{EMAIL}}', email)
            # Limpiar posible markdown wrap de HTML
            if html_content.startswith("```html"):
                html_content = html_content[7:-3].strip()
                
            return html_content
            
        except Exception as e:
            print(f"Error generando contenido con IA: {e}")
            return f"<h1>Error</h1><p>{str(e)}</p>"
