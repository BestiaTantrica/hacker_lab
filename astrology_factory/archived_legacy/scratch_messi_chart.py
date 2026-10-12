import sys
import os
from datetime import datetime

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'astrology_engine'))

from astrology_engine.ephemeris_calculator import EphemerisCalculator

ZODIAC_SIGNS = [
    "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
    "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
]

def get_sign(degree: float) -> str:
    sign_index = int(degree // 30)
    return ZODIAC_SIGNS[sign_index]

def get_degree_in_sign(degree: float) -> str:
    sign_deg = degree % 30
    return f"{int(sign_deg)}°"

def main():
    calc = EphemerisCalculator()
    
    # Datos de Messi
    dt = datetime(1987, 6, 24, 20, 30)
    lat = -32.9468
    lon = -60.6393
    utc_offset = -3 # ART

    print(f"Cálculos para LIONEL MESSI:")
    print(f"Fecha/Hora Local: {dt}")
    print(f"Lugar: Rosario, Argentina (Lat: {lat}, Lon: {lon})")
    print("-" * 40)
    
    planets = calc.calculate_planets(dt, utc_offset_hours=utc_offset)
    print("PLANETAS Y PUNTOS KÁRMICOS:")
    for name, deg in planets.items():
        sign = get_sign(deg)
        deg_in_sign = get_degree_in_sign(deg)
        print(f"{name.ljust(12)}: {sign.ljust(12)} ({deg_in_sign}) - Absoluto: {deg:.2f}°")
        
    print("-" * 40)
    houses = calc.calculate_houses(dt, lat, lon, utc_offset_hours=utc_offset)
    print("CASAS ASTROLÓGICAS:")
    
    asc_sign = get_sign(houses['Ascendente'])
    asc_deg = get_degree_in_sign(houses['Ascendente'])
    print(f"Ascendente  : {asc_sign.ljust(12)} ({asc_deg}) - Absoluto: {houses['Ascendente']:.2f}°")
    
    mc_sign = get_sign(houses['Medio Cielo'])
    mc_deg = get_degree_in_sign(houses['Medio Cielo'])
    print(f"Medio Cielo : {mc_sign.ljust(12)} ({mc_deg}) - Absoluto: {houses['Medio Cielo']:.2f}°")
    
    for i, cusp in enumerate(houses['Casas']):
        c_sign = get_sign(cusp)
        c_deg = get_degree_in_sign(cusp)
        print(f"Casa {str(i+1).ljust(2)}     : {c_sign.ljust(12)} ({c_deg})")
        
if __name__ == '__main__':
    main()
