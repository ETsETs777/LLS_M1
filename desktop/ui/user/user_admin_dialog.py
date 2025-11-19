from functools import partial

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QMessageBox
)

from desktop.database.repositories.user_repository import UserRepository


class UserAdminDialog(QDialog):
    ROLES = ['user', 'analyst', 'admin']

    def __init__(self, repository: UserRepository, current_role: str, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.current_role = current_role
        self.setWindowTitle('Управление пользователями')
        self.resize(560, 360)
        self._init_ui()
        self._load_users()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['ФИО', 'Email', 'Организация', 'Роль'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        refresh_btn = QPushButton('Обновить')
        refresh_btn.clicked.connect(self._load_users)
        buttons.addWidget(refresh_btn)
        buttons.addStretch()
        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def _load_users(self):
        users = self.repository.list_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(user['full_name']))
            self.table.setItem(row, 1, QTableWidgetItem(user['email']))
            self.table.setItem(row, 2, QTableWidgetItem(user['organization']))
            combo = QComboBox()
            combo.addItems(self.ROLES)
            combo.setCurrentText(user.get('role', 'user'))
            combo.currentTextChanged.connect(partial(self._role_changed, user_id=user['id']))
            if self.current_role != 'admin':
                combo.setEnabled(False)
            self.table.setCellWidget(row, 3, combo)

    def _role_changed(self, role: str, user_id: int):
        try:
            self.repository.update_role(user_id, role)
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', str(exc))
            self._load_users()

