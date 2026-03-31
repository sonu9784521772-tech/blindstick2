"""
Camera Diagnostic Tool - Find and test your cameras
This will help identify camera issues and find the best settings.

Usage:
    python diagnose_camera.py
"""

import cv2
import numpy as np
import time

print("=" * 60)
print(" Camera Diagnostic Tool for BlindStick")
print("=" * 60)

# Test different camera backends on Windows
backends = [
    (cv2.CAP_DSHOW, "DirectShow"),
    (cv2.CAP_MSMF, "Media Foundation"),
    (cv2.CAP_ANY, "Auto-detect")
]

resolutions = [
    (640, 480),
    (320, 240),
    (800, 600),
    (1280, 720)
]

print("\nTesting all available cameras...\n")

for backend_id, backend_name in backends:
    print(f"\n--- Testing Backend: {backend_name} ---")
    
    for camera_index in range(4):
        print(f"\nTrying camera {camera_index}...")
        
        cap = cv2.VideoCapture(camera_index, backend_id)
        
        if not cap.isOpened():
            print(f"  ✗ Camera {camera_index} not available with {backend_name}")
            continue
        
        print(f"  ✓ Camera {camera_index} opened!")
        
        # Try different resolutions
        for width, height in resolutions:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Wait a moment for camera to adjust
            time.sleep(0.5)
            
            # Try to grab multiple frames
            success_count = 0
            total_frames = 10
            
            for i in range(total_frames):
                ret, frame = cap.read()
                if ret and frame is not None:
                    success_count += 1
                    
                    # Check if frame is actually black
                    mean_brightness = np.mean(frame)
                    if mean_brightness < 20:
                        print(f"    Resolution {width}x{height}: ✓ Frame captured but VERY DARK (brightness: {mean_brightness:.1f})")
                    elif mean_brightness > 250:
                        print(f"    Resolution {width}x{height}: ✓ Frame captured but OVEREXPOSED (brightness: {mean_brightness:.1f})")
                    else:
                        print(f"    Resolution {width}x{height}: ✓ GOOD (brightness: {mean_brightness:.1f})")
                    
                    # Save a test image
                    if i == 0:
                        filename = f"test_cam{camera_index}_{width}x{height}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"      → Saved test image: {filename}")
                    break
            
            if success_count == 0:
                print(f"    Resolution {width}x{height}: ✗ Failed to capture frames")
        
        # Get actual properties
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"\n  Camera {camera_index} Properties:")
        print(f"    Actual Resolution: {actual_width}x{actual_height}")
        print(f"    FPS: {actual_fps}")
        print(f"    Backend: {backend_name}")
        
        cap.release()
        print(f"  ✓ Camera {camera_index} test complete\n")

print("\n" + "=" * 60)
print(" Diagnostic Complete!")
print("=" * 60)

print("\n📋 RECOMMENDATIONS:\n")
print("1. Look for cameras marked with ✓ GOOD brightness")
print("2. Use the backend that worked best (usually DirectShow)")
print("3. Check saved test images to verify quality")
print("4. If all are dark, improve lighting or check camera")
print("5. If all show 'not available', check USB connections\n")

print("💡 TROUBLESHOOTING TIPS:")
print("  • Close other apps using camera (Zoom, Teams, browsers)")
print("  • Try different USB port")
print("  • Update camera drivers")
print("  • Restart computer")
print("  • Check if camera works in other apps\n")

print("=" * 60)
