import cv2
import numpy as np
import pyautogui
import sys
import os

# Disable the fail-safe
pyautogui.FAILSAFE = False

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    sys.exit(1)

# Get screen size
screen_w, screen_h = pyautogui.size()
print(f"Screen size: {screen_w}x{screen_h}")

# Set webcam resolution
frame_w, frame_h = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_h)

# Load the pre-trained Haar Cascade for face detection
face_cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(face_cascade_path)

if face_cascade.empty():
    print("Error loading face detection model.")
    sys.exit(1)

# Control parameters
smoothing = 0.5  # 0.0 to 1.0 (higher = smoother)
sensitivity = 1.5  # Mouse movement sensitivity
prev_x, prev_y = screen_w // 2, screen_h // 2  # Start at screen center

print("\n=== Head-Controlled Mouse ===")
print("Move your head to control the cursor")
print("Press 'q' to quit")

try:
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            print("Error reading from webcam")
            break

        # Flip the frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) > 0:
            # Get the first face
            x, y, w, h = faces[0]
            
            # Calculate center of face
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Map face position to screen coordinates with sensitivity adjustment
            screen_x = np.interp(face_center_x, 
                               [0, frame_w], 
                               [0, screen_w * sensitivity])
            screen_y = np.interp(face_center_y, 
                               [0, frame_h], 
                               [0, screen_h * sensitivity])
            
            # Smooth the movement
            screen_x = int(prev_x * (1 - smoothing) + screen_x * smoothing)
            screen_y = int(prev_y * (1 - smoothing) + screen_y * smoothing)
            
            # Move the mouse
            pyautogui.moveTo(screen_x, screen_y, _pause=False)
            
            # Update previous positions
            prev_x, prev_y = screen_x, screen_y
            
            # Draw rectangle around face (for visualization)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw crosshair at face center
            cv2.line(frame, (face_center_x-10, face_center_y), 
                    (face_center_x+10, face_center_y), (0, 0, 255), 2)
            cv2.line(frame, (face_center_x, face_center_y-10), 
                    (face_center_x, face_center_y+10), (0, 0, 255), 2)
            
            # Display the coordinates
            cv2.putText(frame, f"X: {screen_x:.0f}, Y: {screen_y:.0f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
        
        # Display instructions
        cv2.putText(frame, "Move your head to control the cursor", 
                   (10, frame_h - 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 1)
        cv2.putText(frame, "Press 'q' to quit", 
                   (10, frame_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 1)
        
        # Display the frame
        cv2.imshow('Head-Controlled Mouse', frame)
        
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nExiting...")

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("Program ended. Thank you for using Head-Controlled Mouse!")
