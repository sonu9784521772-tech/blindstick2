"""
Bypass tflite_support installation issue on Windows to export YOLOv8 to TFLite directly.
"""
from ultralytics import YOLO
import ultralytics.utils.checks
import shutil
import os

# Monkey-patch check_requirements to ignore tflite_support failures
original_check_requirements = ultralytics.utils.checks.check_requirements

def patched_check_requirements(*args, **kwargs):
    req = args[0] if len(args) > 0 else kwargs.get("requirements", "")
    if isinstance(req, str) and "tflite_support" in req:
        print("Skipping check for tflite_support to avoid compilation errors on Windows.")
        return True
    if isinstance(req, list):
        filtered = [r for r in req if "tflite_support" not in r]
        if filtered:
            return original_check_requirements(filtered, *args[1:], **kwargs)
        return True
    return original_check_requirements(*args, **kwargs)

ultralytics.utils.checks.check_requirements = patched_check_requirements

DEST = os.path.join("mobile_app", "assets", "models", "yolov8n.tflite")

def main():
    print("Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")
    
    # We set int8=False, half=False to just get the float32 fallback model
    print("Exporting to TFLite (bypassing MSVC++ Build Tools requirement)...")
    result = model.export(format="tflite", imgsz=640)
    
    # Locate the TFLite file
    tflite_path = None
    search_dirs = [".", "yolov8n_saved_model", "runs"]
    for d in search_dirs:
        if not os.path.exists(d): continue
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.endswith(".tflite"):
                    candidate = os.path.join(root, f)
                    if tflite_path is None or "float32" in f:
                        tflite_path = candidate
                        
    if result and os.path.isfile(str(result)) and str(result).endswith('.tflite'):
        tflite_path = str(result)
        
    if not tflite_path:
        raise FileNotFoundError("Could not find generated .tflite file!")
        
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    shutil.copy2(tflite_path, DEST)
    size = os.path.getsize(DEST) / (1024*1024)
    print(f"\nSUCCESS! Model saved to {DEST} ({size:.1f} MB)")

if __name__ == "__main__":
    main()
