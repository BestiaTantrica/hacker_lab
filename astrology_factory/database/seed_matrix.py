import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'astrology_meanings.sqlite')
SIGNS = ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis']
PLANETS = ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Neptuno', 'Plutón']

def seed_matrix():
    """Rellena la base de datos con una matriz completa para que no quede 'a medias'"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Seed de Tonos Empáticos para los Signos (Cómo hablarles)
    tones = {
        'Aries': 'Directo, motivador, desafiante y que incite a la acción.',
        'Tauro': 'Calmado, seguro, valorando el tiempo, los sentidos y la paciencia.',
        'Géminis': 'Dinámico, curioso, amigable y estimulando la mente.',
        'Cáncer': 'Muy cálido, protector, apelando al hogar, la familia y las emociones.',
        'Leo': 'Reconociendo su brillo, alentador, generoso y celebrando su identidad.',
        'Virgo': 'Práctico, ordenado, útil y enfocado en el bienestar y el servicio.',
        'Libra': 'Armonioso, estético, enfocado en el equilibrio y los vínculos.',
        'Escorpio': 'Profundo, intenso, sin miedo a la sombra y enfocado en la transformación.',
        'Sagitario': 'Aventurero, optimista, expansivo y buscando el sentido o la verdad.',
        'Capricornio': 'Pragmático, maduro, enfocado en metas, logros y el largo plazo.',
        'Acuario': 'Innovador, libre, desapegado y enfocado en el colectivo y el futuro.',
        'Piscis': 'Místico, compasivo, soñador, apelando a la intuición y el alma.'
    }
    
    for sign in SIGNS:
        tone = tones.get(sign, 'Neutro')
        cursor.execute("INSERT OR REPLACE INTO signs (name, empathic_tone) VALUES (?, ?)", (sign, tone))
        
    for planet in PLANETS:
        cursor.execute("INSERT OR REPLACE INTO planets (name) VALUES (?)", (planet,))
        
    # Crear una plantilla base para CADA combinación Planeta-Signo
    for planet in PLANETS:
        for sign in SIGNS:
            base_text = f"Con {planet} en {sign}, es un momento en el que el cielo nos pide conectar con esa energía. Recuerda que para los nativos de {sign}, esto se siente natural, pero todos estamos aprendiendo a integrar esta vibración."
            cursor.execute('''
            INSERT OR IGNORE INTO transit_templates (planet_name, sign_name, template_text, tone)
            VALUES (?, ?, ?, 'Base')
            ''', (planet, sign, base_text))
            
    conn.commit()
    conn.close()
    print("Matriz de 120 combinaciones (10 Planetas x 12 Signos) insertada correctamente.")
    print("Tonos empáticos definidos para los 12 signos.")

if __name__ == "__main__":
    seed_matrix()
