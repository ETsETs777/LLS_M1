"""
Виджет чата для взаимодействия с нейросетью.
Обеспечивает интерфейс для отправки сообщений и отображения ответов.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, 
    QHBoxLayout, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QIcon
import os
from typing import Optional, List
import datetime

from desktop.core.neural_network import NeuralNetwork
from desktop.utils.chat_history import ChatHistory
from desktop.utils.logger import get_logger
from desktop.utils.constants import (
    MAX_MESSAGE_LENGTH, MAX_TAG_LENGTH, MAX_TAGS_COUNT,
    LOADING_INDICATOR_INTERVAL, ICON_BUTTON_SIZE,
    SEND_BUTTON_WIDTH, SEND_BUTTON_HEIGHT,
    TAG_BUTTON_WIDTH, TAG_BUTTON_HEIGHT,
    COLOR_ACCENT, COLOR_SUCCESS, COLOR_ERROR, COLOR_ERROR_DARK,
    COLOR_TEXT_SECONDARY, FONT_SIZE_NORMAL, FONT_SIZE_SMALL,
    MAX_HISTORY_ITEMS_PREVIEW
)
from desktop.ui.styles import (
    get_chat_display_style, get_input_field_style,
    get_send_button_style, get_tag_button_style,
    get_icon_button_style, get_loading_label_style
)

logger = get_logger('desktop.ui.chat_widget')

class ResponseThread(QThread):
    """
    Поток для генерации ответа нейросети.
    
    Выполняет генерацию в отдельном потоке, чтобы не блокировать UI.
    """
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, neural_network: NeuralNetwork, user_input: str):
        """
        Инициализирует поток генерации.
        
        Args:
            neural_network: Экземпляр нейросети
            user_input: Входное сообщение пользователя
        """
        super().__init__()
        self.neural_network = neural_network
        self.user_input = user_input
        self._is_cancelled = False
        
    def cancel(self) -> None:
        """Отменяет выполнение генерации."""
        self._is_cancelled = True
        logger.debug("Генерация ответа отменена")
        
    def run(self) -> None:
        """Выполняет генерацию ответа в отдельном потоке."""
        if self._is_cancelled:
            return
            
        try:
            logger.debug(f"Начало генерации ответа для сообщения длиной {len(self.user_input)}")
            response = self.neural_network.generate_response(self.user_input)
            if not self._is_cancelled:
                self.response_ready.emit(response)
                logger.debug(f"Ответ успешно сгенерирован, длина: {len(response)}")
        except Exception as e:
            logger.exception(f"Ошибка при генерации ответа: {e}")
            if not self._is_cancelled:
                self.error_occurred.emit(str(e))

class ChatWidget(QWidget):
    """
    Виджет чата для взаимодействия с нейросетью.
    
    Предоставляет интерфейс для отправки сообщений, отображения истории
    и управления тегами.
    """
    
    def __init__(self, neural_network: NeuralNetwork, parent: Optional[QWidget] = None):
        """
        Инициализирует виджет чата.
        
        Args:
            neural_network: Экземпляр нейросети для генерации ответов
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.neural_network = neural_network
        self.chat_history = ChatHistory()
        self.response_thread: Optional[ResponseThread] = None
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_indicator)
        self.loading_dots = 0
        self.pending_tags: List[str] = []
        self.init_ui()
        self.load_history()
        logger.debug("ChatWidget инициализирован")
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Центральный контейнер для чата и ввода
        center_container = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(50, 20, 50, 20)
        center_layout.setSpacing(15)
        center_container.setLayout(center_layout)
        
        # Добавляем растяжку сверху для центрирования
        main_layout.addStretch()
        
        # Область чата без рамок
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText('Начните диалог с нейросетью...')
        self.chat_display.setAcceptRichText(True)
        self.chat_display.setFrameShape(QTextEdit.NoFrame)
        # Скрываем скроллбары, прокрутка только колесиком мыши
        self.chat_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        center_layout.addWidget(self.chat_display)
        
        # Поле ввода без рамок
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите ваш вопрос...')
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setFrame(False)
        center_layout.addWidget(self.input_field)
        
        # Контейнер для кнопок и иконок
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)
        buttons_container.setLayout(buttons_layout)
        
        # Получаем путь к иконкам
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui', 'images')
        
        # Добавляем иконки слева
        self.theme_button = QPushButton()
        self.theme_button.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
        self.theme_button.setToolTip('Переключить тему')
        icon_path = os.path.join(icons_dir, 'theme.png')
        if os.path.exists(icon_path):
            self.theme_button.setIcon(QIcon(icon_path))
            self.theme_button.setIconSize(self.theme_button.size())
        buttons_layout.addWidget(self.theme_button)
        
        self.clear_button = QPushButton()
        self.clear_button.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
        self.clear_button.setToolTip('Очистить чат')
        icon_path = os.path.join(icons_dir, 'clear.png')
        if os.path.exists(icon_path):
            self.clear_button.setIcon(QIcon(icon_path))
            self.clear_button.setIconSize(self.clear_button.size())
        buttons_layout.addWidget(self.clear_button)
        
        self.history_button = QPushButton()
        self.history_button.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
        self.history_button.setToolTip('История')
        icon_path = os.path.join(icons_dir, 'history.png')
        if os.path.exists(icon_path):
            self.history_button.setIcon(QIcon(icon_path))
            self.history_button.setIconSize(self.history_button.size())
        buttons_layout.addWidget(self.history_button)
        
        self.statistics_button = QPushButton()
        self.statistics_button.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
        self.statistics_button.setToolTip('Статистика')
        icon_path = os.path.join(icons_dir, 'monitor.png')
        if os.path.exists(icon_path):
            self.statistics_button.setIcon(QIcon(icon_path))
            self.statistics_button.setIconSize(self.statistics_button.size())
        buttons_layout.addWidget(self.statistics_button)
        
        self.actions_button = QPushButton()
        self.actions_button.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
        self.actions_button.setToolTip('Действия')
        icon_path = os.path.join(icons_dir, 'actions.png')
        if os.path.exists(icon_path):
            self.actions_button.setIcon(QIcon(icon_path))
            self.actions_button.setIconSize(self.actions_button.size())
        buttons_layout.addWidget(self.actions_button)
        
        self.loading_label = QLabel('')
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)
        buttons_layout.addWidget(self.loading_label)
        
        buttons_layout.addStretch()
        
        # Маленькие красивые кнопки справа
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedHeight(SEND_BUTTON_HEIGHT)
        self.send_button.setFixedWidth(SEND_BUTTON_WIDTH)
        buttons_layout.addWidget(self.send_button)
        
        self.tag_button = QPushButton('Теги')
        self.tag_button.setFixedHeight(TAG_BUTTON_HEIGHT)
        self.tag_button.setFixedWidth(TAG_BUTTON_WIDTH)
        self.tag_button.setCheckable(True)
        buttons_layout.addWidget(self.tag_button)
        
        center_layout.addWidget(buttons_container)
        
        # Скрытое поле для тегов
        self.tag_field = QLineEdit()
        self.tag_field.setPlaceholderText('Теги (через запятую)')
        self.tag_field.setFrame(False)
        self.tag_field.setVisible(False)
        center_layout.addWidget(self.tag_field)
        
        # Подключаем переключение видимости поля тегов
        self.tag_button.toggled.connect(self.tag_field.setVisible)
        
        main_layout.addWidget(center_container)
        main_layout.addStretch()
        
        # Применяем стили по умолчанию
        self._apply_default_styles()
        
        # Применяем стили к иконкам
        icon_button_style = get_icon_button_style()
        self.theme_button.setStyleSheet(icon_button_style)
        self.clear_button.setStyleSheet(icon_button_style)
        self.history_button.setStyleSheet(icon_button_style)
        self.statistics_button.setStyleSheet(icon_button_style)
        self.actions_button.setStyleSheet(icon_button_style)
        
    def _apply_default_styles(self) -> None:
        """Применяет стили по умолчанию (светлая тема)"""
        theme = 'light'
        self.chat_display.setStyleSheet(get_chat_display_style(theme))
        self.input_field.setStyleSheet(get_input_field_style(theme))
        self.tag_field.setStyleSheet(get_input_field_style(theme))
        self.send_button.setStyleSheet(get_send_button_style(theme))
        self.tag_button.setStyleSheet(get_tag_button_style(theme))
        self.loading_label.setStyleSheet(get_loading_label_style(theme))
        
    def send_message(self) -> None:
        """
        Отправляет сообщение пользователя и запускает генерацию ответа.
        
        Выполняет валидацию ввода перед отправкой.
        """
        user_message = self.input_field.text().strip()
        
        # Валидация ввода
        if not user_message:
            return
        
        validation_error = self._validate_message(user_message)
        if validation_error:
            QMessageBox.warning(self, 'Ошибка валидации', validation_error)
            return
            
        if self.response_thread and self.response_thread.isRunning():
            logger.warning("Попытка отправить сообщение во время генерации ответа")
            QMessageBox.information(self, 'Ожидание', 'Пожалуйста, дождитесь завершения генерации ответа.')
            return
            
        tags = self._current_tags()
        validation_tags_error = self._validate_tags(tags)
        if validation_tags_error:
            QMessageBox.warning(self, 'Ошибка валидации тегов', validation_tags_error)
            return
            
        self.pending_tags = tags
        self.add_user_message(user_message)
        self.chat_history.add_message('user', user_message, tags=tags)
        self.input_field.clear()
        
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        self.show_loading_indicator()
        
        self.response_thread = ResponseThread(self.neural_network, user_message)
        self.response_thread.response_ready.connect(self.on_response_received)
        self.response_thread.error_occurred.connect(self.on_error_occurred)
        self.response_thread.finished.connect(self.on_thread_finished)
        self.response_thread.start()
        logger.info(f"Отправлено сообщение длиной {len(user_message)} символов")
    
    def _validate_message(self, message: str) -> Optional[str]:
        """
        Валидирует сообщение пользователя.
        
        Args:
            message: Текст сообщения
        
        Returns:
            Сообщение об ошибке или None если валидация прошла
        """
        if len(message) > MAX_MESSAGE_LENGTH:
            return f'Сообщение слишком длинное. Максимальная длина: {MAX_MESSAGE_LENGTH} символов.'
        
        # Проверка на потенциально опасные паттерны
        if '..' in message or message.startswith('/'):
            # Базовая защита от path traversal и команд
            logger.warning(f"Обнаружен потенциально опасный паттерн в сообщении")
        
        return None
    
    def _validate_tags(self, tags: List[str]) -> Optional[str]:
        """
        Валидирует теги.
        
        Args:
            tags: Список тегов
        
        Returns:
            Сообщение об ошибке или None если валидация прошла
        """
        if len(tags) > MAX_TAGS_COUNT:
            return f'Слишком много тегов. Максимум: {MAX_TAGS_COUNT} тегов.'
        
        for tag in tags:
            if len(tag) > MAX_TAG_LENGTH:
                return f'Тег "{tag}" слишком длинный. Максимальная длина: {MAX_TAG_LENGTH} символов.'
            if not tag.strip():
                return 'Теги не могут быть пустыми.'
        
        return None
        
    def on_response_received(self, response):
        self.hide_loading_indicator()
        self.add_bot_message(response, self.pending_tags)
        self.chat_history.add_message('assistant', response, tags=self.pending_tags)
        self.chat_history.save_history()
        
    def on_error_occurred(self, error_msg):
        self.hide_loading_indicator()
        self.add_error_message(error_msg, self.pending_tags)
        
    def on_thread_finished(self):
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        
    def add_user_message(self, message):
        timestamp = datetime.datetime.now().strftime('%H:%M')
        tags_html = self._format_tags(self.pending_tags)
        formatted = f'<div style="margin: 15px 0; padding: 0;"><b style="color: #0078d4; font-size: 14px;">Вы</b> <span style="color: #999; font-size: 12px;">({timestamp})</span>{tags_html}<br><div style="padding: 8px 0; margin-top: 5px; color: #333; line-height: 1.6;">{self.escape_html(message)}</div></div>'
        self.chat_display.append(formatted)
        self.scroll_to_bottom()
        
    def add_bot_message(self, message, tags=None):
        timestamp = datetime.datetime.now().strftime('%H:%M')
        tags_html = self._format_tags(tags)
        formatted = f'<div style="margin: 15px 0; padding: 0;"><b style="color: #28a745; font-size: 14px;">Нейросеть</b> <span style="color: #999; font-size: 12px;">({timestamp})</span>{tags_html}<br><div style="padding: 8px 0; margin-top: 5px; color: #333; line-height: 1.6;">{self.escape_html(message)}</div></div>'
        self.chat_display.append(formatted)
        self.scroll_to_bottom()
        
    def add_error_message(self, error_msg, tags=None):
        timestamp = datetime.datetime.now().strftime('%H:%M')
        tags_html = self._format_tags(tags)
        formatted = f'<div style="margin: 15px 0; padding: 0;"><b style="color: #dc3545; font-size: 14px;">Ошибка</b> <span style="color: #999; font-size: 12px;">({timestamp})</span>{tags_html}<br><div style="padding: 8px 0; margin-top: 5px; color: #c62828; line-height: 1.6;">{self.escape_html(error_msg)}</div></div>'
        self.chat_display.append(formatted)
        self.scroll_to_bottom()
        
    def escape_html(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
    def scroll_to_bottom(self):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
        
    def show_loading_indicator(self) -> None:
        """Показывает индикатор загрузки."""
        self.loading_label.setVisible(True)
        self.loading_dots = 0
        self.loading_timer.start(LOADING_INDICATOR_INTERVAL)
        
    def hide_loading_indicator(self):
        self.loading_timer.stop()
        self.loading_label.setVisible(False)
        self.loading_dots = 0
        
    def update_loading_indicator(self):
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = '.' * self.loading_dots
        self.loading_label.setText(f'Нейросеть печатает{dots}')
        
    def clear_chat(self) -> None:
        """Очищает чат и историю."""
        logger.info("Очистка чата")
        self.chat_display.clear()
        self.chat_history.clear_history()
    
    def cleanup(self) -> None:
        """
        Очищает ресурсы виджета.
        
        Останавливает активные потоки и таймеры.
        """
        logger.debug("Очистка ресурсов ChatWidget")
        
        # Останавливаем таймер
        if self.loading_timer.isActive():
            self.loading_timer.stop()
        
        # Останавливаем поток генерации, если он активен
        if self.response_thread and self.response_thread.isRunning():
            logger.info("Остановка активного потока генерации")
            self.response_thread.cancel()
            self.response_thread.wait(3000)  # Ждем до 3 секунд
            if self.response_thread.isRunning():
                logger.warning("Поток не завершился, принудительное завершение")
                self.response_thread.terminate()
                self.response_thread.wait(1000)
        
        self.response_thread = None
        
    def load_history(self):
        history = self.chat_history.load_history()
        for msg in history:
            if msg['role'] == 'user':
                self.pending_tags = msg.get('tags', [])
                self.add_user_message(msg['content'])
            elif msg['role'] == 'assistant':
                self.add_bot_message(msg['content'], msg.get('tags', []))
                
    def apply_theme(self, theme: str, stylesheet: str) -> None:
        """
        Применяет тему к виджету.
        
        Args:
            theme: Название темы ('light' или 'dark')
            stylesheet: Общий stylesheet для родительского виджета
        """
        self.setStyleSheet(stylesheet)
        self.chat_display.setStyleSheet(get_chat_display_style(theme))
        self.input_field.setStyleSheet(get_input_field_style(theme))
        self.tag_field.setStyleSheet(get_input_field_style(theme))
        self.send_button.setStyleSheet(get_send_button_style(theme))
        self.tag_button.setStyleSheet(get_tag_button_style(theme))
        self.loading_label.setStyleSheet(get_loading_label_style(theme))

    def _current_tags(self):
        raw = self.tag_field.text().strip()
        if not raw:
            return []
        return [tag.strip() for tag in raw.split(',') if tag.strip()]

    def _format_tags(self, tags):
        if not tags:
            return ''
        tags_str = ' '.join(f'#{self.escape_html(tag)}' for tag in tags)
        return f' <span style="color:#999; font-size:0.85em;">{tags_str}</span>'
