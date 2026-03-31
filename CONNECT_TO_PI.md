# 🍓 Connect to Raspberry Pi Camera - Quick Guide

## 🎯 **What You Need:**

1. **Raspberry Pi 3** with camera module connected
2. **IP Address** of your Raspberry Pi
3. **Pi Camera Server** running on the Pi
4. **This Client** running on your PC

---

## 📋 **Step-by-Step Setup:**

### On Raspberry Pi:

#### 1. Enable Camera:
```bash
sudo raspi-config
# Interface Options → Camera → Enable
# Finish → Reboot
```

#### 2. Run Camera Server:
```bash
cd ~/BlindStick
python3 pi_camera_server.py
```

You should see:
```
============================================================
 BlindStick Raspberry Pi Camera Server
============================================================

Server IP: 192.168.1.XXX  ← NOTE THIS IP ADDRESS!
Video Stream Port: 8889
Command Port: 8890
============================================================

✓ Camera initialized successfully
✓ Server listening on 0.0.0.0:8889
✓ Command server listening on 0.0.0.0:8890

Waiting for mobile app connection...
```

### On Your PC:

#### 3. Run Client with Pi's IP:
```powershell
python pi_camera_client.py --ip YOUR_PI_IP_ADDRESS
```

**Example:**
```powershell
python pi_camera_client.py --ip 192.168.1.100
```

---

## 🔌 **Connection Flow:**

```
Raspberry Pi 3 (Camera Module)
        ↓ Captures video
    pi_camera_server.py
        ↓ Streams via WiFi
    Port 8889 (Video)
    Port 8890 (Commands)
        ↓
Your PC
        ↓ Receives stream
    pi_camera_client.py
        ↓ Processes frames
    YOLO Object Detection
        ↓ Announces
    Speaker Output
```

---

## 🎯 **Quick Commands:**

### Find Pi's IP Address:
On Raspberry Pi terminal:
```bash
hostname -I
```

### Start Pi Server:
```bash
python3 pi_camera_server.py
```

### Start PC Client:
```powershell
# Replace with actual Pi IP
python pi_camera_client.py --ip 192.168.1.100
```

---

## ✅ **Expected Result:**

When connected successfully, you'll see:

**PC Console:**
```
Connecting to Raspberry Pi at 192.168.1.100...
✓ Connected to video stream on port 8889
✓ Connected to command stream on port 8890
============================================================
 BlindStick - Raspberry Pi Camera Client
============================================================
```

**UI Window Opens Showing:**
- Live video from Pi camera
- Object detection boxes
- Distance measurements
- Voice announcements

---

## 🔧 **Troubleshooting:**

### "Connection refused":
**Problem:** Pi server not running  
**Solution:** Run `python3 pi_camera_server.py` on Pi

### "Connection timed out":
**Problem:** Different WiFi network or firewall  
**Solution:** 
- Ensure both devices on same WiFi
- Check Windows Firewall allows Python
- Disable Pi firewall temporarily:
  ```bash
  sudo ufw disable
  ```

### "No camera available" on Pi:
**Problem:** Camera not enabled or connected  
**Solution:**
```bash
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

---

## 📊 **What Happens:**

1. **Pi captures** video through camera module
2. **Pi streams** compressed JPEG frames over WiFi
3. **PC receives** frames in real-time
4. **PC processes** with YOLO AI model
5. **PC announces** detected objects via speaker

**Latency:** ~200-500ms end-to-end

---

## 🎨 **UI Features:**

### Left Panel (70%):
- Live video feed from Pi
- Colored boxes on detected objects
- Distance labels

### Right Panel (30%):
- Connection status
- Detected objects list
- Speak Now button
- Disconnect button

### Bottom Bar:
- FPS counter
- Object count
- Connection status

---

## 💡 **Pro Tips:**

### For Best Performance:
1. **5GHz WiFi** if available (less interference)
2. **Close range** to router (stronger signal)
3. **Good lighting** for camera (better detection)
4. **Stable mount** for Pi camera (less motion blur)

### Battery Power:
- Use 5V 2.5A power bank for Pi
- Expected runtime: 4-6 hours
- Camera uses ~300mA extra

---

## 🎉 **Success Indicators:**

✅ Console shows "✓ CONNECTED"  
✅ UI window opens  
✅ Live video visible (not black)  
✅ Objects have colored boxes  
✅ Right panel shows detections  
✅ Voice announces every 3 seconds  
✅ FPS shows 10-15  

---

## 📝 **Example Session:**

### Terminal 1 (on Pi):
```bash
pi@raspberrypi:~ $ cd BlindStick
pi@raspberrypi:~/BlindStick $ python3 pi_camera_server.py

============================================================
 BlindStick Raspberry Pi Camera Server
============================================================

Server IP: 192.168.1.105
Video Stream Port: 8889
Command Port: 8890
============================================================

✓ Camera initialized successfully
✓ Server listening on 0.0.0.0:8889
✓ Command server listening on 0.0.0.0:8890
```

### Terminal 2 (on PC):
```powershell
PS C:\BlindStick> python pi_camera_client.py --ip 192.168.1.105

Connecting to Raspberry Pi at 192.168.1.105...
✓ Connected to video stream on port 8889
✓ Connected to command stream on port 8890
============================================================
 BlindStick - Raspberry Pi Camera Client
============================================================
```

**Beautiful UI window opens with live Pi camera feed!**

---

## 🚀 **Ready to Connect!**

**Just give me your Pi's IP address and I'll run it for you right now!**

The client will:
- Automatically connect to Pi
- Receive live camera feed
- Detect objects in real-time
- Announce via speaker
- Show beautiful UI with all info

**Much better than local webcam - Pi camera is higher quality!** 📸✨
