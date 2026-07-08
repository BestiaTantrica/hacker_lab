#!/bin/bash
# run_pipeline.sh — Orquestador del Pipeline de Reconocimiento Pasivo
# Se ejecuta diariamente a las 03:00 UTC vía cron.

BASE_DIR="/home/ubuntu/plataforma_operativa"
LOG_FILE="${BASE_DIR}/logs/cron_output.log"
ENV_FILE="${BASE_DIR}/config/entorno.env"
VENV_ACTIVATE="/home/ubuntu/workspace_lab/venv/bin/activate"

# Función de log en bash
log() {
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") [INFO] $1"
}

log "============================================================"
log "Iniciando run_pipeline.sh"

# 1. Cargar variables de entorno
if [ -f "$ENV_FILE" ]; then
    log "Cargando variables de entorno desde ${ENV_FILE}"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    log "⚠️ No se encontró el archivo de entorno ${ENV_FILE}"
fi

# 2. Activar venv
if [ -f "$VENV_ACTIVATE" ]; then
    log "Activando entorno virtual: ${VENV_ACTIVATE}"
    source "$VENV_ACTIVATE"
else
    log "⚠️ No se encontró el entorno virtual en ${VENV_ACTIVATE}"
fi

# 3. Ejecutar Discovery Pasivo
log "Ejecutando discovery pasivo: ${BASE_DIR}/monitores/discovery_pasivo.py"
python3 "${BASE_DIR}/monitores/discovery_pasivo.py"
DISC_CODE=$?
if [ $DISC_CODE -ne 0 ]; then
    log "❌ discovery_pasivo.py falló con código ${DISC_CODE}"
    exit 1
fi
log "discovery_pasivo.py finalizó exitosamente (código 0)"

# 4. Ejecutar Comparador
log "Ejecutando comparador de deltas: ${BASE_DIR}/monitores/comparador.py"
python3 "${BASE_DIR}/monitores/comparador.py"
COMP_CODE=$?
if [ $COMP_CODE -ne 0 ]; then
    log "❌ comparador.py falló con código ${COMP_CODE}"
    exit 1
fi
log "comparador.py finalizó exitosamente (código 0)"

# 5. Ejecutar Analizador de IA e informe a Telegram
log "Ejecutando analizador de IA: ${BASE_DIR}/monitores/analizador_ia.py"
python3 "${BASE_DIR}/monitores/analizador_ia.py"
IA_CODE=$?
if [ $IA_CODE -ne 0 ]; then
    log "⚠️ analizador_ia.py finalizó con advertencias/error (código ${IA_CODE})"
else
    log "analizador_ia.py finalizó exitosamente (código 0)"
fi

log "Pipeline finalizado exitosamente"
log "============================================================"
