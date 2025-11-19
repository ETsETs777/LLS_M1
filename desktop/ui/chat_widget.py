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
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText('Начните диалог с нейросетью...')
        self.chat_display.setAcceptRichText(True)
        layout.addWidget(self.chat_display)
        
        input_container = QWidget()
        input_layout = QVBoxLayout()
        input_container.setLayout(input_layout)
        
        self.loading_label = QLabel('')
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setVisible(False)
        input_layout.addWidget(self.loading_label)
        
        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите ваш вопрос...')
        self.input_field.returnPressed.connect(self.send_message)
        input_row.addWidget(self.input_field)
        
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMinimumWidth(100)
        input_row.addWidget(self.send_button)
        
        input_layout.addLayout(input_row)
        layout.addWidget(input_container)
        
    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return
            
        if self.response_thread and self.response_thread.isRunning():
            return
            
        self.add_user_message(user_message)
        self.chat_history.add_message('user', user_message)
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
        self.add_bot_message(response)
        self.chat_history.add_message('assistant', response)
        self.chat_history.save_history()
        
    def on_error_occurred(self, error_msg):
        self.hide_loading_indicator()
        self.add_error_message(error_msg)
        
    def on_thread_finished(self):
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        
    def add_user_message(self, message):
        timestamp = datetime.datetime.now().strftime('%H:%M')
        formatted = f'<div style="margin: 10px 0;"><b style="color: #0078d4;">Вы</b> <span style="color: #666; font-size: 0.9em;">({timestamp})</span><br><div style="background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 5px;">{self.escape_html(message)}</div></div>'
        self.chat_display.append(formatted)
        self.scroll_to_bottom()
        
    def add_bot_message(self, message):
        timestamp = datetime.datetime.now().strftime('%H:%M')
        formatted = f'<div style="margin: 10px 0;"><b style="color: #28a745;">Нейросеть</b> <span style="color: #666; font-size: 0.9em;">({timestamp})</span><br><div style="background-color: #f5f5f5; padding: 10px; border-radius: 8px; margin-top: 5px;">{self.escape_html(message)}</div></div>'
        self.chat_display.append(formatted)
        self.scroll_to_bottom()
        
    def add_error_message(self, error_msg):
        timestamp = datetime.datetime.now().strftime('%H:%M')
        formatted = f'<div style="margin: 10px 0;"><b style="color: #dc3545;">Ошибка</b> <span style="color: #666; font-size: 0.9em;">({timestamp})</span><br><div style="background-color: #ffebee; padding: 10px; border-radius: 8px; margin-top: 5px; color: #c62828;">{self.escape_html(error_msg)}</div></div>'
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
                self.add_user_message(msg['content'])
            elif msg['role'] == 'assistant':
                self.add_bot_message(msg['content'])
                
    def apply_theme(self, theme, stylesheet):
        self.setStyleSheet(stylesheet)
        if theme == 'dark':
            self.chat_display.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            self.loading_label.setStyleSheet("color: #ffffff;")
        else:
            self.chat_display.setStyleSheet("""
                QTextEdit {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            self.loading_label.setStyleSheet("color: #000000;")
