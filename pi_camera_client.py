"""
Raspberry Pi Camera Client - Connect to Pi Camera Stream
This connects to your Raspberry Pi 3 and receives the camera feed,
then performs object detection and announces via speaker.

Usage:
    python pi_camera_client.py --ip YOUR_PI_IP_ADDRESS
    
Example:
    python pi_camera_client.py --ip 192.168.1.100
"""

import socket
import struct
import numpy as np
import cv2
import pyttsx3
from ultralytics import YOLO
import threading
import time
import argparse
import tkinter as tk
from PIL import Image, ImageTk


class PiCameraClient:
    """Connect to Raspberry Pi camera server and process video."""
    
    def __init__(self, pi_ip_address, video_port=8889, command_port=8890):
        self.pi_ip = pi_ip_address
        self.video_port = video_port
        self.command_port = command_port
        
        # Initialize model
        self.model = YOLO('yolov8n.pt')
        
        # Initialize TTS
        self.tts_engine = None
        self.is_speaking = False
        self.last_announcement = time.time()
        self.announcement_interval = 3.0
        
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
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
        
        # UI setup
        self.setup_ui()
        
        # Start threads
        self.running = True
        
    def setup_ui(self):
        """Setup graphical interface."""
        self.root = tk.Tk()
        self.root.title(f"BlindStick - Connected to Pi {self.pi_ip}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Title
        title_frame = tk.Frame(self.root, bg='#16213e', height=60)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text=f"👁️ BlindStick - Raspberry Pi Camera @ {self.pi_ip}",
            font=("Arial", 18, "bold"),
            fg='#00d9ff',
            bg='#16213e'
        )
        title_label.pack(pady=15)
        
        # Content area
        content_frame = tk.Frame(self.root, bg='#1a1a2e')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Video
        left_panel = tk.Frame(content_frame, bg='#0f3460')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.video_label = tk.Label(left_panel, bg='#000000')
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Right panel - Info
        right_panel = tk.Frame(content_frame, bg='#0f3460', width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Status section
        status_frame = tk.Frame(right_panel, bg='#16213e')
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            status_frame,
            text="📊 Connection Status",
            font=("Arial", 14, "bold"),
            fg='#00d9ff',
            bg='#16213e'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.status_text = tk.Text(
            status_frame,
            height=8,
            width=40,
            font=("Consolas", 10),
            fg='#ffffff',
            bg='#0f3460',
            wrap=tk.WORD,
            state='disabled'
        )
        self.status_text.pack(fill=tk.X)
        
        # Detections section
        detections_frame = tk.Frame(right_panel, bg='#16213e')
        detections_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            detections_frame,
            text="🎯 Detected Objects",
            font=("Arial", 14, "bold"),
            fg='#00d9ff',
            bg='#16213e'
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.detections_text = tk.Text(
            detections_frame,
            height=15,
            width=40,
            font=("Consolas", 11),
            fg='#ffffff',
            bg='#0f3460',
            wrap=tk.WORD,
            state='disabled'
        )
        self.detections_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls_frame = tk.Frame(right_panel, bg='#16213e')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        btn_speak = tk.Button(
            controls_frame,
            text="🔊 Speak Now",
            command=self.speak_now,
            font=("Arial", 12, "bold"),
            bg='#e94560',
            fg='#ffffff',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_speak.pack(fill=tk.X, pady=5)
        
        btn_disconnect = tk.Button(
            controls_frame,
            text="🔌 Disconnect",
            command=self.disconnect,
            font=("Arial", 12),
            bg='#0f3460',
            fg='#ffffff',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        btn_disconnect.pack(fill=tk.X, pady=5)
        
        # Bottom status bar
        bottom_frame = tk.Frame(self.root, bg='#16213e', height=40)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_bar_label = tk.Label(
            bottom_frame,
            text="Status: Connecting...",
            font=("Consolas", 11),
            fg='#00ff88',
            bg='#16213e',
            anchor=tk.W
        )
        self.status_bar_label.pack(fill=tk.X, padx=10)
    
    def connect_to_pi(self):
        """Establish connection to Raspberry Pi."""
        print(f"\nConnecting to Raspberry Pi at {self.pi_ip}...")
        self.update_status(f"Connecting to\n{self.pi_ip}...\nVideo Port: {self.video_port}")
        
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
            self.update_status(f"✓ CONNECTED\nto Pi {self.pi_ip}\nStreaming video...")
            self.update_status_bar("Connected | Receiving frames")
            
            # Send start command
            self.send_command('start')
            
            return True
            
        except socket.timeout:
            print(f"✗ Connection timed out (5 seconds)")
            print(f"  Is the Pi server running?")
            self.update_status(f"✗ TIMEOUT\nPi not responding\nCheck server is running")
            return False
            
        except ConnectionRefusedError:
            print(f"✗ Connection refused")
            print(f"  Make sure pi_camera_server.py is running on Pi")
            self.update_status(f"✗ REFUSED\nServer not running\nStart on Pi first")
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
            import json
            command = {'type': cmd_type, 'timestamp': int(time.time())}
            if params:
                command.update(params)
            
            self.command_socket.send(json.dumps(command).encode())
        except Exception as e:
            print(f"Command error: {e}")
    
    def receive_frames(self):
        """Receive video frames from Pi."""
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
            self.update_status_bar("Disconnected | Connection lost")
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
        """Detect objects in frame."""
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
        """Draw detections with colored boxes."""
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
            
            label = f"{det['name']} {det['distance']:.1f}m"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return frame
    
    def announce_detections(self):
        """Announce detected objects."""
        current_time = time.time()
        
        if current_time - self.last_announcement < self.announcement_interval:
            return
        
        # Filter nearby (< 20m)
        nearby = [d for d in self.detections if 0 < d['distance'] <= 20.0]
        
        if not nearby:
            return
        
        nearby.sort(key=lambda x: x['distance'])
        top_objects = nearby[:3]
        
        if len(top_objects) == 1:
            obj = top_objects[0]
            if obj['distance'] < 2.0:
                msg = f"Warning! {obj['name']} very close, {obj['distance']} meters"
            elif obj['distance'] < 5.0:
                msg = f"{obj['name']} nearby, {obj['distance']} meters"
            elif obj['distance'] < 10.0:
                msg = f"{obj['name']} ahead, {obj['distance']} meters"
            else:
                msg = f"{obj['name']} in front, {obj['distance']} meters"
        else:
            names = [o['name'] for o in top_objects]
            msg = f"{', '.join(names[:-1])}, and {names[-1]} detected"
        
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
        """Disconnect from Pi."""
        self.running = False
        self.connected = False
        
        if self.video_socket:
            self.video_socket.close()
        if self.command_socket:
            self.command_socket.close()
        
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
        """Update statistics."""
        fps_str = f"FPS: {self.fps:.1f}"
        obj_str = f"Objects: {len(self.detections)}"
        conn_str = "Connected" if self.connected else "Disconnected"
        
        self.update_status_bar(f"{fps_str} | {obj_str} | {conn_str}")
    
    def update_detections_display(self):
        """Update detections list."""
        self.detections_text.config(state='normal')
        self.detections_text.delete('1.0', tk.END)
        
        if not self.detections:
            self.detections_text.insert('1.0', "No objects detected\n")
        else:
            sorted_dets = sorted(self.detections, key=lambda x: x['distance'])
            
            for i, det in enumerate(sorted_dets, 1):
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
                line += f"   Distance: {distance:.1f}m {indicator}\n"
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
        print(" BlindStick - Raspberry Pi Camera Client")
        print("=" * 60)
        print(f"\nConnecting to Pi at {self.pi_ip}...")
        print("Video Port: 8889 | Command Port: 8890")
        print("=" * 60)
        
        # Connect FIRST (before UI mainloop)
        print("\nEstablishing connection...")
        if not self.connect_to_pi():
            print("\n✗ Connection failed! Please check:")
            print("  1. Pi server is running: python3 pi_camera_server.py")
            print("  2. Correct IP address")
            print("  3. Both devices on same network")
            return
        
        # Start frame receiving thread
        receive_thread = threading.Thread(target=self.receive_frames)
        receive_thread.daemon = True
        receive_thread.start()
        
        print("\n✓ Connection successful! Opening UI...")
        
        # Now start UI
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            self.disconnect()


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description='Connect to Raspberry Pi camera server')
    parser.add_argument('--ip', type=str, required=True, help='Raspberry Pi IP address')
    parser.add_argument('--video-port', type=int, default=8889, help='Video stream port')
    parser.add_argument('--command-port', type=int, default=8890, help='Command port')
    
    args = parser.parse_args()
    
    client = PiCameraClient(
        pi_ip_address=args.ip,
        video_port=args.video_port,
        command_port=args.command_port
    )
    client.run()


if __name__ == '__main__':
    main()
