#!/bin/bash

# Script de instalación y configuración automática para Wild_Stream_Hub
# Crea carpetas, pide token, configura systemd y arranca el servicio

set -e

# 1. Solicitar datos al usuario
read -p "Ruta base para almacenamiento [/mnt/main-storage/Wild_Stream_Hub]: " BASE_PATH
BASE_PATH=${BASE_PATH:-/mnt/main-storage/Wild_Stream_Hub}

read -p "Usuario Linux para ejecutar el servicio [$(whoami)]: " SERVICE_USER
SERVICE_USER=${SERVICE_USER:-$(whoami)}

read -p "Token API para autenticación (elige uno fuerte): " API_TOKEN
if [ -z "$API_TOKEN" ]; then
  echo "Debes ingresar un token. Abortando."
  exit 1
fi

# 2. Crear carpetas necesarias
sudo mkdir -p "$BASE_PATH"/{streams,uploads,logs,config,static}

# 3. Copiar archivos del repo si es necesario
# (asume que el repo ya está clonado en $BASE_PATH o que se ejecuta desde la raíz del repo)

# 4. Crear entorno virtual si no existe
if [ ! -d "$BASE_PATH/venv" ]; then
  python3 -m venv "$BASE_PATH/venv"
fi
source "$BASE_PATH/venv/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

deactivate

# 5. Crear archivo systemd
SERVICE_FILE=/etc/systemd/system/wildstream.service
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Wild Stream Hub
After=network.target

[Service]
User=$SERVICE_USER
WorkingDirectory=$BASE_PATH
ExecStart=$BASE_PATH/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
Environment="WILDSTREAM_BASE_PATH=$BASE_PATH"
Environment="WILDSTREAM_API_TOKEN=$API_TOKEN"

[Install]
WantedBy=multi-user.target
EOF

# 6. Recargar systemd y arrancar servicio
sudo systemctl daemon-reload
sudo systemctl enable --now wildstream.service

# 7. Mostrar estado y URL real
if systemctl is-active --quiet wildstream; then
  # Detectar IP local (la primera no-loopback IPv4)
  LOCAL_IP=$(hostname -I | awk '{print $1}')
  PORT=8000
  # Verificar si el puerto está escuchando
  if command -v nc >/dev/null 2>&1 && nc -z "$LOCAL_IP" $PORT; then
    echo -e "\n✅ Wild_Stream_Hub instalado y corriendo en $BASE_PATH"
    echo "Puedes acceder al backend en: http://$LOCAL_IP:$PORT"
    echo "Recuerda usar el token configurado en el header X-API-TOKEN para las peticiones."
  else
    echo -e "\n⚠️ El servicio está activo pero el puerto $PORT no responde en $LOCAL_IP."
    echo "Verifica logs y firewall."
  fi
else
  echo -e "\n❌ Wild_Stream_Hub NO se está ejecutando. Revisa los logs con:"
  echo "    sudo journalctl -u wildstream -e"
  echo "Y el estado con:"
  echo "    sudo systemctl status wildstream"
fi
