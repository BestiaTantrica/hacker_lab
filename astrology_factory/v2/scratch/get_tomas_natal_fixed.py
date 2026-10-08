import datetime
import sys
sys.path.append('.')
from astrology_engine.ephemeris_calculator import EphemerisCalculator

calc = EphemerisCalculator()
# 14:30 UTC-3 -> 17:30 UTC
dt = datetime.datetime.strptime("1995-10-23 17:30", "%Y-%m-%d %H:%M")
pos = calc.calculate_planets(dt)
houses = calc.calculate_houses(dt, -34.6037, -58.3816)

print("--- Planetas ---")
for k,v in pos.items():
    print(f"{k}: {v:.1f}°")

print("\n--- Ascendente ---")
print(f"Asc: {houses['Ascendente']:.1f}°")
