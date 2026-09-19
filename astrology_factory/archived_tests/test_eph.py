import datetime
import sys
sys.path.append('.')
from astrology_engine.ephemeris_calculator import EphemerisCalculator
from astrology_engine.aspects_matcher import AspectsMatcher

calc = EphemerisCalculator()
matcher = AspectsMatcher()
dt = datetime.datetime(2026, 10, 5, 12, 0)
pos = calc.calculate_planets(dt)
aspects = matcher.find_aspects(pos)

print("Posiciones:")
for k,v in pos.items():
    print(f"{k}: {v:.2f}°")

print("\nAspectos:")
for a in aspects:
    print(f"{a['p1']} y {a['p2']} forman un(a) {a['aspect']} (Error: {a['orb_error']}°)")
