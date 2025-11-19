import os
from typing import Dict, List

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


class ReportPlotter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_metrics(self, history: Dict[str, List[Dict[str, float]]], filename: str) -> str:
        if not history:
            raise ValueError('Нет данных для визуализации')

        fig, ax = plt.subplots(figsize=(8, 4.5))
        has_data = False

        for metric_name, points in history.items():
            if not points:
                continue
            steps = [point['step'] for point in points]
            values = [point['value'] for point in points]
            ax.plot(steps, values, label=metric_name)
            has_data = True

        if not has_data:
            raise ValueError('История метрик пуста')

        ax.set_xlabel('Step')
        ax.set_ylabel('Value')
        ax.set_title('Training metrics')
        ax.grid(True, alpha=0.3)
        ax.legend()

        output_path = os.path.join(self.output_dir, filename)
        fig.tight_layout()
        fig.savefig(output_path)
        plt.close(fig)
        return output_path

