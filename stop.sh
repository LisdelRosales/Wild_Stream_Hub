#!/bin/bash
# Wild Stream Hub - Stop Script

echo "🛑 Stopping Wild Stream Hub..."

# Find and kill the process
PID=$(pgrep -f "python.*main.py")

if [ -z "$PID" ]; then
    echo "ℹ️  No running instance found"
else
    echo "Found process: $PID"
    kill $PID
    sleep 2
    
    # Force kill if still running
    if ps -p $PID > /dev/null; then
        echo "Force stopping..."
        kill -9 $PID
    fi
    
    echo "✅ Wild Stream Hub stopped"
fi


