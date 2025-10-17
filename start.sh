#!/bin/bash
# Wild Stream Hub - Quick Start Script

echo "🎬 Starting Wild Stream Hub..."

# Change to backend directory
cd "$(dirname "$0")/backend" || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    echo "📥 Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found"
    source venv/bin/activate
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed!"
    echo "Please install FFmpeg with NVENC support:"
    echo "  sudo apt install ffmpeg -y"
    exit 1
fi

# Check NVENC support
if ! ffmpeg -encoders 2>/dev/null | grep -q nvenc; then
    echo "⚠️  Warning: NVENC support not detected in FFmpeg"
    echo "Hardware acceleration may not work properly"
fi

# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
else
    echo "⚠️  Warning: nvidia-smi not found. GPU monitoring may not work"
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "📡 API will be available at: http://0.0.0.0:8000"
echo "📚 API docs will be at: http://0.0.0.0:8000/docs"
echo "🔐 Default credentials: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python main.py


