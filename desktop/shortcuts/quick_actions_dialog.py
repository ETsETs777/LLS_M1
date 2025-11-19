from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QHBoxLayout
)

from desktop.shortcuts.actions import QuickActionsManager, QuickAction


class QuickActionsDialog(QDialog):
    def __init__(self, manager: QuickActionsManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle('Быстрые действия')
        self.resize(420, 360)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        for action in self.manager.list_actions():
            container_layout.addLayout(self._build_action_row(action))

        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _build_action_row(self, action: QuickAction):
        row = QHBoxLayout()
        info = QLabel(f"<b>{action.label}</b><br><span style='color:#666;'>{action.description}</span>")
        info.setWordWrap(True)
        button = QPushButton('▶')
        button.setFixedWidth(40)
        button.clicked.connect(action.handler)
        row.addWidget(info)
        row.addWidget(button)
        return row

