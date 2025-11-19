from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDateEdit,
    QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QScrollBar

from desktop.history.manager import HistoryManager


class HistoryDialog(QDialog):
    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle('История чатов')
        self.resize(700, 520)
        self._init_ui()
        self._load_messages()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        filter_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText('Поиск по тексту сообщения')
        self.search_field.textChanged.connect(self._load_messages)
        filter_layout.addWidget(self.search_field)

        self.tags_field = QLineEdit()
        self.tags_field.setPlaceholderText('Теги через запятую')
        self.tags_field.textChanged.connect(self._load_messages)
        filter_layout.addWidget(QLabel('Теги'))
        filter_layout.addWidget(self.tags_field)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('dd.MM.yyyy')
        self.start_date_active = False
        self.start_date.dateChanged.connect(self._on_start_date_changed)
        filter_layout.addWidget(QLabel('От'))
        filter_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('dd.MM.yyyy')
        self.end_date_active = False
        self.end_date.dateChanged.connect(self._on_end_date_changed)
        filter_layout.addWidget(QLabel('До'))
        filter_layout.addWidget(self.end_date)

        reset_button = QPushButton('Сбросить')
        reset_button.clicked.connect(self._reset_filters)
        filter_layout.addWidget(reset_button)

        layout.addLayout(filter_layout)

        self.history_list = QListWidget()
        # Скрываем скроллбары, прокрутка только колесиком мыши
        self.history_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.history_list)

        buttons_layout = QHBoxLayout()
        export_json = QPushButton('Экспорт JSON')
        export_json.clicked.connect(lambda: self._export('json'))
        export_md = QPushButton('Экспорт Markdown')
        export_md.clicked.connect(lambda: self._export('md'))
        export_pdf = QPushButton('Экспорт PDF')
        export_pdf.clicked.connect(lambda: self._export('pdf'))
        clear_button = QPushButton('Очистить историю')
        clear_button.clicked.connect(self._clear_history)
        buttons_layout.addWidget(export_json)
        buttons_layout.addWidget(export_md)
        buttons_layout.addWidget(export_pdf)
        buttons_layout.addStretch()
        buttons_layout.addWidget(clear_button)
        layout.addLayout(buttons_layout)

    def _date_to_datetime(self, date_edit: QDateEdit):
        date = date_edit.date()
        if not date.isValid():
            return None
        return datetime(date.year(), date.month(), date.day())

    def _on_start_date_changed(self):
        self.start_date_active = True
        self._load_messages()

    def _on_end_date_changed(self):
        self.end_date_active = True
        self._load_messages()

    def _reset_filters(self):
        self.search_field.clear()
        self.tags_field.clear()
        self.start_date_active = False
        self.end_date_active = False
        self._load_messages()

    def _load_messages(self):
        keyword = self.search_field.text().strip()
        start = self._date_to_datetime(self.start_date) if self.start_date_active else None
        end = self._date_to_datetime(self.end_date) if self.end_date_active else None
        tags = [tag.strip() for tag in self.tags_field.text().split(',') if tag.strip()]
        messages = self.history_manager.search(keyword=keyword, start=start, end=end, tags=tags or None)
        self.history_list.clear()
        for msg in reversed(messages):
            item = QListWidgetItem(f"{msg['timestamp']} | {msg['role']} | {msg['content']}")
            self.history_list.addItem(item)

    def _export(self, fmt: str):
        filters = {
            'json': 'JSON (*.json)',
            'md': 'Markdown (*.md)',
            'pdf': 'PDF (*.pdf)'
        }
        path, _ = QFileDialog.getSaveFileName(self, 'Сохранить историю', filter=filters.get(fmt, '*.*'))
        if not path:
            return
        tags = [tag.strip() for tag in self.tags_field.text().split(',') if tag.strip()]
        target = self.history_manager.export(
            fmt,
            path,
            keyword=self.search_field.text().strip(),
            start=self._date_to_datetime(self.start_date),
            end=self._date_to_datetime(self.end_date),
            tags=tags or None
        )
        QMessageBox.information(self, 'Экспорт завершен', f'История сохранена в {target}')

    def _clear_history(self):
        confirm = QMessageBox.question(self, 'Очистить историю', 'Удалить все записи истории?')
        if confirm == QMessageBox.Yes:
            self.history_manager.history.clear_history()
            self._load_messages()

