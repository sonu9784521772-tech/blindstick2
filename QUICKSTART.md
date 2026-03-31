# BlindStick Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Test Installation
```bash
python test_system.py
```

### Step 3: Run with Pre-trained Model (No Dataset Needed)
```bash
python detect.py --source 0 --weights yolov8n.pt --show-display
```

**That's it!** You now have real-time object detection running.

---

## 📋 Common Commands

### Quick Tests
```bash
# Test system
python test_system.py

# Run detection with webcam
python detect.py --source 0

# Run detection with video file
python detect.py --source video.mp4
```

### Training (After Getting ORBIT Dataset)
```bash
# Prepare dataset
python prepare_dataset.py --source /path/to/orbit --output data/orbit

# Train model
python train.py --data data/orbit --epochs 100 --batch-size 16
```

### Advanced Detection
```bash
# Higher confidence threshold
python detect.py --source 0 --conf-thres 0.7

# Faster inference (smaller image size)
python detect.py --source 0 --img-size 416

# Save output video
python detect.py --source 0 --save-output
```

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `detect.py` | Real-time detection script |
| `train.py` | Training script |
| `config.yaml` | Configuration file |
| `model.py` | Object detection model |
| `tts.py` | Text-to-speech module |

---

## ⚙️ Important Settings

### In `config.yaml`:

**Detection:**
- `inference.conf_threshold`: Minimum confidence (default: 0.5)
- `priority_objects`: Objects to announce first

**TTS:**
- `tts.rate`: Speech speed (default: 150)
- `tts.volume`: Volume level (default: 0.9)

---

## 🔧 Troubleshooting

### Camera Not Working
```bash
# Try different camera index
python detect.py --source 1
# or
python detect.py --source 2
```

### Out of Memory (GPU)
```bash
# Use CPU instead
python detect.py --source 0 --device cpu

# Or use smaller model
python detect.py --source 0 --model yolov8n
```

### No Audio
```bash
# Install TTS engine
pip install pyttsx3

# Test TTS
python tts.py
```

---

## 📊 Performance Tips

**For Speed (FPS):**
- Use `yolov8n` model
- Reduce `--img-size` to 320 or 416
- Increase `--conf-thres` to 0.7

**For Accuracy:**
- Use `yolov8m` or `yolov8l` model
- Increase `--img-size` to 800
- Lower `--conf-thres` to 0.3

---

## 🎤 Using the System

1. **Start Detection**: Run `python detect.py --source 0`
2. **Listen**: The system will announce detected objects
3. **Controls**:
   - Press `q` to quit
   - Press `s` to manually trigger announcement

**What you'll hear:**
- "Detected chair at 2 meters"
- "Warning! Obstacle ahead!"
- "Person detected"

---

## 📁 Dataset Setup (ORBIT)

```bash
# Download ORBIT dataset from official source
# Then organize/prepare it:
python prepare_dataset.py --source /path/to/orbit --output data/orbit

# Verify structure:
data/orbit/
├── images/
│   ├── train/
│   └── val/
└── annotations/
    ├── train.json
    └── val.json
```

---

## 💡 Example Workflow

### Indoor Navigation Setup:
```bash
python detect.py \
  --source 0 \
  --conf-thres 0.5 \
  --announcement-interval 2.0 \
  --show-display
```

### Outdoor Assistance:
```bash
python detect.py \
  --source 0 \
  --conf-thres 0.6 \
  --model yolov8s.pt
```

---

## 📈 Next Steps

1. ✅ **Test pre-trained model** (5 min)
2. 📥 **Download ORBIT dataset** 
3. 🏋️ **Train custom model** (1-2 hours)
4. 🎯 **Fine-tune settings** in config.yaml
5. 🚀 **Deploy on device** (Raspberry Pi, Jetson, etc.)

---

## 🔗 Useful Links

- **ORBIT Dataset**: [Official website](https://orbit-dataset.github.io/)
- **YOLOv8 Docs**: [Ultralytics](https://docs.ultralytics.com/)
- **PyTorch**: [pytorch.org](https://pytorch.org/)

---

## ❓ Need Help?

1. Run `python test_system.py` to diagnose issues
2. Check `README.md` for detailed documentation
3. Review error messages in console

---

**Happy Building! 🎉**

*For more details, see README.md*
