from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class StatusPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.setLayout(layout)
        self.cpu_label = QLabel('CPU: --%')
        self.ram_label = QLabel('RAM: --%')
        self.gpu_label = QLabel('GPU: недоступно')
        self.reload_button = QPushButton('🔄')
        self.reload_button.setFixedWidth(32)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.gpu_label)
        layout.addWidget(self.reload_button)
        layout.addStretch()

    def update_metrics(self, metrics):
        self.cpu_label.setText(f"CPU: {metrics.get('cpu_percent', 0):.0f}%")
        self.ram_label.setText(f"RAM: {metrics.get('memory_percent', 0):.0f}%")
        if 'gpu_name' in metrics:
            self.gpu_label.setText(
                f"GPU: {metrics['gpu_name']} {metrics.get('gpu_memory_used', 0):.2f}/{metrics.get('gpu_memory_total', 0):.2f} GB"
            )
        else:
            self.gpu_label.setText('GPU: нет')

