import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_path = os.path.join(Path.home(), ".gesture_assistant")
        self.config_file = os.path.join(self.config_path, "config.json")
        self.default_config = {
            "language": "en",
            "gestures": {
                "thumbs_up": "Yes",
                "thumbs_down": "No",
                "open_hand": "Hello",
                "fist": "Stop",
                "peace": "Peace",
                "ok": "Okay",
                "call_me": "Call me",
                "rock": "Rock on",
                "love_you": "I love you",
                "point_up": "Look up",
                "point_down": "Look down",
                "point_left": "Look left",
                "point_right": "Look right",
                "shaka": "Hang loose",
                "spiderman": "With great power comes great responsibility"
            },
            "smart_home": {
                "enabled": False,
                "devices": {}
            },
            "languages": {
                "en": "English",
                "hi": "हिंदी",
                "es": "Español",
                "fr": "Français",
                "de": "Deutsch"
            },
            "translations": {
                "Yes": {"hi": "हाँ", "es": "Sí", "fr": "Oui", "de": "Ja"},
                "No": {"hi": "नहीं", "es": "No", "fr": "Non", "de": "Nein"},
                "Hello": {"hi": "नमस्ते", "es": "Hola", "fr": "Bonjour", "de": "Hallo"}
                # More translations can be added here
            }
        }
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        try:
            if not os.path.exists(self.config_path):
                os.makedirs(self.config_path)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                self._save_config(self.default_config)
                return self.default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config
    
    def _save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Get a setting from the config"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set_setting(self, key, value):
        """Update a setting in the config"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        return self._save_config(self.config)
    
    def add_custom_gesture(self, gesture_name, phrase):
        """Add or update a custom gesture"""
        if 'gestures' not in self.config:
            self.config['gestures'] = {}
        self.config['gestures'][gesture_name] = phrase
        return self._save_config(self.config)
    
    def remove_custom_gesture(self, gesture_name):
        """Remove a custom gesture"""
        if 'gestures' in self.config and gesture_name in self.config['gestures']:
            del self.config['gestures'][gesture_name]
            return self._save_config(self.config)
        return False
    
    def get_phrase_translation(self, phrase, language=None):
        """Get translation of a phrase in the current language"""
        if not language:
            language = self.get_setting('language', 'en')
        
        if language == 'en':
            return phrase
            
        translations = self.get_setting('translations', {})
        if phrase in translations and language in translations[phrase]:
            return translations[phrase][language]
        return phrase

# Global config instance
config = Config()
