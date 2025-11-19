from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from desktop.ui.chat_widget import ChatWidget
from desktop.ui.theme_manager import ThemeManager
from desktop.core.neural_network import NeuralNetwork

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.neural_network = NeuralNetwork()
        self.init_ui()
        self.apply_theme(self.theme_manager.current_theme)
        
    def init_ui(self):
        self.setWindowTitle('Нейросеть Чат')
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        header_layout = QHBoxLayout()
        self.theme_button = QPushButton('Темная тема')
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        self.chat_widget = ChatWidget(self.neural_network)
        layout.addWidget(self.chat_widget)
        
    def toggle_theme(self):
        new_theme = 'dark' if self.theme_manager.current_theme == 'light' else 'light'
        self.theme_manager.set_theme(new_theme)
        self.apply_theme(new_theme)
        self.theme_button.setText('Светлая тема' if new_theme == 'dark' else 'Темная тема')
        
    def apply_theme(self, theme):
        stylesheet = self.theme_manager.get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        self.chat_widget.apply_theme(theme, stylesheet)

