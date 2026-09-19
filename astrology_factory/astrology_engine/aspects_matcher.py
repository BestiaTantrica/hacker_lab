class AspectsMatcher:
    def __init__(self):
        # Ángulos y orbes estándar (puedes ajustar el orbe para hacerlo más estricto/holgado)
        self.aspects = {
            'Conjunción': {'angle': 0, 'orb': 8},
            'Oposición': {'angle': 180, 'orb': 8},
            'Trígono': {'angle': 120, 'orb': 6},
            'Cuadratura': {'angle': 90, 'orb': 6},
            'Sextil': {'angle': 60, 'orb': 4}
        }

    def find_aspects(self, positions):
        """
        Busca relaciones geométricas (aspectos) entre una lista de posiciones planetarias.
        positions: diccionario {'Planeta': longitud_en_grados}
        Retorna: lista de diccionarios con los aspectos encontrados.
        """
        found = []
        planets = list(positions.keys())
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                lon1 = positions[p1]
                lon2 = positions[p2]
                
                # Calcular la distancia más corta en un círculo de 360 grados
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                
                # Verificar si cae dentro de algún orbe
                for aspect_name, data in self.aspects.items():
                    error_orb = abs(diff - data['angle'])
                    if error_orb <= data['orb']:
                        found.append({
                            'p1': p1,
                            'p2': p2,
                            'aspect': aspect_name,
                            'angle_diff': round(diff, 2),
                            'orb_error': round(error_orb, 2) # Qué tan "exacto" es (0 es perfecto)
                        })
                        
        # Ordenar por el aspecto más exacto (menor error de orbe)
        found.sort(key=lambda x: x['orb_error'])
        return found

if __name__ == "__main__":
    # Prueba rápida con posiciones simuladas
    matcher = AspectsMatcher()
    cielo = {
        'Sol': 15.0,    # 15 grados Aries
        'Luna': 102.0,  # 12 grados Cáncer (Cuadratura con el Sol, dif ~87)
        'Venus': 135.0, # 15 grados Leo (Trígono con el Sol, dif ~120)
    }
    print("Buscando aspectos en:", cielo)
    aspectos = matcher.find_aspects(cielo)
    for a in aspectos:
        print(f"{a['p1']} y {a['p2']} forman un(a) {a['aspect']} (Error: {a['orb_error']}°)")
