import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.yolo3 import preprocess_input
import os

class ObjectDetector:
    def __init__(self, model_path=None):
        self.model = None
        self.classes = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 
                       'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 
                       'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 
                       'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 
                       'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 
                       'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 
                       'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 
                       'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 
                       'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 
                       'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 
                       'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 
                       'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 
                       'scissors', 'teddy bear', 'hair drier', 'toothbrush']
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """Load the YOLO model from the specified path."""
        try:
            self.model = load_model(model_path, compile=False)
            print(f"Model loaded successfully from {model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def detect_objects(self, frame, confidence_threshold=0.5):
        """Detect objects in the given frame."""
        if self.model is None:
            print("Model not loaded. Please load a model first.")
            return []
        
        # Preprocess the frame
        image_data = self.preprocess_image(frame)
        
        # Make prediction
        predictions = self.model.predict(image_data)
        
        # Process predictions
        detected_objects = self.process_predictions(predictions, confidence_threshold)
        
        return detected_objects
    
    def preprocess_image(self, frame, target_size=(416, 416)):
        """Preprocess the image for YOLO model."""
        # Resize and normalize the image
        image_data = cv2.resize(frame, target_size)
        image_data = image_data / 255.0
        image_data = np.expand_dims(image_data, axis=0)
        return image_data
    
    def process_predictions(self, predictions, confidence_threshold):
        """Process YOLO predictions and return detected objects."""
        boxes = []
        scores = []
        classes = []
        
        # Process each prediction
        for i, pred in enumerate(predictions[0]):
            # Get class probabilities
            class_scores = pred[5:]
            class_id = np.argmax(class_scores)
            confidence = class_scores[class_id]
            
            if confidence > confidence_threshold:
                # Get bounding box coordinates
                center_x = int(pred[0] * predictions[1])
                center_y = int(pred[1] * predictions[2])
                width = int(pred[2] * predictions[1])
                height = int(pred[3] * predictions[2])
                
                # Calculate top-left corner
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)
                
                boxes.append([x, y, width, height])
                scores.append(float(confidence))
                classes.append(class_id)
        
        # Apply non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, scores, confidence_threshold, 0.4)
        
        # Prepare results
        detected_objects = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                detected_objects.append({
                    'class_id': int(classes[i]),
                    'class_name': self.classes[classes[i]],
                    'confidence': scores[i],
                    'bounding_box': (x, y, w, h)
                })
        
        return detected_objects
    
    def draw_detections(self, frame, detected_objects):
        """Draw bounding boxes and labels on the frame."""
        for obj in detected_objects:
            x, y, w, h = obj['bounding_box']
            class_name = obj['class_name']
            confidence = obj['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label background
            label = f"{class_name}: {confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x, y - 20), (x + label_w, y), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(frame, label, (x, y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return frame
