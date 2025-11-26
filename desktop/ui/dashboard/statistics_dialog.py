from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from typing import Dict, List
from desktop.ui.dashboard.dashboard_widget import DashboardWidget


class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Статистика')
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        title_label = QLabel('Статистика приложения')
        title_label.setStyleSheet('font-size: 20px; font-weight: bold; margin-bottom: 10px;')
        layout.addWidget(title_label)
        
        self.dashboard = DashboardWidget(self)
        layout.addWidget(self.dashboard)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton('Закрыть')
        close_button.setFixedHeight(36)
        close_button.setFixedWidth(100)
        close_button.setStyleSheet('font-size: 14px;')
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
    def update_statistics(self, sessions: str, messages: str, plugins: str, training: str, 
                         sessions_subtitle: str = '', messages_subtitle: str = '', 
                         analytics_lines: List[str] = None):
        
        self.dashboard.update_card('sessions', sessions, sessions_subtitle)
        self.dashboard.update_card('messages', messages, messages_subtitle)
        self.dashboard.update_card('active_plugins', plugins)
        self.dashboard.update_card('training', training)
        if analytics_lines:
            self.dashboard.update_analytics(analytics_lines)
        else:
            self.dashboard.update_analytics([])

