"""
Quick Camera Test - Find Working Camera Index
Run this to find which camera index works on your system.

Usage:
    python test_camera.py
"""

import cv2

print("=" * 60)
print(" Camera Detection Test")
print("=" * 60)

# Test camera indices 0-3
for i in range(4):
    print(f"\nTesting camera {i}...")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Try DirectShow first
    
    if cap.isOpened():
        print(f"✓ Camera {i} OPENED successfully!")
        
        # Try to grab a frame
        ret, frame = cap.read()
        if ret:
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            print(f"  ✓ Frame captured successfully!")
            
            # Save test image
            cv2.imwrite(f"test_camera_{i}.jpg", frame)
            print(f"  ✓ Test image saved: test_camera_{i}.jpg")
        else:
            print(f"  ⚠ Could not capture frame")
        
        cap.release()
    else:
        print(f"✗ Camera {i} not available")

print("\n" + "=" * 60)
print("Test complete!")
print("\nIf NO cameras were found:")
print("1. Check camera is connected")
print("2. Close other apps using camera (Zoom, Teams, etc.)")
print("3. Try different USB port")
print("4. Install/update camera drivers")
print("=" * 60)
