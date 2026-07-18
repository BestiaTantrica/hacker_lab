#!/bin/bash

# Este script usa la llave_oci local para conectarse a OCI-2, subir el panel y dejarlo corriendo como servicio web.

cd /home/tomas2/WORKSPACE/tomas2/WORKSPACE/LAB || exit 1

OCI2_IP="143.47.115.34"
LLAVE="llave_oci"

echo "============================================================"
echo "🚀 INICIANDO DESPLIEGUE DEL PANEL C2 EN OCI-2 ($OCI2_IP)"
echo "============================================================"

# Arreglar permisos de la llave local si es necesario
chmod 600 $LLAVE

echo "[1/3] Subiendo archivos del panel C2 al servidor..."
scp -F /dev/null -o StrictHostKeyChecking=no -i $LLAVE -r c2_panel ubuntu@$OCI2_IP:/home/ubuntu/

echo "[2/3] Instalando dependencias y configurando el servidor..."
ssh -F /dev/null -o StrictHostKeyChecking=no -i $LLAVE ubuntu@$OCI2_IP << 'EOF'
  # Actualizar paquetes y dependencias básicas
  sudo apt-get update -y -qq
  sudo apt-get install -y python3-pip python3-venv -qq

  # Crear entorno virtual e instalar requirements
  cd /home/ubuntu/c2_panel
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt --quiet

  # Crear un demonio de Systemd para que el panel corra siempre en background
  cat << 'SYSTEMD' | sudo tee /etc/systemd/system/c2panel.service > /dev/null
[Unit]
Description=C2 HackerLab Panel
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/c2_panel
Environment="PATH=/home/ubuntu/c2_panel/venv/bin"
ExecStart=/home/ubuntu/c2_panel/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
SYSTEMD

  # Abrir puerto 8000 en el firewall (OCI usa iptables por defecto)
  sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
  sudo netfilter-persistent save > /dev/null 2>&1

  # Iniciar el servicio
  sudo systemctl daemon-reload
  sudo systemctl enable c2panel --now
  sudo systemctl restart c2panel
EOF

echo "============================================================"
echo "✅ DESPLIEGUE COMPLETADO CON ÉXITO!"
echo "🌐 Ya puedes acceder a tu panel en: http://$OCI2_IP:8000"
echo "============================================================"
