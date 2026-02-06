import os
import sys
import cv2
import numpy as np
import pyautogui
import threading
import time
import queue
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from modules.eye_tracker import EyeTracker
from modules.object_detector import ObjectDetector
from modules.text_recognizer import TextRecognizer
from modules.cursor_controller import CursorController
from modules.voice_feedback import VoiceFeedback

class EyeAssistApp:
    def __init__(self, root):
        self.root = root
        self.setup_gui()
        self.running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.eye_tracker = EyeTracker()
        self.object_detector = ObjectDetector()
        self.text_recognizer = TextRecognizer()
        self.cursor_controller = CursorController()
        self.voice_feedback = VoiceFeedback()
        self.cap = None
        self.root.title("EyeAssist - Comprehensive Visual Assistance")
        self.root.geometry("1200x800")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            self.root.quit()
            return
            
        # Initialize modules
        # These are already initialized at the start of __init__
        pass
        
        # Create GUI
        self.setup_gui()
        
        # Start the main loop
        self.running = True
        self.process_frame()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video feed
        self.video_label = ttk.Label(main_frame)
        self.video_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Buttons
        ttk.Button(controls_frame, text="Start", command=self.start_system).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="Stop", command=self.stop_system).grid(row=0, column=1, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("System Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
    
    def start_system(self):
        if not self.running:
            self.running = True
            self.status_var.set("System Started")
            # Start eye tracking thread
            threading.Thread(target=self.eye_tracking_loop, daemon=True).start()
    
    def stop_system(self):
        self.running = False
        self.status_var.set("System Stopped")
    
    def process_frame(self):
        """Process each frame from the webcam."""
        if not self.running:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.status_var.set("Error: Could not read from webcam")
            return
        
        # Detect objects in the frame
        detected_objects = self.object_detector.detect_objects(frame)
        
        # Draw detections on the frame
        frame_with_detections = self.object_detector.draw_detections(frame.copy(), detected_objects)
        
        # Convert to RGB for display in Tkinter
        frame_rgb = cv2.cvtColor(frame_with_detections, cv2.COLOR_BGR2RGB)
        
        # Convert to PhotoImage
        img = Image.fromarray(frame_rgb)
        img.thumbnail((800, 600))  # Resize if needed
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update the display
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        
        # Schedule the next frame processing
        self.root.after(10, self.process_frame)
    
    def eye_tracking_loop(self):
        # This method is now handled by process_frame
        pass
    
    def on_close(self):
        """Handle window close event."""
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = EyeAssistApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
