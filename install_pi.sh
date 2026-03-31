#!/bin/bash

# BlindStick Raspberry Pi Installation Script
# This script automates the setup of BlindStick on Raspberry Pi 3

echo "============================================================"
echo " BlindStick Raspberry Pi Installer"
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo (sudo ./install.sh)"
    exit 1
fi

echo "Starting installation..."
echo ""

# Update system
echo "[1/8] Updating system packages..."
apt-get update
apt-get upgrade -y
echo "✓ System updated"
echo ""

# Install Python dependencies
echo "[2/8] Installing Python and pip..."
apt-get install -y python3-pip python3-dev
echo "✓ Python installed"
echo ""

# Install camera library
echo "[3/8] Installing Picamera library..."
apt-get install -y python3-picamera
echo "✓ Picamera installed"
echo ""

# Install other dependencies
echo "[4/8] Installing Python dependencies..."
pip3 install numpy Pillow
echo "✓ Python dependencies installed"
echo ""

# Create BlindStick directory
echo "[5/8] Creating BlindStick directory..."
mkdir -p /home/pi/BlindStick
cd /home/pi/BlindStick
echo "✓ Directory created"
echo ""

# Copy files (if they exist in current directory)
if [ -f "pi_camera_server.py" ]; then
    echo "[6/8] Copying BlindStick files..."
    cp pi_camera_server.py /home/pi/BlindStick/
    cp requirements-pi.txt /home/pi/BlindStick/ 2>/dev/null || true
    echo "✓ Files copied"
else
    echo "[6/8] Skipping file copy (run from BlindStick directory)"
fi
echo ""

# Set permissions
echo "[7/8] Setting permissions..."
chmod +x /home/pi/BlindStick/*.py 2>/dev/null || true
chown -R pi:pi /home/pi/BlindStick
echo "✓ Permissions set"
echo ""

# Create systemd service
echo "[8/8] Creating systemd service..."
cat > /etc/systemd/system/blindstick.service << EOF
[Unit]
Description=BlindStick Camera Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/BlindStick
ExecStart=/usr/bin/python3 /home/pi/BlindStick/pi_camera_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "✓ Systemd service created"
echo ""

# Enable camera
echo "Enabling camera interface..."
raspi-config nonint do_camera 0
echo "✓ Camera enabled"
echo ""

# Final configuration
echo "Applying final configurations..."
echo ""
echo "============================================================"
echo " Installation Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. After reboot, the server will start automatically"
echo "3. Find IP address: hostname -I"
echo "4. Use that IP in the mobile app to connect"
echo ""
echo "Manual start command:"
echo "  cd /home/pi/BlindStick"
echo "  python3 pi_camera_server.py"
echo ""
echo "Service commands:"
echo "  sudo systemctl start blindstick    # Start service"
echo "  sudo systemctl stop blindstick     # Stop service"
echo "  sudo systemctl status blindstick   # Check status"
echo "  sudo systemctl enable blindstick   # Auto-start on boot"
echo ""
echo "============================================================"
