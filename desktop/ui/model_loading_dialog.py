import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from typing import Optional

from desktop.utils.logger import get_logger

logger = get_logger('desktop.ui.model_loading_dialog')


class ModelLoadingThread(QThread):
    """Поток для загрузки модели с сигналами прогресса"""
    progress_signal = pyqtSignal(str)  # Сообщение о прогрессе
    error_signal = pyqtSignal(str)  # Ошибка
    finished_signal = pyqtSignal(bool, str)  # Успех/неудача, сообщение
    
    def __init__(self, model_manager):
        super().__init__()
        self.model_manager = model_manager
        self.is_cancelled = False
    
    def run(self):
        try:
            # Проверяем доступность библиотек
            self.progress_signal.emit("Проверка доступности библиотек...")
            import sys
            import importlib
            
            # Пытаемся импортировать torch
            try:
                import torch
                self.progress_signal.emit(f"[OK] PyTorch {torch.__version__} доступен")
            except Exception as e:
                error_msg = f"PyTorch недоступен: {str(e)}"
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False, error_msg)
                return
            
            # Пытаемся импортировать transformers
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                self.progress_signal.emit("[OK] Transformers библиотека доступна")
            except Exception as e:
                error_msg = f"Transformers недоступен: {str(e)}"
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False, error_msg)
                return
            
            resolved_path = os.path.abspath(self.model_manager.model_path)
            self.progress_signal.emit(f"Путь к модели: {resolved_path}")
            
            # Шаг 1: Загрузка токенизатора
            self.progress_signal.emit("Шаг 1/2: Загрузка токенизатора...")
            import time
            start_time = time.time()
            
            try:
                import torch
                from transformers import AutoTokenizer
                
                self.progress_signal.emit(f"Импорт библиотек завершен")
                self.model_manager.tokenizer = AutoTokenizer.from_pretrained(
                    resolved_path, 
                    trust_remote_code=True
                )
                if self.model_manager.tokenizer.pad_token is None:
                    self.model_manager.tokenizer.pad_token = self.model_manager.tokenizer.eos_token
                
                elapsed = time.time() - start_time
                self.progress_signal.emit(f"[OK] Токенизатор загружен ({elapsed:.1f} сек)")
            except Exception as e:
                error_msg = f"Ошибка загрузки токенизатора: {str(e)}"
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False, error_msg)
                return
            
            # Шаг 2: Загрузка модели
            self.progress_signal.emit("Шаг 2/2: Загрузка модели в память...")
            self.progress_signal.emit("ВНИМАНИЕ: Это может занять 10-30 минут!")
            self.progress_signal.emit("Пожалуйста, не закрывайте приложение...")
            
            import psutil
            import torch
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            self.progress_signal.emit(f"Доступная память: {available_memory_gb:.2f} GB")
            
            try:
                from transformers import AutoModelForCausalLM
                
                self.progress_signal.emit("Начало загрузки весов модели...")
                model_start = time.time()
                
                model = AutoModelForCausalLM.from_pretrained(
                    resolved_path,
                    trust_remote_code=True,
                    dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
                
                model = model.to('cpu')
                model.eval()
                
                self.model_manager.model = model
                self.model_manager.device = torch.device('cpu')
                self.model_manager.is_fallback = False
                
                elapsed = time.time() - model_start
                total_time = time.time() - start_time
                
                self.progress_signal.emit(f"[OK] Модель загружена успешно!")
                self.progress_signal.emit(f"Время загрузки модели: {elapsed/60:.1f} минут")
                self.progress_signal.emit(f"Общее время: {total_time/60:.1f} минут")
                
                self.finished_signal.emit(True, "Модель успешно загружена!")
                
            except Exception as e:
                error_msg = f"Ошибка загрузки модели: {str(e)}"
                self.error_signal.emit(error_msg)
                self.finished_signal.emit(False, error_msg)
                
        except Exception as e:
            error_msg = f"Критическая ошибка: {str(e)}"
            self.error_signal.emit(error_msg)
            self.finished_signal.emit(False, error_msg)


class ModelLoadingDialog(QDialog):
    """Диалог загрузки модели с отображением прогресса"""
    
    def __init__(self, model_manager, parent=None):
        super().__init__(parent)
        self.model_manager = model_manager
        self.loading_thread: Optional[ModelLoadingThread] = None
        self.setWindowTitle("Загрузка нейросети")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Заголовок
        title = QLabel("Загрузка нейросети GigaChat-20B-A3B-instruct")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Информация
        info = QLabel(
            "Модель очень большая (~82GB на диске, ~40GB в памяти).\n"
            "Загрузка может занять 10-30 минут в зависимости от вашей системы.\n"
            "Пожалуйста, подождите..."
        )
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Прогресс-бар (неопределенный)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
        self.progress_bar.setMinimumHeight(30)
        layout.addWidget(self.progress_bar)
        
        # Лог загрузки
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10pt;")
        layout.addWidget(self.log_text)
        
        # Кнопка отмены (будет показана если нужно)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel_loading)
        self.cancel_button.setEnabled(False)  # Пока не поддерживаем отмену
        layout.addWidget(self.cancel_button)
        
        # Старт загрузки
        self.start_loading()
    
    def start_loading(self):
        """Начинает загрузку модели в отдельном потоке"""
        self.add_log("Инициализация загрузки модели...")
        self.loading_thread = ModelLoadingThread(self.model_manager)
        self.loading_thread.progress_signal.connect(self.add_log)
        self.loading_thread.error_signal.connect(self.add_error)
        self.loading_thread.finished_signal.connect(self.loading_finished)
        self.loading_thread.start()
    
    def add_log(self, message: str):
        """Добавляет сообщение в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Автопрокрутка вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        logger.info(f"Loading progress: {message}")
    
    def add_error(self, error: str):
        """Добавляет ошибку в лог"""
        self.add_log(f"ОШИБКА: {error}")
    
    def loading_finished(self, success: bool, message: str):
        """Обработка завершения загрузки"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if success:
            self.add_log("=" * 60)
            self.add_log("МОДЕЛЬ УСПЕШНО ЗАГРУЖЕНА!")
            self.add_log("=" * 60)
            self.add_log("Закрытие окна загрузки...")
            QTimer.singleShot(2000, self.accept)  # Закрыть через 2 секунды
        else:
            self.add_log("=" * 60)
            self.add_log(f"ОШИБКА ЗАГРУЗКИ: {message}")
            self.add_log("=" * 60)
            self.add_log("Приложение будет работать в режиме без модели")
            self.cancel_button.setText("Продолжить без модели")
            self.cancel_button.setEnabled(True)
            self.cancel_button.clicked.disconnect()
            self.cancel_button.clicked.connect(self.accept)
    
    def cancel_loading(self):
        """Отмена загрузки"""
        if self.loading_thread and self.loading_thread.isRunning():
            self.loading_thread.is_cancelled = True
            self.loading_thread.wait(1000)
        self.reject()
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.loading_thread and self.loading_thread.isRunning():
            event.ignore()  # Не позволяем закрыть во время загрузки
            self.add_log("Пожалуйста, дождитесь завершения загрузки...")
        else:
            event.accept()

