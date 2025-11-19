import json
import os
from typing import Dict, Any


class Settings:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(base_dir, 'config')
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
            self.config = self.default_config()
            self.save_config()
            
    def default_config(self) -> Dict[str, Any]:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return {
            'model_path': os.path.join(base_dir, 'models'),
            'theme': 'light',
            'prompt': 'Вы являетесь полезным русскоязычным ассистентом, отвечающим кратко и по делу.',
            'generation': {
                'max_new_tokens': 200,
                'temperature': 0.8,
                'top_p': 0.95,
                'do_sample': True,
                'repetition_penalty': 1.05
            }
        }
            
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
    def get_model_path(self) -> str:
        return self.config.get('model_path') or self.default_config()['model_path']
        
    def get_theme(self) -> str:
        return self.config.get('theme', 'light')
        
    def set_theme(self, theme: str):
        self.config['theme'] = theme
        self.save_config()

    def get_generation_config(self) -> Dict[str, Any]:
        return self.config.get('generation', self.default_config()['generation'])

    def get_prompt(self) -> str:
        return self.config.get('prompt', self.default_config()['prompt'])

