from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from desktop.core.neural_network import NeuralNetwork

class ChatWidget(QWidget):
    def __init__(self, neural_network: NeuralNetwork):
        super().__init__()
        self.neural_network = neural_network
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText('Начните диалог с нейросетью...')
        layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите ваш вопрос...')
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton('Отправить')
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return
            
        self.chat_display.append(f'<b>Вы:</b> {user_message}')
        self.input_field.clear()
        
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        
        try:
            response = self.neural_network.generate_response(user_message)
            self.chat_display.append(f'<b>Нейросеть:</b> {response}')
        except Exception as e:
            self.chat_display.append(f'<b>Ошибка:</b> {str(e)}')
        finally:
            self.send_button.setEnabled(True)
            self.input_field.setEnabled(True)
            self.input_field.setFocus()
            
    def apply_theme(self, theme, stylesheet):
        self.setStyleSheet(stylesheet)

