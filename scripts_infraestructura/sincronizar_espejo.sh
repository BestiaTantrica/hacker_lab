#!/bin/bash
# Script para sincronizar (hacer espejo) del servidor OCI-1 al entorno local.
# Ejecuta esto en TU terminal (no la mía) para que yo pueda ver los archivos del servidor sin bloqueos de red.

DIR_LOCAL="/home/tomas2/WORKSPACE/LAB/espejo_oci1"
SERVER_IP="129.80.73.248"
SSH_KEY="$HOME/.ssh/id_rsa"
DIR_REMOTO="/home/ubuntu/plataforma_operativa/"

echo "============================================================"
echo "🔄 Sincronizando espejo de OCI-1 a entorno local..."
echo "============================================================"

# Crear la carpeta espejo si no existe
mkdir -p "$DIR_LOCAL"

# Usar rsync para traer todos los archivos, logs y resultados (excluyendo el entorno virtual)
rsync -avz --exclude 'venv' --exclude '__pycache__' -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" ubuntu@$SERVER_IP:$DIR_REMOTO $DIR_LOCAL/

echo "============================================================"
echo "✅ Sincronización completa. Ahora Pegaso puede leer los archivos."
echo "============================================================"
