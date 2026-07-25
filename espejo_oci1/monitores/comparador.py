#!/usr/bin/env python3
"""
comparador.py
--------------
Etapa 2: Comparador de deltas (Backend SQLite)
Genera el delta_{zone}_FECHA.json consultando los subdominios nuevos 
insertados en las últimas 24 horas en oci1_db.sqlite.
Mantiene el 100% de compatibilidad con el resto del pipeline.
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
from datetime import datetime, timezone

parser = argparse.ArgumentParser(description="Generador de deltas por zona desde SQLite")
parser.add_argument("--zone", choices=["americas", "emea", "asia", "all"], default="all",
                    help="Zona geográfica a comparar (default: all)")
args, _ = parser.parse_known_args()
ZONA = args.zone

BASE_DIR = os.path.expanduser("~/plataforma_operativa")
if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.expanduser("~/WORKSPACE/LAB/espejo_oci1")
DB_PATH = os.path.join(BASE_DIR, "resultados", "oci1_db.sqlite")
LOG_FILE = os.path.join(BASE_DIR, "logs", "comparador.log")
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados")

def setup_logging():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logger = logging.getLogger("comparador")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")
    if not logger.handlers:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(formatter)
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

def consultar_nuevos(logger):
    """Consulta SQLite para obtener subdominios insertados en las últimas 24h.
    
    Usa streaming por lotes (fetchmany) para evitar carga total en RAM
    cuando hay cientos de miles de registros.
    """
    if not os.path.exists(DB_PATH):
        logger.error(f"Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)
        
    # timeout=30: espera hasta 30s si mass_recon está en plena escritura
    conn = sqlite3.connect(DB_PATH, timeout=30)
    cursor = conn.cursor()

    # ── PRAGMAs de lectura optimizada ───────────────────────────────
    # WAL: permite leer mientras mass_recon escribe sin database locked
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA cache_size = -16000")  # 16 MB de cache en RAM
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA mmap_size = 67108864")  # 64 MB mmap
    
    query = """
        SELECT dominio_padre, subdominio 
        FROM subdominios 
        WHERE descubierto_el >= datetime('now', '-24 hours')
    """
    params = []
    
    if ZONA != "all":
        query += " AND zona = ?"
        params.append(ZONA)
        
    cursor.execute(query, params)
    
    nuevos_activos = {}
    total_nuevos = 0
    
    # Procesar en lotes de 5000 para no saturar RAM con 500k+ registros
    CHUNK_SIZE = 5000
    while True:
        filas = cursor.fetchmany(CHUNK_SIZE)
        if not filas:
            break
        for dominio, subdominio in filas:
            if dominio not in nuevos_activos:
                nuevos_activos[dominio] = []
            nuevos_activos[dominio].append(subdominio)
            total_nuevos += 1

    conn.close()
    return nuevos_activos, total_nuevos

def guardar_delta(nuevos_activos, logger):
    """Genera resultados/delta_{zone}_YYYY-MM-DD.json manteniendo compatibilidad."""
    fecha_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    delta_file = os.path.join(RESULTADOS_DIR, f"delta_{ZONA}_{fecha_str}.json")
    
    contenido = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nuevos_activos": nuevos_activos,
    }
    
    os.makedirs(RESULTADOS_DIR, exist_ok=True)
    with open(delta_file, "w", encoding="utf-8") as f:
        json.dump(contenido, f, indent=2, ensure_ascii=False)
        
    logger.info("Delta guardado en %s", delta_file)
    return delta_file

def main():
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info(f"Iniciando generador de deltas SQLite (Zona: {ZONA})")
    
    nuevos_activos, total_nuevos = consultar_nuevos(logger)
    
    if total_nuevos == 0:
        logger.info("Sin subdominios nuevos en las últimas 24 horas.")
        logger.info("=" * 60)
        sys.exit(0)
        
    logger.info("Total de activos nuevos detectados en la BD: %d", total_nuevos)
    guardar_delta(nuevos_activos, logger)
    
    logger.info("Finalizando comparador.py (con novedades exportadas al JSON delta)")
    logger.info("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()

