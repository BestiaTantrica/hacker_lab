import random
from pathlib import Path

PLANETAS = {
    "Sol": "Identidad y Ego",
    "Luna": "Emociones y Refugio",
    "Mercurio": "Mente y Velocidad",
    "Venus": "Amor y Estética",
    "Marte": "Acción y Fuego",
    "Júpiter": "Expansión y Suerte",
    "Saturno": "Límites y Karma",
    "Urano": "Rebeldía y Electricidad",
    "Neptuno": "Sueños y Niebla",
    "Plutón": "Transformación y Sombras",
    "Quirón": "Herida Inconsciente",
    "Lilith": "Poder Oculto y Tabúes",
    "Nodos Lunares": "Destino Kármico"
}

SIGNOS = {
    "Aries": "Inicios Explosivos",
    "Tauro": "Materia y Lentitud",
    "Géminis": "Dualidad Mental",
    "Cáncer": "Aguas Maternas",
    "Leo": "Fuego Creativo",
    "Virgo": "Orden y Detalle",
    "Libra": "Armonía Estética",
    "Escorpio": "Intensidad Oscura",
    "Sagitario": "Búsqueda de Verdad",
    "Capricornio": "Cima de la Montaña",
    "Acuario": "Visión Futurista",
    "Piscis": "Océano Místico"
}

ASPECTOS = {
    "Conjunción": "Fusión Intensa",
    "Oposición": "Tensión y Espejo",
    "Cuadratura": "Fricción y Conflicto",
    "Trígono": "Flujo Armónico",
    "Sextil": "Oportunidad Creativa"
}

def generar_combinaciones(cantidad=100):
    combinaciones = []
    
    # 1. Planetas en Signos
    for _ in range(cantidad // 2):
        p = random.choice(list(PLANETAS.keys()))
        s = random.choice(list(SIGNOS.keys()))
        tema = f"{PLANETAS[p]} bajo {SIGNOS[s]}"
        titulo = f"{p} en {s}"
        combinaciones.append(f"- [ ] **{titulo}** ({tema})")
        
    # 2. Aspectos entre Planetas
    for _ in range(cantidad // 2):
        p1 = random.choice(list(PLANETAS.keys()))
        p2 = random.choice(list(PLANETAS.keys()))
        while p1 == p2:
            p2 = random.choice(list(PLANETAS.keys()))
        asp = random.choice(list(ASPECTOS.keys()))
        tema = f"{ASPECTOS[asp]} entre {PLANETAS[p1]} y {PLANETAS[p2]}"
        titulo = f"{p1} {asp} {p2}"
        combinaciones.append(f"- [ ] **{titulo}** ({tema})")
        
    # Mezclamos para que queden intercalados
    random.shuffle(combinaciones)
    
    # Filtramos duplicados por las dudas
    return list(dict.fromkeys(combinaciones))

def main():
    FILE_PATH = "/home/LAB/astrology_factory/REGISTRO_ASPECTOS_IA.md"
    nuevas = generar_combinaciones(300)  # Generar 300 combinaciones aleatorias
    
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lineas = f.readlines()
        
    nota_idx = -1
    for i, line in enumerate(lineas):
        if "*Nota: Todas las imágenes" in line:
            nota_idx = i
            break
            
    if nota_idx == -1:
        nota_idx = len(lineas)
        
    nuevo_contenido = lineas[:nota_idx]
    if nuevo_contenido[-1].strip() != "":
        nuevo_contenido.append("\n")
        
    nuevo_contenido.append("### ♾️ Bóveda Infinita (Generación Procedural)\n")
    for c in nuevas:
        nuevo_contenido.append(c + "\n")
        
    if nota_idx < len(lineas):
        nuevo_contenido.append("\n")
        nuevo_contenido.append(lineas[nota_idx])
        
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.writelines(nuevo_contenido)
        
    print(f"✅ Se agregaron {len(nuevas)} combinaciones astrológicas únicas y procedimentales a la bitácora.")

if __name__ == "__main__":
    main()
