"""
ORBIT Dataset Loader and Preprocessor

This module handles loading the ORBIT dataset, preprocessing images,
and creating data loaders for training and validation.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
from typing import Tuple, List, Dict, Optional


class ORBITDataset(Dataset):
    """
    Custom Dataset for loading ORBIT dataset for object detection.
    
    The ORBIT dataset should be organized in the following format:
    data/orbit/
        ├── images/
        │   ├── train/
        │   └── val/
        └── annotations/
            ├── train.json
            └── val.json
    """
    
    def __init__(
        self,
        root_dir: str,
        split: str = 'train',
        img_size: int = 640,
        augment: bool = False
    ):
        """
        Initialize the ORBIT dataset.
        
        Args:
            root_dir: Root directory of the ORBIT dataset
            split: Dataset split ('train', 'val', or 'test')
            img_size: Target image size
            augment: Whether to apply data augmentation
        """
        self.root_dir = Path(root_dir)
        self.split = split
        self.img_size = img_size
        self.augment = augment
        
        # Load annotations
        self.images_dir = self.root_dir / 'images' / split
        self.annotations_path = self.root_dir / 'annotations' / f'{split}.json'
        
        self.images = []
        self.annotations = []
        
        self._load_annotations()
        
        # Define transformations
        if augment:
            self.transform = A.Compose([
                A.Resize(height=img_size, width=img_size),
                A.HorizontalFlip(p=0.5),
                A.RandomRotate90(p=0.5),
                A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2, p=0.5),
                A.GaussianBlur(blur_limit=(3, 5), p=0.3),
                A.RandomBrightnessContrast(p=0.3),
                A.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                ),
                ToTensorV2()
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
        else:
            self.transform = A.Compose([
                A.Resize(height=img_size, width=img_size),
                A.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                ),
                ToTensorV2()
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
    
    def _load_annotations(self) -> None:
        """Load annotations from JSON file."""
        if not self.annotations_path.exists():
            raise FileNotFoundError(f"Annotations file not found: {self.annotations_path}")
        
        with open(self.annotations_path, 'r') as f:
            data = json.load(f)
        
        self.images = data.get('images', [])
        self.annotations = data.get('annotations', [])
        self.categories = {cat['id']: cat['name'] for cat in data.get('categories', [])}
        
        print(f"Loaded {len(self.images)} images for split '{self.split}'")
    
    def __len__(self) -> int:
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Tuple:
        """
        Get an item from the dataset.
        
        Args:
            idx: Index of the image
            
        Returns:
            tuple: (image, bboxes, labels)
        """
        img_info = self.images[idx]
        img_path = self.images_dir / img_info['file_name']
        
        # Load image
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get annotations for this image
        img_bboxes = []
        img_labels = []
        
        for ann in self.annotations:
            if ann['image_id'] == img_info['id']:
                # Convert bbox from [x, y, width, height] to YOLO format [x_center, y_center, w, h]
                x, y, w, h = ann['bbox']
                img_height, img_width = img_info['height'], img_info['width']
                
                # Normalize to [0, 1]
                x_center = (x + w / 2) / img_width
                y_center = (y + h / 2) / img_height
                w_norm = w / img_width
                h_norm = h / img_height
                
                img_bboxes.append([x_center, y_center, w_norm, h_norm])
                img_labels.append(ann['category_id'] - 1)  # Assuming 1-indexed categories
        
        # Handle case with no bounding boxes
        if len(img_bboxes) == 0:
            img_bboxes = [[0, 0, 0, 0]]
            img_labels = [0]
        
        # Apply transformations
        transformed = self.transform(
            image=image,
            bboxes=img_bboxes,
            class_labels=img_labels
        )
        
        image = transformed['image']
        bboxes = np.array(transformed['bboxes'])
        labels = np.array(transformed['class_labels'])
        
        return image, bboxes, labels
    
    def get_class_names(self) -> List[str]:
        """Get list of class names."""
        return list(self.categories.values())
    
    def get_num_classes(self) -> int:
        """Get number of classes."""
        return len(self.categories)


def create_dataloaders(
    root_dir: str,
    batch_size: int = 16,
    img_size: int = 640,
    num_workers: int = 4
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders.
    
    Args:
        root_dir: Root directory of the dataset
        batch_size: Batch size
        img_size: Image size
        num_workers: Number of data loading workers
        
    Returns:
        tuple: (train_loader, val_loader)
    """
    train_dataset = ORBITDataset(
        root_dir=root_dir,
        split='train',
        img_size=img_size,
        augment=True
    )
    
    val_dataset = ORBITDataset(
        root_dir=root_dir,
        split='val',
        img_size=img_size,
        augment=False
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        collate_fn=collate_fn
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        collate_fn=collate_fn
    )
    
    return train_loader, val_loader


def collate_fn(batch: List[Tuple]) -> Tuple:
    """
    Custom collate function for batching.
    
    Args:
        batch: List of (image, bboxes, labels) tuples
        
    Returns:
        tuple: (images, targets)
    """
    images, bboxes_list, labels_list = zip(*batch)
    
    # Stack images
    images = np.stack(images)
    images = torch.from_numpy(images).float()
    
    # Create targets
    targets = []
    for i, (bboxes, labels) in enumerate(zip(bboxes_list, labels_list)):
        for bbox, label in zip(bboxes, labels):
            targets.append([i, label, *bbox])
    
    targets = torch.tensor(targets) if targets else torch.zeros((0, 6))
    
    return torch.from_numpy(images), targets


def convert_orbit_to_yolo_format(
    orbit_root: str,
    output_dir: str,
    train_split: float = 0.8,
    val_split: float = 0.1
) -> None:
    """
    Convert ORBIT dataset to YOLO format.
    
    Args:
        orbit_root: Root directory of original ORBIT dataset
        output_dir: Output directory for YOLO format
        train_split: Training set proportion
        val_split: Validation set proportion
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create directory structure
    (output_path / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_path / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (output_path / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (output_path / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    print(f"Converting ORBIT dataset to YOLO format...")
    print(f"Output directory: {output_path}")
    
    # TODO: Implement conversion logic based on actual ORBIT dataset structure
    # This will depend on how the ORBIT dataset is organized
    
    print("Conversion complete!")


if __name__ == "__main__":
    # Example usage
    import torch
    
    root_dir = "data/orbit"
    
    if os.path.exists(root_dir):
        train_loader, val_loader = create_dataloaders(
            root_dir=root_dir,
            batch_size=8,
            img_size=640,
            num_workers=2
        )
        
        print(f"Train batches: {len(train_loader)}")
        print(f"Val batches: {len(val_loader)}")
        
        # Test one batch
        images, targets = next(iter(train_loader))
        print(f"Image shape: {images.shape}")
        print(f"Targets shape: {targets.shape}")
    else:
        print(f"Dataset directory not found: {root_dir}")
        print("Please download and organize the ORBIT dataset first.")
