#!/bin/bash
# Wild Stream Hub - Setup File Permissions
# Makes all shell scripts executable

echo "🔧 Setting up file permissions for Wild Stream Hub..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR" || exit

# Make shell scripts executable
chmod +x install.sh
chmod +x start.sh
chmod +x stop.sh
chmod +x setup_permissions.sh

echo "✅ Made scripts executable:"
echo "   - install.sh"
echo "   - start.sh"
echo "   - stop.sh"
echo "   - setup_permissions.sh"

# Check if we're on Linux and if the user wants to set up systemd
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo ""
    read -p "Do you want to install the systemd service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Get the current user and paths
        CURRENT_USER=$(whoami)
        CURRENT_PATH=$(pwd)
        SERVICE_FILE="wild-stream-hub.service"
        
        # Update the service file with actual paths
        sed -i "s|YOUR_USERNAME|$CURRENT_USER|g" "$SERVICE_FILE"
        sed -i "s|/path/to/wild_stream_hub|$CURRENT_PATH|g" "$SERVICE_FILE"
        
        # Copy to systemd
        sudo cp "$SERVICE_FILE" /etc/systemd/system/
        sudo systemctl daemon-reload
        
        echo "✅ systemd service installed"
        echo ""
        echo "To enable and start the service:"
        echo "  sudo systemctl enable wild-stream-hub"
        echo "  sudo systemctl start wild-stream-hub"
        echo "  sudo systemctl status wild-stream-hub"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run ./install.sh to install dependencies"
echo "2. Run ./start.sh to start the server"
echo "3. Open frontend/index.html in your browser"
echo ""


