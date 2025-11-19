import os
import json

class Settings:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.ensure_config_dir()
        self.load_config()
        
    def ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'model_path': os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models'),
                'theme': 'light'
            }
            self.save_config()
            
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def get_model_path(self):
        return self.config.get('model_path', 'models')
        
    def get_theme(self):
        return self.config.get('theme', 'light')
        
    def set_theme(self, theme):
        self.config['theme'] = theme
        self.save_config()

