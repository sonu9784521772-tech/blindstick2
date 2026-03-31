"""
BlindStick Professional UI - Raspberry Pi Camera Client
A beautiful, user-friendly interface with light beige theme connecting to Raspberry Pi 3.

Usage:
    python ui_app.py
    
Features:
- Professional light beige theme with modern design
- Connects to Raspberry Pi 3 (IP: 172.22.11.180)
- Real-time object detection with visual feedback
- Continuous audio announcements for every detection
- Clear distance indicators
- Easy-to-read statistics
"""

import cv2
import numpy as np
import pyttsx3
from ultralytics import YOLO
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import queue
import socket
import struct
import json


class BlindStickUI:
    """Professional UI for BlindStick with Raspberry Pi connection and light beige theme."""
    
    def __init__(self, pi_ip='172.22.11.180', video_port=8889, command_port=8890):
        self.pi_ip = pi_ip
        self.video_port = video_port
        self.command_port = command_port
        
        # Initialize model
        self.model = YOLO('yolov8n.pt')
        
        # Initialize TTS - Speak EVERY time an object is detected
        self.tts_engine = None
        self.is_speaking = False
        self.last_announcement = time.time()
        self.announcement_interval = 0.5  # Announce immediately when objects detected
        
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 160)
            self.tts_engine.setProperty('volume', 1.0)
            print("✓ Text-to-speech initialized")
        except Exception as e:
            print(f"⚠ TTS not available: {e}")
        
        # Connection
        self.video_socket = None
        self.command_socket = None
        self.connected = False
        
        # Processing
        self.current_frame = None
        self.detections = []
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
        # Queue for thread-safe frame updates
        self.frame_queue = queue.Queue(maxsize=2)
        
        # UI setup
        self.setup_ui()
        
        # Start threads
        self.running = True
        
        # Connect to Raspberry Pi
        self.connect_to_pi()
        
        # Start frame receiving thread
        if self.connected:
            self.receive_thread = threading.Thread(target=self.receive_frames)
            self.receive_thread.daemon = True
            self.receive_thread.start()
    
    def setup_ui(self):
        """Setup the professional light beige themed graphical user interface."""
        self.root = tk.Tk()
        self.root.title(f"👁️ BlindStick Pro - Raspberry Pi @ {self.pi_ip}")
        self.root.geometry("1400x900")
        
        # Light beige color scheme
        self.colors = {
            'bg_main': '#F5F5DC',      # Light beige background
            'bg_panel': '#FAF0E6',     # Linen (slightly lighter)
            'bg_card': '#FFFFFF',      # White cards
            'accent_primary': '#8B4513',  # Saddle brown (primary accent)
            'accent_secondary': '#D2691E',  # Chocolate (secondary accent)
            'text_primary': '#2C1810',    # Dark brown text
            'text_secondary': '#5C4033',  # Medium brown text
            'success': '#228B22',         # Forest green
            'warning': '#FF8C00',         # Dark orange
            'danger': '#DC143C',          # Crimson
            'border': '#DEB887',          # Burlywood border
        }
        
        self.root.configure(bg=self.colors['bg_main'])
        
        # Title bar with elegant design
        title_frame = tk.Frame(self.root, bg=self.colors['accent_primary'], height=80)
        title_frame.pack(fill=tk.X, padx=15, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="👁️ BLINDSTICK PROFESSIONAL",
            font=("Segoe UI", 24, "bold"),
            fg='#FFFFFF',
            bg=self.colors['accent_primary']
        )
        title_label.pack(pady=(15, 5))
        
        subtitle = tk.Label(
            title_frame,
            text=f"Connected to Raspberry Pi 3 @ {self.pi_ip} | Continuous Object Detection with Audio Feedback",
            font=("Consolas", 11),
            fg='#F5DEB3',
            bg=self.colors['accent_primary']
        )
        subtitle.pack(pady=(0, 15))
        
        # Main content area
        content_frame = tk.Frame(self.root, bg=self.colors['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Video feed (wider)
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_panel'], bd=3, relief=tk.RAISED)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        video_header = tk.Label(
            left_panel,
            text="📹 LIVE CAMERA FEED",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_panel']
        )
        video_header.pack(pady=(10, 5))
        
        self.video_label = tk.Label(left_panel, bg='#000000')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right panel - Information (narrower but styled)
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_panel'], width=420, bd=3, relief=tk.RAISED)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Status section with card styling
        status_frame = tk.Frame(right_panel, bg=self.colors['bg_card'], bd=2, relief=tk.GROOVE)
        status_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            status_frame,
            text="📊 SYSTEM STATUS",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_card']
        ).pack(anchor=tk.W, pady=(0, 12))
        
        self.status_text = tk.Text(
            status_frame,
            height=7,
            width=45,
            font=("Consolas", 11),
            fg=self.colors['success'],
            bg=self.colors['bg_main'],
            wrap=tk.WORD,
            state='disabled',
            bd=1,
            relief=tk.FLAT
        )
        self.status_text.pack(fill=tk.X)
        
        # Detections section with card styling
        detections_frame = tk.Frame(right_panel, bg=self.colors['bg_card'], bd=2, relief=tk.GROOVE)
        detections_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(
            detections_frame,
            text="🎯 DETECTED OBJECTS (Continuous)",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_card']
        ).pack(anchor=tk.W, pady=(0, 12))
        
        self.detections_text = tk.Text(
            detections_frame,
            height=16,
            width=45,
            font=("Consolas", 11),
            fg=self.colors['text_primary'],
            bg=self.colors['bg_main'],
            wrap=tk.WORD,
            state='disabled',
            bd=1,
            relief=tk.FLAT
        )
        self.detections_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls section with modern buttons
        controls_frame = tk.Frame(right_panel, bg=self.colors['bg_card'], bd=2, relief=tk.GROOVE)
        controls_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            controls_frame,
            text="🎛️ CONTROLS",
            font=("Segoe UI", 14, "bold"),
            fg=self.colors['accent_primary'],
            bg=self.colors['bg_card']
        ).pack(anchor=tk.W, pady=(0, 12))
        
        btn_speak = tk.Button(
            controls_frame,
            text="🔊 SPEAK NOW",
            command=self.speak_now,
            font=("Segoe UI", 13, "bold"),
            bg=self.colors['accent_secondary'],
            fg='#FFFFFF',
            cursor='hand2',
            relief=tk.RAISED,
            padx=25,
            pady=12,
            activebackground=self.colors['accent_primary'],
            activeforeground='#FFFFFF'
        )
        btn_speak.pack(fill=tk.X, pady=6)
        
        btn_clear = tk.Button(
            controls_frame,
            text="🔄 CLEAR DETECTIONS",
            command=self.clear_detections,
            font=("Segoe UI", 12),
            bg=self.colors['bg_panel'],
            fg=self.colors['text_primary'],
            cursor='hand2',
            relief=tk.RAISED,
            padx=20,
            pady=10,
            activebackground=self.colors['border'],
            activeforeground=self.colors['text_primary']
        )
        btn_clear.pack(fill=tk.X, pady=6)
        
        btn_disconnect = tk.Button(
            controls_frame,
            text="🔌 DISCONNECT",
            command=self.disconnect,
            font=("Segoe UI", 12),
            bg='#8B0000',
            fg='#FFFFFF',
            cursor='hand2',
            relief=tk.RAISED,
            padx=20,
            pady=10,
            activebackground='#A52A2A',
            activeforeground='#FFFFFF'
        )
        btn_disconnect.pack(fill=tk.X, pady=6)
        
        # Bottom status bar with enhanced info
        bottom_frame = tk.Frame(self.root, bg=self.colors['accent_primary'], height=50)
        bottom_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.fps_label = tk.Label(
            bottom_frame,
            text="⚡ FPS: 0  |  🎯 Objects: 0  |  ✅ Connected  |  🔊 Announcing Every 0.5s",
            font=("Consolas", 12, "bold"),
            fg='#FFFFFF',
            bg=self.colors['accent_primary'],
            anchor=tk.W
        )
        self.fps_label.pack(fill=tk.X, padx=15)
    
    def connect_to_pi(self):
        """Establish connection to Raspberry Pi."""
        print(f"\nConnecting to Raspberry Pi at {self.pi_ip}...")
        self.update_status(f"Connecting to\nRaspberry Pi {self.pi_ip}\nVideo Port: {self.video_port}\nCommand Port: {self.command_port}")
        
        try:
            # Connect to video stream with timeout
            self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.video_socket.settimeout(5)  # 5 second timeout
            
            print(f"  Attempting video port {self.video_port}...")
            self.video_socket.connect((self.pi_ip, self.video_port))
            
            print(f"✓ Connected to video stream on port {self.video_port}")
            
            # Connect to command socket
            self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.command_socket.settimeout(5)
            
            print(f"  Attempting command port {self.command_port}...")
            self.command_socket.connect((self.pi_ip, self.command_port))
            
            print(f"✓ Connected to command stream on port {self.command_port}")
            
            self.connected = True
            self.update_status(f"✓ CONNECTED\nto Raspberry Pi {self.pi_ip}\nStreaming video...\nObject detection active")
            self.update_status_bar("⚡ FPS: 0  |  🎯 Objects: 0  |  ✅ Connected  |  🔊 Continuous Announcements")
            
            # Send start command
            self.send_command('start')
            
            return True
            
        except socket.timeout:
            print(f"✗ Connection timed out (5 seconds)")
            print(f"  Is the Pi server running?")
            self.update_status(f"✗ TIMEOUT\nPi not responding\nCheck server is running\nIP: {self.pi_ip}")
            return False
            
        except ConnectionRefusedError:
            print(f"✗ Connection refused")
            print(f"  Make sure pi_camera_server.py is running on Pi")
            self.update_status(f"✗ REFUSED\nServer not running\nStart pi_camera_server.py\non Raspberry Pi first")
            return False
            
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.update_status(f"✗ FAILED\n{str(e)}")
            return False
    
    def send_command(self, cmd_type, params=None):
        """Send command to Pi server."""
        if not self.command_socket:
            return
        
        try:
            command = {'type': cmd_type, 'timestamp': int(time.time())}
            if params:
                command.update(params)
            
            self.command_socket.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Command error: {e}")
    
    def receive_frames(self):
        """Receive video frames from Raspberry Pi."""
        while self.running and self.connected:
            try:
                # Read frame size (4 bytes)
                size_data = self.read_exact(4)
                if not size_data:
                    break
                
                frame_size = struct.unpack('>I', size_data)[0]
                
                # Check for special markers
                if frame_size == 0xFE:
                    # Metadata frame
                    continue
                
                # Read frame data
                frame_data = self.read_exact(frame_size)
                if not frame_data:
                    break
                
                # Convert to numpy array
                frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    self.current_frame = frame
                    
                    # Process frame for objects
                    self.process_frame(frame)
                    
            except Exception as e:
                if self.running:
                    print(f"Frame receive error: {e}")
                break
        
        # If we get here, connection lost
        if self.running:
            print("✗ Lost connection to Raspberry Pi")
            self.update_status("✗ DISCONNECTED\nConnection lost\nRestart Pi server")
            self.update_status_bar("❌ Disconnected  |  Connection lost  |  Restart Pi server")
            self.connected = False
    
    def read_exact(self, num_bytes):
        """Read exact number of bytes from socket."""
        data = b''
        while len(data) < num_bytes and self.running:
            try:
                chunk = self.video_socket.recv(num_bytes - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                continue
        return data
    
    def process_frame(self, frame):
        """Detect objects in frame from Raspberry Pi."""
        # Update FPS
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
        
        # Detect objects
        results = self.model.predict(frame, conf=0.5, verbose=False)
        
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
        
        # Draw detections on frame
        annotated = self.draw_detections(frame.copy(), self.detections)
        
        # Update UI
        self.update_frame(annotated)
        self.update_stats()
        
        # Announce EVERY detection immediately
        self.announce_detections()
    
    def estimate_distance(self, bbox_height, class_name):
        """Estimate distance based on object size."""
        ref_heights = {
            'person': 170,
            'car': 150,
            'chair': 90,
            'table': 75,
            'door': 200,
            'couch': 85,
            'potted plant': 50,
            'bed': 50,
            'dining table': 100,
            'tv': 60,
        }
        
        ref = ref_heights.get(class_name, 100)
        if bbox_height > 0:
            return round((ref * 480) / (bbox_height * 100), 2)
        return 0.0
    
    def draw_detections(self, frame, detections):
        """Draw detections on frame with beautiful colors."""
        # Enhance brightness if frame is too dark
        if np.mean(frame) < 30:
            # Apply gamma correction to brighten
            gamma = 1.5
            invGamma = 1.0 / gamma
            frame = np.array([((v / 255.0) ** (1.0 / invGamma) * 255)
                for v in np.nditer(frame.astype(float))]).astype("uint8").reshape(frame.shape)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            
            # Color based on distance
            if det['distance'] < 2.0:
                color = (0, 0, 255)  # Red - very close
            elif det['distance'] < 5.0:
                color = (0, 165, 255)  # Orange - nearby
            elif det['distance'] < 10.0:
                color = (0, 255, 255)  # Yellow - medium
            else:
                color = (0, 255, 0)  # Green - far
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            
            # Draw label background
            label = f"{det['name']} {det['distance']:.1f}m"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            cv2.rectangle(
                frame,
                (x1, y1 - label_h - 10),
                (x1 + label_w, y1),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2
            )
        
        return frame
    
    def announce_detections(self):
        """Announce EVERY detected object immediately with continuous feedback."""
        current_time = time.time()
        
        if current_time - self.last_announcement < self.announcement_interval:
            return
        
        # Get ALL detections within 20 meters (no filtering by count)
        nearby = [d for d in self.detections if 0 < d['distance'] <= 20.0]
        
        if not nearby:
            return
        
        # Sort by distance (closest first)
        nearby.sort(key=lambda x: x['distance'])
        
        # Announce ALL detected objects with distances
        if len(nearby) == 1:
            obj = nearby[0]
            distance_str = f"{obj['distance']:.2f}"
            
            if obj['distance'] < 2.0:
                msg = f"⚠️ Warning! {obj['name']} very close at {distance_str} meters!"
            elif obj['distance'] < 5.0:
                msg = f"🟡 {obj['name']} nearby at {distance_str} meters"
            elif obj['distance'] < 10.0:
                msg = f"🟢 {obj['name']} ahead at {distance_str} meters"
            else:
                msg = f"🔵 {obj['name']} in front at {distance_str} meters"
        else:
            # Multiple objects - announce each with distance
            parts = []
            for i, obj in enumerate(nearby[:5], 1):  # Announce up to 5 objects
                distance_str = f"{obj['distance']:.2f}"
                if i == 1:
                    parts.append(f"{obj['name']} at {distance_str} meters")
                else:
                    parts.append(f"{obj['name']} at {distance_str}")
            
            msg = ", then ".join(parts)
        
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
        """Manually trigger speech announcement."""
        if self.detections:
            self.announce_detections()
    
    def clear_detections(self):
        """Clear current detections."""
        self.detections = []
        self.update_detections_display()
    
    def disconnect(self):
        """Disconnect from Raspberry Pi."""
        self.running = False
        self.connected = False
        
        if self.video_socket:
            self.video_socket.close()
        if self.command_socket:
            self.command_socket.close()
        
        self.root.quit()
    
    def update_stats(self):
        """Update statistics display with enhanced info."""
        fps_str = f"⚡ FPS: {self.fps:.1f}"
        obj_str = f"🎯 Objects: {len(self.detections)}"
        conn_str = "✅ Connected" if self.connected else "❌ Disconnected"
        
        self.fps_label.config(text=f"{fps_str}  |  {obj_str}  |  {conn_str}  |  🔊 Announcing Every {self.announcement_interval}s")
    
    def update_status(self, text):
        """Update status text area."""
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', text)
        self.status_text.config(state='disabled')
    
    def update_status_bar(self, text):
        """Update bottom status bar."""
        self.fps_label.config(text=text)
    
    def update_detections_display(self):
        """Update detections text area with professional formatting."""
        self.detections_text.config(state='normal')
        self.detections_text.delete('1.0', tk.END)
        
        if not self.detections:
            self.detections_text.insert('1.0', "⏳ No objects currently detected\n")
        else:
            # Sort by distance
            sorted_dets = sorted(self.detections, key=lambda x: x['distance'])
            
            for i, det in enumerate(sorted_dets, 1):
                distance = det['distance']
                distance_str = f"{distance:.2f}"
                
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
        """Update video frame display."""
        try:
            # Convert to PhotoImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            
            # Update detections display
            self.update_detections_display()
            
        except Exception as e:
            print(f"Frame update error: {e}")
    
    def run(self):
        """Run the application."""
        print("=" * 60)
        print(" 👁️ BLINDSTICK PROFESSIONAL - Raspberry Pi Edition")
        print("=" * 60)
        print(f"\nConnecting to Raspberry Pi 3 @ {self.pi_ip}...")
        print("Video Port: 8889 | Command Port: 8890")
        print("=" * 60)
        print("\nFeatures:")
        print("✓ Light beige professional theme")
        print("✓ Continuous object detection")
        print("✓ Audio announcement for EVERY detection")
        print("✓ Real-time distance measurement")
        print("=" * 60)
        
        # Check connection status
        if not self.connected:
            print("\n⚠️ Could not connect to Raspberry Pi!")
            print("\nPlease ensure:")
            print("1. Raspberry Pi is powered on and connected to network")
            print("2. Pi IP address is correct (currently: 172.22.11.180)")
            print("3. pi_camera_server.py is running on Raspberry Pi:")
            print("   python3 pi_camera_server.py")
            print("4. Both devices are on the same network")
            print("\nYou can modify the IP in the code if needed.")
            print("\nOpening UI anyway (will show disconnected state)...")
        
        print("\n✓ Opening user interface...")
        print("Press Ctrl+C or close window to exit")
        print("=" * 60)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopping application...")
        finally:
            self.disconnect()


def main():
    """Main function with Raspberry Pi connection."""
    # Connect to Raspberry Pi 3 at specified IP
    pi_ip = '172.22.11.180'
    
    print(f"\n👁️ BLINDSTICK PROFESSIONAL")
    print(f"Raspberry Pi 3 Camera Client")
    print(f"Target IP: {pi_ip}")
    print("=" * 60)
    
    app = BlindStickUI(pi_ip=pi_ip)
    app.run()


if __name__ == '__main__':
    main()