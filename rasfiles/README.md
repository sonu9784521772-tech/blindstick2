# 📁 rasfiles - Complete Raspberry Pi Setup

## 📋 What's in This Folder?

This folder contains **ALL files needed** to run BlindStick on Raspberry Pi.

---

## 📂 Files Included

### 1. **`camera_server.py`** ← MAIN SERVER CODE
The actual Python server that streams video from camera.

**Run with:**
```bash
python3 camera_server.py
```

---

### 2. **`install.sh`** ← INSTALLATION SCRIPT
Installs all required packages and enables camera.
**Run this ONCE only!**

**Run with:**
```bash
chmod +x install.sh
./install.sh
```

This will:
- Update system
- Install libcamera packages
- Enable camera interface
- Reboot automatically

---

### 3. **`start_server.sh`** ← QUICK START SCRIPT
Easy launcher for the server (no need to type python3 command).

**Run with:**
```bash
./start_server.sh
```

---

### 4. **`README.md`** ← THIS FILE
Instructions and documentation.

---

## ⚡ QUICK START GUIDE

### First Time Setup (ONE TIME):

```bash
# Step 1: Navigate to folder
cd ~/rasfiles

# Step 2: Run installation
chmod +x install.sh
./install.sh

# Wait for reboot (~2 minutes)
# Then SSH back in
```

### Every Time You Want to Use It:

```bash
# Step 1: Navigate to folder
cd ~/rasfiles

# Step 2: Start server
./start_server.sh

# That's it! Server is running!
```

---

## 🎯 Expected Output

When you run `./start_server.sh`:

```
============================================================
 👁️ BlindStick Camera Server - Starting...
============================================================

🔍 Checking camera...
✓ Camera detected

🚀 Starting server...

============================================================
 👁️ BlindStick Pi Camera Server
============================================================

📡 IP: 172.22.11.180
📹 Port: 8889
🎮 Commands: 8890
⚡ FPS: 7
============================================================

✓ Listening on :8889
✓ Commands on :8890

⏳ Waiting for Windows client...
   Press Ctrl+C to stop

✅ Client connected from 192.168.1.100

🎬 Streaming at 7 FPS...

📊 Sent: 30 (7.1 FPS)
```

---

## 🔧 Troubleshooting

### Problem: "Permission denied"
**Solution:**
```bash
chmod +x install.sh start_server.sh
```

### Problem: "File not found"
**Solution:**
Make sure you're in the right directory:
```bash
pwd
# Should show: /home/pi/rasfiles or /home/arcrobo/rasfiles

cd ~/rasfiles
```

### Problem: "libcamera-hello: command not found"
**Solution:**
Run the install script first:
```bash
./install.sh
```

### Problem: "No cameras available"
**Solution:**
1. Check camera is physically connected
2. Power off Pi, reseat cable, power on
3. Run install script again

---

## 📊 How Many Files to Run?

**Answer: Just ONE file to run regularly!**

| File | When to Run | Frequency |
|------|-------------|-----------|
| `install.sh` | First time setup only | ONCE |
| `start_server.sh` | Every time you use it | EVERY TIME |
| `camera_server.py` | Alternative to start_server.sh | Optional |

**Simple workflow:**
1. First day: Run `install.sh` (once)
2. Every use: Run `start_server.sh`

---

## 🎯 To Stop the Server

Press: **`Ctrl+C`**

---

## ✅ Checklist Before Running

Before using `start_server.sh`:

- [ ] Already ran `install.sh` once
- [ ] Already rebooted after installation
- [ ] In correct directory (`cd ~/rasfiles`)
- [ ] Camera is connected physically
- [ ] Ready to connect from Windows

---

## 🆘 Need Help?

If issues persist:

1. Check logs carefully for error messages
2. Verify camera connection
3. Try rebooting: `sudo reboot`
4. Re-run install script: `./install.sh`

---

## 📞 Connection Info

**Windows connects to:**
- IP: Your Pi's IP (shown when server starts)
- Video Port: `8889`
- Command Port: `8890`

**On Windows laptop:**
```bash
python ui_app.py
```

It will auto-connect to the Pi!

---

**That's all you need! Simple and clean! 🚀**

*Last Updated: March 31, 2026*
*Version: 1.0 - Organized in rasfiles*
