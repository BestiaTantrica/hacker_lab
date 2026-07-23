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
                        parsed = urlparse(row[0])
                        if parsed.hostname and parsed.hostname.endswith(dominio):
                            subdominios.add(parsed.hostname.lower())
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
# ORQUESTADOR SECUENCIAL (BATCHING)
# ─────────────────────────────────────────────────────────────────────────────
def descubrir_dominio(dominio: str, previo: dict) -> list[str]:
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

    # 4. Fallback de emergencia: Preservar histórico si algo falló masivamente
    if not resultados_totales:
        anterior = set(previo.get(dominio, []))
        if anterior:
            log.error(f"[{dominio}] Fuentes fallaron. Preservando {len(anterior)} subdominios históricos.")
            return sorted(list(anterior))

    log.info(f"✅ [{dominio}] Total unificado único: {len(resultados_totales)}")
    return sorted(list(resultados_totales))


def main():
    parser = argparse.ArgumentParser(description="Mass Recon — Red de Pesca Fase 2")
    parser.add_argument("--zone", choices=["americas", "emea", "asia", "all"], default="all",
                        help="Zona geográfica a escanear (default: all)")
    args = parser.parse_args()

    log.info("=" * 70)
    log.info(f"🌐 INICIANDO MASS_RECON (FASE 2 RED DE PESCA) — ZONA: {args.zone.upper()} 🌐")

    objetivos_file = ZONE_FILES.get(args.zone)
    if not objetivos_file or not os.path.isfile(objetivos_file):
        log.error(f"Falta archivo de objetivos para zona '{args.zone}': {objetivos_file}")
        sys.exit(1)

    # El archivo de salida es por zona para no mezclar deltas entre continentes
    global RESULTADO_FILE
    RESULTADO_FILE = os.path.join(RESULT_DIR, f"actual_{args.zone}.json")

    with open(objetivos_file, "r") as f:
        dominios = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not dominios:
        log.error("Archivo de objetivos vacío.")
        sys.exit(1)

    log.info(f"🎯 Total de targets a pescar: {len(dominios)}")

    # 2. Cargar histórico para Fallback
    previo = {}
    if os.path.isfile(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE, "r") as f:
                data = json.load(f)
                previo = data.get("dominios", {})
        except Exception:
            pass

    # 3. Procesamiento en Lotes (Batching para cuidar RAM)
    resultados_finales = {}
    
    for i in range(0, len(dominios), BATCH_SIZE):
        lote = dominios[i:i + BATCH_SIZE]
        log.info(f"\n📦 PROCESANDO LOTE {i//BATCH_SIZE + 1} ({len(lote)} dominios)...")
        
        for dominio in lote:
            subdominios = descubrir_dominio(dominio, previo)
            resultados_finales[dominio] = subdominios
            
        # Podríamos forzar garbage collection aquí si fuera un entorno hiper restrictivo
        # import gc; gc.collect()

    # 4. Guardar archivo final unificado (El mismo JSON que usaba discovery_pasivo)
    salida = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dominios": resultados_finales,
    }
    
    with open(RESULTADO_FILE, "w") as f:
        json.dump(salida, f, indent=2)

    total_subs = sum(len(v) for v in resultados_finales.values())
    log.info("=" * 70)
    log.info(f"🎉 MASS_RECON FINALIZADO. {total_subs} subdominios guardados en {RESULTADO_FILE}")
    log.info("=" * 70)


if __name__ == "__main__":
    main()
