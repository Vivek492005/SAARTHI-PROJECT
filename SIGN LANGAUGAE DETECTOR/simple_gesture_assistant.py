import cv2
import numpy as np
import pyttsx3
import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QLabel, QPushButton, QComboBox, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class SimpleGestureAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Gesture Assistant")
        self.setMinimumSize(800, 600)
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Gesture buffer
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 2.0
        
        # Initialize UI
        self.init_ui()
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
    
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        
        # Video feed
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D2D;
                border-radius: 10px;
                border: 2px solid #3E3E3E;
            }
        """)
        
        # Gesture info
        self.gesture_label = QLabel("No gesture detected")
        self.gesture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gesture_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: #2D2D2D;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
        """)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("हिंदी", "hi")
        self.language_combo.addItem("Español", "es")
        
        # Add widgets to layout
        layout.addWidget(self.video_label, 3)
        layout.addWidget(self.gesture_label, 1)
        layout.addWidget(QLabel("Select Language:"))
        layout.addWidget(self.language_combo)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #4A4A4A;
                border-radius: 4px;
                padding: 5px 10px;
                margin: 5px 0;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
        """)
    
    def detect_gesture(self, frame):
        """Simple gesture detection using contour analysis"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, frame
        
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Draw contour
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
        
        # Simple gesture recognition based on contour area and aspect ratio
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = float(w) / h
        area = cv2.contourArea(largest_contour)
        
        if area < 1000:  # Too small to be a hand
            return None, frame
            
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        # Simple gesture classification
        if aspect_ratio > 1.2:
            return "Open Hand", frame
        elif aspect_ratio < 0.8:
            return "Fist", frame
        else:
            return "Unknown", frame
    
    def say_text(self, text):
        """Convert text to speech"""
        try:
            print(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # Flip the frame horizontally for a selfie-view display
        frame = cv2.flip(frame, 1)
        
        # Detect gesture
        gesture, processed_frame = self.detect_gesture(frame)
        
        # Update UI
        if gesture and gesture != self.last_gesture:
            current_time = time.time()
            if current_time - self.last_gesture_time > self.gesture_cooldown:
                self.last_gesture = gesture
                self.last_gesture_time = current_time
                self.gesture_label.setText(f"Detected: {gesture}")
                self.say_text(gesture)
        
        # Convert the frame to QImage
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Display the frame
        self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
    
    def closeEvent(self, event):
        # Release resources
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = SimpleGestureAssistant()
    window.show()
    
    sys.exit(app.exec())
