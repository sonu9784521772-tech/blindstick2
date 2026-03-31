"""
Raspberry Pi Camera Server for BlindStick App (picamera2 version)
Works with newer Raspberry Pi OS (Bookworm) using libcamera

Usage:
    python3 pi_camera_server_v2.py
"""

import socket
import struct
import io
import time
import json
import threading
from datetime import datetime

# Use picamera2 for newer Pi OS
from picamera2 import Picamera2
from PIL import Image


class PiCameraServer:
    """Raspberry Pi Camera Server using picamera2."""
    
    def __init__(self, host='0.0.0.0', port=8889, command_port=8890):
        self.host = host
        self.port = port
        self.command_port = command_port
        
        # Camera settings
        self.resolution = (640, 480)
        self.fps = 15
        
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
        
        # Camera
        self.camera = None
        
    def setup_camera(self):
        """Setup Raspberry Pi camera using picamera2."""
        try:
            self.camera = Picamera2()
            
            # Configure camera - NO adjustments, raw sensor output
            config = self.camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            
            # NO manual controls - let camera use its default auto settings
            
            # Let camera warm up
            time.sleep(2)
            
            print("✓ Camera initialized successfully (picamera2)")
            return True
            
        except Exception as e:
            print(f"✗ Camera initialization failed: {e}")
            print("  Make sure camera is connected and enabled")
            print("  Check with: libcamera-hello")
            return False
    
    def start_server(self):
        """Start the camera server."""
        print("=" * 60)
        print(" BlindStick Raspberry Pi Camera Server (v2)")
        print("=" * 60)
        
        # Get IP address
        ip_address = self.get_ip_address()
        print(f"\nServer IP: {ip_address}")
        print(f"Video Stream Port: {self.port}")
        print(f"Command Port: {self.command_port}")
        print("=" * 60)
        
        # Setup camera
        if not self.setup_camera():
            print("\n✗ Failed to initialize camera. Exiting.")
            return
        
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
        print("\nWaiting for PC client connection...")
        print(f"\nOn your PC, run:")
        print(f"  python pi_camera_client.py --ip {ip_address}")
        
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
                    data = self.command_client.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    command = json.loads(data)
                    cmd_type = command.get('type', '')
                    print(f"Received command: {cmd_type}")
                    
                    if cmd_type == 'start':
                        self.streaming = True
                        response = {'status': 'started', 'resolution': self.resolution}
                        self.command_client.send(json.dumps(response).encode())
                        
                    elif cmd_type == 'stop':
                        self.streaming = False
                        response = {'status': 'stopped'}
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
        print("Starting video stream...")
        
        try:
            while self.streaming and self.running:
                if not self.client_socket:
                    break
                
                try:
                    # Capture frame
                    frame = self.camera.capture_array()
                    
                    # Fix bluish tint by swapping BGR to RGB
                    frame = frame[:, :, ::-1]
                    
                    # Convert to JPEG
                    img = Image.fromarray(frame)
                    buffer = io.BytesIO()
                    img.save(buffer, format='JPEG', quality=85)
                    data = buffer.getvalue()
                    buffer.close()
                    
                    # Send frame size first (4 bytes, big-endian)
                    size = len(data)
                    self.client_socket.sendall(struct.pack('>I', size))
                    
                    # Send frame data
                    self.client_socket.sendall(data)
                    
                    self.frames_sent += 1
                    
                    # Log every 30 frames
                    if self.frames_sent % 30 == 0:
                        print(f"Frames sent: {self.frames_sent}")
                    
                    # Control frame rate
                    time.sleep(1.0 / self.fps)
                    
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected")
                    break
                except Exception as e:
                    print(f"Frame error: {e}")
                    break
                    
        except Exception as e:
            print(f"Streaming error: {e}")
        finally:
            print("Streaming stopped")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
    
    def get_ip_address(self):
        """Get Raspberry Pi IP address."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
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
            self.camera.stop()
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
