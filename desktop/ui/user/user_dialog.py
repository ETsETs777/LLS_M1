from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QMessageBox
)
from PyQt5.QtCore import Qt

from desktop.config.settings import Settings
from desktop.database.repositories.user_repository import UserRepository


class UserDialog(QDialog):
    def __init__(self, settings: Settings, repository: UserRepository, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.repository = repository
        self.setWindowTitle('Информация о пользователе')
        self.resize(480, 320)
        self.current_user_id = self.settings.get_current_user_id()
        self._init_ui()
        self._load_users()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.info_label = QLabel('Выберите существующего пользователя или заполните данные ниже')
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        self.user_select = QComboBox()
        self.user_select.currentIndexChanged.connect(self._on_user_selected)
        layout.addWidget(self.user_select)
        form_layout = QFormLayout()
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText('Иван Иванов')
        form_layout.addRow('ФИО', self.full_name_edit)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('email@example.com')
        form_layout.addRow('Email', self.email_edit)
        self.org_edit = QLineEdit()
        self.org_edit.setPlaceholderText('Компания или команда')
        form_layout.addRow('Организация', self.org_edit)
        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.save_button = QPushButton('Продолжить')
        self.save_button.clicked.connect(self._save)
        self.cancel_button = QPushButton('Выход')
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

    def _load_users(self):
        self.user_select.blockSignals(True)
        self.user_select.clear()
        self.user_select.addItem('Новый пользователь', userData=None)
        users = self.repository.list_users()
        for user in users:
            label = f"{user['full_name']} ({user['email']})"
            self.user_select.addItem(label, userData=user['id'])
        self.user_select.blockSignals(False)
        if self.current_user_id:
            index = self.user_select.findData(self.current_user_id)
            if index != -1:
                self.user_select.setCurrentIndex(index)

    def _on_user_selected(self, index):
        user_id = self.user_select.itemData(index)
        if user_id:
            user = self.repository.get_user(user_id)
            if user:
                self.full_name_edit.setText(user['full_name'])
                self.email_edit.setText(user['email'])
                self.org_edit.setText(user['organization'])
                self.full_name_edit.setEnabled(False)
                self.email_edit.setEnabled(False)
                self.org_edit.setEnabled(False)
        else:
            self.full_name_edit.clear()
            self.email_edit.clear()
            self.org_edit.clear()
            self.full_name_edit.setEnabled(True)
            self.email_edit.setEnabled(True)
            self.org_edit.setEnabled(True)

    def _save(self):
        user_id = self.user_select.currentData()
        if user_id:
            self.settings.set_current_user_id(user_id)
            self.accept()
            return
        full_name = self.full_name_edit.text().strip()
        email = self.email_edit.text().strip()
        organization = self.org_edit.text().strip()
        if not full_name or not email or not organization:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return
        new_user_id = self.repository.add_user(full_name, email, organization)
        self.settings.set_current_user_id(new_user_id)
        self.accept()

