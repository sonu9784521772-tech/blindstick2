"""
System Requirements Checker for BlindStick
Run this to check if all dependencies are installed.

Usage:
    python check_requirements.py
"""

import sys
import importlib


def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False


def main():
    """Check all requirements."""
    print("=" * 60)
    print(" BlindStick System Requirements Check")
    print("=" * 60)
    print()
    
    # Core packages
    print("Core Dependencies:")
    core_packages = [
        ('torch', 'torch'),
        ('torchvision', 'torchvision'),
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'),
        ('Pillow', 'PIL'),
        ('ultralytics', 'ultralytics'),
        ('pyttsx3', 'pyttsx3'),
    ]
    
    core_installed = []
    for package, import_name in core_packages:
        result = check_package(package, import_name)
        core_installed.append(result)
    
    print()
    
    # Optional packages
    print("Optional Dependencies:")
    optional_packages = [
        ('albumentations', 'albumentations'),
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib'),
        ('yaml', 'yaml'),
    ]
    
    for package, import_name in optional_packages:
        check_package(package, import_name)
    
    print()
    print("=" * 60)
    
    # Summary
    total = len(core_installed)
    installed = sum(core_installed)
    
    print(f"Core packages: {installed}/{total} installed")
    
    if installed == total:
        print("\n✓ All required packages are installed!")
        print("\nYou can now run:")
        print("  python simple_app.py          # Simple PC version")
        print("  python detect.py --source 0   # Full-featured version")
        print("  python train.py --help        # Training")
    else:
        print("\n⚠ Some packages are missing!")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        missing = [pkg for pkg, _ in core_packages if not check_package(pkg, pkg.split('-')[0])]
        if missing:
            print(f"  pip install {' '.join(missing)}")
    
    print("=" * 60)
    
    # Python version check
    print(f"\nPython version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✓ Python version is compatible (3.8+)")
    else:
        print("⚠ Python 3.8 or higher recommended")
    
    # CUDA check
    try:
        import torch
        if torch.cuda.is_available():
            print(f"\n✓ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("\n○ CUDA not available (will use CPU)")
    except:
        pass
    
    print("=" * 60)


if __name__ == '__main__':
    main()
