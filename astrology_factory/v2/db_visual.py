#!/usr/bin/env python3
"""
Base de Datos Visual (SQLite) para Astrology Factory V2.
Permite indexar assets auditados con sus etiquetas extraídas por Gemini.
"""
import sqlite3
import datetime
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = FACTORY_ROOT / "assets_visuales.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruta_archivo TEXT UNIQUE,
                tipo TEXT,
                estado TEXT,
                etiquetas TEXT,
                fecha_auditoria TEXT
            )
        ''')
        conn.commit()

def registrar_asset(ruta_archivo: Path, tipo: str, estado: str, etiquetas: list = None):
    init_db()
    ruta_str = str(ruta_archivo.resolve())
    etiquetas_str = ",".join(etiquetas).lower() if etiquetas else ""
    fecha = datetime.datetime.now().isoformat()
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO assets (ruta_archivo, tipo, estado, etiquetas, fecha_auditoria)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(ruta_archivo) DO UPDATE SET
                estado = excluded.estado,
                etiquetas = excluded.etiquetas,
                fecha_auditoria = excluded.fecha_auditoria
        ''', (ruta_str, tipo, estado, etiquetas_str, fecha))
        conn.commit()

def buscar_assets_aprobados(query_etiquetas: str) -> list[str]:
    init_db()
    palabras = [p.strip().lower() for p in query_etiquetas.split() if p.strip()]
    if not palabras:
        return []
        
    query = "SELECT ruta_archivo FROM assets WHERE estado = 'aprobado'"
    params = []
    
    for palabra in palabras:
        query += " AND etiquetas LIKE ?"
        params.append(f"%{palabra}%")
        
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(query, params)
        resultados = c.fetchall()
        return [f[0] for f in resultados]

def obtener_todos_los_assets_aprobados() -> list[tuple]:
    """Retorna una lista de tuplas (ruta_archivo, etiquetas)."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT ruta_archivo, etiquetas FROM assets WHERE estado = 'aprobado'")
        return c.fetchall()

if __name__ == "__main__":
    init_db()
    print(f"Base de datos visual inicializada en {DB_PATH}")
