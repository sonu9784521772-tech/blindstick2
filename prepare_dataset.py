"""
Dataset Preparation Script for ORBIT Dataset

This script helps prepare and organize the ORBIT dataset for training
with the BlindStick object detection system.

Usage:
    python prepare_dataset.py --source /path/to/orbit --output data/orbit
"""

import argparse
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import random


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Prepare ORBIT dataset for training'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Path to source ORBIT dataset'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/orbit',
        help='Output directory for prepared dataset'
    )
    
    parser.add_argument(
        '--train-split',
        type=float,
        default=0.8,
        help='Training set proportion (default: 0.8)'
    )
    
    parser.add_argument(
        '--val-split',
        type=float,
        default=0.1,
        help='Validation set proportion (default: 0.1)'
    )
    
    parser.add_argument(
        '--test-split',
        type=float,
        default=0.1,
        help='Test set proportion (default: 0.1)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['coco', 'yolo'],
        default='coco',
        help='Output format (coco or yolo)'
    )
    
    return parser.parse_args()


def create_directory_structure(output_dir: str) -> None:
    """Create directory structure for the dataset."""
    output_path = Path(output_dir)
    
    # Create COCO format directories
    (output_path / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_path / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (output_path / 'images' / 'test').mkdir(parents=True, exist_ok=True)
    (output_path / 'annotations').mkdir(parents=True, exist_ok=True)
    
    # Create YOLO format directories
    (output_path / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (output_path / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    print(f"Created directory structure at: {output_dir}")


def collect_images(source_dir: str) -> List[Path]:
    """Collect all images from source directory."""
    source_path = Path(source_dir)
    
    # Common image extensions
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    
    images = []
    for ext in extensions:
        images.extend(source_path.rglob(ext))
    
    print(f"Found {len(images)} images")
    return images


def split_dataset(
    images: List[Path],
    train_split: float,
    val_split: float,
    test_split: float
) -> Tuple[List[Path], List[Path], List[Path]]:
    """Split dataset into train, val, and test sets."""
    # Normalize splits
    total = train_split + val_split + test_split
    train_split /= total
    val_split /= total
    test_split /= total
    
    # Shuffle images
    random.seed(42)
    shuffled = images.copy()
    random.shuffle(shuffled)
    
    # Calculate split indices
    n = len(shuffled)
    train_end = int(n * train_split)
    val_end = int(n * (train_split + val_split))
    
    train_images = shuffled[:train_end]
    val_images = shuffled[train_end:val_end]
    test_images = shuffled[val_end:]
    
    print(f"Dataset split:")
    print(f"  Train: {len(train_images)} images ({train_split:.1%})")
    print(f"  Val:   {len(val_images)} images ({val_split:.1%})")
    print(f"  Test:  {len(test_images)} images ({test_split:.1%})")
    
    return train_images, val_images, test_images


def create_coco_annotation(
    images: List[Path],
    output_path: str,
    categories: Dict[str, int]
) -> Dict:
    """
    Create COCO-format annotation file.
    
    Args:
        images: List of image paths
        output_path: Path to save annotation JSON
        categories: Category name to ID mapping
        
    Returns:
        dict: COCO annotation dictionary
    """
    annotation = {
        'info': {
            'description': 'ORBIT Dataset for BlindStick',
            'version': '1.0',
            'year': 2026
        },
        'licenses': [],
        'categories': [
            {'id': idx, 'name': name, 'supercategory': 'object'}
            for name, idx in categories.items()
        ],
        'images': [],
        'annotations': []
    }
    
    # Add image info
    for img_id, img_path in enumerate(images):
        image_info = {
            'id': img_id,
            'file_name': img_path.name,
            'width': 640,  # Placeholder - should be updated with actual dimensions
            'height': 480,
            'date_captured': '',
            'license': 0,
            'coco_url': '',
            'flickr_url': ''
        }
        annotation['images'].append(image_info)
    
    # Note: You'll need to add actual bounding box annotations here
    # This depends on the format of your source ORBIT dataset
    
    return annotation


def copy_images(
    images: List[Path],
    output_dir: str,
    split: str
) -> None:
    """Copy images to output directory."""
    output_path = Path(output_dir) / 'images' / split
    
    for img_path in images:
        dest = output_path / img_path.name
        try:
            shutil.copy2(img_path, dest)
        except Exception as e:
            print(f"Error copying {img_path}: {e}")


def prepare_yolo_format(
    images: List[Path],
    output_dir: str,
    split: str,
    categories: Dict[str, int]
) -> None:
    """Prepare YOLO format labels."""
    # This function would create YOLO format label files
    # Each image gets a corresponding .txt file with bounding boxes
    pass


def generate_sample_annotations(
    images: List[Path],
    output_dir: str,
    split: str,
    categories: Dict[str, int]
) -> None:
    """
    Generate sample annotations for testing.
    
    Note: This is a placeholder. You should use actual annotations
    from the ORBIT dataset.
    """
    print(f"Generating annotations for {split} set...")
    
    # In a real scenario, you would:
    # 1. Load existing annotations from ORBIT dataset
    # 2. Map them to your category system
    # 3. Convert to COCO or YOLO format
    
    print(f"Note: Please add actual annotations for the {split} set")


def main():
    """Main preparation function."""
    args = parse_args()
    
    print("=" * 60)
    print("ORBIT Dataset Preparation")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Source: {args.source}")
    print(f"  Output: {args.output}")
    print(f"  Format: {args.format}")
    print(f"  Splits: Train={args.train_split}, Val={args.val_split}, Test={args.test_split}")
    print("=" * 60)
    
    # Check source directory
    if not os.path.exists(args.source):
        print(f"\nError: Source directory not found: {args.source}")
        return
    
    # Create output directory structure
    create_directory_structure(args.output)
    
    # Collect images
    print("\nCollecting images...")
    images = collect_images(args.source)
    
    if len(images) == 0:
        print("\nNo images found! Please check the source directory.")
        return
    
    # Split dataset
    print("\nSplitting dataset...")
    train_images, val_images, test_images = split_dataset(
        images,
        args.train_split,
        args.val_split,
        args.test_split
    )
    
    # Copy images
    print("\nCopying images...")
    copy_images(train_images, args.output, 'train')
    copy_images(val_images, args.output, 'val')
    copy_images(test_images, args.output, 'test')
    
    # Define categories (customize based on ORBIT dataset)
    categories = {
        'person': 1,
        'bicycle': 2,
        'car': 3,
        'motorcycle': 4,
        'bus': 5,
        'truck': 6,
        'chair': 7,
        'table': 8,
        'door': 9,
        'stairs': 10,
        'obstacle': 11,
        'wall': 12,
        'furniture': 13,
        'bag': 14,
        'umbrella': 15
    }
    
    # Create annotations
    print("\nCreating annotations...")
    
    if args.format == 'coco':
        # Create COCO annotations
        for split, images_list in [
            ('train', train_images),
            ('val', val_images),
            ('test', test_images)
        ]:
            annotation = create_coco_annotation(images_list, args.output, categories)
            
            annotation_path = Path(args.output) / 'annotations' / f'{split}.json'
            with open(annotation_path, 'w') as f:
                json.dump(annotation, f, indent=2)
            
            print(f"Created COCO annotation: {annotation_path}")
    
    elif args.format == 'yolo':
        # Create YOLO format labels
        for split, images_list in [
            ('train', train_images),
            ('val', val_images)
        ]:
            prepare_yolo_format(images_list, args.output, split, categories)
    
    # Create dataset.yaml for YOLO training
    dataset_yaml = Path(args.output) / 'dataset.yaml'
    yaml_content = f"""# ORBIT Dataset Configuration
path: {os.path.abspath(args.output)}
train: images/train
val: images/val
test: images/test

# Number of classes
nc: {len(categories)}

# Class names
names:
"""
    
    for name, idx in sorted(categories.items(), key=lambda x: x[1]):
        yaml_content += f"  {idx-1}: {name}\n"
    
    with open(dataset_yaml, 'w') as f:
        f.write(yaml_content)
    
    print(f"\nCreated dataset configuration: {dataset_yaml}")
    
    print("\n" + "=" * 60)
    print("Dataset Preparation Complete!")
    print("=" * 60)
    print(f"\nOutput directory: {args.output}")
    print(f"\nNext steps:")
    print("1. Add actual bounding box annotations to the dataset")
    print("2. Verify the dataset structure")
    print("3. Run training: python train.py --data {args.output}")
    
    print("\nDirectory structure:")
    print(f"{args.output}/")
    print("├── images/")
    print("│   ├── train/     ({0} images)".format(len(train_images)))
    print("│   ├── val/       ({0} images)".format(len(val_images)))
    print("│   └── test/      ({0} images)".format(len(test_images)))
    print("├── annotations/   (COCO format)")
    print("├── labels/        (YOLO format)")
    print("└── dataset.yaml")


if __name__ == '__main__':
    main()
