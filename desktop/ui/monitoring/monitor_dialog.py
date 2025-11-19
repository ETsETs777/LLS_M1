from typing import Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from desktop.monitoring.system_monitor import ResourceMonitor


class MonitorDialog(QDialog):
    def __init__(self, monitor: ResourceMonitor, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.monitor = monitor
        self.setWindowTitle('Мониторинг ресурсов')
        self.resize(420, 260)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_stats)
        self._init_ui()
        self._update_stats()
        self._timer.start(1000)

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

        self.cpu_label = QLabel('CPU: — %')
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)

        self.ram_label = QLabel('RAM: — %')
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)

        self.gpu_label = QLabel('GPU: нет данных')
        self.gpu_mem_label = QLabel('')

        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.ram_bar)
        layout.addWidget(self.gpu_label)
        layout.addWidget(self.gpu_mem_label)

        button_row = QHBoxLayout()
        button_row.addStretch()
        self.refresh_button = QPushButton('Обновить сейчас')
        self.refresh_button.clicked.connect(self._update_stats)
        self.close_button = QPushButton('Закрыть')
        self.close_button.clicked.connect(self.close)
        button_row.addWidget(self.refresh_button)
        button_row.addWidget(self.close_button)
        layout.addLayout(button_row)

    def _update_stats(self):
        data = self.monitor.collect()
        cpu = int(data.get('cpu_percent', 0))
        ram = int(data.get('memory_percent', 0))
        self.cpu_label.setText(f'CPU загрузка: {cpu}%')
        self.cpu_bar.setValue(cpu)
        self.ram_label.setText(f'RAM использование: {ram}%')
        self.ram_bar.setValue(ram)
        gpu_name = data.get('gpu_name')
        if gpu_name:
            used = data.get('gpu_memory_used', 0)
            total = data.get('gpu_memory_total', 0)
            self.gpu_label.setText(f'GPU: {gpu_name}')
            self.gpu_mem_label.setText(f'Память: {used:.2f} / {total:.2f} ГБ')
        else:
            self.gpu_label.setText('GPU: нет данных')
            self.gpu_mem_label.setText('')

    def closeEvent(self, event):
        if self._timer.isActive():
            self._timer.stop()
        super().closeEvent(event)

