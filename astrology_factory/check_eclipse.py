import swisseph as swe
swe.set_ephe_path('/usr/share/ephemeris') # Default path, or let it download
jd = swe.julday(2026, 10, 2, 12.0)
print("Sun:", swe.calc_ut(jd, swe.SUN)[0][0])
print("Moon:", swe.calc_ut(jd, swe.MOON)[0][0])
