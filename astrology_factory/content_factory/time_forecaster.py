import sys
import os
from datetime import datetime, timedelta

# Permitir importaciones relativas desde la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from astrology_engine.ephemeris_calculator import EphemerisCalculator
from astrology_engine.aspects_matcher import AspectsMatcher

SIGNS = ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis']

class TimeForecaster:
    def __init__(self):
        self.calc = EphemerisCalculator()
        self.matcher = AspectsMatcher()
        self.planets = ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón']

    def _get_sign(self, lon):
        return SIGNS[int(lon // 30)]

    def forecast_period(self, start_date: datetime, days: int):
        """
        Escanea las energías para un período de tiempo dado (ej. 7 días o 30 días).
        Retorna un diccionario estructurado listo para inyectarse en el cerebro de la IA.
        """
        forecast = {}
        for i in range(days):
            current_day = start_date + timedelta(days=i)
            day_str = current_day.strftime('%Y-%m-%d')
            
            # Calcular posiciones
            positions = self.calc.calculate_planets(current_day)
            
            # Mapear a signos
            planet_signs = {p: self._get_sign(pos) for p, pos in positions.items() if p in self.planets}
            
            # Encontrar aspectos mayores del día (clima energético)
            aspects = self.matcher.find_aspects(positions)
            # Filtramos solo los más exactos (orbe muy estrecho) para no saturar a la IA
            major_aspects = [a for a in aspects if a['orb_error'] < 2.0]
            
            forecast[day_str] = {
                'planets': planet_signs,
                'aspects': major_aspects
            }
            
        return forecast

if __name__ == "__main__":
    tf = TimeForecaster()
    now = datetime.utcnow()
    # Prueba: Escanear la próxima semana (7 días)
    semana = tf.forecast_period(now, 7)
    
    print("--- REPORTE CRUDO DE LA SEMANA ---")
    for dia, datos in semana.items():
        print(f"\nDía: {dia}")
        print("Sol en:", datos['planets']['Sol'])
        print("Luna en:", datos['planets']['Luna'])
        if datos['aspects']:
            print(f"Aspectos clave: {len(datos['aspects'])} detectados.")
