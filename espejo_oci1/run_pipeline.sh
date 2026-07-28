#!/bin/bash
# run_pipeline.sh — Orquestador del Pipeline de Reconocimiento Pasivo
# Se ejecuta diariamente a las 03:00 UTC vía cron.

BASE_DIR="/home/ubuntu/plataforma_operativa"
LOG_FILE="${BASE_DIR}/logs/cron_output.log"
ENV_FILE="${BASE_DIR}/config/entorno.env"
VENV_ACTIVATE="/home/ubuntu/workspace_lab/venv/bin/activate"

# 🔴 FIX CRÍTICO: Cron no tiene directorio de trabajo por defecto. 
# Debemos forzar que se sitúe en la carpeta correcta antes de ejecutar los scripts relativos.
cd "$BASE_DIR" || exit 1

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

# 6. Motor de Dinero (Explotador + Extractor JS) y Mantenimiento
log "=== Corriendo Explotador Automático ==="
echo "=== Corriendo Explotador Automático ===" >> logs/cron.log
python3 monitores/explotador_automatico.py >> logs/cron.log 2>&1

log "=== Corriendo Extractor de Secretos JS ==="
echo "=== Corriendo Extractor de Secretos JS ===" >> logs/cron.log
python3 monitores/extractor_secretos.py >> logs/cron.log 2>&1

find "${BASE_DIR}/resultados/" -type f -mtime +7 -delete

# 7. Escaneo con Nuclei
log "Ejecutando escaneo masivo Nuclei..."
bash monitores/escaneo_nuclei.sh

# 8. Generar Contexto RAG para Pegaso
log "Generando CEREBRO_CONTEXTO.txt para Pegaso..."
python3 "${BASE_DIR}/monitores/generar_contexto_rag.py"

log "Pipeline finalizado exitosamente"
log "============================================================"
