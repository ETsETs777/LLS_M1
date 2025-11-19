import json
import os
from collections import Counter
from datetime import datetime, date
from typing import Optional, Dict, List

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QAction, QStatusBar, QMessageBox, QLabel, QHBoxLayout, QMenu
from PyQt5.QtGui import QIcon

from desktop.ui.chat_widget import ChatWidget
from desktop.ui.theme_manager import ThemeManager
from desktop.core.neural_network import NeuralNetwork
from desktop.config.settings import Settings
from desktop.ui.settings.settings_dialog import SettingsDialog
from desktop.history.manager import HistoryManager
from desktop.ui.history.history_dialog import HistoryDialog
from desktop.ui.history.history_archive_dialog import HistoryArchiveDialog
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
from desktop.ui.dashboard.statistics_dialog import StatisticsDialog
from desktop.ui.monitoring.monitor_dialog import MonitorDialog

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
        self._latest_training_status = 'Нет данных'
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
        self.statistics_dialog = None
        self.monitor_timer.start(5000)
        self.training_timer.start(10000)
        self._update_training_status_label()
        self._update_dashboard_metrics()
        
    def init_ui(self):
        self.setWindowTitle('Нейросеть Чат')
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)

        self.chat_widget = ChatWidget(self.neural_network, self)
        layout.addWidget(self.chat_widget)
        
        # Подключаем обработчики для кнопок в chat_widget
        self.chat_widget.theme_button.clicked.connect(self.toggle_theme)
        self.chat_widget.clear_button.clicked.connect(self.chat_widget.clear_chat)
        self.chat_widget.history_button.clicked.connect(self.open_history)
        self.chat_widget.statistics_button.clicked.connect(self.open_statistics)
        
        # Создаем меню для кнопки действий в chat_widget
        chat_actions_menu = QMenu(self)
        chat_history_action = chat_actions_menu.addAction('📚 Открыть историю')
        chat_history_action.triggered.connect(self.open_history)
        
        chat_backup_action = chat_actions_menu.addAction('💾 Создать бэкап')
        chat_backup_action.triggered.connect(self.open_backup_dialog)
        
        chat_monitor_action = chat_actions_menu.addAction('📊 Мониторинг')
        chat_monitor_action.triggered.connect(self.open_resource_monitor)
        
        chat_quick_actions = chat_actions_menu.addAction('⚡ Быстрые действия')
        chat_quick_actions.triggered.connect(self.open_quick_actions)
        
        self.chat_widget.actions_button.setMenu(chat_actions_menu)
        
        self.create_menu_bar()
        self.create_top_settings_button()
        self.create_status_bar()
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

        archive_action = QAction('Архивы истории', self)
        archive_action.triggered.connect(self.open_history_archives)
        tools_menu.addAction(archive_action)

        plugins_action = QAction('Плагины', self)
        plugins_action.triggered.connect(self.open_plugins)
        tools_menu.addAction(plugins_action)

        verify_action = QAction('Проверить модель', self)
        verify_action.triggered.connect(self.verify_models)
        tools_menu.addAction(verify_action)

        backup_action = QAction('Резервные копии', self)
        backup_action.triggered.connect(self.open_backup_dialog)
        tools_menu.addAction(backup_action)

        monitor_action = QAction('Мониторинг ресурсов', self)
        monitor_action.triggered.connect(self.open_resource_monitor)
        tools_menu.addAction(monitor_action)

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
        
    def create_top_settings_button(self):
        """Создает кнопку настроек в правом верхнем углу"""
        settings_widget = QWidget()
        settings_layout = QHBoxLayout()
        settings_layout.setContentsMargins(0, 0, 10, 0)
        settings_layout.addStretch()
        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setFixedSize(36, 36)
        self.settings_button.setToolTip('Настройки')
        
        # Устанавливаем иконку
        icon_path = os.path.join(os.path.dirname(__file__), 'images', 'settings.png')
        if os.path.exists(icon_path):
            self.settings_button.setIcon(QIcon(icon_path))
            self.settings_button.setIconSize(self.settings_button.size())
        
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 18px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        settings_layout.addWidget(self.settings_button)
        settings_widget.setLayout(settings_layout)
        # Добавляем в menuBar как виджет справа
        self.menuBar().setCornerWidget(settings_widget, Qt.TopRightCorner)
        
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

    def open_history_archives(self):
        dialog = HistoryArchiveDialog(self.history_manager, self)
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

    def open_resource_monitor(self):
        dialog = MonitorDialog(self.resource_monitor, self)
        dialog.exec_()
    
    def open_statistics(self):
        """Открывает окно статистики"""
        if self.statistics_dialog is None or not self.statistics_dialog.isVisible():
            self.statistics_dialog = StatisticsDialog(self)
            # Обновляем статистику перед показом
            self._update_statistics_dialog()
            self.statistics_dialog.exec_()
        else:
            self.statistics_dialog.raise_()
            self.statistics_dialog.activateWindow()
    
    def _update_statistics_dialog(self):
        """Обновляет данные в окне статистики"""
        if self.statistics_dialog is None or not self.statistics_dialog.isVisible():
            return
        
        messages = self.history_manager.list_messages(limit=None)
        total_messages = len(messages)
        today = datetime.utcnow().date()
        messages_today = sum(1 for msg in messages if self._message_date(msg) == today)
        session_ids = {msg.get('session_id') for msg in messages if msg.get('session_id')}
        sessions_today = {msg.get('session_id') for msg in messages if msg.get('session_id') and self._message_date(msg) == today}
        active_plugins = sum(1 for plugin in self.plugin_manager.list_plugins() if plugin.enabled)
        
        tag_counter = Counter()
        for msg in messages:
            for tag in msg.get('tags', []):
                tag_counter[tag] += 1
        top_tags = tag_counter.most_common(3)
        analytics_lines = [f'#{tag}: {count}' for tag, count in top_tags] if top_tags else ['Нет данных по тегам']
        
        self.statistics_dialog.update_statistics(
            sessions=str(len(session_ids)),
            messages=str(total_messages),
            plugins=str(active_plugins),
            training=self._latest_training_status or 'нет данных',
            sessions_subtitle=f'+{len(sessions_today)} сегодня',
            messages_subtitle=f'+{messages_today} сегодня',
            analytics_lines=analytics_lines
        )

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
        self._update_dashboard_metrics()  # Обновляет статистику, если окно открыто

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
            text = f'{icon} Обучение: {status}{suffix} {summary[:30]}'
            self.training_status_label.setText(text)
            self._latest_training_status = f'{icon} {status}'
        elif raw:
            self.training_status_label.setText(f'Обучение: {raw[:60]}')
            self._latest_training_status = raw[:60]
        else:
            self.training_status_label.setText('Обучение: статус неизвестен')
            self._latest_training_status = 'статус неизвестен'

    def _setup_quick_actions(self):
        self.quick_actions = QuickActionsManager()
        self.quick_actions.register(
            QuickAction('Очистить чат', 'Удаляет историю текущей сессии и поле ввода.', lambda _: self.chat_widget.clear_chat())
        )
        self.quick_actions.register(
            QuickAction('Показать статус обучения', 'Открывает последнее сообщение о ходе обучения.', lambda _: self.show_training_status())
        )
        self.quick_actions.register(
            QuickAction('Перезагрузить модель', 'Перезапускает модель и обновляет настройки генерации.', lambda _: self.reload_model())
        )
        self.quick_actions.register(
            QuickAction('Открыть историю', 'Переходит к журналу диалогов с фильтрами.', lambda _: self.open_history())
        )
        self.quick_actions.register(
            QuickAction('Открыть архивы', 'Просмотр сохранённых архивов истории.', lambda _: self.open_history_archives())
        )
        self.quick_actions.register(
            QuickAction('Переключить тему', 'Быстро меняет светлую/тёмную тему.', lambda _: self.toggle_theme())
        )
        self.quick_actions.register(
            QuickAction('Найти в истории', 'Ищет сообщения по ключевому слову и выводит первые совпадения.', self._quick_search_history, requires_input=True)
        )
        self.quick_actions.register(
            QuickAction('Установить температуру', 'Задаёт новое значение температуры генерации (например, 0.7).', self._quick_set_temperature, requires_input=True)
        )
        self.quick_actions.register(
            QuickAction('Открыть настройки', 'Открывает окно настроек приложения.', lambda _: self.open_settings())
        )
        self.quick_actions.register(
            QuickAction('Мониторинг ресурсов', 'Показать окно подробного мониторинга системных ресурсов.', lambda _: self.open_resource_monitor())
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

    def _quick_search_history(self, term: Optional[str]):
        keyword = (term or '').strip()
        if not keyword:
            QMessageBox.warning(self, 'Требуется ввод', 'Введите слово или фразу для поиска.')
            return
        matches = self.history_manager.search(keyword=keyword)
        if not matches:
            QMessageBox.information(self, 'Результат поиска', f'Сообщений с «{keyword}» не найдено.')
            return
        preview = '\n\n'.join(f"{item['timestamp']}: {item['content']}" for item in matches[-3:])
        QMessageBox.information(self, 'Результат поиска', f'Найдено {len(matches)} сообщений.\n\n{preview}')

    def _quick_set_temperature(self, value: Optional[str]):
        raw = (value or '').strip()
        try:
            temp = float(raw)
        except ValueError:
            QMessageBox.warning(self, 'Некорректное значение', 'Введите число, например 0.7.')
            return
        self.settings.update_generation_config({'temperature': temp})
        self.neural_network.update_generation_params({'temperature': temp})
        QMessageBox.information(self, 'Температура обновлена', f'Новая температура: {temp}')

    def _update_dashboard_metrics(self):
        """Обновляет метрики (теперь только для окна статистики)"""
        # Обновляем окно статистики, если оно открыто
        self._update_statistics_dialog()

    def _message_date(self, message: Dict) -> Optional[date]:
        ts = message.get('timestamp')
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts).date()
        except ValueError:
            return None