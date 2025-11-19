import os

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QLabel,
    QMessageBox
)
from PyQt5.QtCore import Qt

from desktop.history.manager import HistoryManager


class HistoryArchiveDialog(QDialog):
    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle('Архивы истории')
        self.resize(720, 500)
        self._init_ui()
        self._load_archives()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()
        self.list_widget = QListWidget()
        # Скрываем скроллбары, прокрутка только колесиком мыши
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.currentItemChanged.connect(self._on_selection)
        top_layout.addWidget(self.list_widget, 1)

        right_panel = QVBoxLayout()
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        # Скрываем скроллбары, прокрутка только колесиком мыши
        self.preview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        right_panel.addWidget(self.preview)

        btn_layout = QHBoxLayout()
        self.refresh_button = QPushButton('Обновить')
        self.refresh_button.clicked.connect(self._load_archives)
        self.open_button = QPushButton('Открыть файл')
        self.open_button.clicked.connect(self._open_selected_file)
        btn_layout.addWidget(self.refresh_button)
        btn_layout.addWidget(self.open_button)
        right_panel.addLayout(btn_layout)
        top_layout.addLayout(right_panel, 2)

        layout.addLayout(top_layout)
        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

    def _load_archives(self):
        self.list_widget.clear()
        archives = self.history_manager.list_archives()
        if not archives:
            self.status_label.setText('Архивы отсутствуют.')
            return
        for name in sorted(archives, reverse=True):
            item = QListWidgetItem(name)
            self.list_widget.addItem(item)
        self.status_label.setText(f'Найдено архивов: {len(archives)}')

    def _on_selection(self, current, previous):
        if not current:
            self.preview.clear()
            return
        filename = current.text()
        messages = self.history_manager.read_archive(filename)
        if not messages:
            self.preview.setPlainText('Архив пуст или недоступен.')
            return
        lines = []
        for msg in messages[:50]:
            stamp = msg.get('timestamp', '')
            role = msg.get('role', '')
            content = msg.get('content', '')
            lines.append(f"{stamp} [{role}] {content}")
        self.preview.setPlainText('\n\n'.join(lines))

    def _open_selected_file(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        filename = item.text()
        path = self.history_manager.get_archive_path(filename)
        if not os.path.exists(path):
            QMessageBox.warning(self, 'Ошибка', 'Файл архива не найден.')
            return
        os.startfile(path)

