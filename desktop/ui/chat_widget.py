from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from desktop.core.neural_network import NeuralNetwork
from desktop.utils.chat_history import ChatHistory
import datetime

class ResponseThread(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, neural_network, user_input):
        super().__init__()
        self.neural_network = neural_network
        self.user_input = user_input
        
    def run(self):
        try:
            response = self.neural_network.generate_response(self.user_input)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ChatWidget(QWidget):
    def __init__(self, neural_network: NeuralNetwork, parent=None):
        super().__init__(parent)
        self.neural_network = neural_network
        self.chat_history = ChatHistory()
        self.response_thread = None
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_indicator)
        self.loading_dots = 0
        self.pending_tags = []
        self.init_ui()
        self.load_history()
        
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
        center_layout.addWidget(self.chat_display)
        
        # Поле ввода без рамок
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите ваш вопрос...')
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setFrame(False)
        center_layout.addWidget(self.input_field)
        
        # Контейнер для кнопок
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)
        buttons_layout.addStretch()
        buttons_container.setLayout(buttons_layout)
        
        self.loading_label = QLabel('')
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)
        buttons_layout.addWidget(self.loading_label)
        
        # Маленькие красивые кнопки
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedHeight(32)
        self.send_button.setFixedWidth(100)
        buttons_layout.addWidget(self.send_button)
        
        self.tag_button = QPushButton('Теги')
        self.tag_button.setFixedHeight(32)
        self.tag_button.setFixedWidth(70)
        self.tag_button.setCheckable(True)
        buttons_layout.addWidget(self.tag_button)
        
        buttons_layout.addStretch()
        
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
        
    def _apply_default_styles(self):
        """Применяет стили по умолчанию (светлая тема)"""
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #000000;
                border: none;
                padding: 10px;
            }
        """)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.05);
                color: #000000;
                border: none;
                border-bottom: 2px solid #0078d4;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #0078d4;
                background-color: rgba(0, 0, 0, 0.08);
            }
        """)
        self.tag_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.05);
                color: #000000;
                border: none;
                border-bottom: 2px solid #0078d4;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #0078d4;
                background-color: rgba(0, 0, 0, 0.08);
            }
        """)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.tag_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.05);
                color: #000000;
                border: 1px solid rgba(0, 0, 0, 0.2);
                border-radius: 16px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton:checked {
                background-color: #0078d4;
                color: white;
                border: 1px solid #0078d4;
            }
        """)
        self.loading_label.setStyleSheet("color: #000000;")
        
    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return
            
        if self.response_thread and self.response_thread.isRunning():
            return
            
        tags = self._current_tags()
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
        
    def show_loading_indicator(self):
        self.loading_label.setVisible(True)
        self.loading_dots = 0
        self.loading_timer.start(500)
        
    def hide_loading_indicator(self):
        self.loading_timer.stop()
        self.loading_label.setVisible(False)
        self.loading_dots = 0
        
    def update_loading_indicator(self):
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = '.' * self.loading_dots
        self.loading_label.setText(f'Нейросеть печатает{dots}')
        
    def clear_chat(self):
        self.chat_display.clear()
        self.chat_history.clear_history()
        
    def load_history(self):
        history = self.chat_history.load_history()
        for msg in history:
            if msg['role'] == 'user':
                self.pending_tags = msg.get('tags', [])
                self.add_user_message(msg['content'])
            elif msg['role'] == 'assistant':
                self.add_bot_message(msg['content'], msg.get('tags', []))
                
    def apply_theme(self, theme, stylesheet):
        self.setStyleSheet(stylesheet)
        if theme == 'dark':
            self.chat_display.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    padding: 10px;
                }
            """)
            self.input_field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border: none;
                    border-bottom: 2px solid #0078d4;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-bottom: 2px solid #0078d4;
                    background-color: rgba(255, 255, 255, 0.15);
                }
            """)
            self.tag_field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border: none;
                    border-bottom: 2px solid #0078d4;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-bottom: 2px solid #0078d4;
                    background-color: rgba(255, 255, 255, 0.15);
                }
            """)
            self.send_button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #666;
                }
            """)
            self.tag_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 16px;
                    padding: 6px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QPushButton:checked {
                    background-color: #0078d4;
                    border: 1px solid #0078d4;
                }
            """)
            self.loading_label.setStyleSheet("color: #ffffff;")
        else:
            self.chat_display.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    color: #000000;
                    border: none;
                    padding: 10px;
                }
            """)
            self.input_field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(0, 0, 0, 0.05);
                    color: #000000;
                    border: none;
                    border-bottom: 2px solid #0078d4;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-bottom: 2px solid #0078d4;
                    background-color: rgba(0, 0, 0, 0.08);
                }
            """)
            self.tag_field.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(0, 0, 0, 0.05);
                    color: #000000;
                    border: none;
                    border-bottom: 2px solid #0078d4;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-bottom: 2px solid #0078d4;
                    background-color: rgba(0, 0, 0, 0.08);
                }
            """)
            self.send_button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                    color: #666;
                }
            """)
            self.tag_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.05);
                    color: #000000;
                    border: 1px solid rgba(0, 0, 0, 0.2);
                    border-radius: 16px;
                    padding: 6px 12px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.1);
                }
                QPushButton:checked {
                    background-color: #0078d4;
                    color: white;
                    border: 1px solid #0078d4;
                }
            """)
            self.loading_label.setStyleSheet("color: #000000;")

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
