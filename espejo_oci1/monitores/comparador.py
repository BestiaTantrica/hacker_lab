#!/usr/bin/env python3
"""
comparador.py
--------------
Etapa 2: Comparador de deltas para el pipeline de monitoreo pasivo de activos.

Compara resultados/actual.json (última corrida de discovery_pasivo.py) contra
estado/previo.json (snapshot de la corrida anterior) para detectar subdominios
NUEVOS por dominio. Si hay novedades, genera resultados/delta_YYYY-MM-DD.json
y actualiza el estado histórico. Si no hay novedades, sólo deja constancia en el log.

Sin dependencias de terceros: sólo librería estándar (json, os, sys, datetime, logging).
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Rutas del entorno (dinámicas, expandidas de forma segura)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.expanduser("~/plataforma_operativa")
ACTUAL_FILE = os.path.join(BASE_DIR, "resultados", "actual.json")
PREVIO_FILE = os.path.join(BASE_DIR, "estado", "previo.json")
LOG_FILE = os.path.join(BASE_DIR, "logs", "comparador.log")
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados")


def setup_logging():
    """Configura logging a archivo y consola usando el módulo estándar logging."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    logger = logging.getLogger("comparador")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def ensure_directories():
    """Crea los directorios necesarios (resultados, estado, logs) si no existen."""
    for path in (ACTUAL_FILE, PREVIO_FILE, LOG_FILE):
        os.makedirs(os.path.dirname(path), exist_ok=True)


def load_json_file(path, logger, required=False):
    """
    Carga un archivo JSON de forma segura.
    Devuelve el dict parseado, o None si no existe / está corrupto.
    Si `required` es True y el archivo falta o está corrupto, termina el script
    con código de salida distinto de 0 (actual.json siempre debe existir y ser válido).
    """
    if not os.path.exists(path):
        if required:
            logger.error("Archivo requerido no encontrado: %s", path)
            sys.exit(1)
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        if required:
            logger.error("No se pudo leer/parsear el archivo requerido %s: %s", path, e)
            sys.exit(1)
        logger.warning("No se pudo leer/parsear %s (%s); se ignora y se trata como inexistente", path, e)
        return None


def calcular_delta(dominios_actual, dominios_previo, logger):
    """
    Compara subdominios actuales contra previos, dominio por dominio.
    Devuelve un dict {dominio: [nuevos_subdominios]} solo con dominios que tengan novedades.
    """
    nuevos_activos = {}
    total_nuevos = 0

    for dominio, subs_actuales in dominios_actual.items():
        subs_previos = set(dominios_previo.get(dominio, []))
        subs_actuales_set = set(subs_actuales)

        nuevos = sorted(subs_actuales_set - subs_previos)

        if nuevos:
            nuevos_activos[dominio] = nuevos
            total_nuevos += len(nuevos)
            logger.info("Dominio '%s': %d subdominio(s) nuevo(s) detectado(s)", dominio, len(nuevos))
        else:
            logger.debug("Dominio '%s': sin novedades", dominio)

    return nuevos_activos, total_nuevos


def guardar_delta(nuevos_activos, logger):
    """Genera resultados/delta_YYYY-MM-DD.json de forma atómica."""
    fecha_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    delta_file = os.path.join(RESULTADOS_DIR, f"delta_{fecha_str}.json")
    tmp_file = delta_file + ".tmp"

    contenido = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "nuevos_activos": nuevos_activos,
    }

    try:
        os.makedirs(RESULTADOS_DIR, exist_ok=True)
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(contenido, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, delta_file)
        logger.info("Delta guardado en %s", delta_file)
        return delta_file
    except OSError as e:
        logger.error("No se pudo escribir el archivo delta %s: %s", delta_file, e)
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except OSError:
                pass
        return None


def actualizar_estado_previo(actual_data, logger):
    """
    Actualiza estado/previo.json con el contenido de actual.json, de forma atómica,
    para que la próxima ejecución compare contra este snapshot.

    NOTA DE DISEÑO (asunción, no pedida explícitamente en el prompt): sin esto,
    cada corrida futura volvería a marcar los mismos subdominios como "nuevos"
    indefinidamente, ya que previo.json nunca reflejaría el estado actual.
    Si preferís otro esquema de actualización de estado, decime y lo ajusto.
    """
    tmp_file = PREVIO_FILE + ".tmp"
    try:
        os.makedirs(os.path.dirname(PREVIO_FILE), exist_ok=True)
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(actual_data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, PREVIO_FILE)
        logger.info("Estado histórico actualizado en %s", PREVIO_FILE)
    except OSError as e:
        logger.error("No se pudo actualizar el estado histórico %s: %s", PREVIO_FILE, e)
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except OSError:
                pass


def main():
    ensure_directories()
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("Iniciando comparador.py")

    actual_data = load_json_file(ACTUAL_FILE, logger, required=True)
    dominios_actual = actual_data.get("dominios", {})

    previo_data = load_json_file(PREVIO_FILE, logger, required=False)

    if previo_data is None:
        # Primera ejecución (o previo.json corrupto/faltante):
        # se trata TODO lo actual como nuevo.
        logger.info(
            "No existe estado previo válido (%s); se tratan todos los subdominios "
            "actuales como nuevos (primera ejecución)", PREVIO_FILE
        )
        dominios_previo = {}
    else:
        dominios_previo = previo_data.get("dominios", {})

    nuevos_activos, total_nuevos = calcular_delta(dominios_actual, dominios_previo, logger)

    if total_nuevos == 0:
        logger.info("Sin cambios detectados")
        # Aun sin novedades, actualizamos el estado por si actual.json trae
        # datos frescos (ej. mismos subdominios pero timestamp nuevo).
        actualizar_estado_previo(actual_data, logger)
        logger.info("Finalizando comparador.py (sin novedades)")
        logger.info("=" * 60)
        sys.exit(0)

    logger.info("Total de activos nuevos detectados: %d", total_nuevos)
    guardar_delta(nuevos_activos, logger)
    actualizar_estado_previo(actual_data, logger)

    logger.info("Finalizando comparador.py (con novedades)")
    logger.info("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
