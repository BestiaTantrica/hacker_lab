import sqlite3
db_path = '/home/ubuntu/plataforma_operativa/resultados/oci1_db.sqlite'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA journal_mode=WAL;')
    mode = cursor.fetchone()[0]
    print(f'WAL mode is now: {mode}')
    conn.close()
except Exception as e:
    print(f'Error enabling WAL: {e}')
