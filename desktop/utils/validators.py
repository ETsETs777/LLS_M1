"""
Валидаторы для проверки пользовательского ввода и данных.
"""
import os
from typing import Optional
from pathlib import Path

from desktop.utils.constants import MAX_PATH_DEPTH
from desktop.utils.logger import get_logger

logger = get_logger('desktop.utils.validators')


class ValidationError(Exception):
    """Исключение для ошибок валидации."""
    pass


def validate_path(path: str, must_exist: bool = False) -> Optional[str]:
    """
    Валидирует путь к файлу или директории.
    
    Args:
        path: Путь для валидации
        must_exist: Должен ли путь существовать
    
    Returns:
        Сообщение об ошибке или None если валидация прошла
    
    Raises:
        ValidationError: При критических ошибках валидации
    """
    if not path:
        return "Путь не может быть пустым"
    
    try:
        # Нормализуем путь
        normalized = os.path.normpath(path)
        
        # Проверка на path traversal
        parts = Path(normalized).parts
        if len(parts) > MAX_PATH_DEPTH:
            logger.warning(f"Подозрительно глубокий путь: {normalized}")
            return f"Путь слишком глубокий (максимум {MAX_PATH_DEPTH} уровней)"
        
        # Проверка на наличие '..' в пути
        if '..' in parts:
            logger.warning(f"Обнаружен path traversal в пути: {normalized}")
            return "Путь содержит недопустимые символы"
        
        # Проверка существования, если требуется
        if must_exist and not os.path.exists(normalized):
            return f"Путь не существует: {normalized}"
        
        return None
    except Exception as e:
        logger.exception(f"Ошибка при валидации пути: {e}")
        return f"Ошибка валидации пути: {str(e)}"


def validate_message_length(message: str, max_length: int) -> Optional[str]:
    """
    Валидирует длину сообщения.
    
    Args:
        message: Текст сообщения
        max_length: Максимальная допустимая длина
    
    Returns:
        Сообщение об ошибке или None если валидация прошла
    """
    if len(message) > max_length:
        return f"Сообщение слишком длинное. Максимальная длина: {max_length} символов."
    return None


def sanitize_input(text: str) -> str:
    """
    Очищает пользовательский ввод от потенциально опасных символов.
    
    Args:
        text: Входной текст
    
    Returns:
        Очищенный текст
    """
    # Базовая санитизация - удаляем управляющие символы
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    return sanitized

