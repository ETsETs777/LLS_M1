from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
    QPlainTextEdit,
    QComboBox,
    QMessageBox,
    QListWidget,
    QListWidgetItem
)
from PyQt5.QtCore import Qt

from desktop.config.settings import Settings
from desktop.core.neural_network import NeuralNetwork


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, neural_network: NeuralNetwork, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.neural_network = neural_network
        self.setWindowTitle('Настройки')
        self.resize(620, 520)
        self.presets = self.settings.get_presets()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.general_tab = QWidget()
        self.tabs.addTab(self.general_tab, 'Основные')
        self._build_general_tab()

        self.generation_tab = QWidget()
        self.tabs.addTab(self.generation_tab, 'Генерация')
        self._build_generation_tab()

        self.prompt_tab = QWidget()
        self.tabs.addTab(self.prompt_tab, 'Промпт')
        self._build_prompt_tab()

        self.presets_tab = QWidget()
        self.tabs.addTab(self.presets_tab, 'Пресеты')
        self._build_presets_tab()

        self.data_tab = QWidget()
        self.tabs.addTab(self.data_tab, 'Данные')
        self._build_data_tab()

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

    def _build_general_tab(self):
        layout = QFormLayout()
        self.general_tab.setLayout(layout)

        self.model_path_edit = QLineEdit()
        browse_button = QPushButton('Выбрать...')
        browse_button.clicked.connect(self._browse_model_path)
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_path_edit)
        model_layout.addWidget(browse_button)
        layout.addRow('Путь к модели', model_layout)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['light', 'dark'])
        layout.addRow('Тема', self.theme_combo)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addRow('Информация о модели', self.info_label)

    def _build_generation_tab(self):
        layout = QFormLayout()
        self.generation_tab.setLayout(layout)

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(16, 2048)
        layout.addRow('Макс. токенов', self.max_tokens_spin)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.1, 2.0)
        self.temperature_spin.setSingleStep(0.05)
        layout.addRow('Температура', self.temperature_spin)

        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.1, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        layout.addRow('Top-p', self.top_p_spin)

        self.repetition_spin = QDoubleSpinBox()
        self.repetition_spin.setRange(0.8, 2.0)
        self.repetition_spin.setSingleStep(0.05)
        layout.addRow('Пенальти повторов', self.repetition_spin)

        self.sampling_combo = QComboBox()
        self.sampling_combo.addItems(['True', 'False'])
        layout.addRow('Стохастическая генерация', self.sampling_combo)

    def _build_prompt_tab(self):
        layout = QVBoxLayout()
        self.prompt_tab.setLayout(layout)
        self.prompt_editor = QPlainTextEdit()
        self.prompt_editor.setPlaceholderText('Опишите системный промпт...')
        layout.addWidget(self.prompt_editor)

    def _build_presets_tab(self):
        layout = QVBoxLayout()
        self.presets_tab.setLayout(layout)
        self.presets_list = QListWidget()
        layout.addWidget(self.presets_list)

        controls_layout = QHBoxLayout()
        self.new_preset_name = QLineEdit()
        self.new_preset_name.setPlaceholderText('Название пресета')
        controls_layout.addWidget(self.new_preset_name)
        save_button = QPushButton('Сохранить текущие настройки')
        save_button.clicked.connect(self._save_current_as_preset)
        controls_layout.addWidget(save_button)
        layout.addLayout(controls_layout)

        preset_buttons = QHBoxLayout()
        self.apply_preset_button = QPushButton('Применить')
        self.apply_preset_button.clicked.connect(self._apply_selected_preset)
        self.delete_preset_button = QPushButton('Удалить')
        self.delete_preset_button.clicked.connect(self._delete_selected_preset)
        preset_buttons.addWidget(self.apply_preset_button)
        preset_buttons.addWidget(self.delete_preset_button)
        layout.addLayout(preset_buttons)

    def _build_data_tab(self):
        layout = QFormLayout()
        self.data_tab.setLayout(layout)

        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 3650)
        layout.addRow('Хранение истории (дней)', self.retention_spin)

        self.export_dir_edit = QLineEdit()
        export_button = QPushButton('Выбрать...')
        export_button.clicked.connect(self._browse_export_dir)
        export_layout = QHBoxLayout()
        export_layout.addWidget(self.export_dir_edit)
        export_layout.addWidget(export_button)
        layout.addRow('Папка экспорта', export_layout)

        self.backup_dir_edit = QLineEdit()
        backup_button = QPushButton('Выбрать...')
        backup_button.clicked.connect(self._browse_backup_dir)
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(self.backup_dir_edit)
        backup_layout.addWidget(backup_button)
        layout.addRow('Папка бэкапов', backup_layout)

    def _load_data(self):
        self.model_path_edit.setText(self.settings.get_model_path())
        self.theme_combo.setCurrentText(self.settings.get_theme())
        generation = self.settings.get_generation_config()
        self.max_tokens_spin.setValue(generation.get('max_new_tokens', 200))
        self.temperature_spin.setValue(generation.get('temperature', 0.8))
        self.top_p_spin.setValue(generation.get('top_p', 0.95))
        self.repetition_spin.setValue(generation.get('repetition_penalty', 1.05))
        self.sampling_combo.setCurrentText(str(generation.get('do_sample', True)))
        self.prompt_editor.setPlainText(self.settings.get_prompt())
        self._refresh_presets()
        info = self.neural_network.get_model_info()
        info_text = f"Путь: {info.get('model_path')}\nУстройство: {info.get('device')}\nКонтекст: {info.get('context_length')}\nVocab: {info.get('vocab_size')}"
        self.info_label.setText(info_text)
        history = self.settings.get_history_config()
        self.retention_spin.setValue(history.get('retention_days', 90))
        self.export_dir_edit.setText(history.get('export_dir', ''))
        backup = self.settings.get_backup_config()
        self.backup_dir_edit.setText(backup.get('dir', ''))

    def _browse_model_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку модели', self.model_path_edit.text())
        if path:
            self.model_path_edit.setText(path)

    def _refresh_presets(self):
        self.presets = self.settings.get_presets()
        self.presets_list.clear()
        for name in self.presets.keys():
            item = QListWidgetItem(name)
            self.presets_list.addItem(item)

    def _save_current_as_preset(self):
        name = self.new_preset_name.text().strip()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Введите название пресета')
            return
        data = {
            'prompt': self.prompt_editor.toPlainText(),
            'generation': {
                'max_new_tokens': self.max_tokens_spin.value(),
                'temperature': self.temperature_spin.value(),
                'top_p': self.top_p_spin.value(),
                'do_sample': self.sampling_combo.currentText() == 'True',
                'repetition_penalty': self.repetition_spin.value()
            },
            'model_path': self.model_path_edit.text()
        }
        self.settings.save_preset(name, data)
        self.new_preset_name.clear()
        self._refresh_presets()

    def _apply_selected_preset(self):
        item = self.presets_list.currentItem()
        if not item:
            return
        name = item.text()
        self.settings.apply_preset(name)
        self._load_data()

    def _delete_selected_preset(self):
        item = self.presets_list.currentItem()
        if not item:
            return
        name = item.text()
        self.settings.delete_preset(name)
        self._refresh_presets()

    def accept(self):
        self.settings.set_model_path(self.model_path_edit.text().strip())
        self.settings.set_theme(self.theme_combo.currentText())
        self.settings.set_prompt(self.prompt_editor.toPlainText())
        self.settings.update_generation_config({
            'max_new_tokens': self.max_tokens_spin.value(),
            'temperature': self.temperature_spin.value(),
            'top_p': self.top_p_spin.value(),
            'do_sample': self.sampling_combo.currentText() == 'True',
            'repetition_penalty': self.repetition_spin.value()
        })
        self.settings.update_history_config({
            'retention_days': self.retention_spin.value(),
            'export_dir': self.export_dir_edit.text().strip()
        })
        self.settings.update_backup_config({
            'dir': self.backup_dir_edit.text().strip()
        })
        super().accept()

    def _browse_export_dir(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку экспорта', self.export_dir_edit.text())
        if path:
            self.export_dir_edit.setText(path)

    def _browse_backup_dir(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку бэкапов', self.backup_dir_edit.text())
        if path:
            self.backup_dir_edit.setText(path)

