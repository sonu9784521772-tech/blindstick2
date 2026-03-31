"""
IP Webcam Client - Connect to Phone/IP Camera
Connects to IP Webcam apps (like DroidCam, IP Webcam, etc.)
and performs real-time object detection with audio feedback.

Usage:
    python ip_webcam_client.py --ip 192.168.137.230 --port 8080
    
Example:
    python ip_webcam_client.py --ip 192.168.137.230 --port 8080
"""

import cv2
import numpy as np
import pyttsx3
from ultralytics import YOLO
import threading
import time
import argparse
import tkinter as tk
from PIL import Image, ImageTk
import requests
from collections import deque
import queue
import torch


class IPWebcamClient:
    """Connect to IP Webcam and process video."""
    
    def __init__(self, ip_address, port=8080):
        self.ip = ip_address
        self.port = port
        self.base_url = f"http://{ip_address}:{port}"
        
        # Initialize model with GPU acceleration if available
        print("\nInitializing YOLO model...")
        try:
            self.model = YOLO('yolov8n.pt')
            # Check for GPU availability
            if torch.cuda.is_available():
                print("✓ CUDA available - Using GPU acceleration!")
                self.device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                print("✓ Apple Silicon MPS available - Using GPU acceleration!")
                self.device = 'mps'
            else:
                print("✓ Using CPU with optimized multi-threading")
                self.device = 'cpu'
        except Exception as e:
            print(f"⚠ Model initialization warning: {e}")
            self.device = 'cpu'
        
        # Initialize TTS
        self.tts_engine = None
        self.is_speaking = False
        self.last_announcement = time.time()
        self.announcement_interval = 1.0  # Announce every second for continuous feedback
        
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 180)  # Faster speech rate
            self.tts_engine.setProperty('volume', 1.0)
            print("✓ Text-to-speech initialized")
        except Exception as e:
            print(f"⚠ TTS not available: {e}")
        
        # Camera stream
        self.cap = None
        self.connected = False
        
        # Processing
        self.current_frame = None
        self.detections = []
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # UI setup
        self.setup_ui()
        
        self.running = True
    
    def setup_ui(self):
        """Setup modern graphical interface with enhanced styling."""
        self.root = tk.Tk()
        self.root.title(f"👁️ BlindStick Pro - Live Detection @ {self.ip}")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f0f23')
        
        # Title with gradient effect
        title_frame = tk.Frame(self.root, bg='#1a1a3e', height=70)
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text=f"👁️  BLINDSTICK PRO - Real-Time Object Detection",
            font=("Segoe UI", 22, "bold"),
            fg='#00ffff',
            bg='#1a1a3e'
        )
        title_label.pack(pady=20)
        
        subtitle = tk.Label(
            title_frame,
            text=f"Connected to: {self.ip}:{self.port} | GPU Accelerated | Continuous Announcements",
            font=("Consolas", 10),
            fg='#88ccff',
            bg='#1a1a3e'
        )
        subtitle.pack(pady=(0, 10))
        
        # Content area
        content_frame = tk.Frame(self.root, bg='#0f0f23')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Content area
        content_frame = tk.Frame(self.root, bg='#1a1a2e')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Video (wider)
        left_panel = tk.Frame(content_frame, bg='#1a1a4e', bd=3, relief=tk.RAISED)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        video_header = tk.Label(
            left_panel,
            text="📹 LIVE VIDEO FEED",
            font=("Segoe UI", 14, "bold"),
            fg='#ffffff',
            bg='#1a1a4e'
        )
        video_header.pack(pady=(10, 5))
        
        self.video_label = tk.Label(left_panel, bg='#000000')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right panel - Info (narrower but styled)
        right_panel = tk.Frame(content_frame, bg='#1a1a4e', width=400, bd=3, relief=tk.RAISED)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Status section with better styling
        status_frame = tk.Frame(right_panel, bg='#0f0f3e')
        status_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            status_frame,
            text="📊 SYSTEM STATUS",
            font=("Segoe UI", 16, "bold"),
            fg='#00ffff',
            bg='#0f0f3e'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        self.status_text = tk.Text(
            status_frame,
            height=7,
            width=45,
            font=("Consolas", 11),
            fg='#00ff88',
            bg='#0a0a2e',
            wrap=tk.WORD,
            state='disabled',
            bd=2,
            relief=tk.FLAT
        )
        self.status_text.pack(fill=tk.X)
        
        # Detections section with better styling
        detections_frame = tk.Frame(right_panel, bg='#0f0f3e')
        detections_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(
            detections_frame,
            text="🎯 DETECTED OBJECTS (Real-Time)",
            font=("Segoe UI", 16, "bold"),
            fg='#00ffff',
            bg='#0f0f3e'
        ).pack(anchor=tk.W, pady=(0, 15))
        
        self.detections_text = tk.Text(
            detections_frame,
            height=18,
            width=45,
            font=("Consolas", 11),
            fg='#ffffff',
            bg='#0a0a2e',
            wrap=tk.WORD,
            state='disabled',
            bd=2,
            relief=tk.FLAT
        )
        self.detections_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls with modern buttons
        controls_frame = tk.Frame(right_panel, bg='#0f0f3e')
        controls_frame.pack(fill=tk.X, padx=15, pady=15)
        
        btn_speak = tk.Button(
            controls_frame,
            text="🔊 SPEAK NOW",
            command=self.speak_now,
            font=("Segoe UI", 14, "bold"),
            bg='#ff6b6b',
            fg='#ffffff',
            cursor='hand2',
            relief=tk.FLAT,
            padx=25,
            pady=12,
            activebackground='#ff8787',
            activeforeground='#ffffff'
        )
        btn_speak.pack(fill=tk.X, pady=8)
        
        btn_disconnect = tk.Button(
            controls_frame,
            text="🔌 DISCONNECT",
            command=self.disconnect,
            font=("Segoe UI", 12),
            bg='#4a4a6a',
            fg='#ffffff',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            activebackground='#6a6a8a',
            activeforeground='#ffffff'
        )
        btn_disconnect.pack(fill=tk.X, pady=8)
        
        # Bottom status bar with enhanced info
        bottom_frame = tk.Frame(self.root, bg='#1a1a3e', height=50)
        bottom_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.status_bar_label = tk.Label(
            bottom_frame,
            text="Status: Initializing...",
            font=("Consolas", 12, "bold"),
            fg='#00ff88',
            bg='#1a1a3e',
            anchor=tk.W
        )
        self.status_bar_label.pack(fill=tk.X, padx=15)
    
    def connect_to_camera(self):
        """Connect to IP Webcam MJPEG stream."""
        print(f"\nConnecting to IP Webcam at {self.base_url}...")
        self.update_status(f"Connecting to\n{self.base_url}...")
        
        try:
            # Try different stream URLs that IP Webcam apps use
            stream_urls = [
                f"{self.base_url}/video",
                f"{self.base_url}/mjpegfeed",
                f"{self.base_url}:8080/video",
                f"http://{self.ip}:{self.port}/videofeed",
            ]
            
            for url in stream_urls:
                print(f"  Trying: {url}")
                
                try:
                    # OpenCV can read MJPEG streams directly
                    self.cap = cv2.VideoCapture(url)
                    
                    if self.cap.isOpened():
                        print(f"✓ Connected to stream: {url}")
                        self.connected = True
                        self.update_status(f"✓ CONNECTED\nto {self.base_url}\nStreaming video...")
                        self.update_status_bar("Connected | Receiving frames")
                        return True
                    
                    self.cap.release()
                    
                except Exception as e:
                    print(f"  ✗ Failed: {e}")
                    continue
            
            # If direct URLs failed, try standard VideoCapture with IP
            print(f"\nTrying standard connection...")
            self.cap = cv2.VideoCapture(f"http://{self.ip}:{self.port}/video")
            
            if self.cap.isOpened():
                print(f"✓ Connected via standard method")
                self.connected = True
                self.update_status(f"✓ CONNECTED\nto {self.base_url}")
                self.update_status_bar("Connected | Receiving frames")
                return True
            else:
                print("✗ All connection methods failed")
                self.update_status(f"✗ FAILED\nCould not connect to\n{self.base_url}\n\nCheck:\n1. IP Webcam app is running\n2. Same WiFi network\n3. Correct IP/Port\n4. Firewall allows connection")
                self.update_status_bar("Disconnected | Connection failed")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            self.update_status(f"✗ ERROR\n{str(e)}")
            return False
    
    def receive_frames(self):
        """Receive and process frames from IP camera."""
        while self.running and self.connected:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    time.sleep(0.1)
                    continue
                
                # Process frame
                self.process_frame(frame)
                
            except Exception as e:
                if self.running:
                    print(f"Frame error: {e}")
                break
        
        if self.running:
            print("✗ Lost connection to IP Webcam")
            self.update_status("✗ DISCONNECTED\nConnection lost")
            self.update_status_bar("Disconnected | Stream lost")
            self.connected = False
    
    def process_frame(self, frame):
        """Detect objects in frame with GPU acceleration."""
        # Update FPS
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
        
        # Detect objects with optimized settings
        results = self.model.predict(
            frame, 
            conf=0.45,  # Slightly lower threshold for more detections
            verbose=False,
            device=self.device,  # Use GPU if available
            imgsz=640,  # Optimal image size
            max_det=10,  # Limit max detections for speed
            classes=None,  # Detect all classes
        )
        
        self.detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                name = results[0].names[cls]
                
                # Calculate distance
                x1, y1, x2, y2 = xyxy
                height = y2 - y1
                distance = self.estimate_distance(height, name)
                
                self.detections.append({
                    'name': name,
                    'confidence': conf,
                    'distance': distance,
                    'bbox': (int(x1), int(y1), int(x2), int(y2))
                })
        
        # Draw detections
        annotated = self.draw_detections(frame.copy(), self.detections)
        
        # Update UI
        self.update_frame(annotated)
        self.update_stats()
        self.update_detections_display()
        
        # Announce
        self.announce_detections()
    
    def estimate_distance(self, bbox_height, class_name):
        """Estimate distance based on object size."""
        ref_heights = {
            'person': 170,
            'car': 150,
            'chair': 90,
            'table': 75,
            'door': 200,
        }
        
        ref = ref_heights.get(class_name, 100)
        if bbox_height > 0:
            return round((ref * 480) / (bbox_height * 100), 2)
        return 0.0
    
    def draw_detections(self, frame, detections):
        """Draw detections with colored boxes and 2 decimal distance."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            
            # Color by distance
            if det['distance'] < 2.0:
                color = (0, 0, 255)  # Red
            elif det['distance'] < 5.0:
                color = (0, 165, 255)  # Orange
            elif det['distance'] < 10.0:
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 255, 0)  # Green
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            
            # Distance with 2 decimal places
            label = f"{det['name']} {det['distance']:.2f}m"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return frame
    
    def announce_detections(self):
        """Announce detected objects continuously with 2 decimal precision."""
        current_time = time.time()
            
        if current_time - self.last_announcement < self.announcement_interval:
            return
            
        # Get all detections within 20 meters
        nearby = [d for d in self.detections if 0 < d['distance'] <= 20.0]
            
        if not nearby:
            return
            
        # Sort by distance (closest first)
        nearby.sort(key=lambda x: x['distance'])
            
        # Announce top 3 closest objects
        top_objects = nearby[:3]
            
        if len(top_objects) == 1:
            obj = top_objects[0]
            distance_str = f"{obj['distance']:.2f}"  # Always 2 decimal places
                
            if obj['distance'] < 2.0:
                msg = f"Warning! {obj['name']} very close at {distance_str} meters"
            elif obj['distance'] < 5.0:
                msg = f"{obj['name']} nearby at {distance_str} meters"
            elif obj['distance'] < 10.0:
                msg = f"{obj['name']} ahead at {distance_str} meters"
            else:
                msg = f"{obj['name']} in front at {distance_str} meters"
        else:
            # Multiple objects - list them with distances
            parts = []
            for obj in top_objects:
                distance_str = f"{obj['distance']:.2f}"
                parts.append(f"{obj['name']} at {distance_str} meters")
                
            if len(parts) == 2:
                msg = f"{parts[0]}, and {parts[1]}"
            else:
                msg = f"{parts[0]}, {parts[1]}, and {parts[2]}"
            
        self.speak(msg)
        self.last_announcement = current_time
    
    def speak(self, text):
        """Speak text asynchronously."""
        if not self.tts_engine or self.is_speaking:
            return
        
        def speak_thread():
            self.is_speaking = True
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
    
    def speak_now(self):
        """Manually trigger announcement."""
        if self.detections:
            self.announce_detections()
    
    def disconnect(self):
        """Disconnect from camera."""
        self.running = False
        self.connected = False
        
        if self.cap:
            self.cap.release()
        
        self.root.quit()
    
    def update_status(self, text):
        """Update status text area."""
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', text)
        self.status_text.config(state='disabled')
    
    def update_status_bar(self, text):
        """Update bottom status bar."""
        self.status_bar_label.config(text=text)
    
    def update_stats(self):
        """Update statistics with enhanced info."""
        fps_str = f"⚡ FPS: {self.fps:.1f}"
        obj_str = f"🎯 Objects: {len(self.detections)}"
        device_str = f"GPU: {self.device.upper()}" if self.connected else "Initializing"
        
        self.update_status_bar(f"{fps_str}  |  {obj_str}  |  {device_str}  |  Announcing Every {self.announcement_interval}s")
    
    def update_detections_display(self):
        """Update detections list with 2 decimal precision."""
        self.detections_text.config(state='normal')
        self.detections_text.delete('1.0', tk.END)
        
        if not self.detections:
            self.detections_text.insert('1.0', "No objects detected\n")
        else:
            sorted_dets = sorted(self.detections, key=lambda x: x['distance'])
            
            for i, det in enumerate(sorted_dets, 1):
                distance_str = f"{det['distance']:.2f}"  # 2 decimal places
                
                distance = det['distance']
                if distance < 2.0:
                    indicator = "⚠️ VERY CLOSE"
                elif distance < 5.0:
                    indicator = "🟡 NEARBY"
                elif distance < 10.0:
                    indicator = "🟢 AHEAD"
                else:
                    indicator = "🔵 IN FRONT"
                
                line = f"{i}. {det['name'].upper()}\n"
                line += f"   Distance: {distance_str}m {indicator}\n"
                line += f"   Confidence: {det['confidence']:.0%}\n\n"
                
                self.detections_text.insert(tk.END, line)
        
        self.detections_text.config(state='disabled')
    
    def update_frame(self, frame):
        """Update video display."""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            
        except Exception as e:
            print(f"Frame update error: {e}")
    
    def run(self):
        """Run the application."""
        print("=" * 60)
        print(" BlindStick - IP Webcam Client")
        print("=" * 60)
        print(f"\nConnecting to IP Webcam at {self.base_url}...")
        print("=" * 60)
        
        # Connect FIRST
        print("\nEstablishing connection...")
        if not self.connect_to_camera():
            print("\n✗ Connection failed! Please check:")
            print("  1. IP Webcam app is running on your phone")
            print("  2. Correct IP address and port")
            print("  3. Both devices on same WiFi network")
            print("  4. Try different stream URL format")
            return
        
        # Start frame receiving thread
        receive_thread = threading.Thread(target=self.receive_frames)
        receive_thread.daemon = True
        receive_thread.start()
        
        print("\n✓ Connection successful! Opening UI...")
        
        # Start UI
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            self.disconnect()


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Connect to IP Webcam')
    parser.add_argument('--ip', type=str, required=True, help='IP Webcam IP address')
    parser.add_argument('--port', type=int, default=8080, help='IP Webcam port')
    
    args = parser.parse_args()
    
    client = IPWebcamClient(
        ip_address=args.ip,
        port=args.port
    )
    client.run()


if __name__ == '__main__':
    main()
