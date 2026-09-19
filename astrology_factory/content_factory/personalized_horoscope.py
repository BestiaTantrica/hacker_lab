import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from astrology_engine.ephemeris_calculator import EphemerisCalculator
from astrology_engine.aspects_matcher import AspectsMatcher
from content_factory.ai_persona_engine import AIPersonaEngine

class PersonalizedHoroscope:
    def __init__(self):
        self.engine = AIPersonaEngine()
        
    def _get_transit_to_natal_aspects(self, natal, transits):
        matcher = AspectsMatcher()
        cross_aspects = []
        for t_planet, t_pos in transits.items():
            for n_planet, n_pos in natal.items():
                diff = abs(t_pos - n_pos)
                if diff > 180: diff = 360 - diff
                for aspect_name, data in matcher.aspects.items():
                    error_orb = abs(diff - data['angle'])
                    if error_orb <= data['orb']:
                        cross_aspects.append(f"{t_planet} en tránsito hace {aspect_name} exacto a {n_planet} natal (Orbe: {round(error_orb, 2)}°)")
        return cross_aspects
        
    def _get_latest_video_script(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            v_path = os.path.join(base_dir, "content_factory", "vademecum.json")
            if os.path.exists(v_path):
                with open(v_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                        return data[0].get("guion", "")
        except:
            pass
        return ""

    def generate_for_user(self, name, birth_date, birth_time, lat=-34.6037, lon=-58.3816):
        calc = EphemerisCalculator()
        
        # 1. Carta Natal Completa
        try:
            dt_natal = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"mensaje_personalizado": "<p>Error en la fecha/hora de nacimiento.</p>"}
            
        natal_positions = calc.calculate_planets(dt_natal, utc_offset_hours=-3)
        natal_houses = calc.calculate_houses(dt_natal, lat, lon, utc_offset_hours=-3)
        
        # 2. Tránsitos Actuales
        now = datetime.utcnow()
        current_positions = calc.calculate_planets(now)
        
        # 3. Aspectos Clínicos Reales
        transitos_a_natal = self._get_transit_to_natal_aspects(natal_positions, current_positions)
        
        # 4. Contexto del último video
        video_context = self._get_latest_video_script()
        
        self.engine.system_prompt = f"""
        Eres un Astrólogo Clínico y Sociológico de la Factoría Astrológica. 
        Tu objetivo es realizar un estudio profundo de TODA LA CARTA NATAL de este usuario y cruzarlo con los tránsitos actuales.
        No te limites a sol/luna/ascendente. Tienes todos los planetas, casas y aspectos exactos (Tránsitos a Natal).
        Usa los grados matemáticos que recibas en el JSON.
        
        El usuario acaba de ver (o recibirá un mail sobre) nuestro último video. El guion de ese video es:
        "{video_context}"
        
        Debes hilar tu lectura personalizada en perfecta cohesión con la temática de ese guion.
        Sé profundo, sociológico y empático. 
        Al final, recuérdale que su aporte y donación permite mantener este servidor corriendo.
        Formato de Salida Obligatorio: Un JSON estricto con una clave "mensaje_personalizado" que contenga el texto completo (HTML).
        """
        
        astro_data = {
            "usuario": name,
            "carta_natal": {
                "planetas_grados_exactos": natal_positions,
                "casas_astrologicas": natal_houses
            },
            "transitos_ahora": current_positions,
            "aspectos_transitos_a_natal": transitos_a_natal
        }
        
        print("Solicitando lectura clínica y sociológica a la IA...")
        content = self.engine.generate_content(astro_data)
        
        if content and "mensaje_personalizado" in content:
            return content
        else:
            return {"mensaje_personalizado": f"<p>Hola {name}, los servidores astronómicos están bajo mucha carga ahora mismo. Vuelve a intentar en unos minutos.</p>"}

if __name__ == "__main__":
    ph = PersonalizedHoroscope()
    res = ph.generate_for_user("Tomy", "1995-10-23", "14:30")
    print(res)
