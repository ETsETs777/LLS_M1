"""
Тесты для валидаторов.
"""
import unittest
import tempfile
import os

from desktop.utils.validators import (
    validate_path, validate_message_length, sanitize_input, ValidationError
)


class TestValidators(unittest.TestCase):
    """Тесты для валидаторов."""
    
    def test_validate_path_empty(self):
        """Тест валидации пустого пути."""
        result = validate_path("")
        self.assertIsNotNone(result)
        self.assertIn("пустым", result.lower())
    
    def test_validate_path_traversal(self):
        """Тест защиты от path traversal."""
        result = validate_path("../../../etc/passwd")
        self.assertIsNotNone(result)
        self.assertIn("недопустимые", result.lower())
    
    def test_validate_message_length(self):
        """Тест валидации длины сообщения."""
        long_message = "a" * 10001
        result = validate_message_length(long_message, 10000)
        self.assertIsNotNone(result)
        self.assertIn("длинное", result.lower())
    
    def test_validate_message_length_ok(self):
        """Тест валидации нормального сообщения."""
        normal_message = "Hello, world!"
        result = validate_message_length(normal_message, 10000)
        self.assertIsNone(result)
    
    def test_sanitize_input(self):
        """Тест очистки ввода."""
        dirty_input = "Hello\x00\x01World"
        cleaned = sanitize_input(dirty_input)
        self.assertNotIn("\x00", cleaned)
        self.assertNotIn("\x01", cleaned)
        self.assertIn("Hello", cleaned)
        self.assertIn("World", cleaned)


if __name__ == '__main__':
    unittest.main()


