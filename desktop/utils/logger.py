import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class AppLogger:
    _instance: Optional['AppLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            AppLogger._initialized = True
    
    def _setup_logging(self):
        base_dir = Path(__file__).parent.parent.parent
        log_dir = base_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger('LLS_M1')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        log_file = log_dir / 'app.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        error_file = log_dir / 'errors.log'
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        if name:
            return self.logger.getChild(name)
        return self.logger


def get_logger(name: str = None) -> logging.Logger:
    app_logger = AppLogger()
    return app_logger.get_logger(name)

