#!/bin/bash

# ==============================================================================
# 🗄️ BÓVEDA PROFUNDA: Sincronización de Base de Datos C2
# ==============================================================================
# Este script se conecta por la red Tailscale a OCI-2, copia la base de datos
# SQLite de producción y la archiva localmente en el disco HDD (sdb).
# ==============================================================================

# Variables de entorno
OCI2_IP="100.121.103.19"
OCI2_USER="ubuntu"
OCI2_DB_PATH="/home/ubuntu/c2_panel/c2_db.sqlite"
LOCAL_KEY="/home/tomas2/WORKSPACE/LAB/llave_oci"

# Rutas locales
BOVEDA_DIR="/home/tomas2/WORKSPACE/LAB/historial_profundo/backups_db"
FECHA=$(date +"%Y-%m-%d_%H%M")
LOCAL_DB_COPY="${BOVEDA_DIR}/c2_db_${FECHA}.sqlite"

echo "========================================================================"
echo "🛡️ INICIANDO RESPALDO PROFUNDO - FECHA: $FECHA"
echo "========================================================================"

# Verificar que la llave SSH existe
if [ ! -f "$LOCAL_KEY" ]; then
    echo "❌ Error: No se encontró la llave SSH en $LOCAL_KEY"
    exit 1
fi

echo "🔄 Descargando base de datos desde OCI-2 ($OCI2_IP)..."

# Ejecutar la copia segura (SCP)
scp -i "$LOCAL_KEY" -o StrictHostKeyChecking=no "${OCI2_USER}@${OCI2_IP}:${OCI2_DB_PATH}" "$LOCAL_DB_COPY"

# Comprobar si la copia fue exitosa
if [ $? -eq 0 ]; then
    TAMANO=$(du -h "$LOCAL_DB_COPY" | awk '{print $1}')
    echo "✅ Respaldo exitoso! Tamaño: $TAMANO"
    echo "📂 Guardado en: $LOCAL_DB_COPY"
    
    # --------------------------------------------------------------------------
    # Rotación Automática (Mantener solo los últimos 30 días)
    # --------------------------------------------------------------------------
    echo "🧹 Limpiando respaldos más antiguos a 30 días..."
    find "$BOVEDA_DIR" -name "c2_db_*.sqlite" -type f -mtime +30 -delete
    echo "========================================================================"
else
    echo "❌ Falló el respaldo de la base de datos."
    echo "========================================================================"
    exit 1
fi
