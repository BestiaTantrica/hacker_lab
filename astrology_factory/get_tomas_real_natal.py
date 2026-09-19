import datetime
import sys
sys.path.append('.')
from astrology_engine.ephemeris_calculator import EphemerisCalculator

calc = EphemerisCalculator()
# 12 de Abril 1982, 02:30 local time Buenos Aires (UTC-3)
# 02:30 + 3 hours = 05:30 UTC
dt = datetime.datetime.strptime("1982-04-12 05:30", "%Y-%m-%d %H:%M")
pos = calc.calculate_planets(dt)
houses = calc.calculate_houses(dt, -34.61, -58.42)

print("--- Planetas ---")
for k,v in pos.items():
    print(f"{k}: {v:.1f}°")

print("\n--- Ascendente ---")
print(f"Asc: {houses['Ascendente']:.1f}°")
