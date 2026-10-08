import os
import shutil

scripts_data = {
    "Semana2_Octubre_Martes": {
        "guion": """Martes 6 de Octubre. Con Mercurio y Venus abrazados en Escorpio, el pensamiento y el deseo se funden.
Hoy las interacciones no tienen grises; o hay una conexión profunda o un rechazo absoluto.
Aprovecha esta energía para investigar, profundizar o mantener esa charla incómoda que venís esquivando.
Al mismo tiempo, Marte hace un sextil con Urano. 
Es el impulso perfecto para romper la inercia con una acción rápida y poco convencional.
No pienses demasiado, simplemente da el paso diferente.""",
        "storyboard": """Dos personas mirándose intensamente en un café oscuro
Una cerradura antigua con una llave girando
Un rayo iluminando un cielo nocturno
Alguien corriendo rápido por una calle moderna
Un candado abriéndose de golpe"""
    },
    "Semana2_Octubre_Miercoles": {
        "guion": """Miércoles 7 de Octubre. El sextil entre Marte y Urano llega a su punto matemático más exacto.
Esta es una inyección de pura electricidad cósmica.
Atrévete a romper las reglas que te impiden avanzar.
Sin embargo, la Luna hace cuadratura a Urano, generando una gran inquietud emocional.
Cuidado con reaccionar desde el nerviosismo o la rebeldía sin causa.
Usa esta chispa para innovar, no para dinamitar lo que ya has construido.""",
        "storyboard": """Una chispa eléctrica saltando entre dos cables
Un reloj antiguo cuyas manecillas giran rápidamente
Un mar picado con olas golpeando rocas
Una mente brillante visualizada como una red neuronal brillante
Un ave rompiendo una jaula y volando alto"""
    },
    "Semana2_Octubre_Jueves": {
        "guion": """Jueves 8 de Octubre. Comienza a sentirse la fricción entre Venus y Marte.
Venus quiere vincularse desde la profundidad de Escorpio, mientras Marte defiende su territorio en Leo.
El deseo choca contra el orgullo.
No es un buen momento para luchas de ego en la pareja o con socios.
Observa cómo tu propia voluntad compite con tu necesidad de conectar.
El poder real hoy reside en no entrar en el juego del conflicto innecesario.""",
        "storyboard": """Dos lobos mirándose fijamente en el bosque
Una rosa roja con espinas afiladas
Un tablero de ajedrez con piezas en tensión
Fuego y agua encontrándose y generando vapor
Un puente roto sobre un río turbulento"""
    },
    "Semana2_Octubre_Viernes": {
        "guion": """Viernes 9 de Octubre. La Luna se opone a Neptuno y fluye en trígono hacia Plutón.
Puede que el día empiece con confusión, como si caminaras por un banco de niebla emocional.
Cuidado con los autoengaños o idealizaciones excesivas de personas o situaciones.
Pero a medida que avanza el día, el trígono con Plutón te devuelve el poder.
Esa bruma se despeja y te das cuenta de lo que realmente tiene valor.
Cierra la semana confiando en tu intuición más instintiva y visceral.""",
        "storyboard": """Un bosque cubierto de niebla densa
Un espejo de agua reflejando la luna distorsionada
Alguien quitándose una venda de los ojos
Un cristal brillando intensamente en la oscuridad
Un sendero iluminado de repente por luz de luna"""
    },
    "Semana2_Octubre_Sabado": {
        "guion": """Sábado 10 de Octubre. La cuadratura exacta entre Venus y Marte domina el fin de semana.
Es una tensión altamente creativa pero también muy inflamable.
La pasión sexual, creativa o la ira pueden encenderse con la mínima chispa.
Usa esta energía sociológica y primaria para mover proyectos estancados, no para pelear.
Si la tensión se siente abrumadora, canalízala físicamente.
Romper un patrón requiere una inmensa cantidad de energía, y hoy la tienes disponible.""",
        "storyboard": """Fuego ardiendo intensamente en una chimenea
Un escultor golpeando la piedra con fuerza
Dos bailarines en un tango apasionado y tenso
Un lienzo en blanco siendo pintado con trazos rápidos de color rojo
Una persona rompiendo una cadena pesada de metal"""
    },
    "Semana2_Octubre_Domingo": {
        "guion": """Domingo 11 de Octubre. Urano y Plutón colaboran silenciosamente en el fondo del cielo con un trígono transformador.
Esta es la energía del cambio de época a nivel macro, operando en tu psique.
Aprovecha el domingo para soltar viejas estructuras mentales que ya no resuenan con tu versión actual.
La evolución no siempre tiene que ser dolorosa; a veces es una liberación instantánea.
Respira hondo. Has sobrevivido a una semana intensa. Prepárate para lo nuevo.""",
        "storyboard": """Un viejo muro de piedra desmoronándose lentamente
Una mariposa saliendo de su capullo en primer plano
Alguien respirando profundamente en la cima de una montaña
Las estrellas girando lentamente en un cielo nocturno limpio
Un amanecer radiante naciendo desde el horizonte"""
    }
}

base_dir = "/home/LAB/astrology_factory/produccion"

for event_name, data in scripts_data.items():
    event_dir = os.path.join(base_dir, event_name)
    os.makedirs(event_dir, exist_ok=True)
    
    with open(os.path.join(event_dir, "guion.txt"), "w", encoding="utf-8") as f:
        f.write(data["guion"])
        
    with open(os.path.join(event_dir, "storyboard.txt"), "w", encoding="utf-8") as f:
        f.write(data["storyboard"])

print("Guiones diarios de la Semana 2 creados exitosamente.")
