import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c2_db.sqlite")

def migrate():
    print(f"[*] Conectando a la base de datos: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla polls
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            theme TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    print("[+] Tabla 'polls' verificada/creada.")

    # Tabla poll_options
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poll_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            psychological_metadata TEXT,
            FOREIGN KEY(poll_id) REFERENCES polls(id) ON DELETE CASCADE
        )
    ''')
    print("[+] Tabla 'poll_options' verificada/creada.")

    # Tabla poll_votes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poll_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option_id INTEGER NOT NULL,
            user_id INTEGER,
            fingerprint TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(poll_id) REFERENCES polls(id) ON DELETE CASCADE,
            FOREIGN KEY(option_id) REFERENCES poll_options(id) ON DELETE CASCADE
        )
    ''')
    print("[+] Tabla 'poll_votes' verificada/creada.")

    conn.commit()
    conn.close()
    print("[*] Migración de base de datos completada con éxito.")

if __name__ == "__main__":
    migrate()
