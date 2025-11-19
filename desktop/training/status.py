import json
import os
from datetime import datetime


class TrainingStatusWriter:
    def __init__(self, status_file: str):
        self.status_file = status_file
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)

    def update(self, status: str, **kwargs):
        payload = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
        }
        payload.update(kwargs)
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

