import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import swisseph as swe

# Asegurar importación de utilidades del calculador natal base
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "carta_natal"))
from calculador_astronomico import CalculadorAstronomico

class CalculadorRevolucionSolar:
    """
    Motor determinístico de cálculo de Revolución Solar (Retorno Solar) con Swiss Ephemeris.
    Precisión matemática absoluta ($0 costo, 0 APIs externas).
    Calcula:
    1. Instante UTC exacto en que el Sol en tránsito coincide con el Sol natal al segundo de arco.
    2. Posiciones planetarias y Casas Placidus en la ubicación del retorno (cumpleaños / residencia).
    3. Matriz de superposición: en qué casa natal cae el Ascendente y cada planeta de la RS.
    4. Aspectos inter-cartas (activaciones de la RS sobre el mapa natal) y aspectos internos de la RS.
    """
    def __init__(self):
        self.calc_base = CalculadorAstronomico()
        self.BODIES = self.calc_base.BODIES
        self.ZODIAC_SIGNS = self.calc_base.ZODIAC_SIGNS
        self.ELEMENTS = self.calc_base.ELEMENTS
        self.MODALITIES = self.calc_base.MODALITIES

    def _get_sun_longitude(self, jd: float) -> Tuple[float, float]:
        """Devuelve (longitud_sol, velocidad_sol_por_dia) en grados."""
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        res, _ = swe.calc_ut(jd, swe.SUN, flags)
        return res[0], res[3]

    def encontrar_retorno_solar(self, sol_natal_deg: float, anio_retorno: int, mes_natal: int, dia_natal: int) -> float:
        """
        Encuentra el Julian Day (UT) exacto en que el Sol transita por sol_natal_deg en el anio_retorno
        usando el método de Newton-Raphson de convergencia rápida.
        """
        # Estimación inicial: día de cumpleaños a las 12:00 UTC en el año de retorno
        dt_estimada = datetime(anio_retorno, mes_natal, dia_natal, 12, 0)
        jd = self.calc_base._datetime_to_julian(dt_estimada)

        for _ in range(15):
            long_actual, velocidad = self._get_sun_longitude(jd)
            # Diferencia angular circular (-180 a +180)
            diff = (long_actual - sol_natal_deg + 180.0) % 360.0 - 180.0
            
            # Si el error es menor a 0.000005° (~0.018 segundos de arco / menos de 0.5s de tiempo), convergemos
            if abs(diff) < 0.000005:
                break
                
            # Paso de Newton: jd_nuevo = jd - diff / velocidad
            jd -= diff / velocidad

        return jd

    def _julian_to_datetime_utc(self, jd: float) -> datetime:
        year, month, day, hour_float = swe.revjul(jd)
        hour = int(hour_float)
        minute_float = (hour_float - hour) * 60.0
        minute = int(minute_float)
        second = int(round((minute_float - minute) * 60.0))
        if second >= 60:
            second = 59
        return datetime(year, month, day, hour, minute, second)

    def calcular_aspectos_intercartas(self, planetas_rs: Dict[str, float], planetas_natal: Dict[str, float]) -> List[Dict[str, Any]]:
        """Calcula los aspectos que hacen los planetas de la RS sobre los planetas de la carta natal."""
        ASPECT_DEFS = [
            {"nombre": "Conjunción", "angulo": 0, "orbe": 6.0, "tipo": "activacion_fuerte", "color": "#f1c40f"},
            {"nombre": "Oposición", "angulo": 180, "orbe": 6.0, "tipo": "tension", "color": "#e74c3c"},
            {"nombre": "Trígono", "angulo": 120, "orbe": 5.0, "tipo": "fluidez", "color": "#3498db"},
            {"nombre": "Cuadratura", "angulo": 90, "orbe": 5.0, "tipo": "tension", "color": "#e67e22"},
            {"nombre": "Sextil", "angulo": 60, "orbe": 4.0, "tipo": "oportunidad", "color": "#2ecc71"}
        ]
        
        aspectos = []
        for p_rs, deg_rs in planetas_rs.items():
            for p_nat, deg_nat in planetas_natal.items():
                diff = abs(deg_rs - deg_nat) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff
                for asp in ASPECT_DEFS:
                    delta = abs(diff - asp["angulo"])
                    if delta <= asp["orbe"]:
                        aspectos.append({
                            "cuerpo_rs": p_rs,
                            "cuerpo_natal": p_nat,
                            "aspecto": asp["nombre"],
                            "angulo_exacto": asp["angulo"],
                            "diferencia": round(diff, 2),
                            "orbe": round(delta, 2),
                            "tipo": asp["tipo"],
                            "color": asp["color"],
                            "descripcion": f"{p_rs} de RS en {asp['nombre']} a {p_nat} natal (orbe {round(delta, 2)}°)"
                        })
                        break
        # Ordenar por orbe más exacto
        return sorted(aspectos, key=lambda x: x["orbe"])

    def calcular_revolucion_solar(
        self,
        carta_natal: Dict[str, Any],
        anio_retorno: int,
        lat_rs: float,
        lon_rs: float,
        utc_offset_rs: float,
        ciudad_retorno: str
    ) -> Dict[str, Any]:
        """
        Calcula la Revolución Solar completa y la superpone con la Carta Natal.
        """
        sujeto = carta_natal["sujeto"]
        sol_natal_deg = carta_natal["planetas"]["Sol"]["grado_absoluto"]
        
        dt_natal_utc = datetime.strptime(sujeto["fecha_hora_utc"], "%Y-%m-%d %H:%M")
        
        # 1. Localizar el instante exacto del Retorno Solar
        jd_rs = self.encontrar_retorno_solar(sol_natal_deg, anio_retorno, dt_natal_utc.month, dt_natal_utc.day)
        dt_rs_utc = self._julian_to_datetime_utc(jd_rs)
        dt_rs_local = dt_rs_utc + timedelta(hours=utc_offset_rs)

        # 2. Calcular planetas en el instante de la RS
        planetas_rs_grados = {}
        for name, body_code in self.BODIES.items():
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            res, _ = swe.calc_ut(jd_rs, body_code, flags)
            planetas_rs_grados[name] = res[0]

        # 3. Calcular Casas Placidus de la RS en la ubicación actual
        cusps_rs, ascmc_rs = swe.houses(jd_rs, lat_rs, lon_rs, b'P')
        cusps_rs_list = list(cusps_rs)
        
        # Cúspides natales para determinar superposición
        cusps_natal_list = carta_natal["cuspides_grados"]

        def get_house(deg: float, cusps: list) -> int:
            deg = deg % 360.0
            for h in range(12):
                c_start = cusps[h]
                c_end = cusps[(h + 1) % 12]
                if c_start < c_end:
                    if c_start <= deg < c_end:
                        return h + 1
                else:
                    if deg >= c_start or deg < c_end:
                        return h + 1
            return 1

        # 4. Formatear planetas de la RS y calcular doble ubicación de casa
        planetas_rs_info = {}
        balance_elem_rs = {"Fuego": 0, "Tierra": 0, "Aire": 0, "Agua": 0}
        balance_modal_rs = {"Cardinal": 0, "Fijo": 0, "Mutable": 0}

        for p_name, p_deg in planetas_rs_grados.items():
            info = self.calc_base._deg_to_sign_info(p_deg)
            info["casa_rs"] = get_house(p_deg, cusps_rs_list)
            info["casa_natal"] = get_house(p_deg, cusps_natal_list)
            planetas_rs_info[p_name] = info
            
            if p_name in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón']:
                balance_elem_rs[info["elemento"]] += 1
                balance_modal_rs[info["modalidad"]] += 1

        # 5. Ángulos y Casas de la RS
        asc_rs_deg = ascmc_rs[0]
        mc_rs_deg = ascmc_rs[1]
        
        asc_rs_info = self.calc_base._deg_to_sign_info(asc_rs_deg)
        asc_rs_info["casa_natal_superpuesta"] = get_house(asc_rs_deg, cusps_natal_list)

        mc_rs_info = self.calc_base._deg_to_sign_info(mc_rs_deg)
        mc_rs_info["casa_natal_superpuesta"] = get_house(mc_rs_deg, cusps_natal_list)

        angulos_rs = {
            "Ascendente_RS": asc_rs_info,
            "Medio_Cielo_RS": mc_rs_info,
            "Descendente_RS": self.calc_base._deg_to_sign_info((asc_rs_deg + 180.0) % 360.0),
            "Fondo_Cielo_RS": self.calc_base._deg_to_sign_info((mc_rs_deg + 180.0) % 360.0)
        }

        casas_rs_info = {}
        for h_idx, c_deg in enumerate(cusps_rs_list):
            h_info = self.calc_base._deg_to_sign_info(c_deg)
            h_info["casa_natal_donde_cae"] = get_house(c_deg, cusps_natal_list)
            casas_rs_info[f"Casa {h_idx + 1}"] = h_info

        # 6. Aspectos internos de la RS y Aspectos inter-cartas (RS sobre Natal)
        aspectos_internos_rs = self.calc_base.calcular_aspectos(planetas_rs_grados)
        
        # Extraer grados absolutos natales
        planetas_natal_grados = {p: info["grado_absoluto"] for p, info in carta_natal["planetas"].items()}
        aspectos_intercartas = self.calcular_aspectos_intercartas(planetas_rs_grados, planetas_natal_grados)

        # 7. Síntesis clave de superposición para el guion
        superposicion_clave = {
            "ascendente_rs_en_casa_natal": {
                "signo": asc_rs_info["signo"],
                "grado_formato": asc_rs_info["formato"],
                "casa_natal": asc_rs_info["casa_natal_superpuesta"],
                "foco_anual": f"El Ascendente de la Revolución Solar cae en {asc_rs_info['formato']}, activando directamente tu Casa Natal {asc_rs_info['casa_natal_superpuesta']}."
            },
            "luna_rs_en_casas": {
                "signo": planetas_rs_info["Luna"]["signo"],
                "formato": planetas_rs_info["Luna"]["formato"],
                "casa_rs": planetas_rs_info["Luna"]["casa_rs"],
                "casa_natal": planetas_rs_info["Luna"]["casa_natal"]
            },
            "marte_rs_en_casas": {
                "signo": planetas_rs_info["Marte"]["signo"],
                "formato": planetas_rs_info["Marte"]["formato"],
                "casa_rs": planetas_rs_info["Marte"]["casa_rs"],
                "casa_natal": planetas_rs_info["Marte"]["casa_natal"]
            },
            "saturno_rs_en_casas": {
                "signo": planetas_rs_info["Saturno"]["signo"],
                "formato": planetas_rs_info["Saturno"]["formato"],
                "casa_rs": planetas_rs_info["Saturno"]["casa_rs"],
                "casa_natal": planetas_rs_info["Saturno"]["casa_natal"]
            },
            "jupiter_rs_en_casas": {
                "signo": planetas_rs_info["Júpiter"]["signo"],
                "formato": planetas_rs_info["Júpiter"]["formato"],
                "casa_rs": planetas_rs_info["Júpiter"]["casa_rs"],
                "casa_natal": planetas_rs_info["Júpiter"]["casa_natal"]
            }
        }

        return {
            "sujeto": sujeto,
            "revolucion_solar": {
                "anio": anio_retorno,
                "ciudad_retorno": ciudad_retorno,
                "fecha_hora_exacta_local": dt_rs_local.strftime("%Y-%m-%d %H:%M:%S"),
                "fecha_hora_exacta_utc": dt_rs_utc.strftime("%Y-%m-%d %H:%M:%S"),
                "julian_day": round(jd_rs, 6),
                "coordenadas": {"latitud": lat_rs, "longitud": lon_rs, "utc_offset": utc_offset_rs}
            },
            "angulos_rs": angulos_rs,
            "casas_rs": casas_rs_info,
            "cuspides_rs_grados": cusps_rs_list,
            "planetas_rs": planetas_rs_info,
            "balances_rs": {
                "elementos": balance_elem_rs,
                "modalidades": balance_modal_rs
            },
            "superposicion_clave": superposicion_clave,
            "aspectos_intercartas": aspectos_intercartas,
            "aspectos_internos_rs": aspectos_internos_rs
        }
