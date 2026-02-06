import cv2
import numpy as np

class EyeTracker:
    def __init__(self):
        # Load Haar cascades for face and eye detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Eye tracking parameters
        self.eye_tracking = False
        self.eye_roi = None
        self.face_roi = None
        self.prev_eye_center = None
        
    def detect_face(self, frame):
        """Detect faces in the frame and return the largest face."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            # Return the largest face
            return max(faces, key=lambda rect: rect[2] * rect[3])
        return None
    
    def detect_eyes(self, face_roi):
        """Detect eyes within a face region."""
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray_face)
        
        if len(eyes) >= 2:
            # Sort eyes by x-coordinate (left to right)
            eyes = sorted(eyes, key=lambda x: x[0])
            return eyes[:2]  # Return only the first two eyes found
        return None
    
    def track_eye(self, eye_roi):
        """Track the pupil within an eye region."""
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
        """Determine the gaze direction based on eye positions."""
        face_rect = self.detect_face(frame)
        if face_rect is None:
            return None
            
        x, y, w, h = face_rect
        face_roi = frame[y:y+h, x:x+w]
        
        eyes = self.detect_eyes(face_roi)
        if eyes is None or len(eyes) < 2:
            return None
            
        # Calculate the center between the two eyes
        eye_centers = []
        for (ex, ey, ew, eh) in eyes[:2]:
            eye_center = (x + ex + ew//2, y + ey + eh//2)
            eye_centers.append(eye_center)
            
        # Calculate the center point between eyes
        center_x = (eye_centers[0][0] + eye_centers[1][0]) // 2
        center_y = (eye_centers[0][1] + eye_centers[1][1]) // 2
        
        # Track pupils
        pupil_positions = []
        for (ex, ey, ew, eh) in eyes[:2]:
            eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
            pupil = self.track_eye(eye_roi)
            if pupil:
                px = x + ex + pupil[0]
                py = y + ey + pupil[1]
                pupil_positions.append((px, py))
        
        if len(pupil_positions) == 2:
            # Calculate gaze direction (simple version)
            avg_pupil_x = sum(x for x, y in pupil_positions) // len(pupil_positions)
            
            if avg_pupil_x < center_x - 20:
                return "left"
            elif avg_pupil_x > center_x + 20:
                return "right"
            else:
                return "center"
        
        return None
