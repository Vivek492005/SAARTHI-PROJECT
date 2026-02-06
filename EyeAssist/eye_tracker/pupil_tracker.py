import cv2
import numpy as np

class PupilTracker:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.prev_eye_center = None
        self.smoothing_factor = 0.5
    
    def detect_eyes(self, frame):
        """Detect eyes in the frame and return their positions."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        eyes = []
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Detect eyes within the face region
            detected_eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
            
            for (ex, ey, ew, eh) in detected_eyes:
                eye_center = (x + ex + ew//2, y + ey + eh//2)
                eyes.append({
                    'center': eye_center,
                    'size': (ew, eh),
                    'roi': roi_color[ey:ey+eh, ex:ex+ew]
                })
        
        return eyes
    
    def track_pupil(self, eye_roi):
        """Track pupil position within an eye ROI."""
        # Convert to grayscale and apply threshold
        gray_eye = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray_eye, 45, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
        
        for cnt in contours:
            # Calculate moments to find the center
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                return (cX, cY)
        
        return None
    
    def get_gaze_direction(self, frame):
        """Determine gaze direction based on eye tracking."""
        eyes = self.detect_eyes(frame)
        
        if len(eyes) >= 2:  # We need both eyes for accurate gaze detection
            # Calculate the center between two eyes
            eye_centers = [eye['center'] for eye in eyes[:2]]
            center_x = sum(x for x, y in eye_centers) // len(eye_centers)
            center_y = sum(y for x, y in eye_centers) // len(eye_centers)
            
            # Track pupils
            pupil_positions = []
            for eye in eyes[:2]:
                pupil = self.track_pupil(eye['roi'])
                if pupil:
                    # Convert pupil position to frame coordinates
                    px = eye['center'][0] - eye['size'][0]//2 + pupil[0]
                    py = eye['center'][1] - eye['size'][1]//2 + pupil[1]
                    pupil_positions.append((px, py))
            
            if len(pupil_positions) == 2:
                # Calculate gaze direction (simple version)
                avg_pupil_x = sum(x for x, y in pupil_positions) // len(pupil_positions)
                gaze_direction = "center"
                
                if avg_pupil_x < center_x - 20:
                    gaze_direction = "left"
                elif avg_pupil_x > center_x + 20:
                    gaze_direction = "right"
                
                return {
                    'gaze': gaze_direction,
                    'eyes_detected': True,
                    'pupils': pupil_positions
                }
        
        return {
            'gaze': None,
            'eyes_detected': len(eyes) > 0,
            'pupils': []
        }
