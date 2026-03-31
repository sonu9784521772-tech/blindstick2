# BlindStick Raspberry Pi + Mobile App - Quick Reference

## 🚀 Quick Start (5 Minutes)

### On Raspberry Pi:
```bash
# 1. Run camera server
cd ~/BlindStick
python3 pi_camera_server.py
```

**Keep terminal open!** Note the IP address shown.

### On Mobile Phone:
1. Install Flutter (or use pre-built APK)
2. Build and run app: `flutter run`
3. Enter Pi's IP address in Connect tab
4. Tap "Connect"
5. Go to "Detect" tab - you should see video feed!

---

## 📁 Project Structure

```
BlindStick/
├── pi_camera_server.py      # Raspberry Pi server
├── requirements-pi.txt       # Pi dependencies
├── mobile_app/               # Flutter app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── services/
│   │   │   ├── connection_service.dart
│   │   │   ├── detection_service.dart
│   │   │   └── speech_service.dart
│   │   └── screens/
│   │       ├── home_screen.dart
│   │       ├── camera_view_screen.dart
│   │       ├── connection_screen.dart
│   │       └── settings_screen.dart
│   └── pubspec.yaml
└── PI_APP_SETUP.md          # Detailed setup guide
```

---

## 🔑 Key Files & Their Purpose

| File | Purpose | Runs On |
|------|---------|---------|
| `pi_camera_server.py` | Streams camera video | Raspberry Pi |
| `connection_service.dart` | Manages WiFi connection | Mobile App |
| `detection_service.dart` | Object detection | Mobile App |
| `speech_service.dart` | Text-to-speech | Mobile App |
| `camera_view_screen.dart` | Shows camera feed | Mobile App |

---

## 🎯 Common Commands

### Raspberry Pi Terminal

```bash
# Find IP address
hostname -I

# Test camera
raspistill -o test.jpg

# Run server
python3 pi_camera_server.py

# Enable camera (if not working)
sudo raspi-config → Interface Options → Camera
```

### Mobile Development

```bash
# Navigate to app folder
cd BlindStick/mobile_app

# Install dependencies
flutter pub get

# Run on connected device
flutter run

# Build Android APK
flutter build apk --release

# Check connected devices
flutter devices
```

---

## 🔌 Connection Flow

```
Raspberry Pi Camera Module
        ↓
    Captures Video
        ↓
    pi_camera_server.py
        ↓
    Streams via WiFi (Port 8889)
        ↓
Mobile App (ConnectionService)
        ↓
    Processes Frames
        ↓
    Detects Objects (1-20m)
        ↓
    Announces via Speaker
```

---

## ⚙️ Default Settings

### Network
- **Video Port:** 8889
- **Command Port:** 8890
- **Protocol:** TCP/IP over WiFi

### Camera
- **Resolution:** 640x480
- **Frame Rate:** 15 FPS
- **Format:** JPEG

### Detection
- **Range:** 1-20 meters
- **Priority:** Objects < 5m
- **Announcement Interval:** 3 seconds

### Speech
- **Language:** English (US)
- **Rate:** 0.5 (medium)
- **Volume:** 1.0 (maximum)

---

## 🎤 Voice Announcements

The app announces objects based on distance:

| Distance | Announcement Example |
|----------|---------------------|
| < 2m | "Warning! Chair **very close**, 1.5 meters" |
| 2-5m | "Person **nearby**, 3.2 meters" |
| 5-10m | "Table **ahead**, 7.5 meters" |
| 10-20m | "Car **in front**, 15 meters" |

---

## 🔧 Troubleshooting Quick Fixes

### No Camera Feed
```bash
# On Pi, check camera connection
raspistill -o test.jpg

# If fails, enable camera
sudo raspi-config → Interface Options → Camera
```

### Can't Connect
```bash
# Verify Pi IP address
hostname -I

# Check if server is running
ps aux | grep pi_camera_server.py

# Restart server
Ctrl+C → python3 pi_camera_server.py
```

### No Audio
1. Check phone volume
2. Enable speech in app Settings
3. Tap "Test Speech" button

### Slow Performance
- Reduce resolution: Edit `pi_camera_server.py` line 27
- Lower FPS: Change `self.fps = 10`
- Increase announcement interval in app settings

---

## 📊 Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Latency | < 300ms | < 500ms |
| FPS | 15 | 10+ |
| Detection Accuracy | > 85% | > 75% |
| Announcement Delay | 3s | 2-5s |

---

## 🔋 Power Requirements

### Raspberry Pi 3
- **Input:** 5V 2.5A
- **Consumption:** ~500mA (idle), ~800mA (camera active)
- **Battery:** 10000mAh → 4-6 hours runtime

### Recommended Battery Packs
- Anker PowerCore 10000
- Xiaomi Mi Power Bank 2
- Any 5V 2A USB power bank

---

## 📱 Mobile App Tabs

### 1. Detect Tab
- Live camera feed
- Object detection display
- Speak/Capture buttons

### 2. Connect Tab
- WiFi connection setup
- Pi IP address entry
- Connection status

### 3. Settings Tab
- Speech rate/volume
- Announcement interval
- Test speech button

---

## 🎯 Testing Checklist

### Before First Use:
- [ ] Camera enabled on Pi (`raspistill -o test.jpg` works)
- [ ] Server runs without errors
- [ ] Both devices on same WiFi
- [ ] App connects successfully
- [ ] Video feed visible
- [ ] Speech working (test in Settings)

### Regular Use:
- [ ] Pi powered on and server running
- [ ] Camera lens clean
- [ ] Phone charged
- [ ] Volume set appropriately
- [ ] WiFi signal strong

---

## 💡 Tips for Best Results

### Hardware Setup:
1. Mount camera at chest height
2. Angle slightly downward (10-15°)
3. Keep lens clean
4. Use stable mount

### Software Configuration:
1. Start with default settings
2. Adjust speech rate to preference
3. Set announcement interval to 3-5 seconds
4. Test indoors first

### Usage Technique:
1. Walk at normal pace
2. Listen for announcements
3. Pause when object announced
4. Turn toward sound for better detection

---

## 🔗 Important Links

- **Detailed Setup:** [PI_APP_SETUP.md](PI_APP_SETUP.md)
- **Main README:** [README.md](README.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Flutter Docs:** https://flutter.dev/docs
- **Raspberry Pi Docs:** https://www.raspberrypi.org/documentation/

---

## 🆘 Emergency Commands

### Force Stop Server (Pi)
```bash
Ctrl+C
# or
killall python3
```

### Restart Everything
```bash
# On Pi:
sudo reboot

# On App:
Disconnect → Close App → Reopen → Connect
```

### Reset to Defaults
```bash
# Delete app data (Android):
Settings → Apps → BlindStick → Storage → Clear Data

# Reinstall app:
flutter clean
flutter pub get
flutter run
```

---

## 📈 Next Steps After Setup

1. **Test Basic Functionality**
   - Detect chairs, tables, people
   - Verify distance estimates
   - Adjust speech settings

2. **Optimize for Your Environment**
   - Indoor vs outdoor testing
   - Different lighting conditions
   - Various object distances

3. **Customize Settings**
   - Announcement frequency
   - Priority objects
   - Speech characteristics

4. **Deploy on Device**
   - Mount phone on blind stick
   - Portable battery setup
   - Cable management

---

**Quick Reference Card - Keep Handy During Setup!** 📋

*For detailed instructions, see [PI_APP_SETUP.md](PI_APP_SETUP.md)*
