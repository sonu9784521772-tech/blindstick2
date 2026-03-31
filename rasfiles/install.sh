#!/bin/bash
# INSTALLATION SCRIPT - Run ONCE on Raspberry Pi
# This will install all required packages and enable camera

echo "============================================================"
echo " 👁️ BlindStick - Installing Dependencies"
echo "============================================================"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update -y
sudo apt upgrade -y

# Install camera packages
echo ""
echo "📦 Installing camera libraries..."
sudo apt install -y \
    libcamera-tools \
    libcamera-apps-lite \
    python3-libcamera \
    python3-numpy \
    python3-pip

# Enable camera
echo ""
echo "📷 Enabling camera interface..."
sudo raspi-config nonint do_camera 1

# Set permissions
echo ""
echo "🔧 Setting permissions..."
chmod +x start_server.sh
chmod +x install.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Reboot your Raspberry Pi:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, SSH back in"
echo ""
echo "3. Navigate to rasfiles folder:"
echo "   cd ~/rasfiles"
echo ""
echo "4. Start the server:"
echo "   ./start_server.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Auto-reboot after 3 seconds
echo "🔄 Auto-rebooting in 3 seconds..."
sleep 3
sudo reboot
