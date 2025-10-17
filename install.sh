#!/bin/bash
# Wild Stream Hub - Installation Script
# This script sets up the environment and dependencies

set -e  # Exit on error

echo "🎬 Wild Stream Hub - Installation Script"
echo "=========================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is designed for Linux systems"
    echo "For other systems, please follow the manual installation in README.md"
    exit 1
fi

# Check if Python 3.9+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.9 or higher:"
    echo "  sudo apt install python3 python3-pip python3-venv -y"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed"
    read -p "Do you want to install FFmpeg now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing FFmpeg..."
        sudo apt update
        sudo apt install ffmpeg -y
    else
        echo "Please install FFmpeg manually before continuing"
        exit 1
    fi
fi

# Check NVENC support
if ffmpeg -encoders 2>/dev/null | grep -q nvenc; then
    echo "✅ FFmpeg has NVENC support"
else
    echo "⚠️  FFmpeg does not have NVENC support"
    echo "You may need to compile FFmpeg with CUDA/NVENC support"
    echo "See: https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/"
fi

# Check NVIDIA drivers
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA drivers detected"
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader)
    echo "   GPU: $GPU_INFO"
else
    echo "⚠️  NVIDIA drivers not found"
    echo "GPU acceleration will not work without NVIDIA drivers"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment
echo ""
echo "📦 Setting up Python virtual environment..."
cd backend

if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate and install dependencies
echo "📥 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Review and modify backend/auth.py to change default credentials"
echo "2. Run ./start.sh to start the server"
echo "3. Open frontend/index.html in your browser"
echo "4. Default login: admin / admin123"
echo ""
echo "📚 For more information, see README.md"
echo ""


