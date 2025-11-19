import json
import os
from typing import Optional

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QAction, QStatusBar, QMessageBox, QLabel

from desktop.ui.chat_widget import ChatWidget
from desktop.ui.theme_manager import ThemeManager
from desktop.core.neural_network import NeuralNetwork
from desktop.config.settings import Settings
from desktop.ui.settings.settings_dialog import SettingsDialog
from desktop.history.manager import HistoryManager
from desktop.ui.history.history_dialog import HistoryDialog
from desktop.monitoring.system_monitor import ResourceMonitor
from desktop.ui.widgets.status_panel import StatusPanel
from desktop.plugins.manager import PluginManager
from desktop.ui.plugins.plugin_dialog import PluginDialog
from desktop.updater.update_manager import UpdateManager
from desktop.backup.backup_manager import BackupManager
from desktop.ui.backup.backup_dialog import BackupDialog
from desktop.ui.user.user_admin_dialog import UserAdminDialog
from desktop.shortcuts.actions import QuickActionsManager, QuickAction
from desktop.shortcuts.quick_actions_dialog import QuickActionsDialog

class MainWindow(QMainWindow):
    def __init__(self, settings: Optional[Settings] = None, user_repository=None):
        super().__init__()
        self.settings = settings or Settings()
        self.theme_manager = ThemeManager()
        self.theme_manager.set_accent_color(self.settings.get_accent_color())
        self.neural_network = NeuralNetwork(settings=self.settings)
        self.user_repository = user_repository
        self.history_manager = HistoryManager(self.settings)
        self.history_manager.cleanup_old_records()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        self.resource_monitor = ResourceMonitor(os.path.join(log_dir, 'metrics.log'))
        self.status_panel = StatusPanel()
        self.update_manager = UpdateManager(self.settings)
        self.backup_manager = BackupManager(self.settings)
        self.training_status_label = QLabel('Обучение: нет данных')
        self.quick_actions = QuickActionsManager()
        updater_cfg = self.settings.get_updater_config()
        if updater_cfg.get('verify_models_on_start'):
            self.update_manager.verify_models()
        self.current_user = None
        self.current_user_role = 'user'
        self._load_current_user()
        self.vram_warning_threshold = 0.9
        self.vram_warning_shown = False
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.refresh_metrics)
        self.training_timer = QTimer(self)
        self.training_timer.timeout.connect(self._update_training_status_label)
        self.init_ui()
        self.load_window_state()
        self.apply_theme(self.settings.get_theme())
        self.monitor_timer.start(5000)
        self.training_timer.start(10000)
        self._update_training_status_label()
        
    def init_ui(self):
        self.setWindowTitle('Нейросеть Чат')
        self.setMinimumSize(800, 600)
        
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)
        
        self.chat_widget = ChatWidget(self.neural_network, self)
        layout.addWidget(self.chat_widget)
        self._setup_quick_actions()
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Файл')
        
        settings_action = QAction('Настройки', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        clear_action = QAction('Очистить чат', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.triggered.connect(self.chat_widget.clear_chat)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu('Вид')
        
        light_theme_action = QAction('Светлая тема', self)
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        view_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('Темная тема', self)
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        view_menu.addAction(dark_theme_action)

        tools_menu = menubar.addMenu('Инструменты')
        history_action = QAction('История чатов', self)
        history_action.setShortcut('Ctrl+H')
        history_action.triggered.connect(self.open_history)
        tools_menu.addAction(history_action)

        plugins_action = QAction('Плагины', self)
        plugins_action.triggered.connect(self.open_plugins)
        tools_menu.addAction(plugins_action)

        verify_action = QAction('Проверить модель', self)
        verify_action.triggered.connect(self.verify_models)
        tools_menu.addAction(verify_action)

        backup_action = QAction('Резервные копии', self)
        backup_action.triggered.connect(self.open_backup_dialog)
        tools_menu.addAction(backup_action)

        training_status_action = QAction('Статус обучения', self)
        training_status_action.triggered.connect(self.show_training_status)
        tools_menu.addAction(training_status_action)

        self.user_admin_action = QAction('Управление пользователями', self)
        self.user_admin_action.triggered.connect(self.open_user_admin)
        tools_menu.addAction(self.user_admin_action)
        quick_actions_action = QAction('Быстрые действия', self)
        quick_actions_action.triggered.connect(self.open_quick_actions)
        tools_menu.addAction(quick_actions_action)
        self._update_role_dependent_actions()
        
    def create_toolbar(self):
        toolbar = self.addToolBar('Панель инструментов')
        
        self.theme_button = QPushButton('🌙 Темная тема')
        self.theme_button.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_button)
        
        toolbar.addSeparator()
        
        clear_button = QPushButton('🗑 Очистить')
        clear_button.clicked.connect(self.chat_widget.clear_chat)
        toolbar.addWidget(clear_button)

        history_button = QPushButton('📚 История')
        history_button.clicked.connect(self.open_history)
        toolbar.addWidget(history_button)
        quick_button = QPushButton('⚡ Действия')
        quick_button.clicked.connect(self.open_quick_actions)
        toolbar.addWidget(quick_button)
        
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addPermanentWidget(self.status_panel)
        self.status_bar.addPermanentWidget(self.training_status_label)
        self.status_panel.reload_button.clicked.connect(self.refresh_metrics)
        if self.current_user:
            self.status_panel.set_user(self.current_user.get('full_name', '—'), self.current_user_role)
        self.status_panel.model_reload_button.clicked.connect(self.reload_model)
        
    def toggle_theme(self):
        current = self.settings.get_theme()
        new_theme = 'dark' if current == 'light' else 'light'
        self.set_theme(new_theme)
        
    def set_theme(self, theme):
        self.settings.set_theme(theme)
        self.theme_manager.set_theme(theme)
        self.apply_theme(theme)
        self.theme_button.setText('☀️ Светлая тема' if theme == 'dark' else '🌙 Темная тема')
        
    def apply_theme(self, theme):
        self.theme_manager.set_accent_color(self.settings.get_accent_color())
        stylesheet = self.theme_manager.get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        self.chat_widget.apply_theme(theme, stylesheet)
        
    def load_window_state(self):
        config = self.settings.config
        if 'window_geometry' in config:
            self.restoreGeometry(bytes.fromhex(config['window_geometry']))
        if 'window_state' in config:
            self.restoreState(bytes.fromhex(config['window_state']))
            
    def save_window_state(self):
        self.settings.config['window_geometry'] = self.saveGeometry().toHex().data().decode()
        self.settings.config['window_state'] = self.saveState().toHex().data().decode()
        self.settings.save_config()
        
    def closeEvent(self, event):
        self.save_window_state()
        event.accept()

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self.neural_network, self)
        if dialog.exec_():
            self.neural_network.refresh_from_settings()
            self.theme_manager.set_accent_color(self.settings.get_accent_color())
            self.apply_theme(self.settings.get_theme())
            self._refresh_plugin_manager()
            self._update_role_dependent_actions()

    def _load_current_user(self):
        user_id = self.settings.get_current_user_id()
        if user_id and self.user_repository:
            self.current_user = self.user_repository.get_user(user_id)
        else:
            self.current_user = None
        if self.current_user:
            self.current_user_role = self.current_user.get('role', 'user')
            self.status_panel.set_user(self.current_user.get('full_name', '—'), self.current_user_role)
        else:
            self.current_user_role = 'user'
            self.status_panel.set_user('—', self.current_user_role)
        self._refresh_plugin_manager()
        self._update_role_dependent_actions()

    def open_history(self):
        dialog = HistoryDialog(self.history_manager, self)
        dialog.exec_()

    def open_plugins(self):
        dialog = PluginDialog(self.plugin_manager, self)
        dialog.exec_()

    def open_user_admin(self):
        if not self.user_repository:
            QMessageBox.warning(self, 'Недоступно', 'Репозиторий пользователей не инициализирован.')
            return
        if self.current_user_role != 'admin':
            QMessageBox.warning(self, 'Недостаточно прав', 'Только администратор может управлять пользователями.')
            return
        dialog = UserAdminDialog(self.user_repository, self.current_user_role, self)
        dialog.exec_()
        self._load_current_user()

    def open_quick_actions(self):
        dialog = QuickActionsDialog(self.quick_actions, self)
        dialog.exec_()

    def verify_models(self):
        result = self.update_manager.verify_models()
        QMessageBox.information(self, 'Проверка модели', result['details'])

    def show_training_status(self):
        status_path, raw, payload = self._get_training_status_payload()
        if not status_path:
            QMessageBox.information(self, 'Статус обучения', 'Нет данных об активных запусках.')
            return
        if raw is None:
            QMessageBox.information(self, 'Статус обучения', 'Файл статуса отсутствует.')
            return
        if payload:
            status = payload.get('status', 'неизвестно').capitalize()
            timestamp = payload.get('timestamp', '—')
            message = payload.get('message') or payload.get('details') or 'Нет сообщения.'
            metrics = payload.get('metrics')
            lines = [
                f"Статус: {status}",
                f"Время: {timestamp}",
                f"Сообщение: {message}"
            ]
            if metrics:
                lines.append(f"Метрики: {metrics}")
            text = '\n'.join(lines)
        else:
            text = raw or 'Файл статуса пуст.'
        QMessageBox.information(self, 'Статус обучения', text)
        self._update_training_status_label()

    def refresh_metrics(self):
        metrics = self.resource_monitor.collect()
        self.status_panel.update_metrics(metrics)
        self._check_vram(metrics)
        self.status_bar.showMessage('Мониторинг обновлён')

    def reload_model(self):
        try:
            self.neural_network.reload_model()
            QMessageBox.information(self, 'Модель перезагружена', 'Модель успешно перезагружена.')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка перезагрузки', str(exc))

    def open_backup_dialog(self):
        dialog = BackupDialog(self.backup_manager, self)
        dialog.exec_()

    def _check_vram(self, metrics):
        total = metrics.get('gpu_memory_total')
        used = metrics.get('gpu_memory_used')
        if not total or not used:
            self.vram_warning_shown = False
            return
        ratio = used / total if total else 0
        if ratio >= self.vram_warning_threshold and not self.vram_warning_shown:
            QMessageBox.warning(
                self,
                'Внимание: мало VRAM',
                'Память GPU почти заполнена. Снизьте параметры генерации или перезагрузите модель.'
            )
            self.vram_warning_shown = True
        elif ratio < self.vram_warning_threshold - 0.1:
            self.vram_warning_shown = False

    def _refresh_plugin_manager(self):
        self.plugin_manager = PluginManager(self.settings, self.current_user_role)

    def _update_role_dependent_actions(self):
        if hasattr(self, 'user_admin_action'):
            self.user_admin_action.setVisible(self.current_user_role == 'admin')

    def _update_training_status_label(self):
        status_path, raw, payload = self._get_training_status_payload()
        if not status_path or raw is None:
            self.training_status_label.setText('Обучение: нет данных')
            return
        if payload:
            status = payload.get('status', 'неизвестно')
            icon = self._status_indicator(status)
            timestamp = payload.get('timestamp')
            summary = payload.get('message') or payload.get('details') or ''
            suffix = f" · {timestamp}" if timestamp else ''
            self.training_status_label.setText(f'{icon} Обучение: {status}{suffix} {summary[:30]}')
        elif raw:
            self.training_status_label.setText(f'Обучение: {raw[:60]}')
        else:
            self.training_status_label.setText('Обучение: статус неизвестен')

    def _setup_quick_actions(self):
        self.quick_actions = QuickActionsManager()
        self.quick_actions.register(
            QuickAction('Очистить чат', 'Удаляет историю текущей сессии и поле ввода.', self.chat_widget.clear_chat)
        )
        self.quick_actions.register(
            QuickAction('Показать статус обучения', 'Открывает последнее сообщение о ходе обучения.', self.show_training_status)
        )
        self.quick_actions.register(
            QuickAction('Перезагрузить модель', 'Перезапускает модель и обновляет настройки генерации.', self.reload_model)
        )
        self.quick_actions.register(
            QuickAction('Открыть историю', 'Переходит к журналу диалогов с фильтрами.', self.open_history)
        )

    def _get_training_status_payload(self):
        training_cfg = self.settings.get_training_config()
        status_path = training_cfg.get('status_file') or os.path.join(training_cfg.get('reports_dir'), 'training_status.json')
        if not status_path or not os.path.exists(status_path):
            return status_path, None, None
        try:
            with open(status_path, 'r', encoding='utf-8') as f:
                data = f.read().strip()
        except Exception:
            return status_path, None, None
        if not data:
            return status_path, '', None
        try:
            payload = json.loads(data)
        except ValueError:
            payload = None
        return status_path, data, payload

    def _status_indicator(self, status: str) -> str:
        normalized = (status or '').lower()
        if normalized in ('completed', 'success', 'done'):
            return '🟢'
        if normalized in ('running', 'in_progress'):
            return '🟡'
        if normalized in ('failed', 'error'):
            return '🔴'
        return '⚪'