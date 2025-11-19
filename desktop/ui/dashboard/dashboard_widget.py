from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
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
        for label in ('Открыть историю', 'Создать бэкап', 'Настройки'):
            btn = QPushButton(label)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            actions_layout.addWidget(btn)
        grid.addWidget(self.actions_container, 2, 0, 1, 2)

    def update_card(self, key: str, value: str, subtitle: str = ''):
        if key in self.cards:
            self.cards[key].update_value(value, subtitle)

