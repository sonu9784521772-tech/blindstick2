"""
Quick Camera Test - Verifies camera is working before running full app
This will show you exactly what the camera sees in a simple window.

Usage:
    python quick_camera_test.py
"""

import cv2
import numpy as np
import time

print("=" * 60)
print(" Quick Camera Test")
print("=" * 60)

# Try to find working camera
camera_indices = [2, 0, 1]
working_camera = None
best_brightness = 0

for cam_idx in camera_indices:
    print(f"\nTesting camera {cam_idx}...")
    
    cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"  ✗ Camera {cam_idx} not available")
        continue
    
    # Wait for camera to initialize
    time.sleep(1.0)
    
    # Try to get frames
    max_brightness = 0
    good_frames = 0
    
    for i in range(30):  # Try 30 frames
        ret, frame = cap.read()
        
        if ret and frame is not None:
            brightness = float(np.mean(frame))
            max_brightness = max(max_brightness, brightness)
            
            if brightness > 20:
                good_frames += 1
    
    cap.release()
    
    print(f"  Max brightness: {max_brightness:.1f}")
    print(f"  Good frames: {good_frames}/30")
    
    if good_frames > 10 and max_brightness > 30:
        print(f"  ✓ Camera {cam_idx} looks GOOD!")
        if max_brightness > best_brightness:
            best_brightness = max_brightness
            working_camera = cam_idx
    else:
        print(f"  ⚠ Camera {cam_idx} has issues")

print("\n" + "=" * 60)

if working_camera is not None:
    print(f"✓ Found working camera: #{working_camera}")
    print(f"  Brightness: {best_brightness:.1f}")
    print("\nOpening camera test window...")
    print("Press 'q' to quit\n")
    
    # Open the working camera with live preview
    cap = cv2.VideoCapture(working_camera, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_count = 0
    last_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("✗ Lost camera signal!")
            break
        
        # Calculate and display brightness
        brightness = float(np.mean(frame))
        
        # Add brightness text to frame
        cv2.putText(frame, f"Brightness: {brightness:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add FPS counter
        frame_count += 1
        current_time = time.time()
        if current_time - last_time >= 1.0:
            fps = frame_count / (current_time - last_time)
            frame_count = 0
            last_time = current_time
            
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow(f'Camera {working_camera} Test', frame)
        
        # Check for quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✓ Test complete!")
    print(f"\nCamera {working_camera} is working correctly.")
    print("You can now run: python ui_app.py")
    
else:
    print("✗ No working cameras found!")
    print("\nTroubleshooting:")
    print("1. Close other apps using camera")
    print("2. Try different USB port")
    print("3. Update camera drivers")
    print("4. Run: python diagnose_camera.py")

print("=" * 60)
