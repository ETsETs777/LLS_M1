from typing import Callable, Dict, List

from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QMenu
from PyQt5.QtCore import Qt


class InfoCard(QWidget):
    def __init__(self, title: str, value: str, subtitle: str = ''):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)
        self.setLayout(layout)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet('font-size:12px; color:#777; text-transform:uppercase;')
        value_layout = QHBoxLayout()
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet('font-size:22px; font-weight:bold;')
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet('color:#888;')
        value_layout.addWidget(self.value_label)
        value_layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addLayout(value_layout)
        layout.addWidget(self.subtitle_label)
        self.setStyleSheet('QWidget { border: 1px solid #e1e1e1; border-radius: 10px; background: #ffffff; }')

    def update_value(self, value: str, subtitle: str = ''):
        self.value_label.setText(value)
        self.subtitle_label.setText(subtitle)


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid)
        self.cards = {}
        self.cards['sessions'] = InfoCard('Сессий за сегодня', '0')
        self.cards['messages'] = InfoCard('Сообщений', '0')
        self.cards['active_plugins'] = InfoCard('Активных плагинов', '0')
        self.cards['training'] = InfoCard('Статус обучения', 'Нет данных')
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for card, pos in zip(self.cards.values(), positions):
            grid.addWidget(card, *pos)
        self.actions_container = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        self.actions_container.setLayout(actions_layout)
        
        # Создаем одну объединенную кнопку с меню
        self.unified_button = QPushButton('⚙️ Действия')
        self.unified_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.unified_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        # Создаем меню для кнопки
        self.actions_menu = QMenu(self)
        
        # Создаем действия для меню
        self.menu_actions = {}
        for key, label in (
            ('history', '📚 Открыть историю'),
            ('backup', '💾 Создать бэкап'),
            ('monitor', '📊 Мониторинг')
        ):
            action = self.actions_menu.addAction(label)
            self.menu_actions[key] = action
        
        self.unified_button.setMenu(self.actions_menu)
        actions_layout.addWidget(self.unified_button)
        
        grid.addWidget(self.actions_container, 2, 0, 1, 2)

        self.analytics_box = QWidget()
        analytics_layout = QVBoxLayout()
        analytics_layout.setContentsMargins(12, 12, 12, 12)
        analytics_layout.setSpacing(4)
        self.analytics_box.setLayout(analytics_layout)
        title = QLabel('Аналитика диалогов')
        title.setStyleSheet('font-size:13px; font-weight:bold;')
        self.analytics_label = QLabel('Нет данных по аналитике.')
        self.analytics_label.setWordWrap(True)
        self.analytics_label.setStyleSheet('color:#555;')
        analytics_layout.addWidget(title)
        analytics_layout.addWidget(self.analytics_label)
        self.analytics_box.setStyleSheet('QWidget { border: 1px solid #e1e1e1; border-radius: 10px; background: #f9fafb; }')
        grid.addWidget(self.analytics_box, 3, 0, 1, 2)

    def update_card(self, key: str, value: str, subtitle: str = ''):
        if key in self.cards:
            self.cards[key].update_value(value, subtitle)

    def update_analytics(self, lines: List[str]):
        if not lines:
            self.analytics_label.setText('Нет данных по аналитике.')
        else:
            self.analytics_label.setText('\n'.join(lines))

    def set_action_handler(self, key: str, label: str, handler: Callable[[], None]):
        action = self.menu_actions.get(key)
        if not action:
            return
        action.setText(label)
        try:
            action.triggered.disconnect()
        except Exception:
            pass
        action.triggered.connect(handler)

