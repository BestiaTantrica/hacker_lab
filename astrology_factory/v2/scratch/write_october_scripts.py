import os
import shutil

scripts_data = {
    "Semana2_Octubre_Resumen": {
        "guion": """El cielo de la segunda semana de Octubre nos presenta una tensión ineludible.
El Sol en Libra se opone exactamente a Saturno en Aries, obligándonos a mirar las estructuras que sostienen nuestras relaciones.
No se trata de romper por romper, sino de cuestionar la madurez de nuestros compromisos sociales.
Al mismo tiempo, Marte se opone a Plutón, una energía de colisión tectónica.
El poder no está en imponerse sobre el otro, sino en la capacidad de transformar la rabia en determinación estructural.
Con Mercurio y Venus unidos en Escorpio, las palabras no serán superficiales; irán directo al hueso de la herida emocional.
Prepárate para conversaciones incómodas pero absolutamente necesarias para la evolución colectiva.""",
        "storyboard": """Un reloj de arena enorme en medio del espacio exterior
Dos rocas tectónicas chocando y generando chispas
Un rostro humano en la sombra con una luz penetrante en los ojos
Un puente de piedra antiguo sosteniendo un gran peso
Una puerta oscura que se abre hacia una luz dorada"""
    },
    "Semana2_Octubre_Lunes": {
        "guion": """Lunes 5 de Octubre. La semana arranca bajo la pesada mirada de la oposición entre el Sol y Saturno.
Sentirás que el deber y la responsabilidad chocan de frente con tu deseo de armonía.
No intentes evadir la carga; la resistencia solo aumenta la fricción.
Abraza la limitación como un marco para tu propia madurez.
La energía de hoy nos pide ser arquitectos de nuestra propia disciplina.""",
        "storyboard": """Una montaña alta bajo un cielo nublado y pesado
Una balanza de metal antiguo desequilibrada
Unas manos construyendo una pared de ladrillos
Una figura solitaria mirando hacia el horizonte gris
Un rayo de sol rompiendo a través de las nubes grises"""
    },
    "Semana3_Octubre_Resumen": {
        "guion": """Llegamos a la tercera semana de Octubre y la densidad comienza a transmutarse en búsqueda de sentido.
Venus ingresa en Sagitario, expandiendo nuestro deseo de conectar más allá de las fronteras conocidas.
Es un momento sociológico donde las verdades absolutas caen para dar paso a la exploración filosófica.
El Sol en sus últimos grados de Libra busca equilibrar la balanza antes de sumergirse en las aguas oscuras.
Aprovecha esta ventana de fuego sagitariano para apuntar tu flecha hacia objetivos más elevados.
La energía colectiva pide menos drama y más visión de futuro.""",
        "storyboard": """Una flecha dorada volando a través de un cielo estrellado
Un grupo de personas diversas caminando juntas hacia la luz
Un libro antiguo abriéndose solo con viento mágico
Un atardecer cálido sobre un horizonte abierto
Una fogata encendida iluminando rostros en la oscuridad"""
    },
    "Semana4_Octubre_Resumen": {
        "guion": """Cuarta semana de Octubre: El Sol hace su entrada triunfal en el signo de Escorpio.
La temporada de la transformación profunda ha comenzado oficialmente.
El enfoque sociológico cambia de la estética y la diplomacia, hacia el poder, el tabú y la resiliencia humana.
Lo que estaba oculto bajo la alfombra colectiva saldrá a la luz con una intensidad irrefutable.
No le temas a tu propia sombra, porque es allí donde reside tu mayor potencial creativo.
Es el momento de morir a lo viejo para renacer con mayor fuerza.""",
        "storyboard": """Un escorpión caminando sobre arena bajo luz de luna roja
Una serpiente cambiando su piel en cámara lenta
Un ojo humano con el iris oscuro y profundo
Una ciudad nocturna con luces de neón parpadeantes
Un fénix de cenizas comenzando a brillar con fuego"""
    }
}

base_dir = "/home/LAB/astrology_factory/produccion"
os.makedirs(base_dir, exist_ok=True)

for event_name, data in scripts_data.items():
    event_dir = os.path.join(base_dir, event_name)
    os.makedirs(event_dir, exist_ok=True)
    
    with open(os.path.join(event_dir, "guion.txt"), "w", encoding="utf-8") as f:
        f.write(data["guion"])
        
    with open(os.path.join(event_dir, "storyboard.txt"), "w", encoding="utf-8") as f:
        f.write(data["storyboard"])

print("Guiones y storyboards creados exitosamente.")
