# 🚀 Quick Start Guide

Get Wild Stream Hub running in 5 minutes!

## 1️⃣ Prerequisites Check

```bash
# Check Python (need 3.9+)
python3 --version

# Check FFmpeg
ffmpeg -version

# Check NVIDIA GPU (optional but recommended)
nvidia-smi
```

## 2️⃣ Installation

### Option A: Automated Installation (Linux)

```bash
cd wild_stream_hub
chmod +x install.sh
./install.sh
```

### Option B: Manual Installation

```bash
# Install dependencies
cd wild_stream_hub/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3️⃣ Start the Server

```bash
# Make start script executable
chmod +x start.sh

# Run the server
./start.sh
```

Or manually:
```bash
cd backend
source venv/bin/activate
python main.py
```

The API will start on `http://localhost:8000`

## 4️⃣ Open the Dashboard

### Option A: Direct File

Open `frontend/index.html` in your web browser

### Option B: HTTP Server

```bash
cd frontend
python3 -m http.server 8080
```

Then open: `http://localhost:8080`

## 5️⃣ Login

- **Username**: `admin`
- **Password**: `admin123`

## 6️⃣ Configure Your First Stream

1. Enter your RTMP URL (e.g., `rtmp://live.twitch.tv/app`)
2. Enter your stream key
3. Add video file paths (one per line):
   ```
   /home/user/videos/video1.mp4
   /home/user/videos/video2.mp4
   /home/user/videos/video3.mp4
   ```
4. Click "▶️ Start Stream"

## 7️⃣ Monitor Your Stream

Watch the dashboard for:
- Real-time bitrate
- Stream uptime
- CPU/GPU/RAM usage
- FFmpeg process stats

## 🛠️ Common RTMP URLs

### Twitch
```
RTMP URL: rtmp://live.twitch.tv/app
Stream Key: Your Twitch stream key
```

### YouTube
```
RTMP URL: rtmp://a.rtmp.youtube.com/live2
Stream Key: Your YouTube stream key
```

### Facebook
```
RTMP URL: rtmps://live-api-s.facebook.com:443/rtmp/
Stream Key: Your Facebook stream key
```

## 🔧 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
sudo lsof -i :8000

# Kill the process if needed
sudo kill -9 <PID>
```

### Can't connect to WebSocket
- Make sure backend is running
- Check browser console for errors
- Verify API URL in `frontend/script.js`

### FFmpeg errors
```bash
# Test FFmpeg manually
ffmpeg -re -i test.mp4 -c:v h264_nvenc -f flv rtmp://test-url

# Check NVENC support
ffmpeg -encoders | grep nvenc
```

### Videos not found
- Use absolute paths: `/home/user/videos/file.mp4`
- Check file permissions: `chmod +r video.mp4`
- Verify files exist: `ls -lh /path/to/video.mp4`

## 📞 Need More Help?

See the full [README.md](README.md) for:
- Detailed installation instructions
- Cloudflare Tunnel setup
- Docker deployment
- Security configuration
- systemd service setup

## ⚡ Pro Tips

1. **Test FFmpeg first**: Before streaming, test FFmpeg with a short video
2. **Monitor resources**: Keep an eye on CPU/GPU usage during streams
3. **Use absolute paths**: Always use full paths for video files
4. **Check stream keys**: Double-check your RTMP URL and stream key
5. **Start small**: Test with one video before adding multiple files

---

**Happy Streaming! 🎬**


