"""
Object Detection Model for BlindStick

This module implements YOLO-based object detection models optimized
for the BlindStick assistive device.
"""

import torch
import torch.nn as nn
from ultralytics import YOLO
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import cv2


class BlindStickDetector:
    """
    Object detection model wrapper for BlindStick using YOLO.
    
    Provides methods for loading models, training, and inference
    with optimizations for assistive navigation.
    """
    
    def __init__(
        self,
        model_type: str = 'yolov8n.pt',
        num_classes: int = 80,
        device: Optional[str] = None,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45
    ):
        """
        Initialize the object detection model.
        
        Args:
            model_type: YOLO model type (yolov8n, yolov8s, yolov8m, etc.)
            num_classes: Number of object classes
            device: Device to run model on ('cuda', 'cpu', or None)
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        self.model_type = model_type
        self.num_classes = num_classes
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        # Set device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"Using device: {self.device}")
        
        # Load model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load YOLO model."""
        try:
            # Check if model_path is a custom trained model or pretrained
            if self.model_type.endswith('.pt'):
                self.model = YOLO(self.model_type)
            else:
                # Load from ultralytics pretrained models
                self.model = YOLO(f'{self.model_type}.pt')
            
            # Move model to device
            self.model.to(self.device)
            
            print(f"Successfully loaded {self.model_type}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def train(
        self,
        data: str,
        epochs: int = 100,
        batch_size: int = 16,
        imgsz: int = 640,
        save_dir: str = 'runs/train',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train the object detection model.
        
        Args:
            data: Path to dataset YAML file
            epochs: Number of training epochs
            batch_size: Training batch size
            imgsz: Image size
            save_dir: Directory to save training results
            **kwargs: Additional training arguments
            
        Returns:
            dict: Training results
        """
        print(f"Starting training on {data}")
        print(f"Epochs: {epochs}, Batch Size: {batch_size}, Image Size: {imgsz}")
        
        # Training arguments
        train_args = {
            'data': data,
            'epochs': epochs,
            'batch': batch_size,
            'imgsz': imgsz,
            'device': self.device.split(':')[0] if ':' in self.device else self.device,
            'project': save_dir,
            'name': 'blindstick_detector',
            'exist_ok': True,
            'verbose': True,
            **kwargs
        }
        
        # Start training
        results = self.model.train(**train_args)
        
        print("Training completed!")
        return results
    
    def detect(
        self,
        source: Any,
        conf: Optional[float] = None,
        iou: Optional[float] = None,
        max_det: int = 100,
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform object detection on an image or video frame.
        
        Args:
            source: Image/frame source (path, numpy array, or PIL image)
            conf: Confidence threshold (overrides default if provided)
            iou: IoU threshold (overrides default if provided)
            max_det: Maximum number of detections
            verbose: Whether to print verbose output
            
        Returns:
            list: List of detection dictionaries with keys:
                  - bbox: [x1, y1, x2, y2]
                  - confidence: detection confidence
                  - class: class index
                  - name: class name
                  - center: (cx, cy) center coordinates
                  - distance: estimated distance (if available)
        """
        conf = conf or self.conf_threshold
        iou = iou or self.iou_threshold
        
        # Run inference
        results = self.model.predict(
            source=source,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=verbose,
            device=self.device
        )
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for i in range(len(boxes)):
                box = boxes[i]
                
                # Extract bounding box
                xyxy = box.xyxy[0].cpu().numpy()
                conf_score = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = result.names[cls_id]
                
                # Calculate center
                x1, y1, x2, y2 = xyxy
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                
                # Estimate distance (simplified - based on object size)
                # This can be improved with depth sensors or stereo vision
                estimated_distance = self._estimate_distance(xyxy, cls_name)
                
                detection = {
                    'bbox': xyxy.tolist(),
                    'confidence': conf_score,
                    'class': cls_id,
                    'name': cls_name,
                    'center': (float(cx), float(cy)),
                    'distance': estimated_distance
                }
                
                detections.append(detection)
        
        return detections
    
    def _estimate_distance(
        self,
        bbox: np.ndarray,
        class_name: str
    ) -> float:
        """
        Estimate distance to object based on bounding box size.
        
        This is a simplified estimation. For accurate distance measurement,
        consider using depth sensors, stereo cameras, or LiDAR.
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            class_name: Object class name
            
        Returns:
            float: Estimated distance in meters
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Average object dimensions (in pixels at reference distance)
        # These values should be calibrated for your specific camera
        reference_dimensions = {
            'person': 180,  # cm
            'car': 450,     # cm
            'chair': 90,    # cm
            'table': 120,   # cm
            'door': 200,    # cm
        }
        
        ref_height = reference_dimensions.get(class_name, 100)
        
        # Simple pinhole camera model approximation
        # distance ≈ (actual_height * focal_length) / pixel_height
        # Assuming focal length ≈ image_height for simplicity
        if height > 0:
            distance = (ref_height * 640) / (height * 100)  # Simplified formula
            return round(distance, 2)
        
        return 0.0
    
    def detect_and_annotate(
        self,
        image: np.ndarray,
        detections: Optional[List[Dict]] = None,
        show_labels: bool = True,
        show_confidence: bool = True,
        show_distance: bool = True
    ) -> np.ndarray:
        """
        Annotate an image with detection results.
        
        Args:
            image: Input image (BGR format for OpenCV)
            detections: Detections from detect() method
            show_labels: Whether to show class labels
            show_confidence: Whether to show confidence scores
            show_distance: Whether to show estimated distances
            
        Returns:
            np.ndarray: Annotated image
        """
        if detections is None:
            detections = self.detect(image)
        
        annotated = image.copy()
        
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw bounding box
            color = (0, 255, 0)  # Green in BGR
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Create label
            label_parts = []
            if show_labels:
                label_parts.append(det['name'])
            if show_confidence:
                label_parts.append(f"{det['confidence']:.2f}")
            if show_distance and det['distance'] > 0:
                label_parts.append(f"{det['distance']}m")
            
            label = " ".join(label_parts)
            
            # Draw label background
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - label_h - 10),
                (x1 + label_w, y1),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )
        
        return annotated
    
    def save_model(self, path: str) -> None:
        """
        Save the trained model.
        
        Args:
            path: Path to save the model
        """
        self.model.export(path)
        print(f"Model saved to {path}")
    
    def load_custom_weights(self, weights_path: str) -> None:
        """
        Load custom trained weights.
        
        Args:
            weights_path: Path to custom weights file
        """
        self.model = YOLO(weights_path)
        self.model.to(self.device)
        print(f"Loaded custom weights from {weights_path}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            dict: Model information
        """
        return {
            'model_type': self.model_type,
            'num_classes': self.num_classes,
            'device': self.device,
            'conf_threshold': self.conf_threshold,
            'iou_threshold': self.iou_threshold
        }


def create_model(
    config: Dict[str, Any]
) -> BlindStickDetector:
    """
    Factory function to create a BlindStickDetector from config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        BlindStickDetector instance
    """
    model_config = config.get('model', {})
    inference_config = config.get('inference', {})
    device_config = config.get('device', {})
    
    detector = BlindStickDetector(
        model_type=model_config.get('type', 'yolov8n'),
        num_classes=model_config.get('num_classes', 80),
        device=f"cuda:{device_config.get('gpu', 0)}" if torch.cuda.is_available() else 'cpu',
        conf_threshold=inference_config.get('conf_threshold', 0.5),
        iou_threshold=inference_config.get('iou_threshold', 0.45)
    )
    
    return detector


if __name__ == "__main__":
    # Example usage
    detector = BlindStickDetector(model_type='yolov8n.pt')
    
    print("\nModel Information:")
    info = detector.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test with sample image (if available)
    test_image_path = "test_image.jpg"
    if os.path.exists(test_image_path):
        image = cv2.imread(test_image_path)
        detections = detector.detect(image)
        
        print(f"\nDetected {len(detections)} objects:")
        for det in detections:
            print(f"  - {det['name']} ({det['confidence']:.2f}) at {det['distance']}m")
        
        # Annotate and save
        annotated = detector.detect_and_annotate(image, detections)
        cv2.imwrite("output.jpg", annotated)
        print("\nOutput saved to output.jpg")
