# 🚀 Guía de Inicio Rápido

¡Pon Wild Stream Hub en funcionamiento en 5 minutos!

## 1️⃣ Verificación de Requisitos Previos

```bash
# Verificar Python (necesitas 3.9+)
python3 --version

# Verificar FFmpeg
ffmpeg -version

# Verificar GPU NVIDIA (opcional pero recomendado)
nvidia-smi
```

## 2️⃣ Instalación

### Opción A: Instalación Automatizada (Linux)

```bash
cd wild_stream_hub
chmod +x install.sh
./install.sh
```

### Opción B: Instalación Manual

```bash
# Instalar dependencias
cd wild_stream_hub/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3️⃣ Iniciar el Servidor

```bash
# Hacer ejecutable el script de inicio
chmod +x start.sh

# Ejecutar el servidor
./start.sh
```

O manualmente:
```bash
cd backend
source venv/bin/activate
python main.py
```

La API iniciará en `http://localhost:8000`

## 4️⃣ Abrir el Panel de Control

### Opción A: Archivo Directo

Abre `frontend/index.html` en tu navegador web

### Opción B: Servidor HTTP

```bash
cd frontend
python3 -m http.server 8080
```

Luego abre: `http://localhost:8080`

## 5️⃣ Iniciar Sesión

- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 6️⃣ Configura Tu Primera Transmisión

1. Ingresa tu URL RTMP (ej., `rtmp://live.twitch.tv/app`)
2. Ingresa tu clave de transmisión
3. Agrega rutas de archivos de video (una por línea):
   ```
   /home/usuario/videos/video1.mp4
   /home/usuario/videos/video2.mp4
   /home/usuario/videos/video3.mp4
   ```
4. Haz clic en "▶️ Iniciar Transmisión"

## 7️⃣ Monitorea Tu Transmisión

Observa el panel para:
- Bitrate en tiempo real
- Tiempo activo de transmisión
- Uso de CPU/GPU/RAM
- Estadísticas del proceso FFmpeg

## 🛠️ URLs RTMP Comunes

### Twitch
```
URL RTMP: rtmp://live.twitch.tv/app
Clave de Transmisión: Tu clave de transmisión de Twitch
```

### YouTube
```
URL RTMP: rtmp://a.rtmp.youtube.com/live2
Clave de Transmisión: Tu clave de transmisión de YouTube
```

### Facebook
```
URL RTMP: rtmps://live-api-s.facebook.com:443/rtmp/
Clave de Transmisión: Tu clave de transmisión de Facebook
```

## 🔧 Solución de Problemas

### El servidor no inicia
```bash
# Verificar si el puerto 8000 está en uso
sudo lsof -i :8000

# Matar el proceso si es necesario
sudo kill -9 <PID>
```

### No se puede conectar a WebSocket
- Asegúrate que el backend esté ejecutándose
- Verifica errores en la consola del navegador
- Verifica la URL de la API en `frontend/script.js`

### Errores de FFmpeg
```bash
# Probar FFmpeg manualmente
ffmpeg -re -i test.mp4 -c:v h264_nvenc -f flv rtmp://url-prueba

# Verificar soporte NVENC
ffmpeg -encoders | grep nvenc
```

### Videos no encontrados
- Usa rutas absolutas: `/home/usuario/videos/archivo.mp4`
- Verifica permisos de archivos: `chmod +r video.mp4`
- Verifica que los archivos existan: `ls -lh /ruta/al/video.mp4`

## 📞 ¿Necesitas Más Ayuda?

Consulta el [README_ES.md](README_ES.md) completo para:
- Instrucciones de instalación detalladas
- Configuración de Cloudflare Tunnel
- Despliegue con Docker
- Configuración de seguridad
- Configuración de servicio systemd

## ⚡ Consejos Profesionales

1. **Prueba FFmpeg primero**: Antes de transmitir, prueba FFmpeg con un video corto
2. **Monitorea recursos**: Mantén un ojo en el uso de CPU/GPU durante transmisiones
3. **Usa rutas absolutas**: Siempre usa rutas completas para archivos de video
4. **Verifica claves de transmisión**: Verifica dos veces tu URL RTMP y clave de transmisión
5. **Empieza pequeño**: Prueba con un video antes de agregar múltiples archivos

---

**¡Feliz Transmisión! 🎬**

## 📋 Lista de Verificación Rápida

Antes de tu primera transmisión:

- [ ] Python 3.9+ instalado
- [ ] FFmpeg instalado con soporte NVENC
- [ ] Drivers NVIDIA instalados
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Servidor ejecutándose en puerto 8000
- [ ] Panel abierto en el navegador
- [ ] Sesión iniciada exitosamente
- [ ] Archivos de video preparados
- [ ] URL RTMP y clave de transmisión listos

## 🎯 Próximos Pasos Después de la Primera Transmisión

1. **Cambiar Credenciales**: Edita `backend/auth.py` para cambiar usuario/contraseña
2. **Configurar Auto-Inicio**: Configura el servicio systemd para inicio automático
3. **Acceso Remoto**: Configura Cloudflare Tunnel para acceso desde cualquier lugar
4. **Optimizar Configuración**: Ajusta bitrate y calidad según tus necesidades
5. **Crear Listas**: Organiza tus videos en listas de reproducción

## 🌟 Características Principales

- ✅ Transmisión con un clic
- ✅ Monitoreo en tiempo real
- ✅ Aceleración por GPU (NVENC)
- ✅ Bucle automático de videos
- ✅ Panel web moderno
- ✅ Acceso remoto seguro

## 📱 Acceder Desde Otro Dispositivo

### En la Misma Red Local

1. Encuentra la IP de tu servidor:
   ```bash
   hostname -I
   ```

2. En otro dispositivo, abre:
   ```
   http://[IP-DEL-SERVIDOR]:8000/docs
   ```

3. Abre el panel:
   - Copia la carpeta `frontend` a tu dispositivo
   - O configura un servidor HTTP en el servidor

### Desde Internet (Cloudflare Tunnel)

Sigue la guía en [README_ES.md#acceso-remoto-con-cloudflare-tunnel](README_ES.md#-acceso-remoto-con-cloudflare-tunnel)

## 🎬 Ejemplo de Configuración Completa

```
URL RTMP: rtmp://live.twitch.tv/app
Clave de Transmisión: live_123456789_abcdefghijklmnop

Archivos de Video:
/home/usuario/streams/intro.mp4
/home/usuario/streams/contenido_principal.mp4
/home/usuario/streams/outro.mp4
```

Cuando inicies la transmisión:
1. Reproducirá `intro.mp4`
2. Luego `contenido_principal.mp4`
3. Luego `outro.mp4`
4. Repetirá desde el inicio automáticamente

## ⚙️ Configuraciones Recomendadas

### Para Twitch (1080p 60fps)
- Bitrate Video: 6000k
- Bitrate Audio: 160k
- Resolución: 1920x1080

### Para YouTube (1080p 60fps)
- Bitrate Video: 6000-9000k
- Bitrate Audio: 128-160k
- Resolución: 1920x1080

### Para Facebook (720p 30fps)
- Bitrate Video: 4000k
- Bitrate Audio: 128k
- Resolución: 1280x720

*Nota: Estas configuraciones se pueden ajustar en `backend/ffmpeg_manager.py`*

---

**¿Listo para transmitir? ¡Adelante! 🚀**


