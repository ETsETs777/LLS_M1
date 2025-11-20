from typing import List

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QMessageBox
)
from PyQt5.QtCore import Qt

from desktop.shortcuts.actions import QuickActionsManager, QuickAction


class QuickActionsDialog(QDialog):
    def __init__(self, manager: QuickActionsManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle('Быстрые действия')
        self.resize(460, 420)
        self.search_text = ''
        self._init_ui()
        self._refresh_actions()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('Поиск действия...')
        self.search_field.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_field)

        self.param_field = QLineEdit()
        self.param_field.setPlaceholderText('Параметр (для действий, требующих ввода)')
        layout.addWidget(self.param_field)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.actions_container = QWidget()
        self.actions_layout = QVBoxLayout()
        self.actions_container.setLayout(self.actions_layout)
        self.scroll.setWidget(self.actions_container)
        layout.addWidget(self.scroll)

        self.status_label = QLabel('')
        self.status_label.setStyleSheet('color: gray; font-size: 11px;')
        layout.addWidget(self.status_label)

    def _on_search_changed(self, text: str):
        self.search_text = text.strip().lower()
        self._refresh_actions()

    def _refresh_actions(self):
        while self.actions_layout.count():
            child = self.actions_layout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.deleteLater()
        filtered = self._filtered_actions()
        if not filtered:
            label = QLabel('Ничего не найдено.')
            label.setAlignment(Qt.AlignCenter)
            self.actions_layout.addWidget(label)
        else:
            for action in filtered:
                self.actions_layout.addWidget(self._build_action_row(action))
        self.actions_layout.addStretch()

    def _filtered_actions(self) -> List[QuickAction]:
        actions = self.manager.list_actions()
        if not self.search_text:
            return actions
        result = []
        for action in actions:
            hay = f"{action.label} {action.description}".lower()
            if self.search_text in hay:
                result.append(action)
        return result

    def _build_action_row(self, action: QuickAction):
        row_widget = QWidget()
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row)
        info = QLabel(f"<b>{action.label}</b><br><span style='color: gray;'>{action.description}</span>")
        info.setWordWrap(True)
        button = QPushButton('▶')
        button.setFixedWidth(40)
        button.clicked.connect(lambda _, act=action: self._execute_action(act))
        if action.requires_input:
            button.setToolTip('Требуется параметр из поля выше')
        row.addWidget(info)
        row.addWidget(button)
        return row_widget

    def _execute_action(self, action: QuickAction):
        param = self.param_field.text().strip()
        if action.requires_input and not param:
            QMessageBox.warning(self, 'Требуется ввод', 'Это действие требует параметр.')
            return
        try:
            action.handler(param if action.requires_input else None)
            self.status_label.setText(f'Действие «{action.label}» выполнено.')
        except Exception as exc:
            self.status_label.setText(f'Ошибка: {exc}')

