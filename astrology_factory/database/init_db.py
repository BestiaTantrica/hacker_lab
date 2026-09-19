import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'astrology_meanings.sqlite')

def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Planetas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS planets (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        keywords TEXT,
        empathic_description TEXT
    )
    ''')
    
    # 2. Signos y Tono Empático de Comunicación
    # Se agregó "empathic_tone" para definir CÓMO hablarle a cada signo.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signs (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        element TEXT,
        quality TEXT,
        keywords TEXT,
        empathic_tone TEXT
    )
    ''')
    
    # 3. Plantillas de Tránsito Generales (Canal de YouTube)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transit_templates (
        id INTEGER PRIMARY KEY,
        planet_name TEXT,
        sign_name TEXT,
        aspect_name TEXT,
        template_text TEXT,
        tone TEXT
    )
    ''')
    
    # 4. Plantillas de Horóscopo Personalizado (Para suscriptores)
    # Diferencia entre carta natal vs tránsito actual.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personalized_templates (
        id INTEGER PRIMARY KEY,
        natal_sign TEXT,
        transit_planet TEXT,
        transit_sign TEXT,
        template_text TEXT
    )
    ''')

    # 5. Feedback de Usuarios (Para mejorar la base de datos a futuro)
    # Permite escalar y adaptar el sistema de forma automática.
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY,
        subscriber_id TEXT,
        horoscope_text TEXT,
        rating INTEGER,
        user_comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Estructura de Base de Datos ampliada en: {db_path}")

if __name__ == "__main__":
    init_db()
