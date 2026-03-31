# 🚀 COMPLETE SETUP INSTRUCTIONS

## For Raspberry Pi OS Lite

---

## 📦 STEP 1: Copy rasfiles Folder to Your Pi

Transfer the entire `rasfiles` folder to your Raspberry Pi home directory.

**Option A: Using SCP (from Windows)**
```powershell
# In PowerShell on Windows
scp -r rasfiles pi@YOUR_PI_IP:/home/pi/
```

**Option B: Create directly on Pi**
```bash
# SSH into Pi
ssh pi@YOUR_PI_IP

# Create folder and files
mkdir ~/rasfiles
cd ~/rasfiles

# Then create each file with nano (copy code from Windows)
nano camera_server.py
nano install.sh
nano start_server.sh
nano README.md
```

---

## ⚙️ STEP 2: Install Dependencies (ONE TIME ONLY)

```bash
# Navigate to folder
cd ~/rasfiles

# Make install script executable
chmod +x install.sh

# Run installation
./install.sh
```

**This will:**
- Update system packages
- Install libcamera libraries
- Enable camera interface
- Reboot automatically

**⏳ Wait for reboot (~2 minutes), then SSH back in!**

---

## ▶️ STEP 3: Start the Server (EVERY TIME YOU USE IT)

After reboot, SSH back in:

```bash
# Navigate to folder
cd ~/rasfiles

# Start server
./start_server.sh
```

**That's it! Server is now running!**

---

## 💻 STEP 4: Connect from Windows

On your Windows laptop:

```bash
python ui_app.py
```

It will automatically connect to your Pi!

---

## 📊 Summary: What to Run When

### First Time Setup:
```bash
cd ~/rasfiles
chmod +x install.sh
./install.sh
# Wait for reboot
```

### Every Time You Use It:
```bash
cd ~/rasfiles
./start_server.sh
```

**That's ALL! Just ONE command to run each time! 🎉**

---

## ✅ Expected Output

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

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Permission denied" | `chmod +x install.sh start_server.sh` |
| "File not found" | `cd ~/rasfiles` first |
| "libcamera not found" | Run `./install.sh` again |
| "No cameras available" | Check physical connection, reboot |

---

## 📁 Files in This Folder

1. **`camera_server.py`** - Main Python server code
2. **`install.sh`** - One-time installation script
3. **`start_server.sh`** - Quick launch script (use this!)
4. **`README.md`** - Documentation

**Total files to run regularly: JUST ONE → `start_server.sh`**

---

## 🎯 To Stop Server

Press: **`Ctrl+C`**

---

**Simple, organized, ready-to-use! 🚀**

*Created: March 31, 2026*
