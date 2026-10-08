import os

days = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
base_dir = "produccion"

transits = [
    "stellium_escorpio", # Lunes
    "stellium_escorpio", # Martes
    "stellium_escorpio", # Miercoles
    "stellium_escorpio", # Jueves
    "stellium_escorpio", # Viernes (Sun enters Scorpio)
    "retrograde_motion", # Sabado (Mercury stations retrograde)
    "retrograde_motion", # Domingo 
]

guiones = [
    # Lunes (Luna Acuario)
    "Arrancamos la semana con la Luna en Acuario, pidiendo libertad mental.\nPero el stellium en Escorpio no te deja evadir tus monstruos con teorías intelectuales.\nNo podés racionalizar el dolor, tenés que sentirlo para que mute.\nHoy cortá con el sobrepensamiento y dejate atravesar por la intensidad.\nEntrá al link de mi perfil, cargá tus datos y mirá dónde está tu bloqueo mental.",
    # Martes (Luna Acuario)
    "La Luna sigue en Acuario y la mente parece un cortocircuito.\nQuerés escapar hacia el futuro, pero la sombra escorpiana te jala al subsuelo.\nEsas emociones reprimidas son exactamente la cadena que no te deja volar.\nRomper la cadena no es huir, es mirar a los ojos lo que te asusta.\nEntrá al link de mi perfil, cargá tu fecha de nacimiento y descubrí cómo liberarte.",
    # Miercoles (Luna Acuario a Piscis)
    "Transición crítica hoy. De la mente fría de Acuario al océano emocional de Piscis.\nEse muro racional que armaste se va a disolver en las próximas horas.\nY ahí, flotando en lo incierto, Escorpio te va a pedir que no tengas miedo de hundirte un poco.\nSolo en la profundidad encontrás las perlas de tu verdadera intuición.\nEntrá al link de mi perfil y preparate para el chapuzón cósmico.",
    # Jueves (Luna Piscis)
    "Con la Luna en Piscis, el velo entre mundos está finísimo.\nY hoy, Mercurio empieza a frenar en Escorpio. Las palabras pierden sentido, pero las tripas hablan fuerte.\nEs un día para escuchar el silencio. Las mentiras que te contás se caen solas.\nDejá que la intuición te guíe como un faro en medio de la niebla.\nEntrá al link de mi perfil, cargá tus datos y descubrí tu verdad oculta.",
    # Viernes (Sol entra en Escorpio)
    "¡Boom! El Sol entra en Escorpio. Oficialmente cruzamos el portal hacia las sombras.\nLa temporada escorpiana ilumina todo lo que escondías debajo de la alfombra.\nY con la Luna en Piscis, la sensibilidad está a flor de piel.\nEs momento de hacer las paces con tu lado más oscuro, porque ahí está tu poder.\nEntrá al link de mi perfil, cargá tu fecha y preparate para la transmutación.",
    # Sabado (Mercurio Retrogrado)
    "Mercurio se clava en el cielo y arranca su retrogradación. Todo parece ir marcha atrás.\nLa Luna en Aries quiere empujar, pero el universo te pone el freno de mano.\nLa frustración es gigante si querés forzar las cosas. Es momento de revisar, no de iniciar.\nCualquier error de comunicación hoy es el karma pidiendo revisión.\nEntrá al link de mi perfil y descubrí qué área de tu vida entra en revisión total.",
    # Domingo (Venus entra en Libra, Luna en Aries)
    "Domingo de chispazos. La Luna en Aries pidiendo guerra y Venus volviendo a Libra pidiendo paz.\nCon Mercurio roto, intentar llegar a un acuerdo con el otro hoy es caminar en un pantano.\nEl verdadero conflicto no es con ellos, es tu propia balanza interna descalibrada.\nAntes de disparar palabras hirientes, preguntate qué herida tuya están tocando.\nEntrá al link de mi perfil, cargá tus datos y armá tu propio mapa de paz."
]

storyboards = [
    # Lunes
    "Escena 1: abstract mind network glitch connection\nEscena 2: deep dark ocean water looking down abyss\nEscena 3: dropping heavy chains letting go realism\nEscena 4: human eye of truth staring\nEscena 5: zodiac wheel cosmic spinning space",
    # Martes
    "Escena 1: glitch art broken mirror reflection\nEscena 2: dark basement shadows hiding\nEscena 3: breaking heavy chains metal snapping\nEscena 4: human eye of truth staring\nEscena 5: cosmic glowing portal deep mystic space",
    # Miercoles
    "Escena 1: ice melting into water fluid transition\nEscena 2: deep dark ocean water abyss sinking\nEscena 3: floating pearls deep sea mystic\nEscena 4: glowing lighthouse in thick fog\nEscena 5: cosmic glowing portal deep mystic space",
    # Jueves
    "Escena 1: foggy path lost in woods mystic\nEscena 2: broken compass not working glitch\nEscena 3: old ruins turning to dust mystic\nEscena 4: glowing lighthouse in thick fog\nEscena 5: cosmic glowing portal deep mystic space",
    # Viernes
    "Escena 1: burning fire in darkness rising\nEscena 2: sweeping dust under rug shadows\nEscena 3: dark silhouette embracing shadow self\nEscena 4: human eye of truth staring\nEscena 5: cosmic glowing portal deep mystic space",
    # Sabado
    "Escena 1: time reversing clock backwards motion\nEscena 2: pushing heavy stone uphill frustration\nEscena 3: rewriting old books old script\nEscena 4: miscommunication glitch static screen\nEscena 5: cosmic glowing portal deep mystic space",
    # Domingo
    "Escena 1: sparking fire embers aggressive\nEscena 2: glitch art broken mirror reflection\nEscena 3: unbalanced scale ancient weights\nEscena 4: deep dark ocean water ripples\nEscena 5: natal chart blueprint sacred geometry astrology",
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

print("Semana 4 creada exitosamente.")
