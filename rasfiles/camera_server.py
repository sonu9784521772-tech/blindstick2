#!/usr/bin/env python3
"""
BlindStick Raspberry Pi Camera Server - MAIN SERVER
For Raspberry Pi OS Lite
Streams video at 7 FPS to Windows client

USAGE:
    cd ~/rasfiles
    python3 camera_server.py
"""

import socket
import struct
import subprocess
import time
import json
import threading


class CameraServer:
    def __init__(self):
        self.port = 8889
        self.command_port = 8890
        self.resolution = (640, 480)
        self.fps = 7
        self.server_socket = None
        self.command_socket = None
        self.client_socket = None
        self.command_client = None
        self.streaming = False
        self.running = True
        self.frames_sent = 0
        
    def check_camera(self):
        try:
            result = subprocess.run(
                ['libcamera-hello', '--list-cameras'],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Camera found: {result.stdout.decode().strip()}")
                return True
        except:
            pass
        print("⚠ No camera detected - will use test mode")
        return False
    
    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
        except:
            return '127.0.0.1'
        finally:
            s.close()
    
    def stream_video(self):
        if not self.check_camera():
            print("ℹ️  Sending test frames (no camera)")
            self.send_test_frames()
            return
        
        print(f"\n🎬 Streaming at {self.fps} FPS...")
        cmd = [
            'libcamera-vid',
            '--width', str(self.resolution[0]),
            '--height', str(self.resolution[1]),
            '--framerate', str(self.fps),
            '--codec', 'mjpeg',
            '--timeout', '0',
            '--inline'
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        buffer = b''
        frame_time = 1.0 / self.fps
        
        try:
            while self.streaming and self.client_socket and process.poll() is None:
                start = time.time()
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                
                buffer += chunk
                start_idx = buffer.find(b'\xff\xd8')
                end_idx = buffer.find(b'\xff\xd9')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    frame = buffer[start_idx:end_idx + 2]
                    try:
                        self.client_socket.sendall(struct.pack('>I', len(frame)))
                        self.client_socket.sendall(frame)
                        self.frames_sent += 1
                        
                        if self.frames_sent % 30 == 0:
                            elapsed = time.time() - self.start_time
                            avg_fps = self.frames_sent / elapsed if elapsed > 0 else 0
                            print(f"📊 Sent: {self.frames_sent} ({avg_fps:.1f} FPS)")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        break
                    buffer = buffer[end_idx + 2:]
                
                sleep_time = max(0, frame_time - (time.time() - start))
                if sleep_time > 0:
                    time.sleep(sleep_time)
        finally:
            process.terminate()
    
    def send_test_frames(self):
        test_frame = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46,
            0x00, 0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
            0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06,
            0x05, 0x08, 0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C,
            0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
            0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28,
            0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27,
            0x39, 0x3D, 0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF,
            0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01,
            0x11, 0x00, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00,
            0x3F, 0x00, 0xFB, 0xD5, 0xDB, 0x20, 0xBA, 0xE3, 0x3D, 0x21,
            0x26, 0x20, 0x89, 0x00, 0x02, 0x1F, 0xFF, 0xD9])
        
        frame_time = 1.0 / self.fps
        try:
            while self.streaming and self.client_socket:
                start = time.time()
                self.client_socket.sendall(struct.pack('>I', len(test_frame)))
                self.client_socket.sendall(test_frame)
                self.frames_sent += 1
                if self.frames_sent % 30 == 0:
                    print(f"📊 Sent: {self.frames_sent} test frames")
                sleep_time = max(0, frame_time - (time.time() - start))
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except Exception as e:
            print(f"Error: {e}")
    
    def handle_commands(self):
        while self.running and self.command_client:
            try:
                self.command_client.settimeout(2.0)
                data = self.command_client.recv(1024).decode('utf-8')
                if not data:
                    break
                cmd = json.loads(data)
                if cmd.get('type') == 'start':
                    self.streaming = True
                    self.start_time = time.time()
                    response = {'status': 'started'}
                    self.command_client.send(json.dumps(response).encode())
                    print("✓ Started streaming")
                elif cmd.get('type') == 'stop':
                    self.streaming = False
                    response = {'status': 'stopped'}
                    self.command_client.send(json.dumps(response).encode())
                elif cmd.get('type') == 'ping':
                    response = {'status': 'pong'}
                    self.command_client.send(json.dumps(response).encode())
            except:
                break
        if self.command_client:
            self.command_client.close()
    
    def accept_commands(self):
        while self.running:
            try:
                self.command_socket.settimeout(1.0)
                try:
                    self.command_client, addr = self.command_socket.accept()
                    print(f"✅ Command client connected")
                    self.handle_commands()
                except socket.timeout:
                    continue
            except Exception as e:
                if self.running:
                    print(f"Command error: {e}")
    
    def start(self):
        print("=" * 60)
        print(" 👁️ BlindStick Pi Camera Server")
        print("=" * 60)
        print(f"\n📡 IP: {self.get_ip()}")
        print(f"📹 Port: {self.port}")
        print(f"🎮 Commands: {self.command_port}")
        print(f"⚡ FPS: {self.fps}")
        print("=" * 60)
        
        # Create sockets
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(1)
        
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_socket.bind(('0.0.0.0', self.command_port))
        self.command_socket.listen(1)
        
        print(f"\n✓ Listening on :{self.port}")
        print(f"✓ Commands on :{self.command_port}")
        print("\n⏳ Waiting for Windows client...")
        print("   Press Ctrl+C to stop\n")
        
        # Start command thread
        threading.Thread(target=self.accept_commands, daemon=True).start()
        
        # Accept connections
        try:
            while self.running:
                self.client_socket, addr = self.server_socket.accept()
                print(f"\n✅ Client connected from {addr[0]}")
                
                # Send connection info
                info = {'type': 'connection_info', 'fps': self.fps}
                data = json.dumps(info).encode()
                self.client_socket.sendall(struct.pack('>I', len(data)))
                self.client_socket.sendall(b'\xFE' + data)
                
                # Start streaming
                self.streaming = True
                self.stream_video()
        except KeyboardInterrupt:
            print("\n\n⏹️ Stopped")
        finally:
            self.cleanup()
    
    def cleanup(self):
        print("\n🧹 Cleaning up...")
        self.running = False
        for sock in [self.client_socket, self.command_client, 
                     self.server_socket, self.command_socket]:
            if sock:
                try:
                    sock.close()
                except:
                    pass
        print(f"✅ Total frames: {self.frames_sent}")


if __name__ == '__main__':
    server = CameraServer()
    server.start()
