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
from desktop.appearance.palette_manager import PaletteManager


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, neural_network: NeuralNetwork, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.neural_network = neural_network
        self.palette_manager = PaletteManager()
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

        self.appearance_tab = QWidget()
        self.tabs.addTab(self.appearance_tab, 'Внешний вид')
        self._build_appearance_tab()

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

        self.plugins_tab = QWidget()
        self.tabs.addTab(self.plugins_tab, 'Плагины')
        self._build_plugins_tab()

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

    def _build_appearance_tab(self):
        layout = QFormLayout()
        self.appearance_tab.setLayout(layout)
        self.accent_combo = QComboBox()
        for option in self.palette_manager.options():
            self.accent_combo.addItem(option['name'], option['value'])
        self.accent_combo.currentIndexChanged.connect(self._on_palette_change)
        layout.addRow('Акцентный цвет', self.accent_combo)

        self.custom_accent_edit = QLineEdit()
        self.custom_accent_edit.setPlaceholderText('#0078d4')
        self.custom_accent_edit.textChanged.connect(self._update_accent_preview)
        layout.addRow('Пользовательский цвет', self.custom_accent_edit)

        self.accent_preview = QLabel()
        self.accent_preview.setFixedHeight(40)
        self.accent_preview.setStyleSheet('border: 1px solid #ccc; border-radius: 4px;')
        layout.addRow('Предпросмотр', self.accent_preview)

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
        accent = self.settings.get_accent_color()
        index = self.accent_combo.findData(accent)
        if index != -1:
            self.accent_combo.setCurrentIndex(index)
        self.custom_accent_edit.setText(accent)
        self._update_accent_preview()
        history = self.settings.get_history_config()
        self.retention_spin.setValue(history.get('retention_days', 90))
        self.export_dir_edit.setText(history.get('export_dir', ''))
        backup = self.settings.get_backup_config()
        self.backup_dir_edit.setText(backup.get('dir', ''))
        self.plugin_config = self.settings.get_plugin_config()
        self._load_plugins_tab()

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
        self.settings.update_appearance({
            'accent_color': self._selected_accent_color()
        })
        self._persist_plugin_state()
        super().accept()

    def _browse_export_dir(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку экспорта', self.export_dir_edit.text())
        if path:
            self.export_dir_edit.setText(path)

    def _browse_backup_dir(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку бэкапов', self.backup_dir_edit.text())
        if path:
            self.backup_dir_edit.setText(path)

    def _on_palette_change(self):
        value = self.accent_combo.currentData()
        if value:
            self.custom_accent_edit.setText(value)
        self._update_accent_preview()

    def _update_accent_preview(self):
        value = self._selected_accent_color()
        if value:
            self.accent_preview.setStyleSheet(f'border: 1px solid {value}; border-radius: 4px; background-color: {value};')
        else:
            self.accent_preview.setStyleSheet('border: 1px solid #ccc; border-radius: 4px;')

    def _selected_accent_color(self) -> str:
        custom = self.custom_accent_edit.text().strip()
        if custom:
            return custom
        data = self.accent_combo.currentData()
        return data or '#0078d4'

    def _build_plugins_tab(self):
        layout = QVBoxLayout()
        self.plugins_tab.setLayout(layout)
        self.plugins_list = QListWidget()
        self.plugins_list.itemSelectionChanged.connect(self._on_plugin_selected)
        layout.addWidget(self.plugins_list)
        roles_layout = QHBoxLayout()
        self.plugin_roles_edit = QLineEdit()
        self.plugin_roles_edit.setPlaceholderText('roles через запятую (user, analyst, admin)')
        roles_layout.addWidget(self.plugin_roles_edit)
        self.save_plugin_roles_button = QPushButton('Сохранить роли')
        self.save_plugin_roles_button.clicked.connect(self._save_selected_plugin_roles)
        roles_layout.addWidget(self.save_plugin_roles_button)
        layout.addLayout(roles_layout)
        self.plugin_info_label = QLabel('Выберите плагин для просмотра описания и ролей.')
        self.plugin_info_label.setWordWrap(True)
        layout.addWidget(self.plugin_info_label)

    def _load_plugins_tab(self):
        if not hasattr(self, 'plugins_list'):
            return
        self.plugins_list.blockSignals(True)
        self.plugins_list.clear()
        plugin_cfg = getattr(self, 'plugin_config', None) or {}
        available = plugin_cfg.get('available', {})
        enabled = set(plugin_cfg.get('enabled', []))
        for plugin_id, meta in available.items():
            name = meta.get('name', plugin_id)
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
            item.setCheckState(Qt.Checked if plugin_id in enabled else Qt.Unchecked)
            item.setData(Qt.UserRole, plugin_id)
            description = meta.get('description', '')
            roles = ', '.join(meta.get('allowed_roles', []))
            tooltip = description
            if roles:
                tooltip += f"\nРоли: {roles}"
            if tooltip:
                item.setToolTip(tooltip)
            self.plugins_list.addItem(item)
        self.plugins_list.blockSignals(False)
        self.plugin_roles_edit.clear()
        self.plugin_info_label.setText('Выберите плагин для настройки ролей.')

    def _on_plugin_selected(self):
        item = self.plugins_list.currentItem()
        if not item:
            self.plugin_roles_edit.clear()
            self.plugin_info_label.setText('Выберите плагин для настройки ролей.')
            return
        plugin_id = item.data(Qt.UserRole)
        meta = self.plugin_config.get('available', {}).get(plugin_id, {})
        roles = ', '.join(meta.get('allowed_roles', []))
        self.plugin_roles_edit.setText(roles)
        description = meta.get('description', 'Нет описания.')
        self.plugin_info_label.setText(description)

    def _save_selected_plugin_roles(self):
        item = self.plugins_list.currentItem()
        if not item:
            return
        plugin_id = item.data(Qt.UserRole)
        roles_raw = self.plugin_roles_edit.text().strip()
        roles = [role.strip() for role in roles_raw.split(',') if role.strip()]
        self.plugin_config.setdefault('available', {}).setdefault(plugin_id, {})['allowed_roles'] = roles
        QMessageBox.information(self, 'Готово', 'Роли плагина обновлены.')

    def _persist_plugin_state(self):
        enabled = []
        if hasattr(self, 'plugins_list'):
            for row in range(self.plugins_list.count()):
                item = self.plugins_list.item(row)
                if item.checkState() == Qt.Checked:
                    enabled.append(item.data(Qt.UserRole))
        self.plugin_config['enabled'] = enabled
        self.settings.update_plugin_config(self.plugin_config)

