#!/bin/bash
set -e

# ==============================================================================
# 🚀 DEPLOY TIENDA ONLINE A OCI-1 (129.80.73.248)
# ==============================================================================

OCI1_IP="129.80.73.248"
OCI1_USER="ubuntu"
LLAVE="/home/LAB/llave_oci"
LOCAL_DIR="/home/LAB/tienda_online"
REMOTE_DIR="/home/ubuntu/tienda_online"

echo "============================================================"
echo "🚀 1. Sincronizando archivos hacia OCI-1 ($OCI1_IP)..."
echo "============================================================"

chmod 600 "$LLAVE"

rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude 'data/*.db' \
  --exclude 'whatsapp_bridge/node_modules' --exclude 'whatsapp_bridge/auth_info' \
  -e "ssh -i $LLAVE -o StrictHostKeyChecking=no" \
  "$LOCAL_DIR/" "${OCI1_USER}@${OCI1_IP}:${REMOTE_DIR}/"

echo "============================================================"
echo "⚙️ 2. Configurando entorno virtual y dependencias en OCI-1..."
echo "============================================================"

ssh -i "$LLAVE" -o StrictHostKeyChecking=no "${OCI1_USER}@${OCI1_IP}" << 'EOF'
set -e

cd /home/ubuntu/tienda_online

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual Python..."
    python3 -m venv venv
fi

echo "Instalando paquetes en venv..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Inicializar BD con datos demo si no existe
./venv/bin/python database.py

# Dependencias de WhatsApp Bot Bridge
if [ -d "whatsapp_bridge" ]; then
    cd whatsapp_bridge
    if [ ! -d "node_modules" ]; then
        echo "Instalando dependencias de WhatsApp Bot..."
        npm install --production
    fi
    cd ..
fi

# 3. Configurar Servicio Systemd para la Tienda
sudo tee /etc/systemd/system/tienda.service > /dev/null << 'SERVICE'
[Unit]
Description=Servicio Web Tienda Online E-commerce
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/tienda_online
ExecStart=/home/ubuntu/tienda_online/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# 3.1 Configurar Servicio Systemd para WhatsApp Bot
sudo tee /etc/systemd/system/whatsapp-bot.service > /dev/null << 'SERVICE'
[Unit]
Description=WhatsApp Bot 24/7 Bridge para EcoMarvex
After=network.target tienda.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/tienda_online/whatsapp_bridge
ExecStart=/usr/bin/node index.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable --now tienda
sudo systemctl restart tienda
sudo systemctl enable --now whatsapp-bot
sudo systemctl restart whatsapp-bot

# 4. Configurar Nginx Reverse Proxy (con soporte SSL LetsEncrypt si existe)
if sudo test -d "/etc/letsencrypt/live/ecomarvex.com"; then
sudo tee /etc/nginx/sites-available/tienda > /dev/null << 'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name ecomarvex.com www.ecomarvex.com _;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    server_name ecomarvex.com www.ecomarvex.com;

    ssl_certificate /etc/letsencrypt/live/ecomarvex.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ecomarvex.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX
else
sudo tee /etc/nginx/sites-available/tienda > /dev/null << 'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX
fi

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/tienda /etc/nginx/sites-enabled/tienda
sudo nginx -t
sudo systemctl reload nginx

echo "✅ Verificando estado del servicio:"
sudo systemctl is-active tienda
sudo systemctl is-active nginx
EOF

echo "============================================================"
echo "🎉 ¡DESPLIEGUE EXITOSO EN OCI-1!"
echo "🌐 Tienda disponible en: http://$OCI1_IP"
echo "🛠️ Panel Administrador: http://$OCI1_IP/admin (PIN: 1234)"
echo "============================================================"
