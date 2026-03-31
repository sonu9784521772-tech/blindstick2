"""
Simple Mobile App Alternative - Python + OpenCV
This runs directly on your PC and provides the same functionality
without needing Flutter/mobile setup.

Usage:
    python simple_app.py
"""

import cv2
import numpy as np
import pyttsx3
from ultralytics import YOLO
import threading
import time
from datetime import datetime


class SimpleBlindStick:
    """Simplified BlindStick for PC testing."""
    
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.tts_engine = None
        self.is_speaking = False
        self.last_announcement = time.time()
        self.announcement_interval = 3.0  # seconds
        
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            print("✓ Text-to-speech initialized")
        except Exception as e:
            print(f"⚠ TTS not available: {e}")
            print("  Will run without audio feedback")
    
    def detect_objects(self, frame):
        """Detect objects in frame."""
        results = self.model.predict(frame, conf=0.5, verbose=False)
        
        detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                name = results[0].names[cls]
                
                # Calculate distance (simplified)
                x1, y1, x2, y2 = xyxy
                height = y2 - y1
                distance = self.estimate_distance(height, name)
                
                detections.append({
                    'name': name,
                    'confidence': conf,
                    'distance': distance,
                    'bbox': (x1, y1, x2, y2)
                })
        
        return detections
    
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
            return round((ref * 640) / (bbox_height * 100), 2)
        return 0.0
    
    def announce(self, detections):
        """Announce detected objects."""
        current_time = time.time()
        
        # Check if enough time passed
        if current_time - self.last_announcement < self.announcement_interval:
            return
        
        # Filter nearby objects (< 20m)
        nearby = [d for d in detections if d['distance'] <= 20.0 and d['distance'] > 0]
        
        if not nearby:
            return
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance'])
        
        # Get top 3 closest
        top_objects = nearby[:3]
        
        # Create announcement
        if len(top_objects) == 1:
            obj = top_objects[0]
            msg = f"{obj['name']} {'very close' if obj['distance'] < 2 else 'nearby'}, {obj['distance']} meters"
        elif len(top_objects) == 2:
            msg = f"{top_objects[0]['name']} and {top_objects[1]['name']} detected"
        else:
            names = [o['name'] for o in top_objects]
            msg = f"{', '.join(names[:-1])}, and {names[-1]} detected"
        
        # Speak
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
    
    def draw_detections(self, frame, detections):
        """Draw detections on frame."""
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            
            # Draw box
            color = (0, 255, 0) if det['distance'] < 5 else (0, 255, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['name']} {det['distance']}m"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def run(self, source=0):
        """Run the application."""
        print("=" * 60)
        print(" BlindStick - Simple PC Version")
        print("=" * 60)
        print("\nStarting camera...")
        print("Press 'q' to quit, 's' to speak current detections")
        print("=" * 60)
        
        # Use DirectShow backend for Windows (more stable)
        cap = cv2.VideoCapture(source if isinstance(source, int) else str(source), cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("✗ Error: Could not open camera")
            print("  Make sure camera is connected")
            return
        
        print(f"✓ Camera opened: {int(cap.get(3))}x{int(cap.get(4))}")
        
        frame_count = 0
        fps = 0
        last_fps_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect
                detections = self.detect_objects(frame)
                
                # Draw
                annotated = self.draw_detections(frame, detections)
                
                # Announce
                self.announce(detections)
                
                # Update FPS
                frame_count += 1
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    fps = frame_count / (current_time - last_fps_time)
                    frame_count = 0
                    last_fps_time = current_time
                
                # Draw FPS
                cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated, f"Objects: {len(detections)}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show
                cv2.imshow('BlindStick - Simple Version', annotated)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.announce(detections)
        
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\nStopped")


def main():
    """Main function."""
    app = SimpleBlindStick()
    app.run(source=0)  # Use webcam


if __name__ == '__main__':
    main()
