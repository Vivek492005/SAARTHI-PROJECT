import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox, 
                            QStackedWidget, QListWidget, QLineEdit, QMessageBox,
                            QDialog, QFormLayout, QCheckBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon, QFont

from config import config

class GestureTrainingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Train New Gesture")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form layout for gesture details
        form_layout = QFormLayout()
        
        self.gesture_name = QLineEdit()
        self.gesture_phrase = QLineEdit()
        self.language_combo = QComboBox()
        
        # Add available languages
        languages = config.get_setting('languages', {'en': 'English'})
        for code, name in languages.items():
            self.language_combo.addItem(name, code)
        
        form_layout.addRow("Gesture Name:", self.gesture_name)
        form_layout.addRow("Phrase/Command:", self.gesture_phrase)
        form_layout.addRow("Language:", self.language_combo)
        
        # Training instructions
        instructions = QLabel("Show the gesture to the camera and click 'Capture' when ready.")
        instructions.setWordWrap(True)
        
        # Video feed for training
        self.video_label = QLabel()
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: #2D2D2D; border-radius: 5px;")
        
        # Buttons
        button_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Gesture")
        self.capture_btn.clicked.connect(self.capture_gesture)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.capture_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Add widgets to main layout
        layout.addLayout(form_layout)
        layout.addWidget(instructions)
        layout.addWidget(self.video_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        
        # Store the captured gesture data
        self.captured_data = None
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get image dimensions
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            # Create QImage from the frame
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scale the image to fit the label while maintaining aspect ratio
            self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.video_label.width(), 
                self.video_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
    
    def capture_gesture(self):
        name = self.gesture_name.text().strip()
        phrase = self.gesture_phrase.text().strip()
        
        if not name or not phrase:
            QMessageBox.warning(self, "Error", "Please enter both a gesture name and phrase.")
            return
        
        # Capture the current frame for training
        ret, frame = self.cap.read()
        if ret:
            # Store the captured frame and gesture data
            self.captured_data = {
                'name': name,
                'phrase': phrase,
                'language': self.language_combo.currentData(),
                'image': frame
            }
            self.accept()
    
    def closeEvent(self, event):
        # Release the camera when the dialog is closed
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        event.accept()

class SmartHomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Home Integration")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Enable/Disable smart home
        self.enable_check = QCheckBox("Enable Smart Home Integration")
        self.enable_check.setChecked(config.get_setting('smart_home.enabled', False))
        self.enable_check.toggled.connect(self.toggle_smart_home)
        
        # Device list
        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(200)
        
        # Device controls
        device_group = QGroupBox("Connected Devices")
        device_layout = QVBoxLayout()
        
        # Add/Edit/Remove buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Device")
        self.edit_btn = QPushButton("Edit")
        self.remove_btn = QPushButton("Remove")
        
        self.add_btn.clicked.connect(self.add_device)
        self.edit_btn.clicked.connect(self.edit_device)
        self.remove_btn.clicked.connect(self.remove_device)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        
        device_layout.addLayout(btn_layout)
        device_layout.addWidget(self.device_list)
        device_group.setLayout(device_layout)
        
        # MQTT Settings
        mqtt_group = QGroupBox("MQTT Settings")
        mqtt_layout = QFormLayout()
        
        self.mqtt_host = QLineEdit(config.get_setting('smart_home.mqtt_host', ''))
        self.mqtt_port = QSpinBox()
        self.mqtt_port.setRange(1, 65535)
        self.mqtt_port.setValue(int(config.get_setting('smart_home.mqtt_port', 1883)))
        self.mqtt_username = QLineEdit(config.get_setting('smart_home.mqtt_username', ''))
        self.mqtt_password = QLineEdit(config.get_setting('smart_home.mqtt_password', ''))
        self.mqtt_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        mqtt_layout.addRow("Broker Host:", self.mqtt_host)
        mqtt_layout.addRow("Port:", self.mqtt_port)
        mqtt_layout.addRow("Username:", self.mqtt_username)
        mqtt_layout.addRow("Password:", self.mqtt_password)
        mqtt_group.setLayout(mqtt_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_box.addWidget(self.save_btn)
        button_box.addWidget(self.cancel_btn)
        
        # Add widgets to main layout
        layout.addWidget(self.enable_check)
        layout.addWidget(device_group)
        layout.addWidget(mqtt_group)
        layout.addLayout(button_box)
        
        self.setLayout(layout)
        
        # Load devices
        self.load_devices()
    
    def toggle_smart_home(self, enabled):
        self.device_list.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)
        self.edit_btn.setEnabled(enabled)
        self.remove_btn.setEnabled(enabled)
    
    def load_devices(self):
        self.device_list.clear()
        devices = config.get_setting('smart_home.devices', {})
        for device_id, device_info in devices.items():
            self.device_list.addItem(f"{device_info.get('name', 'Unknown')} ({device_id})")
    
    def add_device(self):
        # TODO: Implement device addition dialog
        pass
    
    def edit_device(self):
        # TODO: Implement device editing
        pass
    
    def remove_device(self):
        # TODO: Implement device removal
        pass
    
    def save_settings(self):
        # Save MQTT settings
        config.set_setting('smart_home.enabled', self.enable_check.isChecked())
        config.set_setting('smart_home.mqtt_host', self.mqtt_host.text())
        config.set_setting('smart_home.mqtt_port', self.mqtt_port.value())
        config.set_setting('smart_home.mqtt_username', self.mqtt_username.text())
        config.set_setting('smart_home.mqtt_password', self.mqtt_password.text())
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        self.accept()

class GestureAssistantUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Gesture Assistant")
        self.setMinimumSize(1000, 700)
        
        # Initialize UI
        self.init_ui()
        
        # Initialize gesture assistant
        self.gesture_assistant = None
        self.init_gesture_assistant()
        
        # Start video feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
    
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel - Video feed
        left_panel = QVBoxLayout()
        
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
                margin-top: 10px;
            }
        """)
        
        left_panel.addWidget(self.video_label)
        left_panel.addWidget(self.gesture_label)
        
        # Right panel - Controls
        right_panel = QVBoxLayout()
        
        # Language selection
        language_group = QGroupBox("Language Settings")
        language_layout = QVBoxLayout()
        
        self.language_combo = QComboBox()
        languages = config.get_setting('languages', {'en': 'English'})
        for code, name in languages.items():
            self.language_combo.addItem(name, code)
        
        # Set current language
        current_lang = config.get_setting('language', 'en')
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        language_layout.addWidget(QLabel("Select Language:"))
        language_layout.addWidget(self.language_combo)
        language_group.setLayout(language_layout)
        
        # Gesture management
        gesture_group = QGroupBox("Gesture Management")
        gesture_layout = QVBoxLayout()
        
        self.gesture_list = QListWidget()
        self.gesture_list.setMinimumHeight(200)
        self.load_gestures()
        
        btn_layout = QHBoxLayout()
        self.train_btn = QPushButton("Train New Gesture")
        self.edit_btn = QPushButton("Edit")
        self.remove_btn = QPushButton("Remove")
        
        self.train_btn.clicked.connect(self.train_gesture)
        self.edit_btn.clicked.connect(self.edit_gesture)
        self.remove_btn.clicked.connect(self.remove_gesture)
        
        btn_layout.addWidget(self.train_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        
        gesture_layout.addWidget(self.gesture_list)
        gesture_layout.addLayout(btn_layout)
        gesture_group.setLayout(gesture_layout)
        
        # Smart home integration
        smart_home_btn = QPushButton("Smart Home Integration")
        smart_home_btn.clicked.connect(self.open_smart_home_settings)
        
        # Add widgets to right panel
        right_panel.addWidget(language_group)
        right_panel.addWidget(gesture_group)
        right_panel.addWidget(smart_home_btn)
        right_panel.addStretch()
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #4A4A4A;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QListWidget {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                color: #FFFFFF;
            }
            QComboBox {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 3px;
            }
            QLineEdit {
                background-color: #2D2D2D;
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 5px;
            }
        """)
    
    def init_gesture_assistant(self):
        # Initialize the gesture recognition system
        from gesture_assistant import GestureAssistant
        self.gesture_assistant = GestureAssistant()
        
        # Start the gesture recognition in a separate thread
        # (This would be implemented in the gesture_assistant.py)
    
    def update_frame(self):
        if hasattr(self, 'gesture_assistant') and self.gesture_assistant:
            # Get the current frame from the gesture assistant
            frame = self.gesture_assistant.get_current_frame()
            
            if frame is not None:
                # Convert the frame to QImage
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Scale the image to fit the label while maintaining aspect ratio
                self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                    self.video_label.width(), 
                    self.video_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                
                # Update gesture label
                current_gesture = self.gesture_assistant.get_current_gesture()
                if current_gesture:
                    self.gesture_label.setText(f"Detected: {current_gesture}")
                else:
                    self.gesture_label.setText("No gesture detected")
    
    def load_gestures(self):
        self.gesture_list.clear()
        gestures = config.get_setting('gestures', {})
        for gesture_name, phrase in gestures.items():
            self.gesture_list.addItem(f"{gesture_name}: {phrase}")
    
    def train_gesture(self):
        dialog = GestureTrainingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.captured_data:
            # Save the new gesture
            gesture_data = dialog.captured_data
            config.add_custom_gesture(gesture_data['name'], gesture_data['phrase'])
            
            # Update the gesture list
            self.load_gestures()
            
            # TODO: Train the model with the new gesture
            
            QMessageBox.information(self, "Success", "New gesture trained successfully!")
    
    def edit_gesture(self):
        # TODO: Implement gesture editing
        pass
    
    def remove_gesture(self):
        selected_items = self.gesture_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a gesture to remove.")
            return
        
        # Get the gesture name from the selected item
        gesture_text = selected_items[0].text()
        gesture_name = gesture_text.split(':')[0].strip()
        
        # Confirm removal
        reply = QMessageBox.question(
            self, 'Confirm Removal',
            f'Are you sure you want to remove the gesture "{gesture_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove the gesture from config
            if config.remove_custom_gesture(gesture_name):
                self.load_gestures()
                QMessageBox.information(self, "Success", "Gesture removed successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to remove gesture.")
    
    def change_language(self):
        # Update the application language
        language_code = self.language_combo.currentData()
        config.set_setting('language', language_code)
        
        # Update the UI based on the new language
        self.update_ui_for_language(language_code)
    
    def update_ui_for_language(self, language_code):
        # Update all text in the UI based on the selected language
        # This would involve translating all UI elements
        # For now, we'll just update the window title as an example
        language_name = self.language_combo.currentText()
        self.setWindowTitle(f"AI Gesture Assistant - {language_name}")
    
    def open_smart_home_settings(self):
        dialog = SmartHomeDialog(self)
        dialog.exec()
    
    def closeEvent(self, event):
        # Clean up resources
        if hasattr(self, 'gesture_assistant') and self.gesture_assistant:
            self.gesture_assistant.cleanup()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = GestureAssistantUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
