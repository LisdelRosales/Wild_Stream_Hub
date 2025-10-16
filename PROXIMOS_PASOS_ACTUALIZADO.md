# 🎯 Próximos Pasos - Wild Stream Hub (ACTUALIZADO)

## 🚀 Guía Completa de Configuración y Despliegue con Stream Lists

Esta guía te llevará desde la instalación hasta tener tu sistema transmitiendo 24/7 con gestión de listas de videos y acceso remoto via Cloudflare Tunnel.

---

## 📍 PASO 1: Preparación Inicial (Windows - Tu PC Actual)

### 1.1 Verificar que Todo Funcione

Ya que estás en Windows, primero probaremos el sistema localmente:

```powershell
# Navegar al proyecto
cd C:\Users\Lisdel\Videos\prueba\wild_stream_hub\backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python main.py
```

### 1.2 Probar el Panel

1. Abre el archivo `C:\Users\Lisdel\Videos\prueba\wild_stream_hub\frontend\index.html` en tu navegador
2. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. **¡NUEVO!** Verifica que veas la nueva sección **"📁 Stream Lists"**
4. Prueba crear una lista de prueba
5. Verifica que las métricas se actualicen

---

## 📍 PASO 2: Transferir a Tu Servidor Debian 13

### 2.1 Preparar Archivos para Transferir

Desde Windows, comprime el proyecto:

```powershell
# Ir al directorio padre
cd C:\Users\Lisdel\Videos\prueba

# Crear un archivo ZIP (usando 7-Zip, WinRAR, o PowerShell)
Compress-Archive -Path wild_stream_hub -DestinationPath wild_stream_hub.zip
```

### 2.2 Transferir a Debian

**Opción A: Usar WinSCP** (Recomendado - interfaz gráfica)
1. Descarga WinSCP: https://winscp.net/
2. Conecta a tu servidor Debian
3. Arrastra la carpeta `wild_stream_hub` al servidor

**Opción B: Usar SCP (línea de comandos)**
```powershell
scp wild_stream_hub.zip wild-blast@ip-servidor-debian:/home/wild-blast/
```

### 2.3 Descomprimir en Debian

```bash
# Conectar por SSH al servidor
ssh wild-blast@ip-servidor-debian

# Descomprimir
cd ~
unzip wild_stream_hub.zip
cd wild_stream_hub
```

---

## 📍 PASO 3: Instalar en Debian 13

### 3.1 Actualizar Sistema

```bash
# Actualizar paquetes
sudo apt update
sudo apt upgrade -y
```

### 3.2 Instalar Dependencias del Sistema

```bash
# Instalar Python y herramientas
sudo apt install python3 python3-pip python3-venv -y

# Instalar FFmpeg
sudo apt install ffmpeg -y

# Verificar instalación
ffmpeg -version
python3 --version
```

### 3.3 Instalar Drivers NVIDIA (para tu RTX 2060)

```bash
# Agregar repositorio non-free
sudo nano /etc/apt/sources.list
# Agrega "non-free non-free-firmware" a cada línea

# Actualizar
sudo apt update

# Instalar drivers NVIDIA
sudo apt install nvidia-driver nvidia-cuda-toolkit -y

# Reiniciar
sudo reboot

# Después del reinicio, verificar
nvidia-smi
```

### 3.4 Verificar Soporte NVENC

```bash
# Verificar que FFmpeg tenga soporte NVENC
ffmpeg -encoders | grep nvenc
```

Deberías ver:
```
V..... h264_nvenc
V..... hevc_nvenc
```

### 3.5 Ejecutar Instalación Automatizada

```bash
cd ~/wild_stream_hub

# Hacer ejecutables los scripts
chmod +x *.sh

# Ejecutar instalación
./install.sh
```

Este script:
- Creará el entorno virtual Python
- Instalará todas las dependencias (incluyendo aiofiles)
- Verificará FFmpeg y NVIDIA

---

## 📍 PASO 4: Configurar Seguridad

### 4.1 Cambiar Contraseña de Admin

```bash
nano ~/wild_stream_hub/backend/auth.py
```

Busca esta sección:
```python
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),  # CAMBIAR AQUÍ
        "disabled": False,
    }
}
```

Cambia `"admin123"` por tu contraseña segura, por ejemplo:
```python
"hashed_password": pwd_context.hash("MiContraseñaSegura2025!"),
```

### 4.2 Generar Clave Secreta JWT

```bash
# Generar una clave aleatoria
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el resultado y edita el archivo:
```bash
nano ~/wild_stream_hub/backend/auth.py
```

Reemplaza:
```python
SECRET_KEY = "your-secret-key-here-change-in-production"
```

Por:
```python
SECRET_KEY = "TU_CLAVE_ALEATORIA_AQUI"
```

---

## 📍 PASO 5: Configurar Stream Lists

### 5.1 Crear Directorio para Stream Lists

```bash
# Crear directorio base para stream lists
sudo mkdir -p /mnt/main-storage/stream-lists

# Dar permisos al usuario
sudo chown -R wild-blast:wild-blast /mnt/main-storage/stream-lists

# Verificar permisos
ls -la /mnt/main-storage/stream-lists
```

### 5.2 Crear Primera Stream List de Prueba

```bash
# Crear una lista de ejemplo
mkdir -p /mnt/main-storage/stream-lists/intro-videos
mkdir -p /mnt/main-storage/stream-lists/main-content
mkdir -p /mnt/main-storage/stream-lists/outro-videos

# Crear archivos de prueba (opcional)
echo "Este es un video de prueba" > /mnt/main-storage/stream-lists/intro-videos/test.txt
```

### 5.3 Subir Videos (Método Manual)

**Opción A: Usar WinSCP**
1. Conecta con WinSCP al servidor
2. Navega a `/mnt/main-storage/stream-lists/intro-videos/`
3. Arrastra tus archivos de video (.mp4, .mkv, etc.)

**Opción B: Usar SCP desde Windows**
```powershell
# Subir un video
scp C:\ruta\a\tu\video.mp4 wild-blast@ip-servidor:/mnt/main-storage/stream-lists/intro-videos/

# Subir múltiples videos
scp C:\ruta\a\videos\*.mp4 wild-blast@ip-servidor:/mnt/main-storage/stream-lists/main-content/
```

### 5.4 Verificar Videos

```bash
# Listar videos en las listas
ls -la /mnt/main-storage/stream-lists/*/

# Verificar permisos
chmod +r /mnt/main-storage/stream-lists/*/*.mp4
```

---

## 📍 PASO 6: Primera Prueba de Transmisión

### 6.1 Iniciar el Servidor

```bash
cd ~/wild_stream_hub
./start.sh
```

Deberías ver:
```
🚀 Wild_Stream_Hub API starting...
📡 WebSocket monitoring available at /ws/monitor
📚 API documentation available at /docs
🔐 Default credentials: admin / admin123
```

### 6.2 Acceder al Panel (Temporalmente)

**Opción A: Túnel SSH (más fácil para pruebas)**

Desde Windows:
```powershell
ssh -L 8000:localhost:8000 wild-blast@ip-servidor-debian
```

Luego abre en tu navegador Windows: `http://localhost:8000/docs`

**Opción B: Abrir puerto en firewall (temporal)**

En el servidor Debian:
```bash
sudo ufw allow 8000
```

Luego desde Windows: `http://ip-servidor-debian:8000/docs`

### 6.3 Probar la Nueva Funcionalidad de Stream Lists

1. **Abrir el panel**: `http://localhost:8000` o `http://ip-servidor:8000`
2. **Iniciar sesión**: admin / tu-nueva-contraseña
3. **Crear una lista**: En la sección "📁 Stream Lists", crear "intro-videos"
4. **Ver la lista**: Debería aparecer en el dropdown
5. **Seleccionar lista**: Elegir "intro-videos" para transmisión
6. **Ver videos**: Si subiste videos, deberían aparecer en la lista

### 6.4 Configurar Tu Primera Transmisión

1. **Obtener tu clave de transmisión de Twitch:**
   - Ve a https://dashboard.twitch.tv/settings/stream
   - Copia tu "Clave de transmisión principal"

2. **En el panel:**
   - URL RTMP: `rtmp://live.twitch.tv/app`
   - Clave de Transmisión: [tu clave de Twitch]
   - Stream List: Seleccionar "intro-videos"

3. **Iniciar transmisión** y verifica en Twitch que esté transmitiendo

### 6.5 Monitorear

- Observa el bitrate en tiempo real
- Verifica el uso de GPU (debería estar entre 30-50%)
- Verifica el uso de CPU (debería ser bajo, 10-30%)

---

## 📍 PASO 7: Configurar Auto-Inicio (systemd)

Para que el servidor inicie automáticamente al arrancar:

### 7.1 Configurar Servicio

```bash
cd ~/wild_stream_hub

# Editar plantilla del servicio
nano wild-stream-hub.service
```

Reemplaza `YOUR_USERNAME` y las rutas:
```ini
User=wild-blast
WorkingDirectory=/home/wild-blast/wild_stream_hub/backend
Environment="PATH=/home/wild-blast/wild_stream_hub/backend/venv/bin"
ExecStart=/home/wild-blast/wild_stream_hub/backend/venv/bin/python main.py
```

### 7.2 Instalar Servicio

```bash
# Copiar a systemd
sudo cp wild-stream-hub.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar para inicio automático
sudo systemctl enable wild-stream-hub

# Iniciar servicio
sudo systemctl start wild-stream-hub

# Verificar estado
sudo systemctl status wild-stream-hub
```

### 7.3 Comandos Útiles del Servicio

```bash
# Iniciar
sudo systemctl start wild-stream-hub

# Detener
sudo systemctl stop wild-stream-hub

# Reiniciar
sudo systemctl restart wild-stream-hub

# Ver logs
sudo journalctl -u wild-stream-hub -f

# Ver estado
sudo systemctl status wild-stream-hub
```

---

## 📍 PASO 8: Configurar Cloudflare Tunnel (Acceso Remoto GRATUITO)

### 8.1 Crear Cuenta en Cloudflare (Ya hecho ✅)

1. ✅ Ya tienes cuenta en https://dash.cloudflare.com/
2. ✅ Cuenta gratuita (no necesitas dominio)

### 8.2 Instalar Cloudflared

```bash
# Descargar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Instalar
sudo dpkg -i cloudflared-linux-amd64.deb

# Verificar
cloudflared --version
```

### 8.3 Autenticar con Cloudflare

```bash
# Esto abrirá un navegador para autenticar
cloudflared tunnel login
```

**Si estás en SSH sin interfaz gráfica:**
1. El comando te dará una URL como: `https://dash.cloudflare.com/argotunnel/...`
2. Copia esa URL y ábrela en tu PC Windows
3. Autoriza el acceso
4. Vuelve al terminal y presiona Enter

### 8.4 Crear Túnel

```bash
# Crear túnel llamado "wild-stream"
cloudflared tunnel create wild-stream

# Ver el ID del túnel (guárdalo)
cloudflared tunnel list
```

**Anota el ID del túnel** (algo como: `12345678-1234-1234-1234-123456789abc`)

### 8.5 Configurar Túnel

```bash
# Crear archivo de configuración
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Agrega (reemplaza TU-TUNNEL-ID con el ID real):
```yaml
tunnel: TU-TUNNEL-ID
credentials-file: /home/wild-blast/.cloudflared/TU-TUNNEL-ID.json

ingress:
  - hostname: wild-stream-12345678.trycloudflare.com
    service: http://localhost:8000
  - service: http_status:404
```

**Nota:** Cloudflare te dará un subdominio gratuito como `wild-stream-12345678.trycloudflare.com`

### 8.6 Iniciar Túnel (Prueba)

```bash
# Probar el túnel
cloudflared tunnel run wild-stream
```

Deberías ver algo como:
```
2024-10-15T10:30:00Z INF | Your tunnel is now live at https://wild-stream-12345678.trycloudflare.com
```

**¡Anota esta URL!** Es tu acceso remoto.

### 8.7 Configurar como Servicio Permanente

```bash
# Instalar como servicio
sudo cloudflared service install

# Editar configuración del servicio
sudo nano /etc/cloudflared/config.yml
```

Agrega la misma configuración:
```yaml
tunnel: TU-TUNNEL-ID
credentials-file: /home/wild-blast/.cloudflared/TU-TUNNEL-ID.json

ingress:
  - hostname: wild-stream-12345678.trycloudflare.com
    service: http://localhost:8000
  - service: http_status:404
```

```bash
# Iniciar servicio
sudo systemctl start cloudflared

# Habilitar en arranque
sudo systemctl enable cloudflared

# Ver estado
sudo systemctl status cloudflared
```

---

## 📍 PASO 9: Probar Acceso Remoto

### 9.1 Acceder desde Cualquier Lugar

Ahora puedes acceder desde cualquier lugar usando:
- **URL**: `https://wild-stream-12345678.trycloudflare.com`
- **Login**: admin / tu-nueva-contraseña

### 9.2 Probar Funcionalidades Remotas

1. **Crear Stream Lists** desde el navegador
2. **Ver métricas en tiempo real**
3. **Controlar transmisiones**
4. **Monitorear sistema**

### 9.3 Subir Videos Remotamente

**Método 1: WinSCP + Cloudflare**
1. Usa WinSCP para conectar al servidor
2. Navega a `/mnt/main-storage/stream-lists/`
3. Sube videos a las carpetas correspondientes

**Método 2: SCP desde cualquier PC**
```bash
# Desde cualquier PC con acceso a internet
scp video.mp4 wild-blast@ip-servidor:/mnt/main-storage/stream-lists/intro-videos/
```

---

## 📍 PASO 10: Uso Diario y Flujo de Trabajo

### 10.1 Flujo de Trabajo Típico

1. **Acceder remotamente**: `https://wild-stream-12345678.trycloudflare.com`
2. **Crear/administrar Stream Lists**:
   - "intro-videos" → Videos de introducción
   - "main-content" → Contenido principal
   - "outro-videos" → Videos de despedida
3. **Subir videos** a las listas correspondientes
4. **Seleccionar lista** para transmitir
5. **Configurar RTMP** (Twitch, YouTube, etc.)
6. **Iniciar transmisión** 24/7
7. **Monitorear** desde cualquier lugar

### 10.2 Comandos Útiles

```bash
# Ver estado de servicios
sudo systemctl status wild-stream-hub cloudflared

# Ver logs
sudo journalctl -u wild-stream-hub -f
sudo journalctl -u cloudflared -f

# Reiniciar servicios
sudo systemctl restart wild-stream-hub
sudo systemctl restart cloudflared

# Ver uso de recursos
htop
nvidia-smi
```

### 10.3 Gestión de Stream Lists

```bash
# Ver todas las listas
ls -la /mnt/main-storage/stream-lists/

# Ver videos en una lista
ls -la /mnt/main-storage/stream-lists/intro-videos/

# Agregar videos
cp nuevo-video.mp4 /mnt/main-storage/stream-lists/main-content/

# Eliminar videos
rm /mnt/main-storage/stream-lists/outro-videos/video-viejo.mp4
```

---

## 📍 PASO 11: Optimización y Mantenimiento

### 11.1 Ajustar Configuración de Transmisión

```bash
# Editar configuración FFmpeg
nano ~/wild_stream_hub/backend/ffmpeg_manager.py
```

Busca y modifica según necesites:
```python
"-b:v", "4500k",  # Bitrate de video
"-maxrate", "5000k",
"-bufsize", "9000k",
```

### 11.2 Monitoreo Avanzado

```bash
# Ver uso de GPU en tiempo real
watch -n 1 nvidia-smi

# Ver uso de CPU
htop

# Ver espacio en disco
df -h /mnt/main-storage/

# Ver logs en tiempo real
sudo journalctl -u wild-stream-hub -f
```

### 11.3 Backup de Configuración

```bash
# Crear backup
tar -czf wild-stream-backup-$(date +%Y%m%d).tar.gz ~/wild_stream_hub

# Guardar en lugar seguro
scp wild-stream-backup-*.tar.gz tu-pc-windows:/ruta/backup/
```

---

## 🎯 Checklist Final

Antes de considerar el setup completo, verifica:

- [ ] Servidor Debian 13 funcionando
- [ ] Drivers NVIDIA instalados (nvidia-smi funciona)
- [ ] FFmpeg con soporte NVENC instalado
- [ ] Wild Stream Hub instalado en ~/wild_stream_hub
- [ ] Contraseña de admin cambiada
- [ ] Clave secreta JWT cambiada
- [ ] Directorio /mnt/main-storage/stream-lists creado
- [ ] Primera stream list creada y con videos
- [ ] Primera transmisión de prueba exitosa
- [ ] Servicio systemd configurado y funcionando
- [ ] Cloudflare Tunnel configurado y funcionando
- [ ] Puedes acceder al panel remotamente
- [ ] Transmisión se ve correctamente en Twitch/YouTube
- [ ] Métricas del sistema se actualizan en tiempo real
- [ ] Stream Lists funcionan correctamente
- [ ] Backup de configuración creado

---

## 🆘 Solución Rápida de Problemas

### El servidor no inicia
```bash
# Ver errores
sudo journalctl -u wild-stream-hub -n 50

# Verificar manualmente
cd ~/wild_stream_hub/backend
source venv/bin/activate
python main.py
```

### NVENC no funciona
```bash
# Verificar drivers
nvidia-smi

# Si no funciona, reinstalar
sudo apt install --reinstall nvidia-driver
sudo reboot
```

### No puedo acceder remotamente
```bash
# Verificar Cloudflare tunnel
sudo systemctl status cloudflared

# Ver logs
sudo journalctl -u cloudflared -f

# Reiniciar túnel
sudo systemctl restart cloudflared
```

### Stream Lists no funcionan
```bash
# Verificar permisos
ls -la /mnt/main-storage/stream-lists/
sudo chown -R wild-blast:wild-blast /mnt/main-storage/stream-lists/

# Verificar logs
sudo journalctl -u wild-stream-hub -f | grep stream
```

### Transmisión se corta
```bash
# Verificar recursos
htop
nvidia-smi

# Ver logs de FFmpeg
sudo journalctl -u wild-stream-hub -f | grep ffmpeg
```

---

## 📞 Obtener Ayuda

Si te atascas:

1. **Revisa los logs:**
   ```bash
   sudo journalctl -u wild-stream-hub -f
   sudo journalctl -u cloudflared -f
   ```

2. **Verifica el estado:**
   ```bash
   sudo systemctl status wild-stream-hub
   sudo systemctl status cloudflared
   ```

3. **Prueba manualmente:**
   ```bash
   cd ~/wild_stream_hub/backend
   source venv/bin/activate
   python main.py
   ```

4. **Verifica la API:**
   - Abre `https://tu-tunel.trycloudflare.com/docs`
   - Prueba los endpoints de stream-lists

---

## 🎉 ¡Éxito!

Cuando todo esté funcionando:
- ✅ Tu servidor Debian transmitirá 24/7
- ✅ Puedes controlar desde cualquier lugar via Cloudflare
- ✅ Se reiniciará automáticamente si el servidor se reinicia
- ✅ Los videos se repetirán en bucle automáticamente
- ✅ Puedes monitorear todo en tiempo real
- ✅ **¡NUEVO!** Puedes gestionar múltiples listas de videos
- ✅ **¡NUEVO!** Interfaz web para crear/administrar listas

**¡Feliz Transmisión! 🎬**

---

## 🌟 Características Implementadas

### ✅ **Stream Lists (NUEVO)**
- Crear múltiples listas de videos
- Subir videos a las listas
- Seleccionar lista para transmisión
- Ver videos en cada lista
- Eliminar videos de las listas

### ✅ **Acceso Remoto**
- Cloudflare Tunnel con subdominio gratuito
- HTTPS automático
- Acceso desde cualquier lugar
- Sin necesidad de dominio propio

### ✅ **Transmisión 24/7**
- Auto-inicio con systemd
- Reinicio automático en fallos
- Monitoreo en tiempo real
- Control remoto completo

### ✅ **Seguridad**
- JWT authentication
- Contraseñas seguras
- HTTPS via Cloudflare
- Acceso controlado

---

**¡Todo listo para transmitir profesionalmente! 🚀**
