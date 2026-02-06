import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import time
import json
import paho.mqtt.client as mqtt
from googletrans import Translator
from collections import deque
from config import config

# Initialize translator
translator = Translator()

class GestureAssistant:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        
        # Gesture buffer to prevent rapid repeating
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 2.0  # seconds
        
        # Current frame for UI display
        self.current_frame = None
        self.current_gesture = None
        
        # MQTT client for smart home integration
        self.mqtt_client = None
        self.init_mqtt()
        
        # Load gestures from config
        self.gesture_actions = {}
        self.load_gestures()
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        
    def init_mqtt(self):
        """Initialize MQTT client if smart home is enabled"""
        if config.get_setting('smart_home.enabled', False):
            try:
                self.mqtt_client = mqtt.Client()
                
                # Set credentials if available
                username = config.get_setting('smart_home.mqtt_username')
                password = config.get_setting('smart_home.mqtt_password')
                
                if username and password:
                    self.mqtt_client.username_pw_set(username, password)
                
                # Connect to broker
                host = config.get_setting('smart_home.mqtt_host', 'localhost')
                port = int(config.get_setting('smart_home.mqtt_port', 1883))
                self.mqtt_client.connect(host, port, 60)
                self.mqtt_client.loop_start()
            except Exception as e:
                print(f"Failed to initialize MQTT: {e}")
    
    def load_gestures(self):
        """Load gestures from config"""
        self.gesture_actions = {}
        gestures = config.get_setting('gestures', {})
        
        for gesture_name, phrase in gestures.items():
            self.gesture_actions[gesture_name] = lambda p=phrase: self.process_gesture(p)
        
    def say_text(self, text):
        """Convert text to speech with language support"""
        try:
            # Get current language
            target_lang = config.get_setting('language', 'en')
            
            # Get translation from config first
            translated_text = config.get_phrase_translation(text, target_lang)
            
            # If no translation in config, try to translate
            if translated_text == text and target_lang != 'en':
                try:
                    translated = translator.translate(text, dest=target_lang)
                    translated_text = translated.text
                    
                    # Cache the translation
                    translations = config.get_setting('translations', {})
                    if text not in translations:
                        translations[text] = {}
                    translations[text][target_lang] = translated_text
                    config.set_setting('translations', translations)
                except Exception as e:
                    print(f"Translation error: {e}")
            
            print(f"Speaking ({target_lang}): {translated_text}")
            
            # Set voice based on language
            voices = self.engine.getProperty('voices')
            if target_lang == 'hi':  # Hindi
                for voice in voices:
                    if 'hindi' in voice.languages[0].lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            elif target_lang == 'es':  # Spanish
                for voice in voices:
                    if 'spanish' in voice.languages[0].lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            # Add more language cases as needed
            
            self.engine.say(translated_text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
        
    def get_gesture(self, hand_landmarks):
        """Detect which gesture is being shown"""
        # Get hand landmarks
        landmarks = hand_landmarks.landmark
        
        # Thumb tip (4), Index finger tip (8), Middle finger tip (12), Ring finger tip (16), Pinky tip (20)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Calculate distances between finger tips and their respective MCP joints
        def is_finger_up(tip, mcp, pip):
            return tip.y < pip.y and tip.y < mcp.y
            
        # Check which fingers are up
        index_up = is_finger_up(index_tip, landmarks[5], landmarks[6])
        middle_up = is_finger_up(middle_tip, landmarks[9], landmarks[10])
        ring_up = is_finger_up(ring_tip, landmarks[13], landmarks[14])
        pinky_up = is_finger_up(pinky_tip, landmarks[17], landmarks[18])
        thumb_up = thumb_tip.y < landmarks[3].y  # Thumb is up if tip is above IP joint
        
        # Gesture recognition logic
        if all([index_up, middle_up, not ring_up, not pinky_up, not thumb_up]):
            return 'peace'
        elif all([not index_up, not middle_up, not ring_up, not pinky_up, not thumb_up]):
            return 'fist'
        elif all([index_up, not middle_up, not ring_up, not pinky_up, not thumb_up]):
            return 'point_up' if index_tip.y < landmarks[0].y else 'point_down'
        elif all([thumb_up, not index_up, not middle_up, not ring_up, not pinky_up]):
            return 'thumbs_up'
        elif all([not thumb_up, not index_up, not middle_up, not ring_up, not pinky_up]):
            return 'fist'
        elif all([index_up, middle_up, ring_up, pinky_up, thumb_up]):
            return 'open_hand'
        elif all([index_up, thumb_up, not middle_up, not ring_up, not pinky_up]):
            return 'ok'
        elif all([not index_up, not middle_up, not ring_up, pinky_up, thumb_up]):
            return 'call_me'
        elif all([index_up, pinky_up, not middle_up, not ring_up, not thumb_up]):
            return 'rock'
        elif all([index_up, pinky_up, thumb_up, not middle_up, not ring_up]):
            return 'love_you'
        elif all([index_up, not middle_up, not ring_up, not pinky_up, not thumb_up]):
            if abs(index_tip.x - landmarks[0].x) > 0.2:
                if index_tip.x < landmarks[0].x:
                    return 'point_right'
                else:
                    return 'point_left'
        elif all([not index_up, not middle_up, not ring_up, pinky_up, thumb_up]):
            return 'shaka'
        
        return None
    
    def process_gesture(self, phrase):
        """Process a recognized gesture"""
        # Handle smart home commands
        if phrase.startswith("smart:"):
            self.handle_smart_home_command(phrase[6:])  # Remove 'smart:' prefix
        else:
            # Speak the phrase
            self.say_text(phrase)
    
    def handle_smart_home_command(self, command):
        """Handle smart home control commands"""
        if not self.mqtt_client:
            print("Smart home integration not enabled")
            return
        
        try:
            # Parse command (format: device_id/action)
            parts = command.split('/')
            if len(parts) != 2:
                print(f"Invalid command format: {command}")
                return
                
            device_id, action = parts
            
            # Get device info from config
            devices = config.get_setting('smart_home.devices', {})
            if device_id not in devices:
                print(f"Unknown device: {device_id}")
                return
                
            device = devices[device_id]
            topic = device.get('topic', f"home/device/{device_id}/set")
            
            # Publish MQTT message
            payload = json.dumps({
                'device': device_id,
                'action': action,
                'timestamp': int(time.time())
            })
            
            self.mqtt_client.publish(topic, payload)
            print(f"Sent command to {device_id}: {action}")
            
        except Exception as e:
            print(f"Error sending smart home command: {e}")
    
    def get_current_frame(self):
        """Get the current frame for UI display"""
        return self.current_frame
    
    def get_current_gesture(self):
        """Get the currently detected gesture"""
        return self.current_gesture
    
    def process_frame(self, frame):
        """Process a single frame for hand gesture detection"""
        # Store frame for UI
        self.current_frame = frame.copy()
        
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe Hands
        results = self.hands.process(rgb_frame)
        
        # Reset current gesture
        self.current_gesture = None
        
        # If hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Get gesture
                gesture = self.get_gesture(hand_landmarks)
                
                if gesture:
                    # Update current gesture for UI
                    self.current_gesture = gesture
                    
                    # Process gesture if detected and cooldown has passed
                    current_time = time.time()
                    if (gesture != self.last_gesture or 
                        current_time - self.last_gesture_time > self.gesture_cooldown):
                        
                        self.last_gesture = gesture
                        self.last_gesture_time = current_time
                        
                        # Perform action based on gesture
                        if gesture in self.gesture_actions:
                            self.gesture_actions[gesture]()
                    
                    # Display gesture text on frame
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
        return frame
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            
        if hasattr(self, 'mqtt_client') and self.mqtt_client:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
    
    def update(self):
        """Update method for the main loop"""
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)
        
        # Process the frame
        self.process_frame(frame)
        
        return frame

    # This file is now meant to be imported by the UI
    # Run the UI using: python ui_main.py
