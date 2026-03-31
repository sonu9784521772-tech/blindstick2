# BlindStick Raspberry Pi + Mobile App Setup Guide

Complete guide to set up your BlindStick system with Raspberry Pi 3 and mobile app.

## 📋 Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [Mobile App Setup](#mobile-app-setup)
4. [Connecting & Testing](#connecting--testing)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 Hardware Requirements

### Required:
- **Raspberry Pi 3** (Model B or B+)
- **Raspberry Pi Camera Module** (v1 or v2)
- **MicroSD Card** (8GB minimum, 16GB recommended)
- **Power Supply** (5V 2.5A for Pi 3)
- **Smartphone** (Android or iOS)
- **WiFi Network** (both devices on same network)

### Optional:
- **Battery Pack** (for portable use)
- **Phone Mount** (to attach phone to blind stick)
- **Case** for Raspberry Pi

---

## 🍓 Raspberry Pi Setup

### Step 1: Install Raspberry Pi OS

1. **Download Raspberry Pi Imager:**
   - Windows/Mac/Linux: https://www.raspberrypi.com/software/

2. **Flash Raspberry Pi OS:**
   - Insert MicroSD card into computer
   - Open Raspberry Pi Imager
   - Choose OS: **Raspberry Pi OS (32-bit)**
   - Choose Storage: Your MicroSD card
   - Click **Write**

3. **Enable WiFi (before first boot):**
   - After flashing, open the `boot` partition
   - Create file `wpa_supplicant.conf`:
   ```conf
   country=US
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   
   network={
       ssid="YOUR_WIFI_NAME"
       psk="YOUR_WIFI_PASSWORD"
   }
   ```

### Step 2: First Boot & Camera Setup

1. **Boot Raspberry Pi:**
   - Insert SD card into Pi
   - Connect power supply
   - Wait 2-3 minutes for first boot

2. **Enable Camera:**
   ```bash
   sudo raspi-config
   ```
   
   Navigate to:
   - `Interface Options` → `Camera` → `Yes`
   - `Finish` → `Reboot`

3. **Test Camera:**
   ```bash
   raspistill -o test.jpg
   ```
   
   You should hear camera shutter sound. Check if `test.jpg` was created.

### Step 3: Install Python Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python pip
sudo apt-get install -y python3-pip

# Install camera library
sudo apt-get install -y python3-picamera

# Install other dependencies
pip3 install numpy Pillow

# Download BlindStick project
cd ~
git clone <your-repo-url>  # OR copy files manually
cd BlindStick

# Install requirements
pip3 install -r requirements-pi.txt
```

### Step 4: Find Raspberry Pi IP Address

```bash
hostname -I
```

Note down the first IP address (e.g., `192.168.1.100`)

### Step 5: Run Camera Server

```bash
cd ~/BlindStick
python3 pi_camera_server.py
```

You should see:
```
============================================================
 BlindStick Raspberry Pi Camera Server
============================================================

Server IP: 192.168.1.100
Video Stream Port: 8889
Command Port: 8890
============================================================

✓ Camera initialized successfully
✓ Server listening on 0.0.0.0:8889
✓ Command server listening on 0.0.0.0:8890

Waiting for mobile app connection...
```

**Leave this running!** The Pi is now ready to stream video.

---

## 📱 Mobile App Setup

### For Android

#### Option A: Build from Source (Recommended for Development)

1. **Install Flutter:**
   - Download from: https://flutter.dev/docs/get-started/install
   - Follow installation instructions for your OS

2. **Setup Project:**
   ```bash
   cd BlindStick/mobile_app
   
   # Get dependencies
   flutter pub get
   
   # Check setup
   flutter doctor
   ```

3. **Connect Android Device:**
   - Enable Developer Options on phone
   - Enable USB Debugging
   - Connect via USB

4. **Run App:**
   ```bash
   flutter run
   ```

#### Option B: Install APK (Easiest)

1. **Build APK:**
   ```bash
   cd BlindStick/mobile_app
   flutter build apk --release
   ```
   
   APK location: `build/app/outputs/flutter-apk/app-release.apk`

2. **Transfer to Phone:**
   - Copy APK to phone
   - Install (enable "Install from Unknown Sources" if needed)

### For iOS

1. **Install Xcode** (Mac only)

2. **Setup Project:**
   ```bash
   cd BlindStick/mobile_app
   flutter pub get
   ```

3. **Open in Xcode:**
   ```bash
   open ios/Runner.xcworkspace
   ```

4. **Configure Signing:**
   - Add Apple ID account in Xcode preferences
   - Select development team

5. **Run on Device:**
   - Connect iPhone/iPad
   - Select device in Xcode
   - Click Play button

---

## 🔌 Connecting & Testing

### Step 1: Connect Mobile App to Pi

1. **Ensure both devices on same WiFi**

2. **Open BlindStick app**

3. **Go to "Connect" tab**

4. **Enter Raspberry Pi IP address**
   - Example: `192.168.1.100`

5. **Tap "Connect"**

6. **Wait for connection confirmation**
   - Should show "Connected to Raspberry Pi"
   - WiFi icon turns green

### Step 2: Test Video Stream

1. **Go to "Detect" tab**

2. **You should see live camera feed** from Pi

3. **Check for lag:**
   - Normal: 200-500ms delay
   - If very slow, check WiFi signal

### Step 3: Test Object Detection

1. **Point camera at objects**

2. **Watch detection results** at bottom of screen

3. **Listen for announcements:**
   - App should speak detected objects
   - "Chair detected at 2 meters"

4. **Test "Speak" button:**
   - Tap to hear current detections

5. **Test "Capture" button:**
   - Takes high-quality photo
   - Processes for better accuracy

### Step 4: Adjust Settings

Go to **Settings** tab:

- **Speech Rate**: Adjust speaking speed
- **Volume**: Set comfortable volume
- **Announcement Interval**: How often to speak (default: 3 seconds)

---

## 🎯 Usage Instructions

### Basic Operation:

1. **Power on Raspberry Pi** (battery or USB power)
2. **Start camera server:**
   ```bash
   cd ~/BlindStick
   python3 pi_camera_server.py
   ```
3. **Open mobile app**
4. **Connect to Pi** (auto-connects if previously connected)
5. **Mount phone on blind stick**
6. **Start walking** - app will announce objects

### Voice Announcements:

The app announces objects within **20 meters**:

- **Very Close**: < 2 meters - "Warning! Chair very close, 1.5 meters"
- **Nearby**: 2-5 meters - "Person nearby, 3.2 meters"
- **Ahead**: 5-10 meters - "Table ahead, 7.5 meters"
- **In Front**: 10-20 meters - "Car in front, 15 meters"

### Priority Objects:

System prioritizes important objects:
- People
- Vehicles (cars, bicycles)
- Obstacles
- Furniture (chairs, tables)
- Stairs/doors

---

## 🔧 Troubleshooting

### Camera Not Working

**Problem:** "Camera initialization failed"

**Solutions:**
1. Check camera connection (ribbon cable fully inserted)
2. Enable camera: `sudo raspi-config → Interface Options → Camera`
3. Test camera: `raspistill -o test.jpg`
4. Reboot Pi: `sudo reboot`

### Connection Failed

**Problem:** Can't connect to Raspberry Pi

**Solutions:**
1. **Check both devices on same WiFi**
2. **Verify IP address:**
   ```bash
   hostname -I
   ```
3. **Check firewall:**
   ```bash
   sudo ufw allow 8889
   sudo ufw allow 8890
   ```
4. **Restart server:**
   ```bash
   Ctrl+C
   python3 pi_camera_server.py
   ```

### No Video Feed

**Problem:** Connected but no video

**Solutions:**
1. **Check server is running** on Pi
2. **Restart streaming:**
   - Disconnect in app
   - Stop server on Pi (Ctrl+C)
   - Restart server
   - Reconnect
3. **Reduce resolution:**
   - Edit `pi_camera_server.py`
   - Change `self.resolution = (640, 480)` to `(320, 240)`

### No Audio/Speech

**Problem:** App not speaking

**Solutions:**
1. **Check phone volume**
2. **Enable speech in app settings**
3. **Test speech:** Settings → "Test Speech" button
4. **Check TTS engine:**
   - Android: Settings → Accessibility → Text-to-speech
   - iOS: Settings → Accessibility → Spoken Content

### Slow Performance

**Problem:** Laggy video or delayed announcements

**Solutions:**
1. **Reduce frame rate:**
   - Edit `pi_camera_server.py`
   - Change `self.fps = 10` (from 15)
2. **Reduce resolution:**
   - Change `self.resolution = (320, 240)`
3. **Increase announcement interval:**
   - App Settings → Announcement Interval → 5 seconds
4. **Move closer to WiFi router**

### App Crashes

**Problem:** App closes unexpectedly

**Solutions:**
1. **Restart app**
2. **Clear app cache** (Android settings)
3. **Reinstall app**
4. **Check phone compatibility:**
   - Android 8.0+ required
   - iOS 12.0+ required

---

## 🚀 Advanced Configuration

### Auto-Start on Raspberry Pi Boot

Create systemd service:

```bash
sudo nano /etc/systemd/system/blindstick.service
```

Add:
```ini
[Unit]
Description=BlindStick Camera Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/BlindStick
ExecStart=/usr/bin/python3 /home/pi/BlindStick/pi_camera_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable blindstick.service
sudo systemctl start blindstick.service
```

Now server starts automatically on boot!

### Static IP Address

Edit dhcpcd config:
```bash
sudo nano /etc/dhcpcd.conf
```

Add at bottom:
```conf
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Reboot:
```bash
sudo reboot
```

Pi will always have same IP: `192.168.1.100`

### Battery Power Setup

For portable operation:
1. **Use 5V 2A battery pack** (phone charger battery)
2. **Connect to MicroUSB port** on Pi
3. **Expected runtime:** 4-6 hours with 10000mAh battery

---

## 📊 Performance Metrics

### Expected Performance:

| Metric | Value |
|--------|-------|
| Latency | 200-500ms |
| Frame Rate | 10-15 FPS |
| Detection Range | 1-20 meters |
| Announcement Delay | 3 seconds (configurable) |
| Power Consumption | ~500mA (Pi 3) |
| Battery Life | 4-6 hours (10000mAh) |

### Optimization Tips:

**For Faster Performance:**
- Reduce resolution to 320x240
- Lower FPS to 10
- Use wired Ethernet (with adapter)

**For Better Detection:**
- Increase resolution to 800x600
- Ensure good lighting
- Keep camera lens clean

---

## 🎉 Success Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Camera module enabled and tested
- [ ] Python dependencies installed
- [ ] Camera server runs without errors
- [ ] Mobile app installed on phone
- [ ] Both devices on same WiFi
- [ ] App connects to Pi successfully
- [ ] Live video feed visible in app
- [ ] Object detection working
- [ ] Speech announcements working
- [ ] Settings configured properly

---

## 📞 Support & Resources

### Documentation:
- [Main README](../README.md)
- [Quick Start](../QUICKSTART.md)
- [Flutter Documentation](https://flutter.dev/docs)
- [Raspberry Pi Docs](https://www.raspberrypi.org/documentation/)

### Common Commands:

**Raspberry Pi:**
```bash
# Check IP address
hostname -I

# Test camera
raspistill -o test.jpg

# Run server
python3 pi_camera_server.py

# Check if server running
ps aux | grep python3

# Restart server
sudo systemctl restart blindstick.service
```

**Mobile App:**
```bash
# Get dependencies
flutter pub get

# Run on device
flutter run

# Build release APK
flutter build apk --release

# Check connected devices
flutter devices
```

---

## 🌟 Next Steps

1. **Test indoors** first with simple objects
2. **Calibrate distance estimation** for your setup
3. **Customize object priorities** in config
4. **Add more object classes** by retraining model
5. **Integrate TensorFlow Lite** for on-device ML

---

**Congratulations! Your BlindStick system is ready to use! 🎊**

*For questions or issues, check troubleshooting section or consult documentation.*
