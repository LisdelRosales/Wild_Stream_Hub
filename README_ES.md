# 🎬 Wild Stream Hub

**Panel de control web para gestionar transmisiones RTMP en vivo via FFmpeg**

Wild Stream Hub es una aplicación web local potente que permite a usuarios autenticados gestionar transmisiones RTMP en vivo usando FFmpeg con aceleración por hardware NVIDIA NVENC. Monitorea recursos del sistema en tiempo real, gestiona múltiples listas de reproducción de videos y transmite a plataformas como Twitch, YouTube o cualquier servicio compatible con RTMP.

## 🌟 Características

- 🔐 **Autenticación JWT** - Sistema de inicio de sesión seguro
- 🎥 **Gestión de Transmisión** - Iniciar/detener transmisión FFmpeg con NVENC
- 📊 **Monitoreo en Tiempo Real** - Actualizaciones en vivo vía WebSockets
- 💻 **Métricas del Sistema** - Monitoreo de CPU, GPU, RAM y disco
- 🎬 **Soporte de Listas** - Repetir múltiples archivos de video en bucle
- ⚡ **Aceleración por Hardware** - Soporte NVIDIA NVENC (RTX 2060)
- 🌍 **Listo para Acceso Remoto** - Funciona con Cloudflare Tunnel
- 🎨 **UI Moderna** - Panel de control limpio y responsivo

## 🧱 Arquitectura

```
Frontend (HTML/JS) → Backend FastAPI → Subproceso FFmpeg
                              ↓
                       Monitor WebSocket
```

## 📋 Requisitos Previos

### Requisitos del Sistema
- **OS**: Debian 13 (o cualquier distro Linux con soporte FFmpeg)
- **CPU**: Ryzen 5 3600 o mejor
- **GPU**: NVIDIA RTX 2060 o mejor (con soporte NVENC)
- **RAM**: 24 GB (mínimo 8GB recomendado)
- **Almacenamiento**: NVMe 500GB o espacio suficiente para videos

### Requisitos de Software
- Python 3.9 o superior
- FFmpeg con soporte NVENC
- Drivers NVIDIA (para aceleración GPU)
- pip (gestor de paquetes Python)

## 🚀 Instalación

### 1. Clonar o Descargar el Proyecto

```bash
cd /ruta/a/tus/proyectos
# Si tienes git:
git clone <url-repositorio> wild_stream_hub
# O simplemente extrae los archivos al directorio wild_stream_hub
```

### 2. Instalar FFmpeg con Soporte NVENC

```bash
# Actualizar lista de paquetes
sudo apt update

# Instalar FFmpeg (asegúrate que tenga soporte CUDA/NVENC)
sudo apt install ffmpeg -y

# Verificar soporte NVENC
ffmpeg -encoders | grep nvenc
```

Si NVENC no está disponible, puede que necesites compilar FFmpeg desde el código fuente con soporte CUDA. Ver [Guía FFmpeg NVENC](https://developer.nvidia.com/ffmpeg).

### 3. Instalar Drivers NVIDIA

```bash
# Verificar si los drivers NVIDIA están instalados
nvidia-smi

# Si no están instalados, instalar drivers NVIDIA
sudo apt install nvidia-driver -y
sudo reboot
```

### 4. Configurar Entorno Python

```bash
# Navegar al directorio backend
cd wild_stream_hub/backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

### Credenciales Predeterminadas
- **Usuario**: `admin`
- **Contraseña**: `admin123`

**⚠️ IMPORTANTE**: ¡Cambia estas credenciales en `backend/auth.py` antes de desplegar en producción!

### Cambiar Contraseña Predeterminada

Edita `backend/auth.py`:

```python
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("tu-nueva-contraseña"),  # Cambia esto
        "disabled": False,
    }
}
```

### Clave Secreta JWT

Edita `backend/auth.py`:

```python
SECRET_KEY = "tu-super-clave-secreta-aqui"  # ¡Cambia esto a una cadena aleatoria!
```

Generar una clave secreta segura:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🎮 Uso

### Iniciar el Servidor

```bash
# Navegar al directorio backend
cd wild_stream_hub/backend

# Activar entorno virtual
source venv/bin/activate

# Iniciar el servidor FastAPI
python main.py
```

El servidor iniciará en `http://0.0.0.0:8000`

Alternativa usando uvicorn directamente:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Acceder al Panel de Control

1. **Acceso Local**: Abre `wild_stream_hub/frontend/index.html` en tu navegador
2. **O servir via HTTP**: 
   ```bash
   cd wild_stream_hub/frontend
   python3 -m http.server 8080
   ```
   Luego abre `http://localhost:8080`

### Usar el Panel de Control

1. **Iniciar Sesión**: Usa las credenciales predeterminadas (admin/admin123)
2. **Configurar Transmisión**:
   - Ingresa tu URL RTMP (ej., `rtmp://live.twitch.tv/app`)
   - Ingresa tu clave de transmisión
   - Agrega rutas de archivos de video (una por línea)
3. **Iniciar Transmisión**: Haz clic en "▶️ Iniciar Transmisión"
4. **Monitorear**: Observa las métricas en tiempo real actualizándose cada segundo
5. **Detener Transmisión**: Haz clic en "⏹️ Detener Transmisión" cuando termines

## 📡 Endpoints de la API

### Autenticación
- `POST /login` - Autenticar y obtener token JWT

### Gestión de Transmisión
- `POST /stream/start` - Iniciar transmisión
- `POST /stream/stop` - Detener transmisión
- `GET /stream/status` - Obtener estado actual

### WebSocket
- `WS /ws/monitor` - Monitoreo en tiempo real (actualizaciones cada 1 segundo)

### Sistema
- `GET /health` - Verificación de salud
- `GET /docs` - Documentación interactiva de la API (Swagger UI)

## 🌐 Acceso Remoto con Cloudflare Tunnel

### Instalar Cloudflared

```bash
# Descargar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Instalar
sudo dpkg -i cloudflared-linux-amd64.deb

# Verificar instalación
cloudflared --version
```

### Configurar el Túnel

```bash
# Iniciar sesión en Cloudflare
cloudflared tunnel login

# Crear un túnel
cloudflared tunnel create wild-stream-hub

# Configurar el túnel
nano ~/.cloudflared/config.yml
```

Agrega esta configuración:
```yaml
tunnel: <tu-id-tunel>
credentials-file: /home/tunombreusuario/.cloudflared/<id-tunel>.json

ingress:
  - hostname: stream.tudominio.com
    service: http://localhost:8000
  - service: http_status:404
```

### Ejecutar el Túnel

```bash
# Ejecutar túnel
cloudflared tunnel run wild-stream-hub

# O instalar como servicio
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

¡Ahora accede a tu panel desde cualquier lugar via `https://stream.tudominio.com`!

## 🐳 Despliegue con Docker (Opcional)

### Crear Dockerfile

Crea `Dockerfile` en el directorio `backend`:

```dockerfile
FROM python:3.11-slim

# Instalar FFmpeg y dependencias runtime NVIDIA
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Crear docker-compose.yml

Crea `docker-compose.yml` en el directorio raíz:

```yaml
version: '3.8'

services:
  wild-stream-hub:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - /ruta/a/tus/videos:/videos
    environment:
      - PYTHONUNBUFFERED=1
    runtime: nvidia  # Para soporte GPU NVIDIA
    restart: unless-stopped
```

### Ejecutar con Docker

```bash
docker-compose up -d
```

## 📊 Monitoreo del Sistema

El panel muestra:

### Métricas de Transmisión
- Video actual siendo transmitido
- Bitrate (en vivo)
- Tiempo activo de transmisión
- Estado del proceso FFmpeg

### Recursos del Sistema
- **Uso de CPU** - Porcentaje en tiempo real
- **Uso de RAM** - GB Usados/Total y porcentaje
- **Uso de GPU** - Utilización, memoria y temperatura
- **Uso de Disco** - Espacio usado/libre

### Proceso FFmpeg
- Estado del proceso (Ejecutando/Detenido)
- Uso de CPU de FFmpeg
- Consumo de memoria

## 🔧 Solución de Problemas

### FFmpeg No Encontrado
```bash
# Verificar instalación de FFmpeg
which ffmpeg
ffmpeg -version

# Si no se encuentra, instalar
sudo apt install ffmpeg -y
```

### NVENC No Funciona
```bash
# Verificar drivers NVIDIA
nvidia-smi

# Verificar soporte NVENC
ffmpeg -encoders | grep nvenc

# Probar codificación NVENC
ffmpeg -hwaccel cuda -i test.mp4 -c:v h264_nvenc output.mp4
```

### Conexión WebSocket Fallida
- Asegúrate que el backend esté ejecutándose en el puerto 8000
- Verifica configuración del firewall: `sudo ufw allow 8000`
- Verifica configuración CORS en `main.py`

### Permiso Denegado para Archivos de Video
```bash
# Dar permisos de lectura a archivos de video
chmod +r /ruta/a/videos/*.mp4
```

### Transmisión No Inicia
1. Verifica que las rutas de archivos de video sean correctas y accesibles
2. Verifica que la URL RTMP y la clave de transmisión sean válidas
3. Prueba el comando FFmpeg manualmente:
   ```bash
   ffmpeg -re -i video.mp4 -c:v h264_nvenc -f flv rtmp://tu-url/clave-stream
   ```

## 📁 Estructura del Proyecto

```
wild_stream_hub/
├── backend/
│   ├── main.py              # Aplicación FastAPI
│   ├── ffmpeg_manager.py    # Gestor de subprocesos FFmpeg
│   ├── monitor.py           # Monitoreo del sistema
│   ├── auth.py              # Autenticación JWT
│   └── requirements.txt     # Dependencias Python
├── frontend/
│   ├── index.html           # HTML del panel
│   ├── script.js            # JavaScript del frontend
│   └── style.css            # Estilos del panel
└── README_ES.md             # Este archivo
```

## 🛡️ Consideraciones de Seguridad

### Para Uso en Producción:
1. **Cambiar credenciales predeterminadas** en `auth.py`
2. **Generar un SECRET_KEY seguro** para JWT
3. **Configurar CORS** apropiadamente (no usar `allow_origins=["*"]`)
4. **Usar HTTPS** (via Cloudflare Tunnel o proxy reverso)
5. **Implementar limitación de tasa** para endpoints API
6. **Usar una base de datos real** en lugar de fake_users_db
7. **Agregar autenticación WebSocket** (validar JWT en conexión)
8. **Configurar fail2ban** para prevenir ataques de fuerza bruta

## 🔄 Auto-Inicio al Arrancar (systemd)

Crea `/etc/systemd/system/wild-stream-hub.service`:

```ini
[Unit]
Description=Wild Stream Hub API
After=network.target

[Service]
Type=simple
User=tunombreusuario
WorkingDirectory=/ruta/a/wild_stream_hub/backend
Environment="PATH=/ruta/a/wild_stream_hub/backend/venv/bin"
ExecStart=/ruta/a/wild_stream_hub/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Habilitar e iniciar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable wild-stream-hub
sudo systemctl start wild-stream-hub
sudo systemctl status wild-stream-hub
```

## 📝 Mejoras Futuras

- [ ] Sistema de gestión de usuarios (múltiples usuarios)
- [ ] Almacenamiento persistente (base de datos para usuarios y configs)
- [ ] Programación de transmisiones (iniciar/detener en horarios específicos)
- [ ] Presets de calidad de transmisión (1080p, 720p, etc.)
- [ ] Transmisión multi-plataforma (transmitir a múltiples plataformas simultáneamente)
- [ ] Funcionalidad de grabación
- [ ] Filtros avanzados FFmpeg (overlays, transiciones)
- [ ] Monitoreo de salud de transmisión (frames perdidos, problemas de conexión)
- [ ] Notificaciones por Email/Discord para eventos de transmisión
- [ ] Mejoras responsivas para móviles

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Siéntete libre de enviar issues o pull requests.

## 📄 Licencia

Este proyecto es código abierto y está disponible para uso personal y comercial.

## 🙏 Agradecimientos

- **FastAPI** - Framework web moderno
- **FFmpeg** - Potencia de procesamiento de video
- **NVIDIA NVENC** - Aceleración por hardware
- **Cloudflare** - Solución de túnel seguro

## 📞 Soporte

Si encuentras problemas:
1. Verifica la sección de solución de problemas
2. Revisa los logs de la API: `tail -f /var/log/wild-stream-hub.log`
3. Prueba FFmpeg independientemente
4. Verifica que los recursos del sistema sean suficientes

---

**Construido con ❤️ para streamers por streamers**

*Wild Stream Hub v1.0.0*


