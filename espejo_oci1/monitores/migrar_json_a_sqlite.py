#!/usr/bin/env python3
"""
migrar_json_a_sqlite.py
-----------------------
Migra los archivos actual_*.json históricos (si existen) a la nueva
base de datos SQLite `oci1_db.sqlite` para no perder la data existente
y arrancar el nuevo pipeline con la historia intacta.
"""

import os
import json
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.expanduser("~/plataforma_operativa")
if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.expanduser("~/WORKSPACE/LAB/espejo_oci1")

RESULT_DIR = os.path.join(BASE_DIR, "resultados")
os.makedirs(RESULT_DIR, exist_ok=True)
DB_PATH = os.path.join(RESULT_DIR, "oci1_db.sqlite")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subdominios (
            subdominio TEXT PRIMARY KEY,
            dominio_padre TEXT NOT NULL,
            zona TEXT NOT NULL,
            descubierto_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Índice para búsquedas rápidas por dominio o zona
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dominio ON subdominios(dominio_padre)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_zona ON subdominios(zona)")
    conn.commit()
    return conn

def main():
    print(f"Iniciando migración a SQLite en: {DB_PATH}")
    conn = init_db()
    cursor = conn.cursor()
    
    total_migrados = 0
    
    # Buscar archivos JSON de zonas
    zonas = ["americas", "emea", "asia", "all"]
    for zona in zonas:
        json_path = os.path.join(RESULT_DIR, f"actual_{zona}.json")
        # Si no está ahí, buscar el legacy actual.json
        if zona == "all" and not os.path.exists(json_path):
            json_path = os.path.join(RESULT_DIR, "actual.json")
            
        if not os.path.exists(json_path):
            continue
            
        print(f"Procesando {json_path} (Zona: {zona})...")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                dominios = data.get("dominios", {})
                
                batch = []
                for dominio_padre, subs in dominios.items():
                    for sub in subs:
                        batch.append((sub, dominio_padre, zona))
                        
                # Insertar batch
                if batch:
                    cursor.executemany(
                        "INSERT OR IGNORE INTO subdominios (subdominio, dominio_padre, zona) VALUES (?, ?, ?)",
                        batch
                    )
                    conn.commit()
                    total_migrados += len(batch)
                    print(f"  -> {len(batch)} subdominios migrados de {zona}")
                    
        except Exception as e:
            print(f"Error procesando {json_path}: {e}")
            
    conn.close()
    print(f"Migración completada. Total subdominios en BD: {total_migrados}")

if __name__ == "__main__":
    main()
