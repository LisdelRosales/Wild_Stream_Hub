# 🛡️ Características Avanzadas - Wild Stream Hub

## Sistema de Tolerancia a Fallos y Recuperación Automática

---

## ✅ **LO QUE YA ESTÁ IMPLEMENTADO:**

### **1. 🔄 Reintentos Automáticos**

Si FFmpeg falla o se cierra inesperadamente, el sistema:
- **Detecta el fallo** automáticamente
- **Espera 5 segundos** antes de reintentar
- **Reintenta hasta 5 veces** antes de rendirse
- **Resetea el contador** cuando la transmisión funciona correctamente

```python
# Configuración en ffmpeg_manager.py
_max_restart_attempts = 5      # Máximo 5 intentos
_restart_delay = 5              # 5 segundos entre intentos
auto_restart_enabled = True     # Activado por defecto
```

### **2. 💾 Persistencia del Estado**

El sistema guarda automáticamente:
- URL RTMP actual
- Clave de transmisión
- Lista de videos que se está usando
- Timestamp de cuándo se guardó
- Si debe auto-reiniciar

Archivo de estado: `/mnt/main-storage/wild_stream_hub/stream_state.json`

### **3. 🚀 Auto-Recuperación al Reiniciar**

Cuando el servidor se reinicia (reboot, crash, systemd restart):
1. **Lee el estado guardado** al iniciar
2. **Verifica si había una transmisión activa**
3. **Restaura automáticamente** la configuración
4. **Reinicia la transmisión** desde donde estaba

### **4. 🔒 Cloudflare Tunnel (HTTPS Seguro)**

Ya contemplado en GUIA_INSTALACION.md:
- HTTPS automático
- Sin necesidad de certificados SSL
- Subdominio gratuito `.trycloudflare.com`
- Acceso remoto seguro desde cualquier lugar

---

## 📊 **FLUJOS DE TOLERANCIA A FALLOS:**

### **Escenario 1: FFmpeg Se Cierra Inesperadamente**

```
1. FFmpeg falla → Exit code != 0
2. Sistema detecta fallo
3. Espera 5 segundos
4. Intento 1/5: Reinicia FFmpeg
5. Si falla → Intento 2/5
6. Si falla → Intento 3/5
7. ...
8. Si funciona → Reset contador, continúa normal
9. Si 5 intentos fallan → Stop auto-restart, notifica
```

### **Escenario 2: Servidor Se Reinicia**

```
1. Servidor apaga (reboot, crash, systemd)
2. systemd inicia wild-stream-hub.service
3. FastAPI lee stream_state.json
4. Encuentra estado activo
5. Obtiene videos de la stream list
6. Configura FFmpeg con RTMP guardado
7. Inicia transmisión automáticamente
8. Continúa transmitiendo 24/7
```

### **Escenario 3: Usuario Detiene Manualmente**

```
1. Usuario click "Stop Stream"
2. FFmpeg se detiene limpiamente
3. Estado se limpia: active = false
4. NO se auto-reinicia al reboot
5. Sistema queda en reposo
```

### **Escenario 4: Pérdida de Red Temporal**

```
1. Red se cae → FFmpeg pierde conexión RTMP
2. FFmpeg falla con error
3. Sistema detecta fallo
4. Espera 5 segundos (red puede volver)
5. Reintenta conexión
6. Si red volvió → Continúa transmitiendo
7. Si no → Continúa reintentando (hasta 5 veces)
```

---

## 🔧 **ARCHIVOS IMPLEMENTADOS:**

### **1. `backend/state_manager.py` (NUEVO)**
Gestiona la persistencia del estado:
- `save_stream_state()` - Guarda configuración actual
- `clear_stream_state()` - Limpia estado (stop manual)
- `get_stream_state()` - Lee estado guardado
- `should_auto_restart()` - Verifica si debe reiniciar

### **2. `backend/ffmpeg_manager.py` (ACTUALIZADO)**
Agregado sistema de reintentos:
- `_handle_stream_failure()` - Maneja fallos
- `_restart_count` - Contador de intentos
- `auto_restart_enabled` - Flag de auto-restart
- Lógica de reintentos con delay

### **3. `backend/main.py` (ACTUALIZADO)**
Integración completa:
- Guarda estado al iniciar stream
- Limpia estado al detener manualmente
- Restaura stream al startup del servidor
- Logs detallados de recuperación

---

## 📋 **COMPORTAMIENTO EN LOGS:**

### **Inicio Normal:**
```bash
🚀 Wild_Stream_Hub API starting...
📡 WebSocket monitoring available at /ws/monitor
📚 API documentation available at /docs
🔐 Default credentials: admin / admin123
```

### **Con Auto-Recuperación:**
```bash
🚀 Wild_Stream_Hub API starting...
📡 WebSocket monitoring available at /ws/monitor
📚 API documentation available at /docs
🔐 Default credentials: admin / admin123
🔄 Detected previous stream state, attempting to restore...
✅ Stream auto-restored: intro-videos
```

### **Durante Fallos:**
```bash
⚠️ FFmpeg process ended with code 1, attempting restart...
🔄 Restart attempt 1/5
✅ Stream restarted successfully
```

### **Máximo de Intentos Alcanzado:**
```bash
⚠️ FFmpeg process ended with code 1, attempting restart...
🔄 Restart attempt 1/5
❌ Error restarting stream: ...
🔄 Restart attempt 2/5
❌ Error restarting stream: ...
🔄 Restart attempt 3/5
❌ Error restarting stream: ...
🔄 Restart attempt 4/5
❌ Error restarting stream: ...
🔄 Restart attempt 5/5
❌ Max restart attempts (5) reached. Stopping auto-restart.
```

---

## 🎛️ **CONFIGURACIÓN PERSONALIZABLE:**

Si quieres cambiar los parámetros, edita `backend/ffmpeg_manager.py`:

```python
class FFmpegManager:
    def __init__(self):
        # ...
        self._max_restart_attempts = 5  # Cambiar a 10 para más intentos
        self._restart_delay = 5          # Cambiar a 10 para más delay
        self.auto_restart_enabled = True  # Cambiar a False para desactivar
```

---

## 🧪 **CÓMO PROBAR:**

### **Prueba 1: Simular Fallo de FFmpeg**
```bash
# Mientras transmite, matar proceso FFmpeg
sudo kill -9 $(pgrep ffmpeg)

# Observar logs
sudo journalctl -u wild-stream-hub -f

# Debería reiniciar automáticamente
```

### **Prueba 2: Reinicio del Servidor**
```bash
# Iniciar una transmisión
# Luego reiniciar servidor
sudo reboot

# Al volver, verificar
sudo systemctl status wild-stream-hub
sudo journalctl -u wild-stream-hub -n 50

# Debería mostrar "Stream auto-restored"
```

### **Prueba 3: Stop Manual**
```bash
# Detener desde WebUI
# Reiniciar servidor
sudo reboot

# Verificar que NO reinicie automáticamente
# Porque fue stop manual
```

---

## 📊 **RESUMEN DE TOLERANCIA A FALLOS:**

| Escenario | Comportamiento | Auto-Recupera |
|-----------|----------------|---------------|
| FFmpeg crash | Reintenta 5 veces con delay de 5s | ✅ Sí |
| Pérdida de red | Reintenta hasta recuperar | ✅ Sí |
| Servidor reinicia | Restaura stream al iniciar | ✅ Sí |
| Stop manual | No reinicia | ❌ No |
| 5 intentos fallan | Se detiene, requiere intervención | ❌ No |
| Video termina | Pasa al siguiente en la lista | ✅ Sí |

---

## 🔐 **SEGURIDAD (HTTPS/Tunnel):**

Ya implementado via Cloudflare Tunnel:
- ✅ **HTTPS automático** (sin configurar certificados)
- ✅ **Subdominio gratuito** (.trycloudflare.com)
- ✅ **Encriptación TLS** end-to-end
- ✅ **Sin abrir puertos** en router
- ✅ **IP oculta** del servidor
- ✅ **Protección DDoS** de Cloudflare

Ver **GUIA_INSTALACION.md - PASO 8** para configuración.

---

## 🎯 **CONCLUSIÓN:**

**TODO ESTÁ IMPLEMENTADO:**

1. ✅ **Reintentos automáticos** → Hasta 5 intentos con delay
2. ✅ **Detección de fallos** → Monitoreo continuo de FFmpeg
3. ✅ **Persistencia del estado** → Guarda configuración en JSON
4. ✅ **Auto-recuperación** → Restaura al reiniciar servidor
5. ✅ **Tolerancia a fallos** → Maneja crashes, red caída, etc.
6. ✅ **HTTPS/Tunnel seguro** → Cloudflare Tunnel gratuito

**El sistema es robusto y listo para producción 24/7** 🚀

---

## 📝 **Archivos Actualizados:**

```
wild_stream_hub/backend/
├── state_manager.py           ← NUEVO (persistencia)
├── ffmpeg_manager.py          ← ACTUALIZADO (reintentos)
└── main.py                    ← ACTUALIZADO (auto-recovery)
```

**Copia estos archivos al servidor y reinicia el servicio** 👍

