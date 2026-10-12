import os
import swisseph as swe
from datetime import datetime
from typing import Dict, Any, List

class CalculadorAstronomico:
    def __init__(self):
        # Configurar la ruta de efemérides en caso de existir
        ephe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "astrology_engine", "ephe")
        if os.path.exists(ephe_path):
            swe.set_ephe_path(ephe_path)

        self.ZODIAC_SIGNS = [
            "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
            "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"
        ]
        
        self.ELEMENTS = {
            "Aries": "Fuego", "Leo": "Fuego", "Sagitario": "Fuego",
            "Tauro": "Tierra", "Virgo": "Tierra", "Capricornio": "Tierra",
            "Géminis": "Aire", "Libra": "Aire", "Acuario": "Aire",
            "Cáncer": "Agua", "Escorpio": "Agua", "Piscis": "Agua"
        }
        
        self.MODALITIES = {
            "Aries": "Cardinal", "Cáncer": "Cardinal", "Libra": "Cardinal", "Capricornio": "Cardinal",
            "Tauro": "Fijo", "Leo": "Fijo", "Escorpio": "Fijo", "Acuario": "Fijo",
            "Géminis": "Mutable", "Virgo": "Mutable", "Sagitario": "Mutable", "Piscis": "Mutable"
        }

        self.BODIES = {
            'Sol': swe.SUN,
            'Luna': swe.MOON,
            'Mercurio': swe.MERCURY,
            'Venus': swe.VENUS,
            'Marte': swe.MARS,
            'Júpiter': swe.JUPITER,
            'Saturno': swe.SATURN,
            'Urano': swe.URANUS,
            'Neptuno': swe.NEPTUNE,
            'Plutón': swe.PLUTO,
            'Quirón': swe.CHIRON,
            'Nodo Norte': swe.TRUE_NODE,
            'Lilith': swe.MEAN_APOG
        }

    def _datetime_to_julian(self, dt_utc: datetime) -> float:
        hour_decimal = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_decimal)

    def _deg_to_sign_info(self, degree: float) -> Dict[str, Any]:
        deg_norm = degree % 360.0
        sign_idx = int(deg_norm // 30)
        sign_name = self.ZODIAC_SIGNS[sign_idx]
        deg_in_sign = deg_norm % 30.0
        degrees_int = int(deg_in_sign)
        minutes_int = int((deg_in_sign - degrees_int) * 60)
        
        return {
            "grado_absoluto": round(deg_norm, 4),
            "signo": sign_name,
            "grado_en_signo": degrees_int,
            "minuto_en_signo": minutes_int,
            "formato": f"{sign_name} {degrees_int}° {minutes_int:02d}'",
            "elemento": self.ELEMENTS[sign_name],
            "modalidad": self.MODALITIES[sign_name]
        }

    def calcular_aspectos(self, planets_dict: Dict[str, float]) -> List[Dict[str, Any]]:
        ASPECT_DEFS = [
            {"nombre": "Conjunción", "angulo": 0, "orbe": 8.0, "tipo": "armonico_fuerte", "color": "#f1c40f"},
            {"nombre": "Oposición", "angulo": 180, "orbe": 8.0, "tipo": "tension", "color": "#e74c3c"},
            {"nombre": "Trígono", "angulo": 120, "orbe": 7.0, "tipo": "fluidez", "color": "#3498db"},
            {"nombre": "Cuadratura", "angulo": 90, "orbe": 7.0, "tipo": "tension", "color": "#e67e22"},
            {"nombre": "Sextil", "angulo": 60, "orbe": 5.0, "tipo": "oportunidad", "color": "#2ecc71"}
        ]
        
        aspectos = []
        cuerpos = list(planets_dict.keys())
        
        for i in range(len(cuerpos)):
            for j in range(i + 1, len(cuerpos)):
                p1, p2 = cuerpos[i], cuerpos[j]
                deg1, deg2 = planets_dict[p1], planets_dict[p2]
                
                diff = abs(deg1 - deg2) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff
                    
                for asp in ASPECT_DEFS:
                    delta = abs(diff - asp["angulo"])
                    if delta <= asp["orbe"]:
                        aspectos.append({
                            "cuerpo1": p1,
                            "cuerpo2": p2,
                            "aspecto": asp["nombre"],
                            "angulo_exacto": asp["angulo"],
                            "diferencia": round(diff, 2),
                            "orbe": round(delta, 2),
                            "tipo": asp["tipo"],
                            "color": asp["color"]
                        })
                        break
        return aspectos

    def calcular_carta(self, nombre: str, dt_local: datetime, lat: float, lon: float, utc_offset: float) -> Dict[str, Any]:
        from datetime import timedelta
        dt_utc = dt_local - timedelta(hours=utc_offset)
        jd = self._datetime_to_julian(dt_utc)

        # 1. Calcular Planetas y Puntos
        planetas = {}
        for name, body_code in self.BODIES.items():
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            res, _ = swe.calc_ut(jd, body_code, flags)
            planetas[name] = res[0]

        # 2. Calcular Casas (Placidus)
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        
        # 3. Determinar casa de cada planeta
        def get_house_of_degree(deg: float, house_cusps: list) -> int:
            deg = deg % 360.0
            for h in range(12):
                c_start = house_cusps[h]
                c_end = house_cusps[(h + 1) % 12]
                if c_start < c_end:
                    if c_start <= deg < c_end:
                        return h + 1
                else: # Cruce de 0° Aries
                    if deg >= c_start or deg < c_end:
                        return h + 1
            return 1

        planetas_info = {}
        balance_elementos = {"Fuego": 0, "Tierra": 0, "Aire": 0, "Agua": 0}
        balance_modalidades = {"Cardinal": 0, "Fijo": 0, "Mutable": 0}

        for p_name, p_deg in planetas.items():
            info = self._deg_to_sign_info(p_deg)
            info["casa"] = get_house_of_degree(p_deg, list(cusps))
            planetas_info[p_name] = info
            
            # Contar en balance solo planetas mayores
            if p_name in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón']:
                balance_elementos[info["elemento"]] += 1
                balance_modalidades[info["modalidad"]] += 1

        # Casas info
        casas_info = {}
        for h_idx, c_deg in enumerate(cusps):
            casas_info[f"Casa {h_idx + 1}"] = self._deg_to_sign_info(c_deg)

        angulos_info = {
            "Ascendente": self._deg_to_sign_info(ascmc[0]),
            "Medio Cielo": self._deg_to_sign_info(ascmc[1]),
            "Descendente": self._deg_to_sign_info((ascmc[0] + 180.0) % 360.0),
            "Fondo Cielo": self._deg_to_sign_info((ascmc[1] + 180.0) % 360.0)
        }

        # Aspectos
        aspectos = self.calcular_aspectos(planetas)

        return {
            "sujeto": {
                "nombre": nombre,
                "fecha_hora_local": dt_local.strftime("%Y-%m-%d %H:%M"),
                "fecha_hora_utc": dt_utc.strftime("%Y-%m-%d %H:%M"),
                "latitud": lat,
                "longitud": lon,
                "utc_offset": utc_offset
            },
            "planetas": planetas_info,
            "angulos": angulos_info,
            "casas": casas_info,
            "cuspides_grados": list(cusps),
            "aspectos": aspectos,
            "balances": {
                "elementos": balance_elementos,
                "modalidades": balance_modalidades
            }
        }

if __name__ == "__main__":
    calc = CalculadorAstronomico()
    dt = datetime(1987, 6, 24, 20, 30)
    data = calc.calcular_carta("Lionel Messi", dt, -32.9468, -60.6393, -3)
    print("Cálculo exitoso para:", data["sujeto"]["nombre"])
    print("Sol:", data["planetas"]["Sol"]["formato"], "en Casa", data["planetas"]["Sol"]["casa"])
    print("Ascendente:", data["angulos"]["Ascendente"]["formato"])
    print("Total aspectos calculados:", len(data["aspectos"]))
