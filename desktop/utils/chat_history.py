import os
import json
from datetime import datetime

class ChatHistory:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.history_dir = os.path.join(base_dir, 'data')
        self.history_file = os.path.join(self.history_dir, 'chat_history.json')
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
    def add_message(self, role, content):
        if not os.path.exists(self.history_file):
            history = []
        else:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
        history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
            
    def load_history(self, limit=50):
        if not os.path.exists(self.history_file):
            return []
            
        with open(self.history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
            
        return history[-limit:] if limit else history
        
    def save_history(self):
        pass
        
    def clear_history(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)

