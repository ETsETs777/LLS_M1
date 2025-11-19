from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPlainTextEdit
)
from PyQt5.QtCore import Qt

from desktop.plugins.manager import PluginManager


class PluginDialog(QDialog):
    def __init__(self, manager: PluginManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle('Плагины')
        self.resize(520, 420)
        self._init_ui()
        self._refresh_list()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        control_layout = QHBoxLayout()
        self.enable_button = QPushButton('Включить')
        self.enable_button.clicked.connect(self._enable_selected)
        self.disable_button = QPushButton('Отключить')
        self.disable_button.clicked.connect(self._disable_selected)
        control_layout.addWidget(self.enable_button)
        control_layout.addWidget(self.disable_button)
        layout.addLayout(control_layout)

        execute_layout = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText('Тестовый запрос для плагина')
        execute_layout.addWidget(self.query_input)
        run_button = QPushButton('Запустить')
        run_button.clicked.connect(self._execute_plugin)
        execute_layout.addWidget(run_button)
        layout.addLayout(execute_layout)

        self.result_view = QPlainTextEdit()
        self.result_view.setReadOnly(True)
        layout.addWidget(self.result_view)

    def _refresh_list(self):
        self.list_widget.clear()
        for plugin in self.manager.list_plugins():
            status = 'Включен' if plugin.enabled else 'Выключен'
            roles_hint = ''
            if plugin.allowed_roles:
                roles_hint = f"\nДоступно ролям: {', '.join(plugin.allowed_roles)}"
            text = f"{plugin.name} ({status})\n{plugin.description}{roles_hint}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, plugin.id)
            self.list_widget.addItem(item)

    def _selected_plugin_id(self):
        item = self.list_widget.currentItem()
        if not item:
            return None
        return item.data(Qt.UserRole)

    def _enable_selected(self):
        plugin_id = self._selected_plugin_id()
        if not plugin_id:
            return
        self.manager.enable_plugin(plugin_id)
        self._refresh_list()

    def _disable_selected(self):
        plugin_id = self._selected_plugin_id()
        if not plugin_id:
            return
        self.manager.disable_plugin(plugin_id)
        self._refresh_list()

    def _execute_plugin(self):
        plugin_id = self._selected_plugin_id()
        if not plugin_id:
            return
        response = self.manager.execute(plugin_id, self.query_input.text())
        self.result_view.setPlainText(response)


