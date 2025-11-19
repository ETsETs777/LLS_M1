from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QAction, QStatusBar
from desktop.ui.chat_widget import ChatWidget
from desktop.ui.theme_manager import ThemeManager
from desktop.core.neural_network import NeuralNetwork
from desktop.config.settings import Settings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.theme_manager = ThemeManager()
        self.neural_network = NeuralNetwork()
        self.init_ui()
        self.load_window_state()
        self.apply_theme(self.settings.get_theme())
        
    def init_ui(self):
        self.setWindowTitle('Нейросеть Чат')
        self.setMinimumSize(800, 600)
        
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)
        
        self.chat_widget = ChatWidget(self.neural_network, self)
        layout.addWidget(self.chat_widget)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Файл')
        
        clear_action = QAction('Очистить чат', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.triggered.connect(self.chat_widget.clear_chat)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu('Вид')
        
        light_theme_action = QAction('Светлая тема', self)
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        view_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('Темная тема', self)
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        view_menu.addAction(dark_theme_action)
        
    def create_toolbar(self):
        toolbar = self.addToolBar('Панель инструментов')
        
        self.theme_button = QPushButton('🌙 Темная тема')
        self.theme_button.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_button)
        
        toolbar.addSeparator()
        
        clear_button = QPushButton('🗑 Очистить')
        clear_button.clicked.connect(self.chat_widget.clear_chat)
        toolbar.addWidget(clear_button)
        
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Готов')
        
    def toggle_theme(self):
        current = self.settings.get_theme()
        new_theme = 'dark' if current == 'light' else 'light'
        self.set_theme(new_theme)
        
    def set_theme(self, theme):
        self.settings.set_theme(theme)
        self.theme_manager.set_theme(theme)
        self.apply_theme(theme)
        self.theme_button.setText('☀️ Светлая тема' if theme == 'dark' else '🌙 Темная тема')
        
    def apply_theme(self, theme):
        stylesheet = self.theme_manager.get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        self.chat_widget.apply_theme(theme, stylesheet)
        
    def load_window_state(self):
        config = self.settings.config
        if 'window_geometry' in config:
            self.restoreGeometry(bytes.fromhex(config['window_geometry']))
        if 'window_state' in config:
            self.restoreState(bytes.fromhex(config['window_state']))
            
    def save_window_state(self):
        self.settings.config['window_geometry'] = self.saveGeometry().toHex().data().decode()
        self.settings.config['window_state'] = self.saveState().toHex().data().decode()
        self.settings.save_config()
        
    def closeEvent(self, event):
        self.save_window_state()
        event.accept()
