import datetime
import sys
sys.path.append('.')
from astrology_engine.ephemeris_calculator import EphemerisCalculator
from astrology_engine.aspects_matcher import AspectsMatcher

calc = EphemerisCalculator()
matcher = AspectsMatcher()

days = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
start_date = datetime.datetime(2026, 9, 28, 12, 0)

for i, day in enumerate(days):
    dt = start_date + datetime.timedelta(days=i)
    pos = calc.calculate_planets(dt)
    aspects = matcher.find_aspects(pos)
    print(f"\n--- {day} {dt.day} de {dt.strftime('%B')} ---")
    print(f"Sol en {pos['Sol']:.1f}°, Luna en {pos['Luna']:.1f}°")
    aspects.sort(key=lambda x: x['orb_error'])
    for a in aspects[:3]:
        print(f"  {a['p1']} y {a['p2']} forman un(a) {a['aspect']} (Error: {a['orb_error']:.2f}°)")
