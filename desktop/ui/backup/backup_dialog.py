from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt

from desktop.backup.backup_manager import BackupManager


class BackupDialog(QDialog):
    def __init__(self, manager: BackupManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle('Резервные копии')
        self.resize(520, 400)
        self._init_ui()
        self._load_backups()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        controls = QHBoxLayout()
        create_btn = QPushButton('Создать бэкап')
        create_btn.clicked.connect(self._create_backup)
        restore_btn = QPushButton('Восстановить')
        restore_btn.clicked.connect(self._restore_backup)
        open_btn = QPushButton('Открыть папку')
        open_btn.clicked.connect(self._open_folder)
        controls.addWidget(create_btn)
        controls.addWidget(restore_btn)
        controls.addWidget(open_btn)
        layout.addLayout(controls)

    def _load_backups(self):
        self.list_widget.clear()
        for path in self.manager.list_backups():
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

    def _create_backup(self):
        path = self.manager.create_backup()
        self._load_backups()
        QMessageBox.information(self, 'Бэкап создан', f'Файл сохранён: {path}')

    def _selected_backup(self):
        item = self.list_widget.currentItem()
        if not item:
            return None
        return item.data(Qt.UserRole)

    def _restore_backup(self):
        backup_path = self._selected_backup()
        if not backup_path:
            QMessageBox.warning(self, 'Нет выбора', 'Выберите резервную копию для восстановления')
            return
        confirm = QMessageBox.question(
            self,
            'Восстановление',
            'Восстановление перезапишет текущие настройки и данные. Продолжить?'
        )
        if confirm != QMessageBox.Yes:
            return
        self.manager.restore_backup(backup_path)
        QMessageBox.information(
            self,
            'Готово',
            'Данные восстановлены. Перезапустите приложение, чтобы применить изменения.'
        )

    def _open_folder(self):
        path = self.manager.backup_dir
        QMessageBox.information(self, 'Папка бэкапов', f'Файлы находятся в {path}')

