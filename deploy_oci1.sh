#!/bin/bash
# Script para actualizar los scripts monitores en OCI-1
# Ejecuta esto para subir las correcciones de falsos positivos al servidor de monitoreo.

cd /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB || exit 1

OCI1_IP="129.80.73.248"
LLAVE="llave_oci"

echo "============================================================"
echo "🚀 SUBIENDO ACTUALIZACIONES A OCI-1 ($OCI1_IP)"
echo "============================================================"

chmod 600 $LLAVE

# Subir explotador_automatico.py
scp -F /dev/null -o StrictHostKeyChecking=no -i $LLAVE api/explotador_automatico.py ubuntu@$OCI1_IP:/home/ubuntu/plataforma_operativa/monitores/

# Limpiar los resultados antiguos y falsos positivos de hoy para que el panel C2 no los muestre
ssh -F /dev/null -o StrictHostKeyChecking=no -i $LLAVE ubuntu@$OCI1_IP << 'EOF'
  cd /home/ubuntu/plataforma_operativa/resultados
  rm -f explotador_2026-07-17.json
  rm -f explotador_2026-07-21.json
EOF

echo "============================================================"
echo "✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO!"
echo "Los falsos positivos fueron borrados. El Panel C2 ya no mostrará basura."
echo "============================================================"
