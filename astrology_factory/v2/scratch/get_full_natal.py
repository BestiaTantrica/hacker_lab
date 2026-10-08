import datetime
import swisseph as swe
import sys

calc = swe
dt = datetime.datetime.strptime("1982-04-12 05:30", "%Y-%m-%d %H:%M")
year, month, day = dt.year, dt.month, dt.day
hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
jd = swe.julday(year, month, day, hour)

# Calculate true node and chiron with mosheier? swe.FLG_MOSEPH
bodies = {
    'Sol': swe.SUN, 'Luna': swe.MOON, 'Mercurio': swe.MERCURY, 'Venus': swe.VENUS, 'Marte': swe.MARS,
    'Júpiter': swe.JUPITER, 'Saturno': swe.SATURN, 'Urano': swe.URANUS, 'Neptuno': swe.NEPTUNE, 'Plutón': swe.PLUTO,
    'Nodo Norte (Verdadero)': swe.TRUE_NODE,
    'Lilith (Apogeo Lunar Medio)': swe.MEAN_APOG
}

zodiac = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

def to_zodiac(deg):
    sign = int(deg / 30)
    rem = deg % 30
    return f"{rem:.2f}° {zodiac[sign]}"

print("--- CUERPOS CELESTES ---")
for name, body_id in bodies.items():
    try:
        res = swe.calc_ut(jd, body_id, swe.FLG_MOSEPH)[0][0]
        print(f"{name}: {to_zodiac(res)}")
    except Exception as e:
        print(f"{name}: ERROR {e}")

try:
    res = swe.calc_ut(jd, swe.CHIRON, swe.FLG_MOSEPH)[0][0]
    print(f"Quirón: {to_zodiac(res)}")
except Exception as e:
    print(f"Quirón: ERROR {e}")

print("\n--- CASAS (Placidus) ---")
cusps, ascmc = swe.houses(jd, -34.61, -58.42, b'P')
print(f"Ascendente (Casa 1): {to_zodiac(ascmc[0])}")
print(f"Medio Cielo (MC): {to_zodiac(ascmc[1])}")
for i in range(1, 13):
    print(f"Casa {i}: {to_zodiac(cusps[i-1])}")

