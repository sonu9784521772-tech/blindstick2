# 🔧 BlindStick Error Fix Guide

## Quick Fix - Choose Your Path

### ✅ **RECOMMENDED: Use Simple Python Version** (Works NOW!)

**No Flutter, no mobile setup needed!**

```powershell
# Step 1: Check if you have dependencies
python check_requirements.py

# Step 2: If missing packages, install them
pip install -r requirements.txt

# Step 3: Run the simple version
python simple_app.py
```

**This will work immediately** and gives you the same object detection functionality!

---

## 📱 Mobile App Errors (Flutter)

### Error: "Target of URI doesn't exist: 'package:flutter/...'"

**Cause:** Flutter SDK not installed or dependencies not fetched

#### Solution A: Install Flutter (Full Setup)

See: [`INSTALL_FLUTTER.md`](INSTALL_FLUTTER.md)

#### Solution B: Use Python Alternative (Recommended for Testing)

Just run the Python version instead:
```powershell
python simple_app.py
```

---

## 🐍 Python Errors & Solutions

### Error: "ModuleNotFoundError: No module named 'torch'"

**Solution:**
```powershell
pip install torch torchvision
```

Or install all at once:
```powershell
pip install -r requirements.txt
```

### Error: "No module named 'cv2'"

**Solution:**
```powershell
pip install opencv-python
```

### Error: "No module named 'ultralytics'"

**Solution:**
```powershell
pip install ultralytics
```

### Error: "No module named 'pyttsx3'"

**Solution:**
```powershell
pip install pyttsx3
```

---

## ⚡ One-Command Fix

Run this to check and fix everything:

```powershell
# Navigate to project
cd C:\Users\Tashu\OneDrive\Desktop\BlindStick

# Check what's missing
python check_requirements.py

# Install missing packages
pip install -r requirements.txt

# Test it works
python simple_app.py
```

---

## 🎯 Specific Error Messages & Fixes

### Camera Errors

**Error:** "Camera not found" or "Cannot open camera"

**Solutions:**
1. Check camera is connected
2. Try different USB port
3. On Windows, close other apps using camera (Zoom, Teams, etc.)
4. Try camera index 1 or 2:
   ```python
   python simple_app.py  # Change source=0 to source=1 in code
   ```

### TTS (Text-to-Speech) Errors

**Error:** "TTS not available" or "Failed to initialize engine"

**Solutions:**
1. Install pyttsx3:
   ```powershell
   pip install pyttsx3
   ```
2. On Windows, also install:
   ```powershell
   pip install comtypes
   ```
3. Restart your computer (sometimes needed for TTS drivers)

### CUDA/GPU Errors

**Error:** "CUDA out of memory" or GPU-related crashes

**Solutions:**
1. Use CPU instead:
   ```powershell
   # Edit simple_app.py or detect.py
   # Add device='cpu' parameter
   ```

2. Or reduce batch size in training:
   ```powershell
   python train.py --batch-size 8
   ```

### Performance Issues

**Problem:** Slow FPS (< 5)

**Solutions:**
1. Reduce image size in code:
   ```python
   # In simple_app.py or detect.py
   # Look for img_size parameter and reduce it
   img_size=416  # Instead of 640
   ```

2. Use smaller model:
   ```powershell
   python simple_app.py --weights yolov8n.pt  # Nano model (fastest)
   ```

3. Close other applications

---

## 🔍 Diagnostic Commands

Use these to check your system:

```powershell
# Check Python version
python --version

# Check installed packages
pip list

# Check if camera works
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"

# Check PyTorch CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# Quick test
python check_requirements.py
```

---

## 🆘 Still Having Issues?

### Nuclear Option - Complete Reinstall

```powershell
# Uninstall everything
pip uninstall torch torchvision opencv-python ultralytics pyttsx3 numpy pillow

# Clear pip cache
pip cache purge

# Reinstall fresh
pip install --upgrade pip
pip install -r requirements.txt

# Test
python check_requirements.py
python simple_app.py
```

### Virtual Environment (Clean Setup)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1  # PowerShell
# or
.\venv\Scripts\activate.bat  # CMD

# Install fresh
pip install -r requirements.txt

# Test
python simple_app.py
```

---

## ✅ Success Checklist

Your system is working correctly when:

- [ ] `python check_requirements.py` shows all ✓
- [ ] `python simple_app.py` opens camera window
- [ ] Objects are detected (boxes drawn on screen)
- [ ] FPS counter shows > 5 FPS
- [ ] Audio announcements work (if TTS installed)
- [ ] Pressing 'q' closes the app cleanly

---

## 📞 Getting More Help

If errors persist:

1. **Run diagnostics:**
   ```powershell
   python check_requirements.py > error_log.txt
   ```

2. **Check error_log.txt** for specific missing packages

3. **Search for exact error message** + "BlindStick" or "object detection"

4. **Try the PC version first** before mobile app setup

---

## 🎯 Recommended Workflow

**For fastest results:**

1. ✅ Start with `simple_app.py` (works in 5 minutes)
2. ✅ Test object detection on PC
3. ✅ Later: Set up Raspberry Pi + mobile app
4. ✅ Finally: Customize and optimize

**Don't let Flutter installation block you from testing!**

---

**Quick Start Command:**
```powershell
cd C:\Users\Tashu\OneDrive\Desktop\BlindStick
python check_requirements.py
python simple_app.py
```

*This bypasses all mobile app complexity and gets you running immediately!*
