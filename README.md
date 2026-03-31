# BlindStick - AI-Powered Assistive Navigation Device

An intelligent object detection and navigation assistant for visually impaired individuals, powered by deep learning and text-to-speech technology.

## 🎯 Project Overview

BlindStick is a comprehensive assistive device that uses computer vision to detect objects, obstacles, and navigate the environment. It provides real-time audio feedback through speakers to help users understand their surroundings and move safely.

### Key Features

- **Real-time Object Detection**: Detects multiple objects simultaneously using state-of-the-art YOLO models
- **Distance Estimation**: Estimates distance to detected objects
- **Audio Feedback**: Text-to-speech announcements of detected objects and warnings
- **Priority Detection**: Prioritizes important objects (people, vehicles, obstacles)
- **Warning System**: Alerts users to potential dangers
- **Camera Support**: Works with webcams, USB cameras, and video files
- **Customizable**: Configurable thresholds, priorities, and speech settings

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (optional but recommended for faster inference)
- Camera device (webcam or USB camera)

### Step 1: Clone/Setup Project

```bash
cd BlindStick
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter issues with PyTorch CUDA installation, visit [pytorch.org](https://pytorch.org/get-started/locally/) for the correct installation command for your system.

### Step 3: Download ORBIT Dataset

The ORBIT dataset is used for training the object detection model. 

1. Download the ORBIT dataset from the official source
2. Organize it in the following structure:

```
data/
└── orbit/
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── annotations/
        ├── train.json
        ├── val.json
        └── test.json
```

Alternatively, use YOLO format:

```
data/
└── orbit/
    ├── images/
    │   ├── train/
    │   └── val/
    └── labels/
        ├── train/
        └── val/
```

## 🚀 Quick Start

### Using Pre-trained Model (Recommended for Testing)

Run real-time detection with a pre-trained YOLOv8 model:

```bash
python detect.py --source 0 --weights yolov8n.pt --show-display
```

### Using Custom Trained Model

After training your own model (see Training section):

```bash
python detect.py --source 0 --weights runs/train/blindstick_detector/weights/best.pt
```

### Command Options

```bash
# Basic usage with webcam
python detect.py --source 0

# With custom confidence threshold
python detect.py --source 0 --conf-thres 0.6

# Save output video
python detect.py --source 0 --save-output

# Process video file
python detect.py --source path/to/video.mp4 --save-output

# Run without display (headless mode)
python detect.py --source 0
```

## 🏋️ Training

### Train on ORBIT Dataset

```bash
# Using default configuration
python train.py --config config.yaml

# Custom parameters
python train.py --data data/orbit --epochs 100 --batch-size 16 --model yolov8n
```

### Training Options

```bash
# Resume training
python train.py --resume runs/train/blindstick_detector/weights/last.pt

# Use pretrained weights
python train.py --pretrained yolov8s.pt --epochs 150

# Specify GPU
python train.py --device cuda:0
```

### Monitoring Training

Training results are saved to `runs/train/`. Monitor:
- Loss curves
- mAP metrics
- Precision/Recall curves
- Model checkpoints

## 📁 Project Structure

```
BlindStick/
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── dataset.py              # Dataset loader and preprocessing
├── model.py                # Object detection model wrapper
├── train.py                # Training script
├── detect.py               # Real-time inference script
├── tts.py                  # Text-to-speech module
├── README.md               # This file
└── data/                   # Dataset directory
    └── orbit/
        ├── images/
        └── annotations/
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

### Model Settings
- `model.type`: YOLO model variant (yolov8n/s/m/l/x)
- `model.num_classes`: Number of object classes

### Training Settings
- `training.epochs`: Number of training epochs
- `training.batch_size`: Batch size
- `training.lr0`: Initial learning rate

### Inference Settings
- `inference.conf_threshold`: Detection confidence threshold
- `inference.iou_threshold`: IoU threshold for NMS

### TTS Settings
- `tts.rate`: Speech rate
- `tts.volume`: Volume level
- `tts.voice`: Voice selection

### Priority Objects
Define which objects to announce first:
```yaml
priority_objects:
  - person
  - car
  - bicycle
  - obstacle
```

## 🔧 Usage Examples

### Example 1: Indoor Navigation

```bash
python detect.py --source 0 --conf-thres 0.5 --announcement-interval 2.0
```

This configuration:
- Uses default confidence threshold
- Announces objects every 2 seconds
- Ideal for indoor environments

### Example 2: Outdoor Assistance

```bash
python detect.py --source 0 --conf-thres 0.6 --max-detections 50
```

Higher confidence threshold for outdoor scenes with more objects.

### Example 3: Video Analysis

```bash
python detect.py --source walking_path.mp4 --save-output --show-display
```

Analyze recorded video and save annotated output.

## 🎤 Text-to-Speech Features

The system provides various audio announcements:

### Object Announcements
- "Detected chair at 2 meters"
- "Detected person and table"
- "Detected door, stairs, and chair"

### Warnings
- "Warning! Obstacle ahead!"
- "Caution! Stairs detected!"
- "Person nearby!"

### Controls
- Press 'q' to quit
- Press 's' to manually trigger announcement

## 📊 Performance Optimization

### For Faster Inference
1. Use smaller model: `--model yolov8n`
2. Reduce image size: `--img-size 416`
3. Increase confidence threshold: `--conf-thres 0.7`

### For Better Accuracy
1. Use larger model: `--model yolov8l`
2. Increase image size: `--img-size 800`
3. Lower confidence threshold: `--conf-thres 0.3`

## 🔬 Model Architecture

The system uses YOLOv8 (You Only Look Once v8) for object detection:

### Available Models
- **YOLOv8n**: Nano - Fastest, lower accuracy
- **YOLOv8s**: Small - Good balance
- **YOLOv8m**: Medium - Better accuracy
- **YOLOv8l**: Large - High accuracy
- **YOLOv8x**: Extra large - Best accuracy, slowest

### Recommended for BlindStick
- **Indoor use**: YOLOv8n or YOLOv8s (speed priority)
- **Outdoor use**: YOLOv8m or YOLOv8l (accuracy priority)

## 🛠️ Troubleshooting

### Common Issues

**Issue**: Camera not opening
```bash
# Try different camera index
python detect.py --source 1
# or
python detect.py --source 2
```

**Issue**: Out of memory (GPU)
```bash
# Reduce batch size during training
python train.py --batch-size 8

# Use smaller model
python detect.py --model yolov8n
```

**Issue**: No audio output
- Check speaker/headphone connection
- Verify TTS engine is installed: `pip install pyttsx3`
- Test TTS separately: `python tts.py`

**Issue**: Low FPS
- Use CPU instead of GPU if GPU is slower: `--device cpu`
- Reduce image size: `--img-size 320`
- Use smaller model

## 📈 Future Enhancements

- [ ] Integration with depth sensors for accurate distance measurement
- [ ] Stereo vision support
- [ ] GPS integration for outdoor navigation
- [ ] Smartphone app interface
- [ ] Obstacle tracking and trajectory prediction
- [ ] Voice command recognition
- [ ] Multi-language support
- [ ] Cloud-based model updates

## 🤝 Contributing

Contributions are welcome! Areas of focus:
- Improving distance estimation accuracy
- Adding new object classes
- Optimizing for embedded devices
- Enhancing TTS naturalness
- Adding new features for user safety

## 📄 License

This project is for educational and assistive purposes. Please ensure compliance with all applicable licenses for:
- YOLO/ultralytics
- ORBIT dataset
- Other dependencies

## 🙏 Acknowledgments

- **ORBIT Dataset**: For providing object detection dataset
- **Ultralytics**: For YOLO implementation
- **PyTorch**: For deep learning framework
- **All contributors**: For making assistive technology accessible

## 📞 Support

For issues, questions, or suggestions:
1. Check this README
2. Review configuration files
3. Check console error messages
4. Consult documentation for dependencies

## 🌟 Success Stories

This project aims to make navigation safer and more accessible for visually impaired individuals worldwide. By combining cutting-edge computer vision with intuitive audio feedback, BlindStick represents a step forward in assistive technology.

---

**Made with ❤️ for accessibility and inclusion**

*Last Updated: March 2026*
