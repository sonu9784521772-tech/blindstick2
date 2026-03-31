"""
Raspberry Pi Camera Server for BlindStick App

This script runs on Raspberry Pi 3 and:
1. Captures images from Pi Camera Module
2. Streams images to mobile app via WiFi
3. Receives commands from app

Usage:
    python pi_camera_server.py
    
Setup:
    1. Enable camera: sudo raspi-config -> Interface Options -> Camera
    2. Install dependencies: pip install -r requirements-pi.txt
    3. Run this script
"""

import socket
import struct
import io
import time
import picamera
import json
import threading
from datetime import datetime


class PiCameraServer:
    """Raspberry Pi Camera Server."""
    
    def __init__(self, host='0.0.0.0', port=8889, command_port=8890):
        """
        Initialize Pi camera server.
        
        Args:
            host: Server host IP
            port: Port for video streaming
            command_port: Port for receiving commands
        """
        self.host = host
        self.port = port
        self.command_port = command_port
        
        # Camera settings
        self.resolution = (640, 480)
        self.fps = 15
        self.use_camera = True
        
        # Server sockets
        self.server_socket = None
        self.command_socket = None
        self.client_socket = None
        self.command_client = None
        
        # Control flags
        self.streaming = False
        self.running = True
        
        # Status
        self.connected_clients = 0
        self.frames_sent = 0
        
    def setup_camera(self):
        """Setup Raspberry Pi camera."""
        try:
            self.camera = picamera.PiCamera()
            self.camera.resolution = self.resolution
            self.camera.framerate = self.fps
            
            # Adjust camera settings for better quality
            self.camera.brightness = 50
            self.camera.contrast = 60
            self.camera.sharpness = 20
            
            print("✓ Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"✗ Camera initialization failed: {e}")
            print("  Make sure camera is connected and enabled")
            print("  Enable with: sudo raspi-config -> Interface Options -> Camera")
            self.use_camera = False
            return False
    
    def start_server(self):
        """Start the camera server."""
        print("=" * 60)
        print(" BlindStick Raspberry Pi Camera Server")
        print("=" * 60)
        
        # Get IP address
        ip_address = self.get_ip_address()
        print(f"\nServer IP: {ip_address}")
        print(f"Video Stream Port: {self.port}")
        print(f"Command Port: {self.command_port}")
        print("=" * 60)
        
        # Setup camera
        if self.use_camera:
            self.setup_camera()
        
        # Create sockets
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_socket.bind((self.host, self.command_port))
        self.command_socket.listen(1)
        
        print(f"\n✓ Server listening on {self.host}:{self.port}")
        print(f"✓ Command server listening on {self.host}:{self.command_port}")
        print("\nWaiting for mobile app connection...")
        
        # Start command listener thread
        command_thread = threading.Thread(target=self.accept_commands)
        command_thread.daemon = True
        command_thread.start()
        
        # Accept client connections
        try:
            while self.running:
                self.client_socket, address = self.server_socket.accept()
                print(f"\n✓ Client connected from {address[0]}")
                self.connected_clients += 1
                
                # Send connection info
                self.send_connection_info()
                
                # Start streaming
                self.streaming = True
                self.stream_video()
                
        except KeyboardInterrupt:
            print("\n\nServer stopped by user")
        finally:
            self.cleanup()
    
    def accept_commands(self):
        """Accept command connections from app."""
        while self.running:
            try:
                self.command_socket.settimeout(1.0)
                try:
                    self.command_client, address = self.command_socket.accept()
                    print(f"✓ Command client connected from {address[0]}")
                    
                    # Handle commands
                    self.handle_commands()
                    
                except socket.timeout:
                    continue
                    
            except Exception as e:
                if self.running:
                    print(f"Command error: {e}")
    
    def handle_commands(self):
        """Handle commands from mobile app."""
        while self.running and self.command_client:
            try:
                self.command_client.settimeout(2.0)
                
                try:
                    # Receive command
                    data = self.command_client.recv(1024).decode('utf-8')
                    
                    if not data:
                        break
                    
                    command = json.loads(data)
                    cmd_type = command.get('type', '')
                    
                    print(f"Received command: {cmd_type}")
                    
                    # Process command
                    if cmd_type == 'start':
                        self.streaming = True
                        self.resolution = (command.get('width', 640), 
                                         command.get('height', 480))
                        self.fps = command.get('fps', 15)
                        
                        if self.use_camera:
                            self.camera.resolution = self.resolution
                            self.camera.framerate = self.fps
                        
                        response = {'status': 'started', 'resolution': self.resolution}
                        self.command_client.send(json.dumps(response).encode())
                        
                    elif cmd_type == 'stop':
                        self.streaming = False
                        response = {'status': 'stopped'}
                        self.command_client.send(json.dumps(response).encode())
                        
                    elif cmd_type == 'capture':
                        # Capture single high-quality image
                        if self.use_camera:
                            self.capture_and_send_image()
                        response = {'status': 'captured'}
                        self.command_client.send(json.dumps(response).encode())
                        
                    elif cmd_type == 'ping':
                        response = {'status': 'pong', 'timestamp': time.time()}
                        self.command_client.send(json.dumps(response).encode())
                        
                    elif cmd_type == 'disconnect':
                        self.running = False
                        break
                        
                except socket.timeout:
                    continue
                except json.JSONDecodeError:
                    continue
                    
            except Exception as e:
                print(f"Command handling error: {e}")
                break
        
        if self.command_client:
            self.command_client.close()
            self.command_client = None
            print("Command client disconnected")
    
    def stream_video(self):
        """Stream video to connected client."""
        if not self.use_camera:
            print("No camera available, sending test pattern")
            return
        
        try:
            # Create stream
            stream = io.BytesIO()
            
            for frame in self.camera.capture_continuous(
                stream,
                format='jpeg',
                use_video_port=True,
                thumbnail=None,
                splitter_port=1
            ):
                if not self.streaming:
                    break
                
                if not self.client_socket:
                    break
                
                # Get frame data
                data = stream.getvalue()
                
                # Send frame size first
                size = len(data)
                self.client_socket.sendall(struct.pack('>I', size))
                
                # Send frame data
                self.client_socket.sendall(data)
                
                self.frames_sent += 1
                
                # Log every 30 frames
                if self.frames_sent % 30 == 0:
                    print(f"Frames sent: {self.frames_sent}")
                
                # Reset stream
                stream.seek(0)
                stream.truncate()
                
                # Small delay to control FPS
                time.sleep(1.0 / self.fps)
                
        except Exception as e:
            print(f"Streaming error: {e}")
        finally:
            stream.close()
    
    def capture_and_send_image(self):
        """Capture high-quality image and send to client."""
        if not self.client_socket or not self.use_camera:
            return
        
        try:
            # Capture high-quality image
            stream = io.BytesIO()
            self.camera.capture(stream, format='jpeg', quality=95)
            data = stream.getvalue()
            stream.close()
            
            # Send as special frame type (image)
            # Prefix with marker: 0xFF for image
            self.client_socket.sendall(struct.pack('>BI', 0xFF, len(data)))
            self.client_socket.sendall(data)
            
            print(f"Captured and sent image ({len(data)} bytes)")
            
        except Exception as e:
            print(f"Image capture error: {e}")
    
    def send_connection_info(self):
        """Send connection information to client."""
        if not self.client_socket:
            return
        
        try:
            info = {
                'type': 'connection_info',
                'server': 'BlindStick Pi Server',
                'version': '1.0',
                'resolution': self.resolution,
                'fps': self.fps,
                'timestamp': time.time()
            }
            
            # Send as JSON
            data = json.dumps(info).encode('utf-8')
            self.client_socket.sendall(struct.pack('>I', len(data)))
            self.client_socket.sendall(b'\xFE' + data)  # Marker 0xFE for metadata
            
        except Exception as e:
            print(f"Error sending info: {e}")
    
    def get_ip_address(self):
        """Get Raspberry Pi IP address."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    
    def cleanup(self):
        """Cleanup resources."""
        print("\nCleaning up...")
        
        self.running = False
        self.streaming = False
        
        if self.camera:
            self.camera.close()
        
        if self.client_socket:
            self.client_socket.close()
        
        if self.command_client:
            self.command_client.close()
        
        if self.server_socket:
            self.server_socket.close()
        
        if self.command_socket:
            self.command_socket.close()
        
        print("Server stopped")
        print(f"Total frames sent: {self.frames_sent}")


def main():
    """Main function."""
    server = PiCameraServer()
    server.start_server()


if __name__ == '__main__':
    main()
