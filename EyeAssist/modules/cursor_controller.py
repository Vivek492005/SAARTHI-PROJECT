import pyautogui
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import numpy as np

class CursorController:
    def __init__(self, smoothing=0.5, scroll_sensitivity=1.0):
        """
        Initialize the cursor controller.
        
        Args:
            smoothing (float): Smoothing factor for cursor movement (0.0 to 1.0)
            scroll_sensitivity (float): Sensitivity factor for scrolling
        """
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.smoothing = max(0.0, min(1.0, smoothing))  # Clamp between 0 and 1
        self.scroll_sensitivity = max(0.1, scroll_sensitivity)  # Ensure positive value
        self.prev_x, self.prev_y = pyautogui.position()
        self.click_threshold = 1.5  # Seconds to hold for click
        self.last_click_time = 0
        self.click_cooldown = 0.5  # Cooldown between clicks (seconds)
        self.gaze_start_time = None
        self.gaze_direction = None
        
        # Disable pyautogui failsafe
        pyautogui.FAILSAFE = False
    
    def move_to(self, x, y, relative=False):
        """
        Move cursor to absolute (x, y) or relative to current position.
        
        Args:
            x (int): X coordinate or X offset
            y (int): Y coordinate or Y offset
            relative (bool): If True, treats x,y as relative movement
        """
        if relative:
            # Calculate smoothed relative movement
            dx = int(x * (1 - self.smoothing) + (self.prev_x * self.smoothing))
            dy = int(y * (1 - self.smoothing) + (self.prev_y * self.smoothing))
            pyautogui.moveRel(dx, dy, _pause=False)
        else:
            # Apply smoothing to absolute position
            target_x = int(x * (1 - self.smoothing) + (self.prev_x * self.smoothing))
            target_y = int(y * (1 - self.smoothing) + (self.prev_y * self.smoothing))
            pyautogui.moveTo(target_x, target_y, _pause=False)
        
        self.prev_x, self.prev_y = pyautogui.position()
    
    def click(self, button='left', duration=0.1):
        """
        Simulate a mouse click.
        
        Args:
            button (str): 'left', 'right', or 'middle'
            duration (float): Time to hold the button down (seconds)
        """
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        if button.lower() == 'left':
            pyautogui.mouseDown(button='left')
            time.sleep(duration)
            pyautogui.mouseUp(button='left')
        elif button.lower() == 'right':
            pyautogui.mouseDown(button='right')
            time.sleep(duration)
            pyautogui.mouseUp(button='right')
        elif button.lower() == 'middle':
            pyautogui.mouseDown(button='middle')
            time.sleep(duration)
            pyautogui.mouseUp(button='middle')
        
        self.last_click_time = current_time
        return True
    
    def scroll(self, amount):
        """
        Scroll up (positive) or down (negative).
        
        Args:
            amount (int): Number of 'clicks' to scroll
        """
        pyautogui.scroll(int(amount * self.scroll_sensitivity))
    
    def drag_to(self, x, y, button='left'):
        """
        Click and drag to the specified position.
        
        Args:
            x (int): Target X coordinate
            y (int): Target Y coordinate
            button (str): Mouse button to use for dragging
        """
        pyautogui.mouseDown(button=button)
        self.move_to(x, y)
        pyautogui.mouseUp(button=button)
    
    def type_text(self, text):
        """
        Type the specified text.
        
        Args:
            text (str): Text to type
        """
        self.keyboard.type(text)
    
    def press_key(self, key):
        """
        Press and release a key.
        
        Args:
            key (str or Key): Key to press (e.g., 'a', 'enter', Key.esc)
        """
        try:
            self.keyboard.press(key)
            self.keyboard.release(key)
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
    
    def hold_click_detector(self, gaze_direction, threshold_seconds=1.5):
        """
        Detect if gaze is held in a position for a click.
        
        Args:
            gaze_direction (str): Current gaze direction ('left', 'right', 'center')
            threshold_seconds (float): Time to hold gaze for click
            
        Returns:
            bool: True if click was triggered, False otherwise
        """
        current_time = time.time()
        
        if gaze_direction == 'center':
            if self.gaze_direction != 'center':
                self.gaze_start_time = current_time
                self.gaze_direction = 'center'
            
            if current_time - self.gaze_start_time >= threshold_seconds:
                self.click()
                self.gaze_start_time = current_time  # Reset timer
                return True
        else:
            # Reset timer if not looking at center
            if self.gaze_direction == 'center':
                self.gaze_start_time = None
            self.gaze_direction = gaze_direction
        
        return False
