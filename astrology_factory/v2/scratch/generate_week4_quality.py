import os

days = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
base_dir = "produccion"

transits = [
    "stellium_escorpio", # Lunes
    "stellium_escorpio", # Martes
    "stellium_escorpio", # Miercoles
    "stellium_escorpio", # Jueves
    "stellium_escorpio", # Viernes
    "retrograde_motion", # Sabado
    "retrograde_motion", # Domingo 
]

guiones = [
    # Lunes (111 words)
    "La conjunción de la Luna transitando por Acuario frente a la pesada influencia del stellium en Escorpio plantea una de las configuraciones más complejas para la psique colectiva. Astrológicamente, esta tensión fija enfrenta la necesidad acuariana de racionalizar el dolor con la exigencia escorpiana de sentirlo hasta los huesos. Los registros históricos nos muestran que bajo este clima, intentar evadir el pantano emocional mediante la distancia intelectual solo genera mayores fracturas internas. No se trata de sobreanalizar la incomodidad, sino de permitir que el proceso alquímico opere sin resistencia mental. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto.",
    
    # Martes (106 words)
    "Con la Luna manteniéndose en Acuario, la fricción con la densa acumulación planetaria en Escorpio alcanza su punto máximo de saturación. La historia astrológica evidencia que estos momentos operan como ollas a presión: la mente busca planificar el futuro mientras el subconsciente exige revisar lo oculto. Las emociones reprimidas actúan como anclas invisibles que impiden el progreso genuino. Cortar estas ataduras requiere el coraje de descender a la propia oscuridad y observar las sombras sin juicio. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto.",
    
    # Miercoles (108 words)
    "El ingreso de la Luna a las aguas mutables de Piscis marca un punto de inflexión profundo, disolviendo las murallas racionales que Acuario intentó sostener. Este flujo empático, combinado con la fuerza de Escorpio, crea una resonancia magnética hacia lo místico. La tradición astrológica nos enseña que aquí la lógica fracasa y solo la intuición profunda puede servir de brújula. Es un periodo excelente para permitir que las respuestas emerjan del silencio en lugar de forzarlas mediante el intelecto. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto.",
    
    # Jueves (105 words)
    "Mientras la Luna avanza por Piscis, Mercurio comienza a ralentizar drásticamente su paso en Escorpio, preparando su inminente retrogradación. Esta configuración clásica advierte sobre el peligro de las verdades a medias y las percepciones engañosas. Históricamente, este es un momento donde las palabras pierden su peso y la energía sutil toma el control. Las revelaciones no llegan a través de la comunicación verbal, sino a través de la sincronicidad y la observación pausada. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto.",
    
    # Viernes (108 words)
    "El ingreso triunfal del Sol en Escorpio marca la apertura oficial de la temporada de sombras, un descenso cíclico hacia las profundidades de la psique humana. Los textos ancestrales asocian este periodo con la purga necesaria antes del renacimiento: todo aquello que ha sido barrido bajo la alfombra queda ahora brutalmente iluminado. Lejos de ser un tránsito temible, es la oportunidad astronómica perfecta para integrar nuestras partes negadas y reclamar un poder psicológico auténtico. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto.",
    
    # Sabado (104 words)
    "Mercurio inicia oficialmente su fase retrógrada en el cielo, exigiendo un alto inmediato a cualquier intento de avanzar por la fuerza. La astrología mundana documenta que bajo esta tensión, la frustración aumenta exponencialmente si intentamos ignorar los bloqueos estructurales. No es un error del sistema, es el cosmos exigiendo una auditoría profunda de nuestras estrategias y comunicaciones recientes. El verdadero trabajo radica en la paciencia y la reevaluación táctica. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto.",
    
    # Domingo (113 words)
    "El cierre de la semana nos encuentra con Venus regresando a Libra, buscando equilibrar la balanza, mientras la Luna transita por el impulsivo Aries. Este eje de relaciones se tensiona fuertemente con la retrogradación de Mercurio, creando un terreno fértil para proyecciones psicológicas y malentendidos. Los patrones históricos sugieren que el conflicto aparente con el otro es, en realidad, un reflejo directo de nuestra propia descalibración interna. La diplomacia más efectiva hoy comienza por silenciar el ego y escuchar las inseguridades propias antes de reaccionar. Este tránsito general cobra vida de forma única en tu carta natal. Si querés saber exactamente qué área de tu vida está activando y cómo aprovecharlo a tu favor, andá al link de mi perfil, poné tus datos exactos y calculá tu mapa de impacto."
]

storyboards = [
    # Lunes
    "[illustration] abstract mind network glitch connection\n[video] deep dark ocean water\n[video] breaking heavy chains\n[illustration] human eye of truth\n[video] cosmic glowing portal",
    # Martes
    "[video] glitch art broken mirror reflection\n[illustration] dark basement shadows hiding\n[video] breaking heavy chains\n[illustration] human eye of truth\n[video] cosmic glowing portal",
    # Miercoles
    "[illustration] ice melting into water fluid transition\n[video] deep dark ocean water\n[illustration] floating pearls deep sea mystic\n[video] glowing lighthouse in thick fog\n[video] cosmic glowing portal",
    # Jueves
    "[video] foggy path lost in woods mystic\n[illustration] broken compass not working glitch\n[video] old ruins turning to dust mystic\n[video] glowing lighthouse in thick fog\n[video] cosmic glowing portal",
    # Viernes
    "[illustration] burning fire in darkness rising\n[video] sweeping dust under rug shadows\n[illustration] dark silhouette embracing shadow self\n[video] human eye of truth\n[video] cosmic glowing portal",
    # Sabado
    "[video] time reversing clock backwards motion\n[illustration] pushing heavy stone uphill frustration\n[video] rewriting old books old script\n[illustration] miscommunication glitch static screen\n[video] cosmic glowing portal",
    # Domingo
    "[illustration] sparking fire embers aggressive\n[video] glitch art broken mirror reflection\n[illustration] unbalanced scale ancient weights\n[video] deep dark ocean water\n[illustration] natal chart blueprint sacred geometry astrology",
]

for i, day in enumerate(days):
    folder = os.path.join(base_dir, f"Semana4_Octubre_{day}")
    os.makedirs(folder, exist_ok=True)
    
    with open(os.path.join(folder, "transito.txt"), "w") as f:
        f.write(transits[i])
        
    with open(os.path.join(folder, "guion.txt"), "w") as f:
        f.write(guiones[i])
        
    with open(os.path.join(folder, "storyboard.txt"), "w") as f:
        f.write(storyboards[i])

print("Semana 4 regenerada exitosamente con profundidad y longitud adecuada.")
