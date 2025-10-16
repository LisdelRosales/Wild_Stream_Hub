# 🎬 Wild Stream Hub

**Web-based control panel for managing RTMP livestreams via FFmpeg**

Wild Stream Hub is a powerful, local web application that allows authenticated users to manage RTMP livestreams using FFmpeg with NVIDIA NVENC hardware acceleration. Monitor system resources in real-time, manage multiple video playlists, and stream to platforms like Twitch, YouTube, or any RTMP-compatible service.

## 🌟 Features

- 🔐 **JWT Authentication** - Secure login system
- 🎥 **Stream Management** - Start/stop FFmpeg streaming with NVENC
- 📊 **Real-time Monitoring** - Live updates via WebSockets
- 💻 **System Metrics** - CPU, GPU, RAM, and disk usage monitoring
- 🎬 **Playlist Support** - Loop through multiple video files
- ⚡ **Hardware Acceleration** - NVIDIA NVENC (RTX 2060) support
- 🌍 **Remote Access Ready** - Works with Cloudflare Tunnel
- 🎨 **Modern UI** - Clean, responsive dashboard

## 🧱 Architecture

```
Frontend (HTML/JS) → FastAPI Backend → FFmpeg Subprocess
                              ↓
                         WebSocket Monitor
```

## 📋 Prerequisites

### System Requirements
- **OS**: Debian 13 (or any Linux distro with FFmpeg support)
- **CPU**: Ryzen 5 3600 or better
- **GPU**: NVIDIA RTX 2060 or better (with NVENC support)
- **RAM**: 24 GB (minimum 8GB recommended)
- **Storage**: NVMe 500GB or sufficient space for videos

### Software Requirements
- Python 3.9 or higher
- FFmpeg with NVENC support
- NVIDIA drivers (for GPU acceleration)
- pip (Python package manager)

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd /path/to/your/projects
# If you have git:
git clone <repository-url> wild_stream_hub
# Or simply extract the files to wild_stream_hub directory
```

### 2. Install FFmpeg with NVENC Support

```bash
# Update package list
sudo apt update

# Install FFmpeg (ensure it has CUDA/NVENC support)
sudo apt install ffmpeg -y

# Verify NVENC support
ffmpeg -encoders | grep nvenc
```

If NVENC is not available, you may need to compile FFmpeg from source with CUDA support. See [FFmpeg NVENC Guide](https://developer.nvidia.com/ffmpeg).

### 3. Install NVIDIA Drivers

```bash
# Check if NVIDIA drivers are installed
nvidia-smi

# If not installed, install NVIDIA drivers
sudo apt install nvidia-driver -y
sudo reboot
```

### 4. Set Up Python Environment

```bash
# Navigate to backend directory
cd wild_stream_hub/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change these credentials in `backend/auth.py` before deploying to production!

### Change Default Password

Edit `backend/auth.py`:

```python
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("your-new-password"),  # Change this
        "disabled": False,
    }
}
```

### JWT Secret Key

Edit `backend/auth.py`:

```python
SECRET_KEY = "your-super-secret-key-here"  # Change this to a random string!
```

Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🎮 Usage

### Starting the Server

```bash
# Navigate to backend directory
cd wild_stream_hub/backend

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server
python main.py
```

The server will start on `http://0.0.0.0:8000`

Alternative using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing the Dashboard

1. **Local Access**: Open `wild_stream_hub/frontend/index.html` in your browser
2. **Or serve via HTTP**: 
   ```bash
   cd wild_stream_hub/frontend
   python3 -m http.server 8080
   ```
   Then open `http://localhost:8080`

### Using the Dashboard

1. **Login**: Use default credentials (admin/admin123)
2. **Configure Stream**:
   - Enter your RTMP URL (e.g., `rtmp://live.twitch.tv/app`)
   - Enter your stream key
   - Add video file paths (one per line)
3. **Start Stream**: Click "▶️ Start Stream"
4. **Monitor**: Watch real-time metrics update every second
5. **Stop Stream**: Click "⏹️ Stop Stream" when done

## 📡 API Endpoints

### Authentication
- `POST /login` - Authenticate and get JWT token

### Stream Management
- `POST /stream/start` - Start streaming
- `POST /stream/stop` - Stop streaming
- `GET /stream/status` - Get current status

### WebSocket
- `WS /ws/monitor` - Real-time monitoring (updates every 1 second)

### System
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

## 🌐 Remote Access with Cloudflare Tunnel

### Install Cloudflared

```bash
# Download cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# Install
sudo dpkg -i cloudflared-linux-amd64.deb

# Verify installation
cloudflared --version
```

### Set Up Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create a tunnel
cloudflared tunnel create wild-stream-hub

# Configure the tunnel
nano ~/.cloudflared/config.yml
```

Add this configuration:
```yaml
tunnel: <your-tunnel-id>
credentials-file: /home/yourusername/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: stream.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

### Run the Tunnel

```bash
# Run tunnel
cloudflared tunnel run wild-stream-hub

# Or install as a service
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

Now access your dashboard from anywhere via `https://stream.yourdomain.com`!

## 🐳 Docker Deployment (Optional)

### Create Dockerfile

Create `Dockerfile` in the `backend` directory:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg and NVIDIA runtime dependencies
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

### Create docker-compose.yml

Create `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  wild-stream-hub:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - /path/to/your/videos:/videos
    environment:
      - PYTHONUNBUFFERED=1
    runtime: nvidia  # For NVIDIA GPU support
    restart: unless-stopped
```

### Run with Docker

```bash
docker-compose up -d
```

## 📊 System Monitoring

The dashboard displays:

### Stream Metrics
- Current video being streamed
- Bitrate (live)
- Stream uptime
- FFmpeg process status

### System Resources
- **CPU Usage** - Real-time percentage
- **RAM Usage** - Used/Total GB and percentage
- **GPU Usage** - Utilization, memory, and temperature
- **Disk Usage** - Used/Free space

### FFmpeg Process
- Process status (Running/Stopped)
- CPU usage of FFmpeg
- Memory consumption

## 🔧 Troubleshooting

### FFmpeg Not Found
```bash
# Check FFmpeg installation
which ffmpeg
ffmpeg -version

# If not found, install
sudo apt install ffmpeg -y
```

### NVENC Not Working
```bash
# Check NVIDIA drivers
nvidia-smi

# Verify NVENC support
ffmpeg -encoders | grep nvenc

# Test NVENC encoding
ffmpeg -hwaccel cuda -i test.mp4 -c:v h264_nvenc output.mp4
```

### WebSocket Connection Failed
- Ensure the backend is running on port 8000
- Check firewall settings: `sudo ufw allow 8000`
- Verify CORS settings in `main.py`

### Permission Denied for Video Files
```bash
# Give read permissions to video files
chmod +r /path/to/videos/*.mp4
```

### Stream Not Starting
1. Verify video file paths are correct and accessible
2. Check RTMP URL and stream key are valid
3. Test FFmpeg command manually:
   ```bash
   ffmpeg -re -i video.mp4 -c:v h264_nvenc -f flv rtmp://your-url/stream-key
   ```

## 📁 Project Structure

```
wild_stream_hub/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── ffmpeg_manager.py    # FFmpeg subprocess manager
│   ├── monitor.py           # System monitoring
│   ├── auth.py              # JWT authentication
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Dashboard HTML
│   ├── script.js            # Frontend JavaScript
│   └── style.css            # Dashboard styles
└── README.md                # This file
```

## 🛡️ Security Considerations

### For Production Use:
1. **Change default credentials** in `auth.py`
2. **Generate a secure SECRET_KEY** for JWT
3. **Configure CORS** properly (don't use `allow_origins=["*"]`)
4. **Use HTTPS** (via Cloudflare Tunnel or reverse proxy)
5. **Implement rate limiting** for API endpoints
6. **Use a real database** instead of fake_users_db
7. **Add WebSocket authentication** (validate JWT on connection)
8. **Set up fail2ban** to prevent brute force attacks

## 🔄 Auto-Start on Boot (systemd)

Create `/etc/systemd/system/wild-stream-hub.service`:

```ini
[Unit]
Description=Wild Stream Hub API
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/wild_stream_hub/backend
Environment="PATH=/path/to/wild_stream_hub/backend/venv/bin"
ExecStart=/path/to/wild_stream_hub/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable wild-stream-hub
sudo systemctl start wild-stream-hub
sudo systemctl status wild-stream-hub
```

## 📝 TODO / Future Enhancements

- [ ] Add user management (multiple users)
- [ ] Persistent storage (database for users and stream configs)
- [ ] Stream scheduling (start/stop at specific times)
- [ ] Stream quality presets (1080p, 720p, etc.)
- [ ] Multi-platform streaming (stream to multiple platforms simultaneously)
- [ ] Recording functionality
- [ ] Advanced FFmpeg filters (overlays, transitions)
- [ ] Stream health monitoring (dropped frames, connection issues)
- [ ] Email/Discord notifications for stream events
- [ ] Mobile-responsive improvements

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

This project is open source and available for personal and commercial use.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **FFmpeg** - Video processing powerhouse
- **NVIDIA NVENC** - Hardware acceleration
- **Cloudflare** - Secure tunneling solution

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review API logs: `tail -f /var/log/wild-stream-hub.log`
3. Test FFmpeg independently
4. Verify system resources are sufficient

---

**Built with ❤️ for streamers by streamers**

*Wild Stream Hub v1.0.0*


