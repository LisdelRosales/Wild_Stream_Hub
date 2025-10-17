# 🚀 Guía de Instalación - Wild Stream Hub

## Guía simple y directa para Debian 13

---

## 📋 Requisitos

- Servidor Debian 13
- CPU: Ryzen 5 3600 (o similar)
- GPU: NVIDIA RTX 2060 con drivers instalados
- RAM: 24 GB
- Python 3.9+
- FFmpeg con soporte NVENC
- Cuenta gratuita en Cloudflare

---

## 🎯 PASO 1: Descargar el Proyecto

```bash
# Ir a tu directorio de trabajo
cd /mnt/main-storage

# Opción A: Descargar con git
git clone <url-del-repo> wild_stream_hub

# Opción B: Subir manualmente (SCP, WinSCP, etc.)
# O Opción C: Descomprimir si ya lo tienes
cd wild_stream_hub
```

---

## 🔧 PASO 2: Instalar Dependencias del Sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install python3 python3-pip python3-venv -y

# Instalar FFmpeg
sudo apt install ffmpeg -y

# Verificar NVENC
ffmpeg -encoders | grep nvenc

# Deberías ver:
# V..... h264_nvenc
# V..... hevc_nvenc
```

---

## 🎮 PASO 3: Verificar Drivers NVIDIA

```bash
# Verificar drivers
nvidia-smi

# Si no están instalados:
sudo apt install nvidia-driver nvidia-cuda-toolkit -y
sudo reboot

# Después del reinicio, verificar de nuevo
nvidia-smi
```

---

## 🐍 PASO 4: Instalar Dependencias Python

```bash
cd /mnt/main-storage/wild_stream_hub/backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
python3 -c "import fastapi, uvicorn, pydantic; print('✅ Todo OK!')"
```

---

## 🔐 PASO 5: Configurar Seguridad

### 5.1 Cambiar Contraseña Admin

```bash
nano backend/auth.py
```

Busca y cambia:
```python
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("TU_NUEVA_CONTRASEÑA_AQUI"),
        "disabled": False,
    }
}
```

### 5.2 Generar y Configurar JWT Secret

```bash
# Generar clave
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar el resultado y editar:
```bash
nano backend/auth.py
```

Cambiar:
```python
SECRET_KEY = "PEGAR_TU_CLAVE_AQUI"
```

---

## 📁 PASO 6: Crear Directorio para Stream Lists

```bash
# Crear directorio
sudo mkdir -p /mnt/main-storage/stream-lists

# Dar permisos
sudo chown -R $USER:$USER /mnt/main-storage/stream-lists

# Verificar
ls -la /mnt/main-storage/stream-lists
```

---

## ▶️ PASO 7: Iniciar el Servidor

```bash
cd /mnt/main-storage/wild_stream_hub/backend
source venv/bin/activate
python main.py
```

Deberías ver:
```
🚀 Wild_Stream_Hub API starting...
📡 WebSocket monitoring available at /ws/monitor
📚 API documentation available at /docs
```

**Mantén este terminal abierto** (o usa screen/tmux)

---

## 🌐 PASO 8: Configurar Cloudflare Tunnel

### 8.1 Instalar Cloudflared

```bash
# En una nueva terminal SSH
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
cloudflared --version
```

### 8.2 Autenticar

```bash
cloudflared tunnel login
```

Esto te dará una URL. **Cópiala y ábrela en tu navegador**, autoriza el acceso.

### 8.3 Crear Túnel

```bash
cloudflared tunnel create wild-stream
```

**Anota el ID del túnel** que aparece (algo como: `abc123-def456-...`)

### 8.4 Configurar Túnel

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Agregar (reemplaza `TU_TUNNEL_ID` con tu ID real):
```yaml
tunnel: TU_TUNNEL_ID
credentials-file: /home/TUNOMBREDEUSUARIO/.cloudflared/TU_TUNNEL_ID.json

ingress:
  - service: http://localhost:8000
```

### 8.5 Iniciar Túnel (Temporal para Probar)

```bash
cloudflared tunnel run wild-stream
```

Cloudflare te dará una URL como:
```
https://wild-stream-abc123.trycloudflare.com
```

**¡Guarda esta URL!** Es tu acceso remoto.

### 8.6 Configurar como Servicio Permanente

```bash
# Copiar configuración
sudo mkdir -p /etc/cloudflared
sudo cp ~/.cloudflared/config.yml /etc/cloudflared/
sudo cp ~/.cloudflared/*.json /etc/cloudflared/

# Instalar servicio
sudo cloudflared service install

# Iniciar
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Verificar
sudo systemctl status cloudflared
```

---

## 🎉 PASO 9: Usar la WebUI

### 9.1 Acceder al Panel

Abre en tu navegador:
- **Remoto**: `https://wild-stream-abc123.trycloudflare.com`
- **Local**: `http://localhost:8000` (si estás en el servidor)

### 9.2 Iniciar Sesión

- Usuario: `admin`
- Contraseña: `TU_NUEVA_CONTRASEÑA`

### 9.3 Crear Stream List

1. En la sección **"📁 Stream Lists"**
2. Escribir nombre: `intro-videos`
3. Click **"📁 Create"**

### 9.4 Subir Videos (¡DESDE LA WEBUI!)

1. **Seleccionar la lista** en el dropdown
2. Click **"📤 Choose Files to Upload"**
3. Seleccionar tus archivos de video (.mp4, .mkv, etc.)
4. **¡Los videos se suben automáticamente!**
5. Verás la lista de videos actualizada

### 9.5 Iniciar Transmisión

1. **Configurar stream**:
   - RTMP URL: `rtmp://live.twitch.tv/app`
   - Stream Key: [Tu clave de Twitch]
   - Stream List: Seleccionar `intro-videos`

2. Click **"▶️ Start Stream"**

3. **Monitorear en tiempo real**:
   - Bitrate
   - Tiempo activo
   - CPU/GPU/RAM
   - Video actual

---

## 🔄 PASO 10: Auto-Inicio (Opcional pero Recomendado)

### 10.1 Crear Servicio systemd

```bash
sudo nano /etc/systemd/system/wild-stream-hub.service
```

Agregar:
```ini
[Unit]
Description=Wild Stream Hub API
After=network.target

[Service]
Type=simple
User=TU_USUARIO
WorkingDirectory=/mnt/main-storage/wild_stream_hub/backend
Environment="PATH=/mnt/main-storage/wild_stream_hub/backend/venv/bin"
ExecStart=/mnt/main-storage/wild_stream_hub/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 10.2 Habilitar y Iniciar

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar auto-inicio
sudo systemctl enable wild-stream-hub

# Iniciar servicio
sudo systemctl start wild-stream-hub

# Verificar estado
sudo systemctl status wild-stream-hub
```

### 10.3 Comandos Útiles

```bash
# Ver logs
sudo journalctl -u wild-stream-hub -f

# Reiniciar
sudo systemctl restart wild-stream-hub

# Detener
sudo systemctl stop wild-stream-hub
```

---

## ✅ Checklist Final

- [ ] Servidor Debian actualizado
- [ ] Drivers NVIDIA funcionando (nvidia-smi)
- [ ] FFmpeg con NVENC instalado
- [ ] Dependencias Python instaladas
- [ ] Contraseña admin cambiada
- [ ] Clave JWT generada y configurada
- [ ] Directorio stream-lists creado
- [ ] Servidor ejecutándose correctamente
- [ ] Cloudflare Tunnel configurado y funcionando
- [ ] Puedes acceder remotamente al panel
- [ ] Creaste tu primera stream list
- [ ] Subiste videos desde la WebUI
- [ ] Iniciaste una transmisión de prueba exitosa
- [ ] Servicios configurados para auto-inicio

---

## 🎯 Flujo de Trabajo Diario

1. **Acceder**: `https://tu-tunel.trycloudflare.com`
2. **Iniciar sesión**
3. **Crear/gestionar listas** desde la WebUI
4. **Subir videos** con el botón "📤 Choose Files"
5. **Seleccionar lista** para transmitir
6. **Configurar RTMP** (Twitch, YouTube, etc.)
7. **Iniciar transmisión** 24/7
8. **Monitorear** en tiempo real

---

## 🆘 Solución de Problemas

### Servidor no inicia
```bash
cd /mnt/main-storage/wild_stream_hub/backend
source venv/bin/activate
python main.py
# Ver errores en la consola
```

### NVENC no funciona
```bash
nvidia-smi  # Verificar GPU
ffmpeg -encoders | grep nvenc  # Verificar FFmpeg
```

### No puedo acceder remotamente
```bash
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -f
```

### No puedo subir videos
```bash
# Verificar permisos
ls -la /mnt/main-storage/stream-lists/
sudo chown -R $USER:$USER /mnt/main-storage/stream-lists/
```

---

## 📚 URLs Útiles

- **Panel Web**: `https://tu-tunel.trycloudflare.com`
- **API Docs**: `https://tu-tunel.trycloudflare.com/docs`
- **Health Check**: `https://tu-tunel.trycloudflare.com/health`
- **Twitch Dashboard**: https://dashboard.twitch.tv/settings/stream
- **YouTube Studio**: https://studio.youtube.com/

---

## 🎬 ¡Listo para Transmitir!

Ahora tienes un sistema profesional de transmisión 24/7 con:
- ✅ Gestión web de listas de videos
- ✅ Subida de archivos desde cualquier lugar
- ✅ Acceso remoto seguro vía Cloudflare
- ✅ Monitoreo en tiempo real
- ✅ Auto-inicio y reinicio automático

**¡Feliz Transmisión! 🚀**
