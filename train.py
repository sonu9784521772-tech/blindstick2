"""
Training Script for BlindStick Object Detection Model

This script trains a YOLO-based object detection model on the ORBIT dataset
for use in the BlindStick assistive navigation device.

Usage:
    python train.py --config config.yaml
    
    Or with custom parameters:
    python train.py --data data/orbit --epochs 100 --batch-size 16
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
import torch
from ultralytics import YOLO


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Train object detection model for BlindStick'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        default=None,
        help='Path to dataset directory or YAML file'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Number of training epochs'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='Training batch size'
    )
    
    parser.add_argument(
        '--img-size',
        type=int,
        default=None,
        help='Image size for training'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Model type (yolov8n, yolov8s, yolov8m, etc.)'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        help='Device to run training on (cuda/cpu)'
    )
    
    parser.add_argument(
        '--save-dir',
        type=str,
        default='runs/train',
        help='Directory to save training results'
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        default=None,
        help='Resume training from checkpoint'
    )
    
    parser.add_argument(
        '--pretrained',
        type=str,
        default=None,
        help='Path to pretrained weights'
    )
    
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        print("Using default configuration")
        return {}
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def create_dataset_yaml(dataset_dir: str, output_path: str = 'dataset.yaml') -> str:
    """
    Create a dataset YAML file for YOLO training.
    
    Args:
        dataset_dir: Root directory of the dataset
        output_path: Path to save the dataset YAML
        
    Returns:
        str: Path to created dataset YAML
    """
    dataset_path = Path(dataset_dir)
    
    # Define class names (customize based on ORBIT dataset)
    # These are example classes - adjust based on actual ORBIT labels
    class_names = [
        'person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck',
        'chair', 'table', 'door', 'stairs', 'obstacle', 'wall',
        'furniture', 'bag', 'umbrella', 'backpack', 'suitcase'
    ]
    
    dataset_yaml = {
        'path': str(dataset_path.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)
    
    print(f"Dataset YAML created: {output_path}")
    return output_path


def main():
    """Main training function."""
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    data_path = args.data or config.get('dataset', {}).get('root_dir', 'data/orbit')
    epochs = args.epochs or config.get('training', {}).get('epochs', 100)
    batch_size = args.batch_size or config.get('training', {}).get('batch_size', 16)
    img_size = args.img_size or config.get('preprocessing', {}).get('img_size', 640)
    model_type = args.model or config.get('model', {}).get('type', 'yolov8n')
    save_dir = args.save_dir
    
    # Set device
    if args.device:
        device = args.device
    else:
        gpu_id = config.get('device', {}).get('gpu', 0)
        device = f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu'
    
    print("=" * 60)
    print("BlindStick Object Detection Training")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Dataset: {data_path}")
    print(f"  Model: {model_type}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Image Size: {img_size}")
    print(f"  Device: {device}")
    print(f"  Save Directory: {save_dir}")
    print("=" * 60)
    
    # Check if dataset exists
    if not os.path.exists(data_path):
        print(f"\nWarning: Dataset directory not found: {data_path}")
        print("\nTo prepare the ORBIT dataset:")
        print("1. Download the ORBIT dataset")
        print("2. Organize it in the following format:")
        print("   data/orbit/")
        print("   ├── images/")
        print("   │   ├── train/")
        print("   │   ├── val/")
        print("   │   └── test/")
        print("   └── annotations/")
        print("       ├── train.json")
        print("       ├── val.json")
        print("       └── test.json")
        print("\nOr use YOLO format:")
        print("   data/orbit/")
        print("   ├── images/")
        print("   │   ├── train/")
        print("   │   └── val/")
        print("   └── labels/")
        print("       ├── train/")
        print("       └── val/")
        sys.exit(1)
    
    # Create dataset YAML if needed
    dataset_yaml_path = os.path.join(data_path, 'dataset.yaml')
    if not os.path.exists(dataset_yaml_path):
        print("\nCreating dataset YAML file...")
        dataset_yaml_path = create_dataset_yaml(data_path)
    
    # Initialize model
    print("\nInitializing model...")
    if args.pretrained:
        print(f"Loading pretrained weights from {args.pretrained}")
        model = YOLO(args.pretrained)
    else:
        print(f"Loading {model_type} model...")
        model = YOLO(f'{model_type}.pt')
    
    # Set device
    model.to(device)
    
    # Training arguments
    train_args = {
        'data': dataset_yaml_path,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': img_size,
        'device': device.split(':')[0] if ':' in device else device,
        'project': save_dir,
        'name': f'blindstick_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'exist_ok': True,
        'verbose': True,
        'patience': 50,  # Early stopping patience
        'save': True,
        'save_period': 10,  # Save checkpoint every 10 epochs
        'plots': True,  # Generate training plots
    }
    
    # Add augmentation settings from config
    aug_config = config.get('augmentation', {})
    if aug_config:
        train_args.update({
            'hsv_h': aug_config.get('hsv_h', 0.015),
            'hsv_s': aug_config.get('hsv_s', 0.7),
            'hsv_v': aug_config.get('hsv_v', 0.4),
            'degrees': aug_config.get('degrees', 10.0),
            'translate': aug_config.get('translate', 0.1),
            'scale': aug_config.get('scale', 0.5),
            'shear': aug_config.get('shear', 0.0),
            'perspective': aug_config.get('perspective', 0.0),
            'flipud': aug_config.get('flipud', 0.0),
            'fliplr': aug_config.get('fliplr', 0.5),
            'mosaic': aug_config.get('mosaic', 1.0),
            'mixup': aug_config.get('mixup', 0.0),
        })
    
    # Resume training if specified
    if args.resume:
        print(f"\nResuming training from {args.resume}")
        train_args['resume'] = args.resume
    
    print("\nStarting training...")
    print("=" * 60)
    
    try:
        # Train the model
        results = model.train(**train_args)
        
        print("\n" + "=" * 60)
        print("Training Completed Successfully!")
        print("=" * 60)
        
        # Print training metrics
        print(f"\nFinal Metrics:")
        print(f"  Best fitness: {results.results_dict.get('fitness', 'N/A')}")
        print(f"  Best mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
        print(f"  Best mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
        
        # Get best model path
        best_model_path = Path(save_dir) / f'blindstick_*' / 'weights' / 'best.pt'
        best_models = list(Path(save_dir).glob('**/weights/best.pt'))
        
        if best_models:
            print(f"\nBest model saved to: {best_models[-1]}")
        
        # Export model
        print("\nExporting model to ONNX format...")
        try:
            export_path = model.export(format='onnx')
            print(f"Model exported to: {export_path}")
        except Exception as e:
            print(f"Could not export model: {e}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
