import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any

from desktop.config.settings import Settings


class UpdateManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.cache_dir = os.path.join(base_dir, 'data', 'updater')
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        self.hash_file = os.path.join(self.cache_dir, 'model_hashes.json')

    def verify_models(self) -> Dict[str, Any]:
        model_path = Path(self.settings.get_model_path())
        hashes = {}
        if not model_path.exists():
            return {'status': 'missing', 'details': 'Каталог с моделью не найден'}
        for file_path in model_path.glob('**/*'):
            if file_path.is_file() and file_path.suffix in ('.bin', '.json', '.txt', '.safetensors'):
                hashes[str(file_path)] = self._sha256(file_path)
        with open(self.hash_file, 'w', encoding='utf-8') as f:
            json.dump(hashes, f, ensure_ascii=False, indent=2)
        return {'status': 'ok', 'details': f'Проверено файлов: {len(hashes)}'}

    def _sha256(self, file_path: Path) -> str:
        hash_obj = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

    def check_updates(self) -> Dict[str, Any]:
        updater_config = self.settings.get_updater_config()
        channel = updater_config.get('channel', 'stable')
        return {
            'status': 'pending',
            'details': f'Автообновление подключено к каналу {channel}. Реальная проверка будет добавлена после интеграции с сервером.'
        }


