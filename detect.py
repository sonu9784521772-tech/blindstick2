"""
Real-time Inference Script for BlindStick

This script performs real-time object detection using a camera feed
and provides audio feedback through text-to-speech.

Usage:
    python detect.py --weights path/to/best.pt --config config.yaml
    
    Or with webcam:
    python detect.py --source 0 --weights path/to/best.pt
"""

import argparse
import os
import sys
import yaml
import time
from datetime import datetime
from typing import Dict, List, Optional
import cv2
import numpy as np
import torch


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Real-time object detection for BlindStick'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        default='0',
        help='Video source (camera index or video file path)'
    )
    
    parser.add_argument(
        '--weights',
        type=str,
        default='yolov8n.pt',
        help='Path to model weights'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--img-size',
        type=int,
        default=640,
        help='Image size for inference'
    )
    
    parser.add_argument(
        '--conf-thres',
        type=float,
        default=0.5,
        help='Confidence threshold'
    )
    
    parser.add_argument(
        '--iou-thres',
        type=float,
        default=0.45,
        help='IoU threshold for NMS'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        help='Device to run inference on (cuda/cpu)'
    )
    
    parser.add_argument(
        '--show-display',
        action='store_true',
        help='Show display window (for debugging)'
    )
    
    parser.add_argument(
        '--save-output',
        action='store_true',
        help='Save output video'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='runs/detect',
        help='Directory to save output'
    )
    
    parser.add_argument(
        '--announcement-interval',
        type=float,
        default=3.0,
        help='Minimum seconds between announcements'
    )
    
    parser.add_argument(
        '--max-detections',
        type=int,
        default=100,
        help='Maximum number of detections'
    )
    
    return parser.parse_args()


class BlindStickInference:
    """
    Real-time inference engine for BlindStick.
    
    Combines object detection with text-to-speech feedback
    for assistive navigation.
    """
    
    def __init__(
        self,
        weights_path: str,
        config_path: str = 'config.yaml',
        conf_thres: float = 0.5,
        iou_thres: float = 0.45,
        img_size: int = 640,
        device: Optional[str] = None,
        announcement_interval: float = 3.0
    ):
        """
        Initialize inference engine.
        
        Args:
            weights_path: Path to model weights
            config_path: Path to configuration file
            conf_thres: Confidence threshold
            iou_thres: IoU threshold
            img_size: Image size
            device: Device specification
            announcement_interval: Minimum seconds between announcements
        """
        self.weights_path = weights_path
        self.config_path = config_path
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.img_size = img_size
        self.announcement_interval = announcement_interval
        
        # Load configuration
        self.config = self._load_config()
        
        # Set device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        print(f"Using device: {self.device}")
        
        # Load model
        self._load_model()
        
        # Initialize TTS
        self._init_tts()
        
        # Tracking variables
        self.last_announcement_time = 0
        self.current_detections = []
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            print(f"Config file not found: {self.config_path}")
            print("Using default configuration")
            return {}
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _load_model(self):
        """Load YOLO model."""
        from ultralytics import YOLO
        
        print(f"Loading model from {self.weights_path}...")
        
        try:
            self.model = YOLO(self.weights_path)
            self.model.to(self.device)
            print(f"Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def _init_tts(self):
        """Initialize text-to-speech."""
        from tts import SpeechAnnouncer
        
        tts_config = self.config.get('tts', {})
        self.announcer = SpeechAnnouncer(tts_config)
        print("Text-to-speech initialized")
    
    def detect_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in a frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            list: List of detections
        """
        # Run inference
        results = self.model.predict(
            source=frame,
            conf=self.conf_thres,
            iou=self.iou_thres,
            max_det=100,
            verbose=False,
            device=self.device.split(':')[0] if ':' in self.device else self.device
        )
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for i in range(len(boxes)):
                box = boxes[i]
                
                # Extract information
                xyxy = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                name = result.names[cls]
                
                # Calculate center and distance
                x1, y1, x2, y2 = xyxy
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                
                # Estimate distance
                distance = self._estimate_distance(xyxy, name)
                
                detection = {
                    'bbox': xyxy.tolist(),
                    'confidence': conf,
                    'class': cls,
                    'name': name,
                    'center': (cx, cy),
                    'distance': distance
                }
                
                detections.append(detection)
        
        return detections
    
    def _estimate_distance(self, bbox: np.ndarray, class_name: str) -> float:
        """Estimate distance to object."""
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        
        # Reference heights (in cm)
        ref_heights = {
            'person': 170,
            'car': 150,
            'chair': 90,
            'table': 75,
            'door': 200,
        }
        
        ref_height = ref_heights.get(class_name, 100)
        
        if height > 0:
            # Simplified distance estimation
            distance = (ref_height * 640) / (height * 100)
            return round(distance, 2)
        
        return 0.0
    
    def process_detections(self, detections: List[Dict]):
        """
        Process detections and make announcements.
        
        Args:
            detections: List of detections
        """
        current_time = time.time()
        
        if not detections:
            return
        
        # Check if enough time has passed since last announcement
        if current_time - self.last_announcement_time < self.announcement_interval:
            return
        
        # Get priority objects from config
        priority_objects = self.config.get('priority_objects', [])
        
        # Announce objects
        self.announcer.announce_objects(
            detections=detections,
            priority_objects=priority_objects,
            max_objects=3,
            include_distance=True
        )
        
        # Update last announcement time
        self.last_announcement_time = current_time
        
        # Check for warnings
        self._check_warnings(detections)
    
    def _check_warnings(self, detections: List[Dict]):
        """Check for dangerous situations and warn."""
        for det in detections:
            name = det['name'].lower()
            distance = det.get('distance', 0)
            
            # Check for immediate obstacles
            if distance > 0 and distance < 2.0:
                if name in ['person', 'car', 'bicycle', 'obstacle']:
                    self.announcer.announce_warning(
                        warning_type=name,
                        details=f"at {distance} meters"
                    )
    
    def annotate_frame(
        self,
        frame: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Annotate frame with detections.
        
        Args:
            frame: Input frame
            detections: Detections to draw
            
        Returns:
            np.ndarray: Annotated frame
        """
        annotated = frame.copy()
        
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Create label
            label = f"{det['name']} {det['confidence']:.2f}"
            if det.get('distance', 0) > 0:
                label += f" {det['distance']}m"
            
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
        
        # Draw FPS
        cv2.putText(
            annotated,
            f"FPS: {self.fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Draw detection count
        cv2.putText(
            annotated,
            f"Objects: {len(detections)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        return annotated
    
    def run(self, source: str = '0', show_display: bool = False, save_output: bool = False):
        """
        Run real-time inference.
        
        Args:
            source: Video source
            show_display: Whether to show display window
            save_output: Whether to save output
        """
        # Parse source
        if source.isdigit():
            source = int(source)
            print(f"Opening camera {source}...")
        else:
            print(f"Opening video file: {source}")
        
        # Open video capture
        cap = cv2.VideoCapture(source if isinstance(source, int) else str(source))
        
        if not cap.isOpened():
            print(f"Error: Could not open video source")
            sys.exit(1)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video properties: {width}x{height} @ {fps} FPS")
        
        # Setup video writer if saving
        if save_output:
            output_dir = self.config.get('output_dir', 'runs/detect')
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'blindstick_{timestamp}.avi')
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            print(f"Saving output to: {output_path}")
        
        print("\nStarting real-time detection...")
        print("Press 'q' to quit, 's' to stop/speak current detections")
        
        running = True
        
        try:
            while running:
                ret, frame = cap.read()
                
                if not ret:
                    print("End of video stream")
                    break
                
                # Detect objects
                self.current_detections = self.detect_frame(frame)
                
                # Process and announce
                self.process_detections(self.current_detections)
                
                # Annotate frame
                annotated = self.annotate_frame(frame, self.current_detections)
                
                # Save frame if needed
                if save_output:
                    out.write(annotated)
                
                # Show display if requested
                if show_display:
                    cv2.imshow('BlindStick Detection', annotated)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        running = False
                    elif key == ord('s'):
                        # Manual announcement
                        if self.current_detections:
                            self.process_detections(self.current_detections)
                
                # Update FPS
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.fps = self.frame_count / (current_time - self.last_fps_time)
                    self.frame_count = 0
                    self.last_fps_time = current_time
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            # Cleanup
            cap.release()
            if save_output:
                out.release()
            if show_display:
                cv2.destroyAllWindows()
            
            # Shutdown announcer
            self.announcer.shutdown()
            
            print("\nInference stopped")
    
    def shutdown(self):
        """Shutdown the inference engine."""
        if hasattr(self, 'announcer'):
            self.announcer.shutdown()


def main():
    """Main function."""
    args = parse_args()
    
    print("=" * 60)
    print("BlindStick Real-time Object Detection")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Model Weights: {args.weights}")
    print(f"  Video Source: {args.source}")
    print(f"  Confidence Threshold: {args.conf_thres}")
    print(f"  IoU Threshold: {args.iou_thres}")
    print(f"  Image Size: {args.img_size}")
    print(f"  Announcement Interval: {args.announcement_interval}s")
    print("=" * 60)
    
    # Check if weights file exists
    if not os.path.exists(args.weights) and args.weights not in ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt']:
        print(f"\nWarning: Weights file not found: {args.weights}")
        print("Using pretrained YOLOv8 model instead")
        args.weights = 'yolov8n.pt'
    
    # Create inference engine
    engine = BlindStickInference(
        weights_path=args.weights,
        config_path=args.config,
        conf_thres=args.conf_thres,
        iou_thres=args.iou_thres,
        img_size=args.img_size,
        device=args.device,
        announcement_interval=args.announcement_interval
    )
    
    # Run inference
    try:
        engine.run(
            source=args.source,
            show_display=args.show_display,
            save_output=args.save_output
        )
    except Exception as e:
        print(f"\nError during inference: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.shutdown()


if __name__ == '__main__':
    main()
