# 🧪 Testing Guide

This guide will help you test Wild Stream Hub before going live.

## Pre-Flight Checklist

### System Requirements
- [ ] Python 3.9+ installed
- [ ] FFmpeg with NVENC support installed
- [ ] NVIDIA drivers installed (for GPU acceleration)
- [ ] At least one test video file available
- [ ] 8GB RAM available
- [ ] Internet connection for streaming

### Installation Verification
- [ ] Virtual environment created
- [ ] All Python dependencies installed
- [ ] Backend starts without errors
- [ ] Frontend loads in browser

## 🔧 Component Testing

### 1. Backend API Testing

#### Start the Server
```bash
cd backend
source venv/bin/activate
python main.py
```

Expected output:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
🚀 Wild_Stream_Hub API starting...
📡 WebSocket monitoring available at /ws/monitor
📚 API documentation available at /docs
🔐 Default credentials: admin / admin123
```

#### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Wild_Stream_Hub",
  "version": "1.0.0"
}
```

#### Test API Documentation
Open in browser: `http://localhost:8000/docs`
- [ ] Swagger UI loads correctly
- [ ] All endpoints are visible
- [ ] Can expand endpoint details

### 2. Authentication Testing

#### Test Login (using curl)
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Expected response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Test Invalid Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=wrongpassword"
```

Expected: HTTP 401 Unauthorized

### 3. FFmpeg Testing

#### Test FFmpeg Installation
```bash
ffmpeg -version
```

Verify output shows version information.

#### Test NVENC Support
```bash
ffmpeg -encoders | grep nvenc
```

Expected output should include:
```
h264_nvenc
hevc_nvenc
```

#### Test Basic Encoding
```bash
ffmpeg -i test_video.mp4 -c:v h264_nvenc -t 5 test_output.mp4
```

If this works, NVENC is functional.

#### Test RTMP Streaming (Local Test)
```bash
# Install RTMP test server (optional)
# docker run -d -p 1935:1935 tiangolo/nginx-rtmp

# Test streaming
ffmpeg -re -i test_video.mp4 \
  -c:v h264_nvenc \
  -c:a aac \
  -f flv rtmp://localhost:1935/live/test
```

### 4. Frontend Testing

#### Open Dashboard
1. Open `frontend/index.html` in browser
2. Or serve via HTTP:
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```
   Open: `http://localhost:8080`

#### Test Login Flow
- [ ] Login modal appears
- [ ] Enter credentials: admin / admin123
- [ ] Successfully redirects to dashboard
- [ ] Username badge shows in header

#### Test UI Components
- [ ] All cards render correctly
- [ ] Stream status badge shows "Inactive"
- [ ] System monitor sections visible
- [ ] All form fields are functional

### 5. WebSocket Testing

#### Browser Console Test
Open browser console (F12) and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/monitor');
ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

Expected: Receive JSON data every 1 second with system stats.

### 6. Stream Testing

#### Test with Local Video

1. **Prepare Test Video**
   ```bash
   # Download a test video (small file)
   wget https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4 -O test_video.mp4
   ```

2. **Configure Stream**
   - RTMP URL: Use a test RTMP server or your actual streaming platform
   - Stream Key: Your test stream key
   - Video List: `/absolute/path/to/test_video.mp4`

3. **Start Stream**
   - Click "▶️ Start Stream"
   - Watch for success message
   - Verify status badge changes to "Active"

4. **Monitor Stream**
   - [ ] Current video name displays
   - [ ] Bitrate updates (should be > 0)
   - [ ] Uptime counter starts
   - [ ] FFmpeg process shows as running
   - [ ] System metrics update every second

5. **Stop Stream**
   - Click "⏹️ Stop Stream"
   - Verify status returns to "Inactive"
   - Verify uptime resets to 00:00:00

### 7. System Monitoring Testing

#### CPU Test
Run CPU-intensive task:
```bash
# In another terminal
stress --cpu 4 --timeout 30s
```
Watch CPU usage increase in dashboard.

#### Memory Test
```bash
# In another terminal
stress --vm 2 --vm-bytes 1G --timeout 30s
```
Watch RAM usage increase in dashboard.

#### GPU Test (if streaming)
Start a stream and watch GPU utilization.

### 8. Error Handling Testing

#### Test Invalid Video Path
1. Enter non-existent video path
2. Try to start stream
3. Expected: Error message displayed

#### Test Invalid RTMP URL
1. Enter invalid RTMP URL (e.g., "invalid-url")
2. Try to start stream
3. Expected: Stream fails to start

#### Test Network Interruption
1. Start a stream
2. Disconnect network
3. Expected: WebSocket reconnects automatically after network returns

## 🎯 Integration Testing

### Full Workflow Test

1. **Start Backend**
   ```bash
   ./start.sh
   ```

2. **Open Frontend**
   - Open `frontend/index.html`

3. **Login**
   - Username: admin
   - Password: admin123

4. **Configure Stream**
   - RTMP URL: Your test URL
   - Stream Key: Your test key
   - Videos: Add 2-3 test videos

5. **Start Streaming**
   - Click Start Stream
   - Verify stream begins

6. **Monitor for 5 Minutes**
   - [ ] Stream stays active
   - [ ] Bitrate remains stable
   - [ ] No error messages
   - [ ] System metrics update consistently
   - [ ] Videos loop correctly

7. **Stop Stream**
   - Click Stop Stream
   - Verify clean shutdown

8. **Logout**
   - Click Logout
   - Verify returns to login

## 🐛 Common Issues & Solutions

### Backend Won't Start
```bash
# Check if port is in use
sudo lsof -i :8000

# Check Python version
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### WebSocket Won't Connect
- Check backend is running
- Verify no firewall blocking port 8000
- Check browser console for errors

### FFmpeg Crashes
```bash
# Check video file
ffmpeg -i video.mp4

# Test encoding manually
ffmpeg -i video.mp4 -c:v h264_nvenc -t 5 test.mp4

# Check system resources
free -h
nvidia-smi
```

### Stream Not Appearing on Platform
- Verify RTMP URL is correct
- Check stream key is valid
- Test with different streaming software (OBS)
- Check platform's ingestion server status

## 📊 Performance Benchmarks

Expected performance on recommended hardware (Ryzen 5 3600, RTX 2060):

- **CPU Usage**: 10-30% (with NVENC)
- **GPU Usage**: 30-50%
- **RAM Usage**: 500MB - 2GB
- **Bitrate**: 4500 kbps (adjustable)
- **Latency**: < 5 seconds to platform

## ✅ Pre-Production Checklist

Before deploying to production:

### Security
- [ ] Changed default admin password
- [ ] Generated secure JWT secret key
- [ ] Configured CORS properly
- [ ] Set up HTTPS (Cloudflare Tunnel)
- [ ] Reviewed authentication logic

### Configuration
- [ ] Tested with production RTMP URLs
- [ ] Verified video file paths
- [ ] Configured proper bitrate settings
- [ ] Set up logging
- [ ] Configured auto-restart (systemd)

### Documentation
- [ ] Documented custom configurations
- [ ] Created user guide for collaborators
- [ ] Noted any platform-specific settings

### Backup
- [ ] Backed up configuration files
- [ ] Documented video file locations
- [ ] Created restore procedure

## 🔄 Continuous Testing

Recommended ongoing tests:
- Daily: Verify stream starts successfully
- Weekly: Check system resource trends
- Monthly: Update dependencies, test compatibility

---

**Testing Complete?** You're ready to go live! 🎉

For production deployment, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).


