# BlindStick Raspberry Pi + Mobile App System Architecture

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BLINDSTICK SYSTEM                             │
│         Raspberry Pi + Mobile App Architecture                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐              ┌──────────────────────┐
│   RASPBERRY PI 3     │              │    MOBILE PHONE      │
│   (Camera Server)    │              │   (Processing Unit)  │
│                      │              │                      │
│  ┌────────────────┐  │   WiFi TCP   │  ┌────────────────┐  │
│  │ Camera Module  │──┼──────────────┼──│ Connection     │  │
│  │ (Video Input)  │  │  Port 8889   │  │ Service        │  │
│  └────────────────┘  │              │  └────────────────┘  │
│         │            │              │         │            │
│         ▼            │              │         ▼            │
│  ┌────────────────┐  │              │  ┌────────────────┐  │
│  │ picamera       │  │              │  │ Frame          │  │
│  │ Library        │  │              │  │ Processing     │  │
│  └────────────────┘  │              │  └────────────────┘  │
│         │            │              │         │            │
│         ▼            │              │         ▼            │
│  ┌────────────────┐  │              │  ┌────────────────┐  │
│  │ pi_camera_     │  │              │  │ Detection      │  │
│  │ server.py      │  │              │  │ Service        │  │
│  │                │  │              │  │ (Object ML)    │  │
│  │ - Video Stream │  │              │  └────────────────┘  │
│  │ - Command Sock │  │              │         │            │
│  └────────────────┘  │              │         ▼            │
│         │            │              │  ┌────────────────┐  │
│         │            │              │  │ Speech         │  │
│         │            │              │  │ Service        │  │
│         │            │              │  │ (TTS Output)   │  │
│         │            │              │  └────────────────┘  │
│         │            │              │         │            │
└─────────┼────────────┘              │         ▼            │
          │                           │  ┌────────────────┐  │
          │                           │  │ Phone Speaker  │  │
          │                           │  │ Audio Output   │  │
          │                           │  └────────────────┘  │
          │                           │                      │
          └───────────────────────────┘
                  WiFi Network
```

---

## 🔄 Data Flow Diagram

### Video Streaming Pipeline

```
┌─────────────┐
│ Scene/      │
│ Environment │
└──────┬──────┘
       │ Light rays
       ▼
┌─────────────┐
│ Pi Camera   │
│ Module      │
└──────┬──────┘
       │ Raw image data
       ▼
┌─────────────┐
│ picamera    │
│ Library     │
└──────┬──────┘
       │ JPEG frames
       ▼
┌─────────────┐
│ Socket      │
│ Streaming   │
└──────┬──────┘
       │ Network packets (TCP/IP)
       ▼
┌─────────────┐
│ WiFi        │
│ Router      │
└──────┬──────┘
       │ Wireless transmission
       ▼
┌─────────────┐
│ Mobile App  │
│ Connection  │
│ Service     │
└──────┬──────┘
       │ Uint8List frame data
       ▼
┌─────────────┐
│ Image       │
│ Decoder     │
└──────┬──────┘
       │ Decoded image
       ▼
┌─────────────┐
│ Object      │
│ Detection   │
│ (ML Model)  │
└──────┬──────┘
       │ Detected objects + distances
       ▼
┌─────────────┐
│ Text-to-    │
│ Speech      │
│ Engine      │
└──────┬──────┘
       │ Audio waveform
       ▼
┌─────────────┐
│ Phone       │
│ Speaker     │
└─────────────┘
    "Chair detected at 2 meters"
```

---

## 🏗️ Component Architecture

### 1. Raspberry Pi Components

```
┌────────────────────────────────────────────┐
│         RASPBERRY PI 3                     │
│                                            │
│  Hardware Layer:                           │
│  ┌──────────────────────────────────────┐ │
│  │ • Camera Module (CSI interface)      │ │
│  │ • Broadcom BCM2837 CPU               │ │
│  │ • WiFi Adapter (802.11n)             │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  OS Layer (Raspberry Pi OS):               │
│  ┌──────────────────────────────────────┐ │
│  │ • Linux Kernel                       │ │
│  │ • Camera Driver                      │ │
│  │ • Network Stack                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Application Layer:                        │
│  ┌──────────────────────────────────────┐ │
│  │ pi_camera_server.py                  │ │
│  │                                      │ │
│  │ ┌────────────────────────────────┐   │ │
│  │ │ Camera Manager                 │   │ │
│  │ │ - Resolution: 640x480          │   │ │
│  │ │ - FPS: 15                      │   │ │
│  │ │ - Format: JPEG                 │   │ │
│  │ └────────────────────────────────┘   │ │
│  │                                      │ │
│  │ ┌────────────────────────────────┐   │ │
│  │ │ Video Stream Server            │   │ │
│  │ │ - TCP Socket (Port 8889)       │   │ │
│  │ │ - Frame Size Prefixing         │   │ │
│  │ │ - Continuous Streaming         │   │ │
│  │ └────────────────────────────────┘   │ │
│  │                                      │ │
│  │ ┌────────────────────────────────┐   │ │
│  │ │ Command Server                 │   │ │
│  │ │ - TCP Socket (Port 8890)       │   │ │
│  │ │ - JSON Protocol                │   │ │
│  │ │ - Start/Stop/Capture Commands  │   │ │
│  │ └────────────────────────────────┘   │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

### 2. Mobile App Components

```
┌────────────────────────────────────────────┐
│         MOBILE APPLICATION                 │
│                                            │
│  UI Layer (Flutter Widgets):               │
│  ┌──────────────────────────────────────┐ │
│  │ HomeScreen                           │ │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ │ │
│  │ │Detect   │ │Connect  │ │Settings │ │ │
│  │ │Screen   │ │Screen   │ │Screen   │ │ │
│  │ └─────────┘ └─────────┘ └─────────┘ │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  State Management (Provider):              │
│  ┌──────────────────────────────────────┐ │
│  │ ChangeNotifiers                      │ │
│  │ • ConnectionService                  │ │
│  │ • DetectionService                   │ │
│  │ • SpeechService                      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Service Layer:                            │
│  ┌──────────────────────────────────────┐ │
│  │ ConnectionService                    │ │
│  │ ├─ TCP Client (8889)                 │ │
│  │ ├─ Command Client (8890)             │ │
│  │ ├─ Frame Stream Parser               │ │
│  │ └─ Connection State Manager          │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ DetectionService                     │ │
│  │ ├─ Image Decoder                     │ │
│  │ ├─ Object Detector (ML)              │ │
│  │ ├─ Distance Estimator                │ │
│  │ └─ Result Formatter                  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ SpeechService                        │ │
│  │ ├─ TTS Engine (flutter_tts)          │ │
│  │ ├─ Voice Selector                    │ │
│  │ ├─ Rate/Volume Control               │ │
│  │ └─ Announcement Manager              │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Platform Layer:                           │
│  ┌──────────────────────────────────────┐ │
│  │ • Android / iOS                      │ │
│  │ • Network Stack                      │ │
│  │ • Audio System                       │ │
│  │ • Display                            │ │
│  └──────────────────────────────────────┘ │
└────────────────────────────────────────────┘
```

---

## 🔌 Communication Protocol

### Video Stream Protocol (Port 8889)

```
Frame Transmission Format:

┌────────────────┬─────────────────────────┐
│ Frame Size (4B)│ Frame Data (N bytes)    │
│ Big-endian     │ JPEG compressed         │
│ uint32         │ image data              │
└────────────────┴─────────────────────────┘

Example:
[0x00, 0x02, 0xA3, 0xB4] [JPEG data... 679,092 bytes]
     ↑                          ↑
  Size = 679,092              Image content
```

### Command Protocol (Port 8890)

```
JSON Message Format:

Request (App → Pi):
{
  "type": "start|stop|capture|ping",
  "timestamp": 1234567890,
  "width": 640,      // optional
  "height": 480,     // optional
  "fps": 15          // optional
}

Response (Pi → App):
{
  "status": "started|stopped|captured|pong",
  "resolution": [640, 480],  // optional
  "timestamp": 1234567890
}
```

---

## 📊 Sequence Diagram

### Typical Usage Session

```
User     Mobile App        WiFi Network      Raspberry Pi
 │            │                  │                  │
 │            │                  │                  │
 ├──(1) Open App────────────────────────────────────►│
 │            │                  │                  │
 │            │◄────(2) Run pi_camera_server.py──────┤
 │            │                  │                  │
 │            │                  │                  │
 ├──(3) Enter IP (192.168.1.100)────────────────────►│
 │            │                  │                  │
 │            ├─(4) Connect TCP:8889───────────────►│
 │            │                  │                  │
 │            ├─(5) Connect TCP:8890───────────────►│
 │            │                  │                  │
 │            │◄────(6) Connection OK───────────────┤
 │            │                  │                  │
 │            │                  │                  │
 │            │◄═════════(7) Video Stream ══════════┤
 │            │   (JPEG frames @ 15 FPS)             │
 │            │                  │                  │
 │            │                  │                  │
 │            ├─(8) Process Frame───────────────────┤
 │            │   Decode → Detect → Estimate        │
 │            │                  │                  │
 │            │                  │                  │
 │            ├─(9) Generate Announcement───────────┤
 │            │   "Chair at 2 meters"               │
 │            │                  │                  │
 │            │                  │                  │
 │◄─(10) Speak──────────────────────────────────────┤
 │   Audio out                                        │
 │            │                  │                  │
 │            │◄════════(11) Continue Stream ═══════►│
 │            │   (Real-time updates)                │
 │            │                  │                  │
 │            │                  │                  │
 ├──(12) Disconnect─────────────────────────────────►│
 │            │                  │                  │
 │            ├─(13) Close Sockets─────────────────►│
 │            │                  │                  │
 │            │◄────(14) Disconnected───────────────┤
 │            │                  │                  │
```

---

## 🎯 Object Detection Pipeline

### Detailed Processing Flow

```
┌──────────────────────────────────────────────────────┐
│ Frame Received from Pi (640x480 JPEG)                │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ 1. Image Decoding                                    │
│    - Decode JPEG to RGB                              │
│    - Convert to format suitable for ML model         │
│    - Resize if needed                                │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ 2. Object Detection (ML Inference)                   │
│    Options:                                           │
│    a) TensorFlow Lite (on-device)                    │
│    b) Pre-trained YOLO model                         │
│    c) Custom trained ORBIT model                     │
│                                                       │
│    Output: List of detections                        │
│    [                                                 │
│      {class: "person", bbox: [x1,y1,x2,y2],          │
│       conf: 0.92},                                   │
│      {class: "chair", bbox: [x1,y1,x2,y2],           │
│       conf: 0.87}                                     │
│    ]                                                 │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ 3. Distance Estimation                               │
│    For each detection:                               │
│    - Calculate bounding box height                   │
│    - Apply pinhole camera model:                     │
│      distance = (ref_height × focal_length) /        │
│                 (pixel_height × 100)                 │
│    - Calibrate based on object class                 │
│                                                       │
│    Example results:                                  │
│    - Person: 3.2 meters                              │
│    - Chair: 1.8 meters                               │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ 4. Filtering & Prioritization                        │
│    - Keep objects within 20m radius                  │
│    - Sort by distance (nearest first)                │
│    - Apply priority weighting:                       │
│      High: person, car, obstacle                     │
│      Medium: chair, table, bicycle                   │
│      Low: wall, door, furniture                      │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ 5. Announcement Generation                           │
│    Create natural language description:              │
│                                                       │
│    If distance < 2m:                                 │
│      "Warning! {object} very close, {dist} meters"   │
│    If 2m < distance < 5m:                            │
│      "{object} nearby, {dist} meters"                │
│    If 5m < distance < 10m:                           │
│      "{object} ahead, {dist} meters"                 │
│    If 10m < distance < 20m:                          │
│      "{object} in front, {dist} meters"              │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│ 6. Text-to-Speech Output                             │
│    - Send text to flutter_tts                        │
│    - Configure voice, rate, volume                   │
│    - Play through phone speaker                      │
│                                                       │
│    Audio: "Chair nearby, 1.8 meters"                 │
└──────────────────────────────────────────────────────┘
```

---

## 🔐 Security Considerations

### Network Security

```
┌────────────────────────────────────────────────────┐
│ Current Implementation:                            │
│ • Unencrypted TCP communication                    │
│ • Local network only (WiFi)                        │
│ • No authentication                                │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ Recommended Improvements:                          │
│ • Add simple token-based auth                      │
│ • Use TLS/SSL for encryption                       │
│ • Implement device pairing                         │
│ • Firewall rules on Pi                             │
└────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Characteristics

### Latency Breakdown

```
Component              | Latency    | Optimization
-----------------------|------------|------------------
Camera Capture         | ~30ms      | Fixed hardware
JPEG Encoding          | ~50ms      | GPU acceleration
Network Transmission   | ~20-100ms  | WiFi quality
Frame Decoding         | ~20ms      | Optimized codec
Object Detection       | ~200-500ms | Model size/rate
Distance Calculation   | ~5ms       | Already fast
TTS Processing         | ~100ms     | Cached phonemes
Audio Playback         | ~50ms      | System dependent
-----------------------|------------|------------------
Total (one cycle)      | ~475-825ms | Can optimize ML
```

### Optimization Strategies

1. **Reduce Network Latency:**
   - Use 5GHz WiFi
   - Reduce resolution
   - Lower FPS

2. **Speed Up Detection:**
   - Use smaller ML model
   - Quantize weights (FP32 → INT8)
   - Run on GPU (if available)

3. **Parallel Processing:**
   - Process frames asynchronously
   - Pipeline: Capture → Decode → Detect → Speak
   - Don't wait for speech to finish before next detection

---

## 📱 Mobile App Architecture Patterns

### State Management (Provider Pattern)

```
┌─────────────────────────────────────────────┐
│                 UI Widgets                   │
│  (Screens, Buttons, Lists)                  │
└────────────────┬────────────────────────────┘
                 │ Listen to
                 ▼
┌─────────────────────────────────────────────┐
│              Providers                       │
│  (ChangeNotifier classes)                   │
│  ┌──────────────┐ ┌──────────────┐          │
│  │Connection    │ │Detection     │          │
│  │Service       │ │Service       │          │
│  └──────────────┘ └──────────────┘          │
└────────────────┬────────────────────────────┘
                 │ Update
                 ▼
┌─────────────────────────────────────────────┐
│            Business Logic                    │
│  (Services process data)                    │
└────────────────┬────────────────────────────┘
                 │ Access
                 ▼
┌─────────────────────────────────────────────┐
│          Platform APIs                       │
│  (Camera, Network, Audio, Storage)          │
└─────────────────────────────────────────────┘
```

---

## 🎨 User Interface Flow

```
┌─────────────┐
│ Launch App  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Home Screen │───Tab Bar───┐
└──────┬──────┘             │
       │                    │
       ├────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Detect Tab  │      │Connect Tab  │      │Settings Tab │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       ├─ Camera View       ├─ IP Input          ├─ Speech Rate
       ├─ Detections        ├─ Connect Btn       ├─ Volume
       ├─ Speak Btn         ├─ Status            ├─ Interval
       └─ Capture Btn       └─ Controls          └─ Test Btn
```

---

**This architecture provides:**
- ✅ Real-time video streaming
- ✅ Low-latency object detection
- ✅ Clear audio feedback
- ✅ Easy extensibility
- ✅ Modular design
- ✅ Cross-platform support

*For implementation details, see individual source files.*
