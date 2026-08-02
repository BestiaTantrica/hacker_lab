#!/bin/bash
# backup_oci_storage.sh - Backup Automatico de c2_db.sqlite a OCI Object Storage
# ================================================================================
# Uso: ./backup_oci_storage.sh
# Cron: 0 3 * * * /home/ubuntu/c2_panel/backup_oci_storage.sh >> /home/ubuntu/c2_panel/logs/backup.log 2>&1
#
# Dependencias: oci-cli configurado en el servidor OCI-2 (instalar con: bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)")
# Variables de entorno requeridas (en .env o exportadas):
#   OCI_BACKUP_BUCKET   -> nombre del bucket en OCI Object Storage (ej: "hackerlab-backups")
#   OCI_BACKUP_NS       -> namespace del tenancy (ver en OCI Console > Object Storage)
# ================================================================================

set -euo pipefail

# -- Configuracion ------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${0}")" && pwd)"
DB_SOURCE="${SCRIPT_DIR}/c2_db.sqlite"
BACKUP_BASENAME="c2_db_backup"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%SZ")
BACKUP_FILE="/tmp/${BACKUP_BASENAME}_${TIMESTAMP}.sqlite"
BACKUP_GZ="/tmp/${BACKUP_BASENAME}_${TIMESTAMP}.sqlite.gz"
LOG_PREFIX="$(date -u +"%Y-%m-%dT%H:%M:%SZ") [BACKUP]"

# Variables de entorno (con fallback a valores por defecto inofensivos)
# Cargar desde .env si existe
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    # shellcheck disable=SC1090
    source "${SCRIPT_DIR}/.env"
    set +a
fi

OCI_BACKUP_BUCKET="${OCI_BACKUP_BUCKET:-hackerlab-backups}"
OCI_BACKUP_NS="${OCI_BACKUP_NS:-idd9nlzkvn8c}"
OCI_PAR_URL="${OCI_PAR_URL:-}"

# -- Validaciones previas -----------------------------------------------------
log() { echo "${LOG_PREFIX} $1"; }
error_exit() { echo "${LOG_PREFIX} [ERROR] $1"; rm -f "${BACKUP_FILE}" "${BACKUP_GZ}"; exit 1; }

log "======================================================"
log "Iniciando backup de c2_db.sqlite"

# Verificar que la DB existe
[ -f "${DB_SOURCE}" ] || error_exit "Base de datos no encontrada en ${DB_SOURCE}"

# Verificar método de subida
if [ -n "${OCI_PAR_URL}" ]; then
    log "Método de subida: URL Pre-Autenticada (curl PAR - ultraliviano)"
else
    command -v oci > /dev/null 2>&1 || error_exit "Ni OCI_PAR_URL está configurada ni oci-cli está instalado."
    log "Método de subida: oci-cli"
fi

# -- Paso 1: Snapshot seguro de SQLite ----------------------------------------
# sqlite3 .backup es transaccional y seguro incluso con la DB en uso.
log "Paso 1/3: Creando snapshot SQLite en ${BACKUP_FILE}..."
if command -v sqlite3 > /dev/null 2>&1; then
    sqlite3 "${DB_SOURCE}" ".backup '${BACKUP_FILE}'" \
        || error_exit "Fallo el snapshot de SQLite via CLI."
else
    python3 -c "import sqlite3; src=sqlite3.connect('${DB_SOURCE}'); dst=sqlite3.connect('${BACKUP_FILE}'); src.backup(dst); dst.close(); src.close()" \
        || error_exit "Fallo el snapshot de SQLite via Python API."
fi
log "Snapshot creado: $(du -sh "${BACKUP_FILE}" | cut -f1)"

# -- Paso 2: Comprimir con gzip -----------------------------------------------
log "Paso 2/3: Comprimiendo snapshot (gzip -9)..."
gzip -9 "${BACKUP_FILE}" \
    || error_exit "Fallo la compresion gzip."
# Verificar que el .gz existe y no esta vacio
[ -s "${BACKUP_GZ}" ] || error_exit "El archivo comprimido esta vacio. Abortando."
log "Archivo comprimido: $(du -sh "${BACKUP_GZ}" | cut -f1) -> ${BACKUP_GZ}"

# -- Paso 3: Subir a OCI Object Storage ---------------------------------------
OBJECT_NAME="${BACKUP_BASENAME}_${TIMESTAMP}.sqlite.gz"
log "Paso 3/3: Subiendo a OCI Object Storage (${OBJECT_NAME})..."

if [ -n "${OCI_PAR_URL}" ]; then
    # Garantizar que la PAR URL termine con '/'
    PAR_ENDPOINT="${OCI_PAR_URL}"
    [[ "${PAR_ENDPOINT}" != */ ]] && PAR_ENDPOINT="${PAR_ENDPOINT}/"
    
    curl -s -f -X PUT --data-binary "@${BACKUP_GZ}" "${PAR_ENDPOINT}${OBJECT_NAME}" \
        || error_exit "Fallo la subida via curl PAR. Verificar validez de OCI_PAR_URL."
else
    OCI_CMD="oci os object put \
        --bucket-name \"${OCI_BACKUP_BUCKET}\" \
        --file \"${BACKUP_GZ}\" \
        --name \"${OBJECT_NAME}\" \
        --force"
    if [ -n "${OCI_BACKUP_NS}" ]; then
        OCI_CMD="${OCI_CMD} --namespace \"${OCI_BACKUP_NS}\""
    fi
    eval "${OCI_CMD}" > /dev/null \
        || error_exit "Fallo la subida a OCI Object Storage via oci-cli."
fi

log "Backup subido exitosamente: ${OBJECT_NAME}"

# -- Limpieza de temporales ---------------------------------------------------
rm -f "${BACKUP_GZ}"
log "Archivos temporales limpiados."

# -- Rotacion: Eliminar backups con mas de 30 dias del bucket -----------------
# Lista los objetos y elimina los que tengan mas de 30 dias
log "Verificando rotacion de backups antiguos (> 30 dias)..."
CUTOFF_DATE=$(date -u -d "30 days ago" +"%Y%m%d" 2>/dev/null || date -u -v-30d +"%Y%m%d" 2>/dev/null || echo "00000000")

# Listar objetos del bucket y purgar los que superen la fecha de corte
OCI_LIST_CMD="oci os object list --bucket-name \"${OCI_BACKUP_BUCKET}\" --query 'data[*].name' --raw-output 2>/dev/null || true"
if [ -n "${OCI_BACKUP_NS}" ]; then
    OCI_LIST_CMD="oci os object list --bucket-name \"${OCI_BACKUP_BUCKET}\" --namespace \"${OCI_BACKUP_NS}\" --query 'data[*].name' --raw-output 2>/dev/null || true"
fi

# Extraer nombres y comparar fechas (formato: c2_db_backup_YYYYMMDD_HHMMSSz.sqlite.gz)
eval "${OCI_LIST_CMD}" | tr -d '[]"' | tr ',' '\n' | grep "^${BACKUP_BASENAME}_" | while read -r obj_name; do
    obj_date=$(echo "${obj_name}" | grep -oE '[0-9]{8}' | head -1 || echo "99999999")
    if [ "${obj_date}" -lt "${CUTOFF_DATE}" ] 2>/dev/null; then
        log "Eliminando backup antiguo: ${obj_name}"
        OCI_DEL_CMD="oci os object delete --bucket-name \"${OCI_BACKUP_BUCKET}\" --object-name \"${obj_name}\" --force 2>/dev/null || true"
        [ -n "${OCI_BACKUP_NS}" ] && OCI_DEL_CMD="oci os object delete --bucket-name \"${OCI_BACKUP_BUCKET}\" --namespace \"${OCI_BACKUP_NS}\" --object-name \"${obj_name}\" --force 2>/dev/null || true"
        eval "${OCI_DEL_CMD}"
    fi
done || true

log "Backup completado exitosamente."
log "======================================================"
