#!/bin/bash
# ==============================================================================
# 🚀 DEPLOY WEB APP A OCI-2 (portaltarotmistico.com)
# ==============================================================================
set -e

OCI_IP="143.47.115.34"
OCI_USER="ubuntu"
SSH_KEY="/home/LAB/llave_oci"
REMOTE_BASE="/home/ubuntu/astrology_web"

chmod 600 "$SSH_KEY" 2>/dev/null || true

echo "========================================================================"
echo "🌐 DESPLEGANDO WEB TENEBRISTA & RELOJ ASTROLÓGICO A OCI-2 ($OCI_IP)"
echo "========================================================================"

# 1. Sincronizar web_app (templates, static, main.py) sin tocar la base de datos de usuarios
echo "📦 Sincronizando web_app/..."
rsync -avz --delete \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude="database" \
    --exclude="venv" \
    --exclude="__pycache__" \
    --exclude="*.log" \
    --exclude=".env" \
    /home/LAB/astrology_factory/web_app/ \
    ${OCI_USER}@${OCI_IP}:${REMOTE_BASE}/web_app/

# 2. Sincronizar astrology_engine y content_factory para soporte de cálculos matemáticos
echo "📦 Sincronizando astrology_engine/ y content_factory/..."
rsync -avz \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude="__pycache__" \
    --exclude="*.mp4" \
    --exclude="*.mp3" \
    --exclude="temp" \
    /home/LAB/astrology_factory/astrology_engine/ \
    ${OCI_USER}@${OCI_IP}:${REMOTE_BASE}/astrology_engine/

rsync -avz \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude="__pycache__" \
    --exclude="*.mp4" \
    --exclude="*.mp3" \
    --exclude="temp" \
    /home/LAB/astrology_factory/content_factory/ \
    ${OCI_USER}@${OCI_IP}:${REMOTE_BASE}/content_factory/

# 3. Reiniciar servicio FastAPI en OCI-2
echo "🔄 Reiniciando servicio astrology_web en OCI-2..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ${OCI_USER}@${OCI_IP} "sudo systemctl restart astrology_web && sudo systemctl is-active astrology_web"

# 4. Verificar salud en vivo
echo "🔍 Verificando endpoint en vivo..."
sleep 2
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no ${OCI_USER}@${OCI_IP} "curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/"

echo ""
echo "========================================================================"
echo "✅ DESPLIEGUE EXITOSO EN OCI-2"
echo "🔗 Visita: https://portaltarotmistico.com"
echo "========================================================================"
