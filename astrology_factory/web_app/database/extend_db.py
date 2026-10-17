import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'users.sqlite')

def extend_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla para Tracking de Interacciones (Estudio Sociológico)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        platform TEXT, -- 'web' o 'telegram'
        role TEXT, -- 'user' o 'model'
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES subscribers(id)
    )
    ''')
    
    # Tabla para la Hoja de Pendientes (Caching Predictivo y Videos)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pending_video_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        video_type TEXT NOT NULL, -- 'predictive_cache', 'natal_chart', 'solar_return'
        status TEXT DEFAULT 'pending', -- 'pending', 'downloading_assets', 'ready_for_render', 'completed'
        payment_status TEXT DEFAULT 'unpaid', -- 'unpaid', 'paid'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Asegurarnos de que telegram_id y telegram_username existen en subscribers
    try:
        cursor.execute("ALTER TABLE subscribers ADD COLUMN telegram_id TEXT")
    except sqlite3.OperationalError:
        pass # La columna ya existe

    try:
        cursor.execute("ALTER TABLE subscribers ADD COLUMN telegram_username TEXT")
    except sqlite3.OperationalError:
        pass

    # Tabla para persistencia y reintento de solicitudes de Telegram
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pending_telegram_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        email TEXT,
        request_type TEXT DEFAULT 'horoscopo_hoy',
        status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
        error_log TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
        
    conn.commit()
    conn.close()
    print(f"Base de datos extendida con éxito en: {db_path}")

if __name__ == "__main__":
    extend_db()
