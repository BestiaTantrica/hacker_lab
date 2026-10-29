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
        
    def _degrees_to_zodiac(self, degree):
        signs = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]
        sign_index = int(degree / 30) % 12
        sign_degree = degree % 30
        return f"{int(sign_degree)}° {signs[sign_index]}"
        
    def _build_natal_chart_html(self, natal_positions, natal_houses):
        html = '<div style="background: rgba(13, 19, 38, 0.9); padding: 22px; border-radius: 12px; margin-bottom: 20px; border: 1.5px solid rgba(246, 196, 69, 0.4); box-shadow: 0 8px 30px rgba(0,0,0,0.7); color: #e2e8f0;">'
        html += '<h3 style="color: #f6c445; margin-top: 0; font-family: \'Cinzel\', serif; font-size: 1.25rem; display: flex; align-items: center; gap: 8px;"><span>🌌</span> Fotografía Celeste de tu Nacimiento</h3>'
        html += '<p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 16px;">Posiciones astronómicas exactas calculadas con efemérides profesionales (Swiss Ephemeris):</p>'
        html += '<table style="width: 100%; border-collapse: collapse; font-size: 0.92rem;">'
        html += '<tr style="border-bottom: 1px solid rgba(255,255,255,0.15); color: #f6c445; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;"><th style="text-align: left; padding: 10px 8px;">Astro / Ángulo</th><th style="text-align: left; padding: 10px 8px;">Signo y Grado Exacto</th></tr>'
        
        # Ascendente primero si está disponible
        if 'Ascendente' in natal_houses:
            html += f'<tr style="border-bottom: 1px solid rgba(255,255,255,0.06); background: rgba(0, 242, 254, 0.04);"><td style="padding: 10px 8px; color: #00f2fe; font-weight: 700;">◀ ASCENDENTE</td><td style="padding: 10px 8px; font-weight: 600; color: #fff;">{self._degrees_to_zodiac(natal_houses["Ascendente"])}</td></tr>'
        
        # Planetas
        for planet, deg in natal_positions.items():
            p_color = "#f6c445" if planet == "Sol" else ("#e2e8f0" if planet == "Luna" else "#38bdf8")
            html += f'<tr style="border-bottom: 1px solid rgba(255,255,255,0.06);"><td style="padding: 9px 8px; color: {p_color}; font-weight: 600;">{planet}</td><td style="padding: 9px 8px; color: #cbd5e1;">{self._degrees_to_zodiac(deg)}</td></tr>'
            
        html += '</table></div>'
        return html
        
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

    def generate_for_user(self, name, birth_date, birth_time, lat=-34.6037, lon=-58.3816, mode='welcome'):
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
        
        if mode == 'weekly':
            self.engine.system_prompt = f"""
            Eres un Astrólogo Clínico y Sociológico de la Factoría Astrológica. 
            Tu objetivo es realizar un PRONÓSTICO SEMANAL para el usuario basándote en cómo los tránsitos planetarios actuales impactan su Carta Natal.
            
            El usuario recibirá una tabla con sus datos duros (planetas y signos exactos). 
            Tu tarea es enfocarte en los eventos y energías disponibles para los PRÓXIMOS 7 DÍAS.
            No es necesario que expliques toda su carta desde cero, ve directo al grano sobre cómo los tránsitos actuales movilizan sus posiciones natales.
            
            El usuario acaba de ver (o recibirá un mail sobre) nuestro último video. El guion de ese video es:
            "{video_context}"
            
            Debes hilar tu lectura en perfecta cohesión con la temática de ese guion.
            Sé profundo, sociológico y empático. 
            Al final, recuérdale que su aporte y donación permite mantener este servidor corriendo.
            Formato de Salida Obligatorio: Un JSON estricto con una clave "mensaje_personalizado" que contenga el texto completo (HTML). No incluyas la tabla matemática.
            """
        else:
            self.engine.system_prompt = f"""
            Eres un Astrólogo Clínico y Sociológico de la Factoría Astrológica. 
            Tu objetivo es realizar un estudio profundo de TODA LA CARTA NATAL de este usuario y cruzarlo con los tránsitos actuales.
            El usuario recibirá una tabla con sus datos duros (planetas y signos exactos). 
            Tu tarea es EXPLICAR esos datos: comienza haciendo un breve diagnóstico técnico pero muy didáctico de su Sol, Luna y Ascendente para que entienda qué significan en su personalidad.
            Luego, cruza esta información con los tránsitos actuales.
            
            El usuario acaba de ver (o recibirá un mail sobre) nuestro último video. El guion de ese video es:
            "{video_context}"
            
            Debes hilar tu lectura personalizada en perfecta cohesión con la temática de ese guion.
            Sé profundo, sociológico y empático. 
            Al final, recuérdale que su aporte y donación permite mantener este servidor corriendo.
            Formato de Salida Obligatorio: Un JSON estricto con una clave "mensaje_personalizado" que contenga el texto completo (HTML). No incluyas la tabla matemática, nosotros ya la inyectaremos antes de tu mensaje.
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
        
        chart_html = self._build_natal_chart_html(natal_positions, natal_houses)
        if content and "mensaje_personalizado" in content:
            content["mensaje_personalizado"] = chart_html + content["mensaje_personalizado"]
            content["error"] = False
            return content
        else:
            fallback_msg = f"<div style='margin-top: 15px; color: #cbd5e1; line-height: 1.6;'><p><strong>Hola {name}</strong>, hemos calculado tus coordenadas natales exactas con precisión astronómica (revisa la tabla superior).</p><p>El oráculo está sintetizando el análisis de tus tránsitos en profundidad. Puedes iniciar la conversación abajo en el chat en vivo para explorar cualquier casa o planeta.</p></div>"
            return {"mensaje_personalizado": chart_html + fallback_msg, "error": False}

if __name__ == "__main__":
    ph = PersonalizedHoroscope()
    res = ph.generate_for_user("Tomy", "1995-10-23", "14:30")
    print(res)
