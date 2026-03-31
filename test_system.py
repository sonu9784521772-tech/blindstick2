"""
Test Script for BlindStick System

This script tests all components of the BlindStick system
to ensure everything is working correctly.

Usage:
    python test_system.py
"""

import sys
import os
from pathlib import Path


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def test_imports():
    """Test if all required packages can be imported."""
    print_header("Testing Package Imports")
    
    required_packages = {
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'yaml': 'PyYAML',
        'ultralytics': 'Ultralytics (YOLO)'
    }
    
    failed = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name} ({package}) - OK")
        except ImportError as e:
            print(f"✗ {name} ({package}) - FAILED")
            print(f"  Error: {e}")
            failed.append(package)
    
    # Optional packages
    optional_packages = {
        'pyttsx3': 'pyttsx3 TTS',
        'gtts': 'gTTS',
        'playsound': 'playsound'
    }
    
    print("\nOptional Packages:")
    for package, name in optional_packages.items():
        try:
            __import__(package)
            print(f"✓ {name} ({package}) - OK")
        except ImportError:
            print(f"○ {name} ({package}) - Not installed (optional)")
    
    if failed:
        print(f"\n⚠ Missing required packages: {', '.join(failed)}")
        print("Install with: pip install " + ' '.join(failed))
        return False
    
    print("\n✓ All required packages are installed!")
    return True


def test_cuda():
    """Test CUDA availability."""
    print_header("Testing CUDA/GPU Support")
    
    try:
        import torch
        
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda if cuda_available else None
        
        if cuda_available:
            print(f"✓ CUDA is available!")
            print(f"  CUDA Version: {cuda_version}")
            print(f"  GPU Count: {torch.cuda.device_count()}")
            print(f"  Current GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("○ CUDA is not available")
            print("  Will use CPU for inference (slower but functional)")
            print("  For GPU support, install CUDA-enabled PyTorch:")
            print("  Visit: https://pytorch.org/get-started/locally/")
        
        return True
        
    except Exception as e:
        print(f"✗ Error checking CUDA: {e}")
        return False


def test_model_loading():
    """Test if YOLO model can be loaded."""
    print_header("Testing Model Loading")
    
    try:
        from ultralytics import YOLO
        
        print("Loading YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        
        print("✓ Model loaded successfully!")
        print(f"  Model type: {type(model)}")
        
        # Test model info
        info = model.info()
        print(f"  Model parameters: {info}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection (model downloads on first use)")
        print("2. Try: pip install ultralytics --upgrade")
        return False


def test_config():
    """Test configuration file."""
    print_header("Testing Configuration")
    
    config_path = Path('config.yaml')
    
    if not config_path.exists():
        print("✗ config.yaml not found!")
        print("  Creating default configuration...")
        return False
    
    try:
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print("✓ Configuration file loaded successfully!")
        print(f"  Dataset: {config.get('dataset', {}).get('name', 'N/A')}")
        print(f"  Model: {config.get('model', {}).get('type', 'N/A')}")
        print(f"  TTS Engine: {config.get('tts', {}).get('engine', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading config: {e}")
        return False


def test_tts():
    """Test text-to-speech functionality."""
    print_header("Testing Text-to-Speech")
    
    try:
        from tts import TTSEngine
        
        print("Initializing TTS engine...")
        tts = TTSEngine(engine_type='pyttsx3', rate=150)
        
        print("✓ TTS engine initialized!")
        
        # Test speech
        test_text = "BlindStick system test successful"
        print(f"Testing speech: '{test_text}'")
        tts.speak(test_text, async_mode=False)
        
        tts.shutdown()
        print("✓ TTS test completed!")
        
        return True
        
    except ImportError as e:
        print(f"○ TTS not available: {e}")
        print("  Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"✗ TTS error: {e}")
        return False


def test_camera():
    """Test camera access."""
    print_header("Testing Camera Access")
    
    try:
        import cv2
        
        print("Attempting to open default camera...")
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera opened successfully!")
                print(f"  Frame size: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
                return True
            else:
                print("✗ Could not read from camera")
                cap.release()
                return False
        else:
            print("○ No camera found or camera is in use")
            print("  You can still use video files for testing")
            return False
            
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def test_directory_structure():
    """Test project directory structure."""
    print_header("Testing Directory Structure")
    
    required_files = [
        'config.yaml',
        'requirements.txt',
        'dataset.py',
        'model.py',
        'train.py',
        'detect.py',
        'tts.py',
        'README.md'
    ]
    
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            missing.append(file)
    
    if missing:
        print(f"\n⚠ Missing files: {', '.join(missing)}")
        return False
    
    print("\n✓ All required files present!")
    return True


def run_quick_inference():
    """Run quick inference test."""
    print_header("Running Quick Inference Test")
    
    try:
        from ultralytics import YOLO
        import numpy as np
        
        # Create a test image (random noise)
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        print("Loading model...")
        model = YOLO('yolov8n.pt')
        
        print("Running inference on test image...")
        results = model.predict(test_image, verbose=False)
        
        print("✓ Inference completed successfully!")
        
        if results[0].boxes is not None:
            print(f"  Detections: {len(results[0].boxes)}")
        else:
            print("  Detections: 0 (expected for random noise)")
        
        return True
        
    except Exception as e:
        print(f"✗ Inference test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(" BlindStick System Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results['directory'] = test_directory_structure()
    results['imports'] = test_imports()
    results['config'] = test_config()
    results['cuda'] = test_cuda()
    results['model'] = test_model_loading()
    results['inference'] = run_quick_inference()
    results['tts'] = test_tts()
    results['camera'] = test_camera()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Download ORBIT dataset")
        print("2. Prepare dataset: python prepare_dataset.py --source /path/to/orbit --output data/orbit")
        print("3. Train model: python train.py --data data/orbit")
        print("4. Run detection: python detect.py --source 0")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCritical failures (must fix):")
        if not results['imports']:
            print("  - Package imports (run: pip install -r requirements.txt)")
        if not results['model']:
            print("  - Model loading")
        if not results['directory']:
            print("  - Directory structure")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
