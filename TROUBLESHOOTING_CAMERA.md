# Troubleshooting Guide: No Camera Feed in App

## Problem
Camera feed not showing visuals from Raspberry Pi camera in the BlindStick app.

## Changes Made to Fix Blue Tint Issue

### Files Modified (Mobile App ONLY):
1. **`mobile_app/lib/screens/camera_view_screen.dart`**
   - Removed problematic `ColorFiltered` widget that was blocking visuals
   - Simplified image display to use raw `Image.memory()` 
   - Added debug logging for frame reception

2. **`mobile_app/lib/services/connection_service.dart`**
   - Added detailed debug logging to track data flow
   - Logs bytes received from socket
   - Logs frame sizes and streaming status

3. **`mobile_app/lib/services/detection_service.dart`**
   - Enhanced comments to emphasize NO color processing
   - Clarified raw image preservation

### NO Changes to Raspberry Pi Code
The Pi server code (`pi_camera_server.py`) was NOT modified.

---

## How to Test

### Step 1: Restart the Flutter App
```bash
cd d:\blindstick\BlindStick\mobile_app

# Stop current app (Ctrl+C if running)

# Clean and rebuild
flutter clean
flutter run
```

### Step 2: Watch Debug Logs
When you run the app, you should see these debug messages in the terminal:

**Expected Output:**
```
📡 Received 15234 bytes from socket
🖼️ Expected frame size: 15230 bytes
✅ Adding frame to stream: 15230 bytes
📸 Received frame: 15230 bytes
```

**If you DON'T see these messages:**
- The Pi is not sending data
- Check network connection
- Verify Pi server is running

### Step 3: Verify Connection Status
In the app UI, check the top-right corner:
- ✅ **Green "Connected"** = Good connection
- ❌ **Red "Disconnected"** = Not connected to Pi

### Step 4: Check Raspberry Pi Server
On your Raspberry Pi, verify the server is running:
```bash
python pi_camera_server.py
```

**Expected output on Pi:**
```
✓ Client connected from 192.168.x.x
Frames sent: 30
Frames sent: 60
```

---

## Common Issues & Solutions

### Issue 1: "No camera feed" message in app
**Cause:** Not connected to Raspberry Pi

**Solution:**
1. Go to Connection Screen in app
2. Enter correct Pi IP address
3. Tap "Connect"
4. Wait for green "Connected" status

### Issue 2: Black screen but logs show frames received
**Cause:** Image decoding issue or codec problem

**Solution:**
The JPEG format from Pi might need adjustment. Try modifying Pi camera settings:
```python
# In pi_camera_server.py, line 238
format='jpeg',  # Keep as JPEG
quality=85,     # Adjust quality (75-95)
```

### Issue 3: Logs show 0 bytes or very small frames
**Cause:** Camera not initialized or streaming error

**Solution:**
Check Pi camera connection:
```bash
# Test camera on Pi
raspistill -o test.jpg

# If this fails:
sudo raspi-config
# Enable camera: Interface Options -> Camera
```

### Issue 4: Blue/purple tint on visuals
**Cause:** Color space conversion issue

**Current Fix:**
We're now displaying raw JPEG data without any color processing. This should show natural colors.

---

## Quick Diagnostic Commands

### On Windows (check connectivity):
```powershell
# Ping your Raspberry Pi
ping <PI_IP_ADDRESS>
```

### On Raspberry Pi:
```bash
# Check if server ports are listening
netstat -tlnp | grep 8889
netstat -tlnp | grep 8890

# Check camera module
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera capture
raspistill -o /tmp/test.jpg -v
```

---

## What Changed from Original Code?

### Before (with blue tint):
```dart
Image.memory(
  _currentFrame!,
  fit: BoxFit.contain,
)
```

### After (raw visuals, no processing):
```dart
Image.memory(
  _currentFrame!,
  fit: BoxFit.contain,
  cacheWidth: 640,
  cacheHeight: 480,
)
```

**Key improvements:**
- ✅ No automatic color enhancement
- ✅ No filters or adjustments
- ✅ Direct JPEG rendering
- ✅ Better performance with caching
- ✅ Debug logging for troubleshooting

---

## Next Steps

1. **Rebuild the app** with `flutter clean && flutter run`
2. **Connect to Pi** from the app's connection screen
3. **Watch the logs** in terminal for frame reception
4. **Report back** what you see in the logs

If still not working, share:
- Terminal logs from Flutter app
- Console output from Pi server
- Connection status shown in app
