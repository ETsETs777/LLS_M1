import os
from datetime import datetime
from typing import List, Dict, Optional

from desktop.utils.chat_history import ChatHistory
from desktop.config.settings import Settings
from desktop.history.exporters import HistoryExporter


class HistoryManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.history = ChatHistory()
        self.exporter = HistoryExporter()
        self.history_config = self.settings.get_history_config()
        self._ensure_directories()

    def _ensure_directories(self):
        export_dir = self.history_config.get('export_dir')
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def list_messages(self, limit: Optional[int] = 200) -> List[Dict]:
        return self.history.load_history(limit)

    def search(self, keyword: str = '', start: Optional[datetime] = None,
               end: Optional[datetime] = None, tags: Optional[List[str]] = None) -> List[Dict]:
        return self.history.filter_history(keyword, start, end, tags)

    def export(self, fmt: str, path: Optional[str] = None, **filters) -> str:
        messages = self.search(**filters)
        target = path or self._default_export_path(fmt)
        self.exporter.export(messages, fmt, target)
        return target

    def _default_export_path(self, fmt: str) -> str:
        export_dir = self.history_config.get('export_dir')
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f'history-{timestamp}.{fmt}'
        return os.path.join(export_dir, filename)

    def cleanup_old_records(self):
        retention = self.history_config.get('retention_days', 90)
        if retention <= 0:
            return
        threshold = datetime.utcnow().timestamp() - retention * 86400
        all_messages = self.history.load_history(limit=None)
        filtered = [msg for msg in all_messages if datetime.fromisoformat(msg['timestamp']).timestamp() >= threshold]
        if len(filtered) != len(all_messages):
            self.history._save_all(filtered)

