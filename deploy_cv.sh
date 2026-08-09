#!/bin/bash

# ==============================================================================
# 🚀 SMART CV DEPLOYER
# ==============================================================================
# Este script toma el CV local (NUEVO_CV_TOMAS.html), le inyecta las variables
# de Jinja2 para la telemetría en vivo, y lo sube al servidor C2 (OCI-2).
# ==============================================================================

# Variables de entorno
OCI2_IP="143.47.115.34" # IP Pública o Tailscale IP, usamos la pública del túnel SSH
OCI2_USER="ubuntu"
LOCAL_KEY="/home/tomas2/WORKSPACE/LAB/llave_oci"
CV_LOCAL="/home/tomas2/WORKSPACE/LAB/NUEVO_CV_TOMAS.html"
TMP_HTML="/tmp/portfolio_template.html"
REMOTE_PATH="/home/ubuntu/c2_panel/templates/portfolio.html"

echo "========================================================================"
echo "🌐 INICIANDO DESPLIEGUE DEL PORTAFOLIO INTELIGENTE (SMART CV)"
echo "========================================================================"

# Verificar que la llave SSH existe
if [ ! -f "$LOCAL_KEY" ]; then
    echo "❌ Error: No se encontró la llave SSH en $LOCAL_KEY"
    exit 1
fi

if [ ! -f "$CV_LOCAL" ]; then
    echo "❌ Error: No se encontró el CV local en $CV_LOCAL"
    exit 1
fi

echo "⚙️ Preparando plantilla Jinja2..."

# 1. Copiar el CV a temporal
cp "$CV_LOCAL" "$TMP_HTML"

# 2. Inyectar variables Jinja2 reemplazando los placeholders
# Reemplazamos todo el contenido entre los tags <!-- JINJA_DELTAS --> y su cierre
sed -i -E 's/<!-- JINJA_DELTAS -->.*<!-- \/JINJA_DELTAS -->/{{ "{:,}".format(total_deltas) }}/g' "$TMP_HTML"
sed -i -E 's/<!-- JINJA_FINDINGS -->.*<!-- \/JINJA_FINDINGS -->/{{ total_findings }}/g' "$TMP_HTML"

# Cambiar "Offline" o "Conectando" a "Online" o algo dinámico si quisieras, pero los datos reales lo reemplazan.

echo "🚀 Subiendo a OCI-2 ($OCI2_IP)..."

# 3. Subir vía SCP
scp -i "$LOCAL_KEY" -o StrictHostKeyChecking=no "$TMP_HTML" "${OCI2_USER}@${OCI2_IP}:${REMOTE_PATH}"

if [ $? -eq 0 ]; then
    echo "✅ Despliegue exitoso!"
    echo "🔗 Tu CV inteligente ya está vivo en la red C2."
else
    echo "❌ Falló el despliegue."
fi

# Limpieza
rm -f "$TMP_HTML"
echo "========================================================================"
