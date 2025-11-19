import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from zipfile import ZipFile

from desktop.config.settings import Settings


class BackupManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.backup_dir = os.path.join(self.base_dir, 'data', 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        self.history_file = os.path.join(self.base_dir, 'data', 'chat_history.json')

    def _files(self) -> List[Dict[str, str]]:
        files = []
        if os.path.exists(self.settings.config_file):
            files.append({
                'path': self.settings.config_file,
                'arcname': 'config/config.json'
            })
        database_path = self.settings.get_database_path()
        if database_path and os.path.exists(database_path):
            rel_path = os.path.relpath(database_path, self.base_dir)
            files.append({'path': database_path, 'arcname': rel_path})
        if os.path.exists(self.history_file):
            files.append({'path': self.history_file, 'arcname': 'data/chat_history.json'})
        return files

    def create_backup(self) -> str:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'backup-{timestamp}.zip')
        files = self._files()
        with ZipFile(backup_path, 'w') as archive:
            for item in files:
                archive.write(item['path'], arcname=item['arcname'])
        return backup_path

    def list_backups(self) -> List[str]:
        backups = sorted(Path(self.backup_dir).glob('backup-*.zip'), reverse=True)
        return [str(path) for path in backups]

    def restore_backup(self, backup_path: str):
        if not os.path.exists(backup_path):
            raise FileNotFoundError('Указанный бэкап не найден')
        with ZipFile(backup_path, 'r') as archive:
            archive.extractall(self.base_dir)

    def latest_backup(self) -> str:
        backups = self.list_backups()
        return backups[0] if backups else ''

