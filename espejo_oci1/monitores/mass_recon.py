#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mass_recon.py — Motor de Reconocimiento Masivo ("Red de Pesca" Fase 2)
======================================================================
Ejecuta descubrimiento secuencial por lotes (batching) para no ahogar la RAM de OCI-1.
Integra múltiples fuentes:
  1. Subfinder (Búsqueda rápida en 30+ fuentes DNS)
  2. Wayback Machine (URLs y subdominios muertos/legados)
  3. crt.sh (Fallback si Subfinder falla)

Genera la misma estructura de salida que `discovery_pasivo.py` para compatibilidad
total con el `comparador.py` y `analizador_ia.py` subsiguientes.
"""

import os
import sys
import json
import logging
import subprocess
import argparse
import datetime
import urllib.request
import urllib.error
import socket
from urllib.parse import urlparse

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN Y RUTAS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.expanduser("~/plataforma_operativa")
if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.expanduser("~/WORKSPACE/LAB/espejo_oci1")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
RESULT_DIR = os.path.join(BASE_DIR, "resultados")
LOG_DIR    = os.path.join(BASE_DIR, "logs")

# Mapeo de zonas horarias a archivos de objetivos
ZONE_FILES = {
    "americas": os.path.join(CONFIG_DIR, "objetivos_americas.txt"),
    "emea":     os.path.join(CONFIG_DIR, "objetivos_emea.txt"),
    "asia":     os.path.join(CONFIG_DIR, "objetivos_asia.txt"),
    "all":      os.path.join(CONFIG_DIR, "objetivos.txt"),  # Legado
}

RESULTADO_FILE = os.path.join(RESULT_DIR, "actual.json")
LOG_FILE       = os.path.join(LOG_DIR, "mass_recon.log")

BATCH_SIZE = 5 # Cantidad de dominios a procesar simultáneamente en memoria
TIMEOUT_GLOBAL = 300 # Timeout de 5 minutos por dominio para evitar bloqueos

os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# MOTORES DE RECONOCIMIENTO
# ─────────────────────────────────────────────────────────────────────────────
def run_subfinder(dominio: str) -> set:
    """Busca subdominios usando el binario Subfinder (muy rápido y ligero)."""
    subdominios = set()
    ruta_subfinder = None
    
    # Buscar binario
    for candidato in [os.path.expanduser("~/.local/bin/subfinder"), "/usr/local/bin/subfinder", "/usr/bin/subfinder"]:
        if os.path.isfile(candidato) and os.access(candidato, os.X_OK):
            ruta_subfinder = candidato
            break

    if not ruta_subfinder:
        log.warning(f"[{dominio}] subfinder no encontrado.")
        return subdominios

    try:
        res = subprocess.run(
            [ruta_subfinder, "-d", dominio, "-silent", "-all"],
            capture_output=True, text=True, timeout=TIMEOUT_GLOBAL
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                sub = line.strip().lower()
                if sub and sub.endswith(dominio):
                    subdominios.add(sub)
            log.info(f"[{dominio}] Subfinder: {len(subdominios)} encontrados.")
    except subprocess.TimeoutExpired:
        log.error(f"[{dominio}] Subfinder TIMEOUT.")
    except Exception as e:
        log.error(f"[{dominio}] Subfinder Error: {e}")

    return subdominios


def run_wayback(dominio: str) -> set:
    """Extrae hosts antiguos de la Wayback Machine. Mina de oro para APIs legacy."""
    subdominios = set()
    url = f"http://web.archive.org/cdx/search/cdx?url=*.{dominio}/*&output=json&fl=original&collapse=urlkey"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=45) as r:
            data = json.loads(r.read().decode("utf-8"))
            
            # El primer elemento es el header ['original']
            if len(data) > 1:
                for row in data[1:]:
                    try:
                        # Limpiar barras dobles raras en urls de Wayback: //subdomain.com/
                        raw_url = row[0].replace("///", "//")
                        parsed = urlparse(raw_url)
                        if parsed.hostname:
                            # Eliminar puerto si existe (ej. subdomain.com:8080)
                            clean_host = parsed.hostname.split(":")[0].lower().strip()
                            if clean_host.endswith(dominio):
                                subdominios.add(clean_host)
                    except:
                        pass
        log.info(f"[{dominio}] Wayback Machine: {len(subdominios)} hosts extraídos.")
    except Exception as e:
        log.warning(f"[{dominio}] Wayback Machine Falló (Posible Rate Limit): {e}")

    return subdominios


def run_crtsh(dominio: str) -> set:
    """Fallback si no encontramos nada, escanea certificados SSL."""
    subdominios = set()
    url = f"https://crt.sh/?q=%.{dominio}&output=json"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
            for entry in data:
                val = entry.get("name_value", "").lower().strip().lstrip("*.")
                if val.endswith(dominio):
                    subdominios.add(val)
        log.info(f"[{dominio}] crt.sh: {len(subdominios)} encontrados.")
    except Exception as e:
        log.warning(f"[{dominio}] crt.sh Falló: {e}")

    return subdominios


# ─────────────────────────────────────────────────────────────────────────────
# ORQUESTADOR SECUENCIAL (BATCHING CON SQLITE)
# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    """Inicializa la base de datos SQLite para la zona de recolección."""
    db_path = os.path.join(RESULT_DIR, "oci1_db.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subdominios (
            subdominio TEXT PRIMARY KEY,
            dominio_padre TEXT NOT NULL,
            zona TEXT NOT NULL,
            descubierto_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dominio ON subdominios(dominio_padre)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_zona ON subdominios(zona)")
    conn.commit()
    return conn

def descubrir_dominio(dominio: str) -> list[str]:
    """Combina todas las fuentes para un dominio dado y fusiona resultados."""
    log.info(f"--- Iniciando recolección para: {dominio} ---")
    resultados_totales = set()

    # 1. Subfinder (Core)
    resultados_totales.update(run_subfinder(dominio))
    
    # 2. Wayback Machine (Legacy endpoints)
    resultados_totales.update(run_wayback(dominio))

    # 3. crt.sh (Fallback si hay pocos)
    if len(resultados_totales) < 10:
        resultados_totales.update(run_crtsh(dominio))

    log.info(f"✅ [{dominio}] Total unificado único: {len(resultados_totales)}")
    return sorted(list(resultados_totales))


def main():
    parser = argparse.ArgumentParser(description="Mass Recon — Red de Pesca Fase 2 (SQLite Backend)")
    parser.add_argument("--zone", choices=["americas", "emea", "asia", "all"], default="all",
                        help="Zona geográfica a escanear (default: all)")
    args = parser.parse_args()

    log.info("=" * 70)
    log.info(f"🌐 INICIANDO MASS_RECON (FASE 2 RED DE PESCA) — ZONA: {args.zone.upper()} 🌐")

    objetivos_file = ZONE_FILES.get(args.zone)
    if not objetivos_file or not os.path.isfile(objetivos_file):
        log.error(f"Falta archivo de objetivos para zona '{args.zone}': {objetivos_file}")
        sys.exit(1)

    with open(objetivos_file, "r") as f:
        dominios = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not dominios:
        log.error("Archivo de objetivos vacío.")
        sys.exit(1)

    log.info(f"🎯 Total de targets a pescar: {len(dominios)}")

    # 1. Inicializar la base de datos (Streaming Backend)
    conn = init_db()
    cursor = conn.cursor()

    # 2. Procesamiento Secuencial con Flush Inmediato
    total_nuevos_corrida = 0
    
    for i, dominio in enumerate(dominios):
        log.info(f"\n📦 PROCESANDO [{i+1}/{len(dominios)}]: {dominio}")
        
        # Obtener los subdominios
        subdominios = descubrir_dominio(dominio)
        
        # Preparamos el batch para insertar
        batch_insert = [(sub, dominio, args.zone) for sub in subdominios]
        
        if batch_insert:
            # Usamos INSERT OR IGNORE para que solo cuenten los que no existían previamente
            cursor.executemany(
                "INSERT OR IGNORE INTO subdominios (subdominio, dominio_padre, zona) VALUES (?, ?, ?)",
                batch_insert
            )
            # Frecuencia de impacto real (filas insertadas)
            nuevos_insertados = cursor.rowcount
            conn.commit()
            total_nuevos_corrida += nuevos_insertados
            log.info(f"💾 Guardados en SQLite: {len(batch_insert)} (Nuevos reales: {nuevos_insertados})")

    conn.close()
    
    log.info("=" * 70)
    log.info(f"🎉 MASS_RECON FINALIZADO (ZONA {args.zone.upper()}).")
    log.info(f"Nuevos subdominios puros inyectados en la BD: {total_nuevos_corrida}")
    log.info("=" * 70)


if __name__ == "__main__":
    main()
