import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class ChatHistory:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.history_dir = os.path.join(base_dir, 'data')
        self.history_file = os.path.join(self.history_dir, 'chat_history.json')
        self.archive_dir = os.path.join(self.history_dir, 'archives')
        self.max_records = 500
        self.ensure_data_dir()
        self.session_id = datetime.now().strftime('%Y%m%d-%H%M%S')
        
    def ensure_data_dir(self):
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
            
    def _load_all(self) -> List[Dict]:
        if not os.path.exists(self.history_file):
            return []
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_all(self, history: List[Dict]):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def add_message(self, role: str, content: str, tags: Optional[List[str]] = None):
        history = self._load_all()
        history.append({
            'id': str(uuid.uuid4()),
            'session_id': self.session_id,
            'role': role,
            'content': content,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat()
        })
        if len(history) > self.max_records:
            overflow = history[:-self.max_records]
            history = history[-self.max_records:]
            self._archive_messages(overflow)
        self._save_all(history)
            
    def load_history(self, limit: Optional[int] = 50) -> List[Dict]:
        history = self._load_all()
        if limit:
            return history[-limit:]
        return history

    def filter_history(self, keyword: Optional[str] = None, start: Optional[datetime] = None,
                       end: Optional[datetime] = None, tags: Optional[List[str]] = None) -> List[Dict]:
        records = self._load_all()
        result = []
        for item in records:
            ts = datetime.fromisoformat(item['timestamp'])
            if start and ts < start:
                continue
            if end and ts > end:
                continue
            if keyword and keyword.lower() not in item['content'].lower():
                continue
            if tags and not set(tags).issubset(set(item.get('tags', []))):
                continue
            result.append(item)
        return result
        
    def save_history(self):
        pass
        
    def clear_history(self):
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        if os.path.exists(self.archive_dir):
            for name in os.listdir(self.archive_dir):
                os.remove(os.path.join(self.archive_dir, name))

    def list_archives(self) -> List[str]:
        if not os.path.exists(self.archive_dir):
            return []
        return sorted(os.listdir(self.archive_dir))

    def _archive_messages(self, messages: List[Dict]):
        if not messages:
            return
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        archive_path = os.path.join(self.archive_dir, f'chat-{timestamp}.json')
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

