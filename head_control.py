import cv2
import numpy as np
import pyautogui
import dlib
from scipy.spatial import distance as dist
from imutils import face_utils
import time

# Initialize variables
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()
frame_w, frame_h = 640, 480
smoothing = 0.5
prev_x, prev_y = screen_w//2, screen_h//2

# Initialize dlib's face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, frame_w)
cap.set(4, frame_h)

# Constants for blink detection
EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 2
COUNTER = 0
TOTAL = 0

# Constants for smile detection
SMILE_AR_THRESH = 0.5
SMILE_CONSEC_FRAMES = 5
smile_counter = 0

# Mouse control parameters
mouse_sensitivity = 1.5
clicking = False
right_clicking = False
last_click_time = 0
click_delay = 1.0  # seconds between clicks

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    
    # Compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    
    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

def smile_aspect_ratio(mouth):
    # Compute the euclidean distances between the horizontal
    # mouth landmark (x, y)-coordinates
    A = dist.euclidean(mouth[0], mouth[6])  # 48, 54
    B = dist.euclidean(mouth[3], mouth[9])  # 51, 57
    
    # Compute the mouth aspect ratio
    mar = B / A if A != 0 else 0
    return mar

def move_mouse(x, y):
    global prev_x, prev_y
    
    # Calculate the new mouse position with smoothing
    new_x = int(prev_x * (1 - smoothing) + x * smoothing)
    new_y = int(prev_y * (1 - smoothing) + y * smoothing)
    
    # Move the mouse
    pyautogui.moveTo(new_x, new_y, _pause=False)
    
    # Update previous positions
    prev_x, prev_y = new_x, new_y

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the grayscale frame
        rects = detector(gray, 0)
        
        # Loop over the face detections
        for rect in rects:
            # Get facial landmarks
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            
            # Extract the left and right eye coordinates
            left_eye = shape[42:48]
            right_eye = shape[36:42]
            
            # Extract the mouth coordinates
            mouth = shape[48:68]
            
            # Calculate eye aspect ratio for both eyes
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)
            
            # Average the eye aspect ratio
            ear = (left_ear + right_ear) / 2.0
            
            # Calculate mouth aspect ratio
            mar = smile_aspect_ratio(mouth)
            
            # Check for blink
            if ear < EYE_AR_THRESH:
                COUNTER += 1
            else:
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL += 1
                    pyautogui.click()  # Left click on eye blink
                COUNTER = 0
            
            # Check for smile (right click)
            if mar > SMILE_AR_THRESH:
                smile_counter += 1
                if smile_counter >= SMILE_CONSEC_FRAMES and not right_clicking:
                    pyautogui.rightClick()
                    right_clicking = True
            else:
                smile_counter = 0
                right_clicking = False
            
            # Get the center of the face
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Map face position to screen coordinates with sensitivity adjustment
            screen_x = np.interp(face_center_x, [0, frame_w], 
                               [0, screen_w * mouse_sensitivity])
            screen_y = np.interp(face_center_y, [0, frame_h], 
                               [0, screen_h * mouse_sensitivity])
            
            # Move the mouse
            move_mouse(screen_x, screen_y)
            
            # Draw face bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw eyes and mouth
            cv2.drawContours(frame, [left_eye], -1, (0, 255, 255), 1)
            cv2.drawContours(frame, [right_eye], -1, (0, 255, 255), 1)
            cv2.drawContours(frame, [mouth], -1, (0, 255, 255), 1)
            
            # Display EAR and MAR values
            cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display the frame
        cv2.imshow("Head Control", frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
