#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
discovery_pasivo.py — Motor de Descubrimiento Pasivo de Activos.

Estrategia de fuentes (en orden de prioridad):
  1. subfinder  — binario local, 30+ fuentes simultáneas, sin timeout, PRIMERA OPCIÓN.
  2. crt.sh     — API web pública, inestable para dominios grandes, FALLBACK.

Salida: /home/ubuntu/plataforma_operativa/resultados/actual.json
Formato:
  {
    "timestamp": "ISO8601",
    "dominios": {
      "mongodb.com": ["sub1.mongodb.com", "sub2.mongodb.com"],
      ...
    }
  }
"""

import os
import sys
import json
import logging
import subprocess
import datetime
import urllib.request
import urllib.error
import socket

# ─────────────────────────────────────────────────────────────────────────────
# Configuración de rutas
BASE_DIR   = os.path.expanduser("~/plataforma_operativa")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
RESULT_DIR = os.path.join(BASE_DIR, "resultados")
LOG_DIR    = os.path.join(BASE_DIR, "logs")

OBJETIVOS_FILE = os.path.join(CONFIG_DIR, "objetivos.txt")
RESULTADO_FILE = os.path.join(RESULT_DIR, "actual.json")
LOG_FILE       = os.path.join(LOG_DIR, "discovery.log")

# ─────────────────────────────────────────────────────────────────────────────
# Logging
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
# FUENTE 1: subfinder (principal)
def descubrir_con_subfinder(dominio: str) -> list[str] | None:
    """
    Ejecuta subfinder localmente. Devuelve lista de subdominios o None si falla.
    """
    ruta_subfinder = None
    for candidato in [os.path.expanduser("~/.local/bin/subfinder"),
                      "/usr/local/bin/subfinder", "/usr/bin/subfinder",
                      os.path.expanduser("~/go/bin/subfinder")]:
        if os.path.isfile(candidato) and os.access(candidato, os.X_OK):
            ruta_subfinder = candidato
            break

    if not ruta_subfinder:
        log.warning("subfinder no está instalado. Usando fallback crt.sh.")
        return None

    log.info(f"[subfinder] Escaneando '{dominio}'...")
    try:
        resultado = subprocess.run(
            [ruta_subfinder, "-d", dominio, "-silent", "-timeout", "120"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if resultado.returncode != 0 and not resultado.stdout.strip():
            log.warning(f"[subfinder] Falló para '{dominio}': {resultado.stderr.strip()[:200]}")
            return None

        subdominios = sorted(set(
            line.strip().lower()
            for line in resultado.stdout.splitlines()
            if line.strip() and dominio in line.strip()
        ))
        log.info(f"[subfinder] '{dominio}': {len(subdominios)} subdominios encontrados.")
        return subdominios

    except subprocess.TimeoutExpired:
        log.error(f"[subfinder] Timeout para '{dominio}'.")
        return None
    except Exception as e:
        log.error(f"[subfinder] Excepción para '{dominio}': {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# FUENTE 2: crt.sh (fallback)
def descubrir_con_crtsh(dominio: str, reintentos: int = 3) -> list[str] | None:
    """
    Consulta crt.sh. Devuelve lista o None si falla tras los reintentos.
    """
    url = f"https://crt.sh/?q=%.{dominio}&output=json"
    esperas = [5, 10, 20]

    for intento in range(1, reintentos + 1):
        log.info(f"[crt.sh] Consultando '{dominio}' (intento {intento}/{reintentos})")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                datos = json.loads(r.read().decode("utf-8"))

            subdominios = sorted(set(
                entry.get("name_value", "").lower().strip().lstrip("*.")
                for entry in datos
                if dominio in entry.get("name_value", "")
            ))
            log.info(f"[crt.sh] '{dominio}': {len(subdominios)} subdominios encontrados.")
            return subdominios

        except urllib.error.HTTPError as e:
            log.warning(f"[crt.sh] Error HTTP '{dominio}' (intento {intento}): {e}")
        except urllib.error.URLError as e:
            log.warning(f"[crt.sh] Error URL '{dominio}' (intento {intento}): {e}")
        except socket.timeout:
            log.warning(f"[crt.sh] Timeout '{dominio}' (intento {intento}).")
        except Exception as e:
            log.warning(f"[crt.sh] Error inesperado '{dominio}' (intento {intento}): {e}")

        if intento < reintentos:
            import time
            espera = esperas[intento - 1]
            log.info(f"[crt.sh] Esperando {espera}s antes de reintentar...")
            time.sleep(espera)

    log.error(f"[crt.sh] Fallaron todos los intentos para '{dominio}'.")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Motor principal
def descubrir_dominio(dominio: str, previo: dict) -> list[str]:
    """
    Intenta subfinder primero, luego crt.sh, luego preserva datos anteriores.
    """
    # Intento 1: subfinder
    resultado = descubrir_con_subfinder(dominio)

    # Intento 2: crt.sh como fallback
    if resultado is None:
        resultado = descubrir_con_crtsh(dominio)

    # Intento 3: preservar el último resultado válido si todo falla
    if resultado is None:
        anterior = previo.get(dominio, [])
        if anterior:
            log.warning(f"Todas las fuentes fallaron para '{dominio}'. "
                        f"Preservando {len(anterior)} subdominios del último resultado válido.")
        else:
            log.error(f"Todas las fuentes fallaron para '{dominio}' y no hay historial previo.")
        return anterior

    return resultado


def main():
    log.info("=" * 60)
    log.info("Iniciando discovery_pasivo.py")

    # Cargar objetivos
    if not os.path.isfile(OBJETIVOS_FILE):
        log.error(f"No se encontró el archivo de objetivos: {OBJETIVOS_FILE}")
        sys.exit(1)

    with open(OBJETIVOS_FILE) as f:
        dominios = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    if not dominios:
        log.error("El archivo de objetivos está vacío.")
        sys.exit(1)

    log.info(f"Cargados {len(dominios)} dominio(s) objetivo.")

    # Cargar resultado previo para el fallback
    previo = {}
    if os.path.isfile(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE) as f:
                data = json.load(f)
                previo = data.get("dominios", {})
        except Exception:
            pass

    # Ejecutar el discovery de cada dominio
    resultados = {}
    hubo_errores = False
    for dominio in dominios:
        log.info(f"Procesando: {dominio}")
        subdominios = descubrir_dominio(dominio, previo)
        resultados[dominio] = subdominios
        if not subdominios and not previo.get(dominio):
            hubo_errores = True

    # Guardar
    salida = {
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dominios": resultados,
    }
    with open(RESULTADO_FILE, "w") as f:
        json.dump(salida, f, indent=2)

    total = sum(len(v) for v in resultados.values())
    log.info(f"Resultados guardados en {RESULTADO_FILE} — Total: {total} subdominios.")

    if hubo_errores:
        log.warning("Discovery finalizado CON errores parciales.")
    else:
        log.info("Discovery finalizado correctamente.")

    log.info("=" * 60)


if __name__ == "__main__":
    main()
