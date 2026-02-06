import pyttsx3
import threading
import queue
import time

class VoiceFeedback:
    def __init__(self, rate=150, volume=1.0, voice_id=None):
        """
        Initialize the voice feedback system.
        
        Args:
            rate (int): Speech rate (words per minute)
            volume (float): Volume level (0.0 to 1.0)
            voice_id (str): Specific voice ID to use (None for default)
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        
        # Set voice if specified
        if voice_id:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if voice_id in voice.id:
                    self.engine.setProperty('voice', voice.id)
                    break
        
        self.message_queue = queue.Queue()
        self.is_speaking = False
        self.stop_thread = False
        
        # Start the message processing thread
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
    
    def say(self, text, interrupt=False):
        """
        Add a message to the speech queue.
        
        Args:
            text (str): Text to speak
            interrupt (bool): If True, clear the queue before adding this message
        """
        if interrupt:
            self.stop()
        self.message_queue.put(text)
    
    def _process_queue(self):
        """Process messages from the queue and speak them."""
        while not self.stop_thread:
            if not self.message_queue.empty():
                text = self.message_queue.get()
                self.is_speaking = True
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Error in speech synthesis: {e}")
                self.is_speaking = False
                self.message_queue.task_done()
            time.sleep(0.1)
    
    def stop(self):
        """Stop the current speech and clear the queue."""
        self.engine.stop()
        while not self.message_queue.empty():
            try:
                self.message_queue.get(False)
                self.message_queue.task_done()
            except queue.Empty:
                continue
    
    def set_rate(self, rate):
        """Set the speech rate."""
        self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set the volume level (0.0 to 1.0)."""
        self.engine.setProperty('volume', min(1.0, max(0.0, volume)))
    
    def set_voice(self, voice_id):
        """
        Set the voice to use for speech.
        
        Args:
            voice_id (str): Voice ID to use (partial match)
        """
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice_id.lower() in voice.name.lower() or voice_id in voice.id:
                self.engine.setProperty('voice', voice.id)
                return True
        return False
    
    def get_available_voices(self):
        """Get a list of available voices."""
        voices = self.engine.getProperty('voices')
        return [{'id': voice.id, 'name': voice.name} for voice in voices]
    
    def is_busy(self):
        """Check if the voice feedback is currently speaking."""
        return self.is_speaking or not self.message_queue.empty()
    
    def __del__(self):
        """Clean up resources."""
        self.stop_thread = True
        if self.thread.is_alive():
            self.thread.join()
        self.engine.stop()
