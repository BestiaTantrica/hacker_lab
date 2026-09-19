import swisseph as swe
from datetime import datetime

class EphemerisCalculator:
    def __init__(self):
        # Configurar la ruta de los archivos de efemérides (opcional si se usa el modelo básico)
        # swe.set_ephe_path('/path/to/ephe')
        pass

    def _datetime_to_julian(self, dt: datetime) -> float:
        """Convierte datetime a día juliano (UT)."""
        year, month, day = dt.year, dt.month, dt.day
        hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        return swe.julday(year, month, day, hour)

    def calculate_planets(self, dt: datetime, utc_offset_hours: float = 0):
        """
        Calcula las posiciones de los planetas principales.
        Retorna un diccionario con los grados en el zodiaco (0 a 360).
        """
        from datetime import timedelta
        # Convertir hora local a UTC restando el offset
        if utc_offset_hours != 0:
            dt = dt - timedelta(hours=utc_offset_hours)
            
        jd = self._datetime_to_julian(dt)
        
        # Cuerpos celestes principales
        bodies = {
            'Sol': swe.SUN,
            'Luna': swe.MOON,
            'Mercurio': swe.MERCURY,
            'Venus': swe.VENUS,
            'Marte': swe.MARS,
            'Júpiter': swe.JUPITER,
            'Saturno': swe.SATURN,
            'Urano': swe.URANUS,
            'Neptuno': swe.NEPTUNE,
            'Plutón': swe.PLUTO
        }
        
        positions = {}
        for name, body_id in bodies.items():
            # swe.calc_ut retorna (posición, error). posición es [longitud, latitud, distancia, vel_long, vel_lat, vel_dist]
            res = swe.calc_ut(jd, body_id)
            # Longitud en grados (0-360) desde 0 Aries
            positions[name] = res[0][0]
            
        return positions

    def calculate_houses(self, dt: datetime, lat: float, lon: float, hsys: str = 'P', utc_offset_hours: float = 0):
        """
        Calcula las cúspides de las casas astrológicas.
        hsys: 'P' = Placidus, 'K' = Koch, 'C' = Campanus, etc.
        """
        from datetime import timedelta
        # Convertir hora local a UTC restando el offset
        if utc_offset_hours != 0:
            dt = dt - timedelta(hours=utc_offset_hours)
            
        jd = self._datetime_to_julian(dt)
        # houses retorna (cúspides, ascmc). cúspides es una tupla de 1 a 12.
        cusps, ascmc = swe.houses(jd, lat, lon, hsys.encode('ascii'))
        
        return {
            'Ascendente': ascmc[0],
            'Medio Cielo': ascmc[1],
            'Casas': cusps[1:] # Las casas son indexadas 1-12
        }

if __name__ == "__main__":
    # Prueba rápida de precisión militar
    calc = EphemerisCalculator()
    now = datetime.utcnow()
    print(f"Cálculos para: {now} (UTC)")
    print("Planetas:", calc.calculate_planets(now))
    # Buenos Aires (aprox)
    print("Casas (Buenos Aires):", calc.calculate_houses(now, -34.6037, -58.3816))
