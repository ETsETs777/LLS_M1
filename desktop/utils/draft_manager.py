"""
Менеджер черновиков для автосохранения незавершенных сообщений.
"""
import json
import os
from typing import Optional
from pathlib import Path

from desktop.utils.logger import get_logger

logger = get_logger('desktop.utils.draft_manager')


class DraftManager:
    """
    Менеджер для сохранения и восстановления черновиков сообщений.
    """
    
    def __init__(self, draft_file: Optional[str] = None):
        """
        Инициализирует менеджер черновиков.
        
        Args:
            draft_file: Путь к файлу черновиков (по умолчанию в data/drafts.json)
        """
        if draft_file is None:
            base_dir = Path(__file__).parent.parent.parent
            draft_file = base_dir / 'data' / 'drafts.json'
        
        self.draft_file = Path(draft_file)
        self.draft_file.parent.mkdir(parents=True, exist_ok=True)
        self._draft: Optional[str] = None
        self._tags: list = []
    
    def save_draft(self, message: str, tags: Optional[list] = None) -> None:
        """
        Сохраняет черновик сообщения.
        
        Args:
            message: Текст сообщения
            tags: Список тегов (опционально)
        """
        try:
            self._draft = message
            self._tags = tags or []
            
            data = {
                'message': message,
                'tags': self._tags,
                'timestamp': None  # Можно добавить timestamp
            }
            
            with open(self.draft_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Черновик сохранен: {len(message)} символов")
        except Exception as e:
            logger.warning(f"Не удалось сохранить черновик: {e}")
    
    def load_draft(self) -> tuple[Optional[str], list]:
        """
        Загружает черновик сообщения.
        
        Returns:
            Кортеж (сообщение, теги) или (None, []) если черновика нет
        """
        try:
            if not self.draft_file.exists():
                return None, []
            
            with open(self.draft_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            message = data.get('message', '')
            tags = data.get('tags', [])
            
            if message:
                logger.debug(f"Черновик загружен: {len(message)} символов")
                return message, tags
            else:
                return None, []
        except Exception as e:
            logger.warning(f"Не удалось загрузить черновик: {e}")
            return None, []
    
    def clear_draft(self) -> None:
        """Очищает черновик."""
        try:
            if self.draft_file.exists():
                self.draft_file.unlink()
            self._draft = None
            self._tags = []
            logger.debug("Черновик очищен")
        except Exception as e:
            logger.warning(f"Не удалось очистить черновик: {e}")
    
    def has_draft(self) -> bool:
        """
        Проверяет наличие черновика.
        
        Returns:
            True если есть черновик, False иначе
        """
        return self.draft_file.exists() and self._draft is not None

