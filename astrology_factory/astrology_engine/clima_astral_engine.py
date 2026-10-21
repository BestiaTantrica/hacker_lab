"""
Motor de Clima Astral y Tránsitos (Swiss Ephemeris)
Provee los cálculos astronómicos exactos para el Clima Astral diario del canal de Telegram
y para el Horóscopo Personalizado interactivo.
100% autónomo y autocontenido con pyswisseph.
"""

import os
import re
import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class CalculadorAstronomico:
    def __init__(self):
        # Configurar la ruta de efemérides en caso de existir, o usar Moshier integrado
        posibles_rutas = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ephe"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "astrology_engine", "ephe")
        ]
        for ephe_path in posibles_rutas:
            if os.path.exists(ephe_path):
                swe.set_ephe_path(ephe_path)
                break

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
            {"nombre": "Conjunción", "angulo": 0, "orbe": 8.0, "tipo": "armonico_fuerte"},
            {"nombre": "Oposición", "angulo": 180, "orbe": 8.0, "tipo": "tension"},
            {"nombre": "Trígono", "angulo": 120, "orbe": 7.0, "tipo": "fluidez"},
            {"nombre": "Cuadratura", "angulo": 90, "orbe": 7.0, "tipo": "tension"},
            {"nombre": "Sextil", "angulo": 60, "orbe": 5.0, "tipo": "oportunidad"}
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
                            "tipo": asp["tipo"]
                        })
                        break
        return aspectos

    def calcular_carta(self, nombre: str, dt_local: datetime, lat: float, lon: float, utc_offset: float) -> Dict[str, Any]:
        dt_utc = dt_local - timedelta(hours=utc_offset)
        jd = self._datetime_to_julian(dt_utc)

        # 1. Calcular Planetas y Puntos
        planetas = {}
        for name, body_code in self.BODIES.items():
            try:
                flags = swe.FLG_SWIEPH | swe.FLG_SPEED
                res, _ = swe.calc_ut(jd, body_code, flags)
            except swe.Error:
                flags = swe.FLG_MOSEPH | swe.FLG_SPEED
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
            
            if p_name in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón']:
                balance_elementos[info["elemento"]] += 1
                balance_modalidades[info["modalidad"]] += 1

        casas_info = {}
        for h_idx, c_deg in enumerate(cusps):
            casas_info[f"Casa {h_idx + 1}"] = self._deg_to_sign_info(c_deg)

        angulos_info = {
            "Ascendente": self._deg_to_sign_info(ascmc[0]),
            "Medio Cielo": self._deg_to_sign_info(ascmc[1]),
            "Descendente": self._deg_to_sign_info((ascmc[0] + 180.0) % 360.0),
            "Fondo Cielo": self._deg_to_sign_info((ascmc[1] + 180.0) % 360.0)
        }

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

_calc_singleton = None

def get_calc() -> CalculadorAstronomico:
    global _calc_singleton
    if _calc_singleton is None:
        _calc_singleton = CalculadorAstronomico()
    return _calc_singleton

def parse_flexible_date(date_str: str) -> Optional[datetime]:
    """Parsea fechas en formatos YYYY-MM-DD, DD/MM/YYYY o DD-MM-YYYY."""
    if not date_str:
        return None
    date_str = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    return None

def parse_flexible_time(time_str: str) -> (int, int):
    """Parsea hora en formato HH:MM o HH:MM:SS. Default (12, 0)."""
    if not time_str:
        return 12, 0
    time_str = time_str.strip()
    match = re.match(r"^(\d{1,2}):(\d{1,2})", time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
    return 12, 0

def calcular_fase_lunar(sol_deg: float, luna_deg: float) -> Dict[str, Any]:
    """Calcula la fase lunar a partir de la elongación Sol-Luna."""
    dif = (luna_deg - sol_deg) % 360.0
    
    if dif < 45.0:
        nombre = "Luna Nueva"
        descripcion = "Inicio de ciclo, siembra sutil, energía replegada."
    elif dif < 90.0:
        nombre = "Luna Creciente"
        descripcion = "Primer impulso de manifestación, toma de contacto con la intención."
    elif dif < 135.0:
        nombre = "Cuarto Creciente"
        descripcion = "Tensión de crecimiento, fricción dinámica, acción concreta y definiciones."
    elif dif < 180.0:
        nombre = "Gibosa Creciente"
        descripcion = "Ajuste fino de detalles, acumulación de energía hacia el clímax."
    elif dif < 225.0:
        nombre = "Luna Llena"
        descripcion = "Culminación, máxima iluminación psíquica, visibilidad y polaridad consciente."
    elif dif < 270.0:
        nombre = "Gibosa Menguante (Diseminadora)"
        descripcion = "Distribución del fruto, síntesis reflexiva, compartir el aprendizaje."
    elif dif < 315.0:
        nombre = "Cuarto Menguante"
        descripcion = "Crisis de conciencia, corte de lo que no sirve, reorientación interna."
    else:
        nombre = "Luna Menguante (Balsámica)"
        descripcion = "Cierre de ciclo, vaciado, descanso mental y preparación para lo nuevo."

    return {
        "nombre": nombre,
        "angulo": round(dif, 1),
        "descripcion": descripcion
    }

def obtener_resumen_cielo_hoy(dt: Optional[datetime] = None) -> str:
    """
    Calcula las posiciones celestes y aspectos exactos para el Clima Astral diario.
    Retorna un texto formateado para inyectar en el prompt de la IA.
    """
    if dt is None:
        dt = datetime.now()
        
    calc = get_calc()
    # Coordenadas de referencia Buenos Aires (-34.6037, -58.3816, UTC -3)
    carta = calc.calcular_carta("Cielo de Hoy", dt, -34.6037, -58.3816, -3.0)
    
    # 1. Posiciones planetarias
    lineas_planetas = []
    planetas_clave = ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón', 'Quirón', 'Nodo Norte']
    for p in planetas_clave:
        if p in carta['planetas']:
            data = carta['planetas'][p]
            lineas_planetas.append(f"- {p}: {data['formato']} ({data['elemento']}, {data['modalidad']})")
        
    # 2. Fase Lunar
    sol_deg = carta['planetas']['Sol']['grado_absoluto']
    luna_deg = carta['planetas']['Luna']['grado_absoluto']
    fase = calcular_fase_lunar(sol_deg, luna_deg)
    
    # 3. Aspectos activos con orbe <= 4.5°
    aspectos_ordenados = sorted(carta['aspectos'], key=lambda x: x['orbe'])
    aspectos_texto = []
    for a in aspectos_ordenados:
        if a['orbe'] <= 4.5:
            aspectos_texto.append(
                f"- {a['cuerpo1']} en {a['aspecto']} con {a['cuerpo2']} (orbe exacto: {a['orbe']}° | naturaleza: {a['tipo']})"
            )
            
    dias_es = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
    meses_es = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 
                7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
    
    dia_nom = dias_es.get(dt.weekday(), "")
    mes_nom = meses_es.get(dt.month, "")
    fecha_formateada = f"{dia_nom} {dt.day} de {mes_nom} de {dt.year}"
    
    prompt_datos = f"""FECHA DEL REPORTE: {fecha_formateada}
FASE LUNAR: {fase['nombre']} (Ángulo Sol-Luna: {fase['angulo']}° - {fase['descripcion']})

POSICIONES PLANETARIAS EXACTAS (Swiss Ephemeris):
""" + "\n".join(lineas_planetas) + """

ASPECTOS PRINCIPALES ACTIVOS HOY (Orbe menor a 4.5°):
""" + "\n".join(aspectos_texto)

    return prompt_datos

def calcular_transitos_personales(name: str, birth_date_str: str, birth_time_str: str, birth_city: str = "", dt_transito: Optional[datetime] = None) -> str:
    """
    Calcula la Carta Natal del usuario y sus tránsitos exactos para hoy.
    Determina qué casas natales transita cada planeta y qué aspectos forma con la carta del usuario.
    """
    calc = get_calc()
    
    dt_birth = parse_flexible_date(birth_date_str)
    if not dt_birth:
        return f"Consultante: {name}. Datos natales: {birth_date_str} {birth_time_str}."
        
    hour, minute = parse_flexible_time(birth_time_str)
    dt_birth = dt_birth.replace(hour=hour, minute=minute)
    
    if dt_transito is None:
        dt_transito = datetime.now()
        
    natal = calc.calcular_carta(name, dt_birth, -34.6037, -58.3816, -3.0)
    cielo = calc.calcular_carta("Tránsitos Hoy", dt_transito, -34.6037, -58.3816, -3.0)
    
    natal_cusps = natal['cuspides_grados']
    
    def get_house(deg: float) -> int:
        deg = deg % 360.0
        for h in range(12):
            c_start = natal_cusps[h]
            c_end = natal_cusps[(h + 1) % 12]
            if c_start < c_end:
                if c_start <= deg < c_end:
                    return h + 1
            else:
                if deg >= c_start or deg < c_end:
                    return h + 1
        return 1

    # 1. Tránsito de planetas por las casas natales del usuario
    planetas_transito_casas = []
    for p in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón']:
        if p in cielo['planetas']:
            deg = cielo['planetas'][p]['grado_absoluto']
            casa_activa = get_house(deg)
            formato = cielo['planetas'][p]['formato']
            planetas_transito_casas.append(f"- {p} en tránsito ({formato}) transita por tu Casa {casa_activa}")

    # 2. Aspectos entre tránsitos actuales y planetas natales (orbe estrecho <= 3.5°)
    ASPECTOS_DEF = [
        {"nombre": "Conjunción", "angulo": 0, "orbe": 4.0},
        {"nombre": "Oposición", "angulo": 180, "orbe": 4.0},
        {"nombre": "Trígono", "angulo": 120, "orbe": 3.5},
        {"nombre": "Cuadratura", "angulo": 90, "orbe": 3.5},
        {"nombre": "Sextil", "angulo": 60, "orbe": 3.0}
    ]
    
    aspectos_transito_natal = []
    for p_tr, data_tr in cielo['planetas'].items():
        if p_tr not in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Plutón']:
            continue
        deg_tr = data_tr['grado_absoluto']
        for p_nat, data_nat in natal['planetas'].items():
            if p_nat not in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Ascendente']:
                continue
            deg_nat = data_nat['grado_absoluto']
            diff = abs(deg_tr - deg_nat) % 360.0
            if diff > 180.0:
                diff = 360.0 - diff
                
            for asp in ASPECTOS_DEF:
                orbe = abs(diff - asp['angulo'])
                if orbe <= asp['orbe']:
                    aspectos_transito_natal.append({
                        "texto": f"- {p_tr} en tránsito ({data_tr['formato']}) forma {asp['nombre']} a tu {p_nat} natal ({data_nat['formato']}) [orbe {round(orbe, 2)}°]",
                        "orbe": orbe
                    })
                    break

    aspectos_transito_natal.sort(key=lambda x: x['orbe'])
    lineas_aspectos_tn = [a['texto'] for a in aspectos_transito_natal[:5]]
    
    sol_deg = cielo['planetas']['Sol']['grado_absoluto']
    luna_deg = cielo['planetas']['Luna']['grado_absoluto']
    fase = calcular_fase_lunar(sol_deg, luna_deg)

    resumen = f"""DATOS NATALES DE {name.upper()}:
- Sol Natal: {natal['planetas']['Sol']['formato']} en Casa {natal['planetas']['Sol']['casa']}
- Luna Natal: {natal['planetas']['Luna']['formato']} en Casa {natal['planetas']['Luna']['casa']}
- Ascendente Natal: {natal['angulos']['Ascendente']['formato']}
- Medio Cielo: {natal['angulos']['Medio Cielo']['formato']}

FASE LUNAR ACTUAL: {fase['nombre']} (Luna en {cielo['planetas']['Luna']['formato']})

TRÁNSITOS ACTIVOS POR TUS CASAS NATALES HOY:
""" + "\n".join(planetas_transito_casas) + """

ASPECTOS DIRECTOS DEL CIELO DE HOY A TU CARTA NATAL:
""" + ("\n".join(lineas_aspectos_tn) if lineas_aspectos_tn else "- No hay aspectos mayores partiles hoy a tus planetas personales; rige el tránsito por casas.")

    return resumen
