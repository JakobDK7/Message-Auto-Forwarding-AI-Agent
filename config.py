import os
import json
from pathlib import Path

class Config:
    """Configuration class for the message forwarding system"""
    
    def __init__(self, config_file=None):
        self.config_file = config_file or os.path.join(os.getcwd(), 'config.json')
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        config_path = Path(self.config_file)
        
        # Create default config if file doesn't exist
        if not config_path.exists():
            default_config = {
                "selenium": {
                    "driver_path": "",
                    "headless": True,
                    "implicit_wait": 10
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "file": "message_forwarder.log"
                },
                "notification": {
                    "email": {
                        "enabled": False,
                        "smtp_server": "",
                        "smtp_port": 587,
                        "sender": "",
                        "password": "",
                        "recipients": []
                    }
                }
            }
            
            # Save default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self):
        """Save current configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """Set a configuration value by key"""
        keys = key.split('.')
        config = self.config
        
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
