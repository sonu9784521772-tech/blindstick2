#!/bin/bash
# START SERVER - Quick launch script
# Run this every time you want to start the camera server

echo "============================================================"
echo " 👁️ BlindStick Camera Server - Starting..."
echo "============================================================"
echo ""

# Check if running in rasfiles directory
if [ ! -f "camera_server.py" ]; then
    echo "❌ Error: Please run from ~/rasfiles directory"
    echo "   cd ~/rasfiles"
    exit 1
fi

# Check if camera is available
echo "🔍 Checking camera..."
if libcamera-hello --list-cameras > /dev/null 2>&1; then
    echo "✓ Camera detected"
else
    echo "⚠ No camera detected (will use test mode)"
fi

echo ""
echo "🚀 Starting server..."
echo ""

# Run the Python server
python3 camera_server.py
