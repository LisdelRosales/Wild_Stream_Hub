# 🎯 Próximos Pasos - Wild Stream Hub

## 🚀 Guía Completa de Configuración y Despliegue

Esta guía te llevará desde la instalación hasta tener tu sistema transmitiendo 24/7.

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
3. Verifica que veas el panel y las métricas se actualicen

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

Opciones para transferir:

**Opción A: Usar SCP (si tienes SSH configurado)**
```powershell
scp wild_stream_hub.zip usuario@ip-servidor-debian:/home/usuario/
```

**Opción B: Usar WinSCP** (interfaz gráfica)
1. Descarga WinSCP: https://winscp.net/
2. Conecta a tu servidor Debian
3. Arrastra la carpeta `wild_stream_hub`

**Opción C: Usar USB o Red Local**
1. Copia la carpeta a USB
2. Conecta USB al servidor Debian
3. Copia al home del usuario

### 2.3 Descomprimir en Debian

```bash
# Conectar por SSH al servidor
ssh usuario@ip-servidor-debian

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

Deberías ver información de tu RTX 2060.

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
- Instalará todas las dependencias
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

## 📍 PASO 5: Preparar Tus Videos

### 5.1 Crear Directorio para Videos

```bash
# Crear carpeta para videos
mkdir -p ~/videos/stream

# Dar permisos
chmod 755 ~/videos/stream
```

### 5.2 Subir Tus Videos

Desde Windows, usa WinSCP o SCP para subir tus videos:

```powershell
# Ejemplo con SCP
scp C:\ruta\a\tu\video.mp4 usuario@ip-servidor:/home/usuario/videos/stream/
```

### 5.3 Verificar Videos

```bash
# Listar videos
ls -lh ~/videos/stream/

# Verificar permisos de lectura
chmod +r ~/videos/stream/*.mp4

# Probar un video con FFmpeg
ffmpeg -i ~/videos/stream/video.mp4
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
ssh -L 8000:localhost:8000 usuario@ip-servidor-debian
```

Luego abre en tu navegador Windows: `http://localhost:8000/docs`

**Opción B: Abrir puerto en firewall (temporal)**

En el servidor Debian:
```bash
sudo ufw allow 8000
```

Luego desde Windows: `http://ip-servidor-debian:8000/docs`

### 6.3 Configurar Tu Primera Transmisión

1. **Obtener tu clave de transmisión de Twitch:**
   - Ve a https://dashboard.twitch.tv/settings/stream
   - Copia tu "Clave de transmisión principal"

2. **En el panel:**
   - URL RTMP: `rtmp://live.twitch.tv/app`
   - Clave de Transmisión: [tu clave de Twitch]
   - Lista de Videos:
     ```
     /home/usuario/videos/stream/video1.mp4
     /home/usuario/videos/stream/video2.mp4
     ```

3. **Iniciar transmisión** y verifica en Twitch que esté transmitiendo

### 6.4 Monitorear

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
User=tu-usuario-debian
WorkingDirectory=/home/tu-usuario-debian/wild_stream_hub/backend
Environment="PATH=/home/tu-usuario-debian/wild_stream_hub/backend/venv/bin"
ExecStart=/home/tu-usuario-debian/wild_stream_hub/backend/venv/bin/python main.py
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

## 📍 PASO 8: Configurar Cloudflare Tunnel (Acceso Remoto)

Para acceder desde cualquier lugar de forma segura.

### 8.1 Crear Cuenta en Cloudflare

1. Ve a https://dash.cloudflare.com/sign-up
2. Crea una cuenta gratuita
3. (Opcional) Agrega tu dominio si tienes uno

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

Si estás en SSH sin interfaz gráfica:
1. El comando te dará una URL
2. Copia esa URL y ábrela en tu PC Windows
3. Autoriza el acceso

### 8.4 Crear Túnel

```bash
# Crear túnel llamado "wild-stream"
cloudflared tunnel create wild-stream

# Ver el ID del túnel (guárdalo)
cloudflared tunnel list
```

### 8.5 Configurar Túnel

```bash
# Crear archivo de configuración
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Agrega (reemplaza TU-TUNNEL-ID):
```yaml
tunnel: TU-TUNNEL-ID
credentials-file: /home/tu-usuario/.cloudflared/TU-TUNNEL-ID.json

ingress:
  - hostname: stream.tu-dominio.com  # O usa el subdominio que Cloudflare te dé
    service: http://localhost:8000
  - service: http_status:404
```

**Nota:** Si no tienes dominio, Cloudflare te dará un subdominio gratuito como `tu-tunel.trycloudflare.com`

### 8.6 Configurar DNS (si tienes dominio)

```bash
# Agregar registro DNS
cloudflared tunnel route dns wild-stream stream.tu-dominio.com
```

### 8.7 Iniciar Túnel

**Prueba temporal:**
```bash
cloudflared tunnel run wild-stream
```

**Configurar como servicio permanente:**
```bash
# Instalar como servicio
sudo cloudflared service install

# Iniciar servicio
sudo systemctl start cloudflared

# Habilitar en arranque
sudo systemctl enable cloudflared

# Ver estado
sudo systemctl status cloudflared
```

### 8.8 Acceder Remotamente

Ahora puedes acceder desde cualquier lugar:
- `https://stream.tu-dominio.com` (si configuraste dominio)
- O la URL que Cloudflare te proporcionó

---

## 📍 PASO 9: Uso Diario

### 9.1 Iniciar/Detener Transmisión

**Desde el servidor:**
```bash
# Ver logs en tiempo real
sudo journalctl -u wild-stream-hub -f

# Detener servicio si necesitas
sudo systemctl stop wild-stream-hub
```

**Desde el navegador:**
1. Accede a tu panel (local o via Cloudflare)
2. Inicia sesión
3. Configura y controla tu transmisión

### 9.2 Agregar Nuevos Videos

```bash
# Subir videos al servidor
scp nuevo-video.mp4 usuario@servidor:~/videos/stream/

# O desde el servidor
cd ~/videos/stream/
# Agrega tus videos aquí
```

### 9.3 Monitorear el Sistema

```bash
# Ver uso de recursos
htop

# Ver GPU
nvidia-smi

# Ver logs del servicio
sudo journalctl -u wild-stream-hub -n 100
```

---

## 📍 PASO 10: Optimización y Mantenimiento

### 10.1 Ajustar Bitrate

Si necesitas cambiar el bitrate, edita:
```bash
nano ~/wild_stream_hub/backend/ffmpeg_manager.py
```

Busca y modifica:
```python
"-b:v", "4500k",  # Bitrate de video (cambiar según necesites)
"-maxrate", "5000k",
"-bufsize", "9000k",
```

Reinicia el servicio:
```bash
sudo systemctl restart wild-stream-hub
```

### 10.2 Actualizar el Sistema

```bash
# Actualizar sistema Debian
sudo apt update && sudo apt upgrade -y

# Actualizar dependencias Python
cd ~/wild_stream_hub/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 10.3 Backup de Configuración

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
- [ ] Videos subidos al servidor
- [ ] Primera transmisión de prueba exitosa
- [ ] Servicio systemd configurado y funcionando
- [ ] Cloudflare Tunnel configurado (opcional pero recomendado)
- [ ] Puedes acceder al panel remotamente
- [ ] Transmisión se ve correctamente en Twitch/YouTube
- [ ] Métricas del sistema se actualizan en tiempo real
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
   ```

2. **Verifica el estado:**
   ```bash
   sudo systemctl status wild-stream-hub
   ```

3. **Prueba manualmente:**
   ```bash
   cd ~/wild_stream_hub/backend
   source venv/bin/activate
   python main.py
   ```

4. **Consulta la documentación:**
   - README_ES.md - Documentación completa
   - INICIO_RAPIDO.md - Guía rápida
   - TESTING.md - Pruebas y solución de problemas

---

## 🎉 ¡Éxito!

Cuando todo esté funcionando:
- ✅ Tu servidor Debian transmitirá 24/7
- ✅ Puedes controlar desde cualquier lugar via Cloudflare
- ✅ Se reiniciará automáticamente si el servidor se reinicia
- ✅ Los videos se repetirán en bucle automáticamente
- ✅ Puedes monitorear todo en tiempo real

**¡Feliz Transmisión! 🎬**


