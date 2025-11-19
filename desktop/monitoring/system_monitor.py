import os
import time
from pathlib import Path
from typing import Dict, Any

import psutil

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None


class ResourceMonitor:
    def __init__(self, log_path: str):
        self.log_path = log_path
        Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)

    def collect(self) -> Dict[str, Any]:
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=None),
            'memory_percent': psutil.virtual_memory().percent,
            'timestamp': time.time()
        }
        if TORCH_AVAILABLE and torch is not None and torch.cuda.is_available():
            try:
                gpu_index = torch.cuda.current_device()
                total_mem = torch.cuda.get_device_properties(gpu_index).total / (1024 ** 3)
                free_mem, total = torch.cuda.mem_get_info()
                used_mem = (total - free_mem) / (1024 ** 3)
                metrics.update({
                    'gpu_name': torch.cuda.get_device_name(gpu_index),
                    'gpu_memory_total': round(total_mem, 2),
                    'gpu_memory_used': round(used_mem, 2)
                })
            except Exception:
                # Если возникла ошибка при работе с CUDA, просто пропускаем GPU метрики
                pass
        self._log(metrics)
        return metrics

    def _log(self, metrics: Dict[str, Any]):
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | CPU {metrics['cpu_percent']}% | RAM {metrics['memory_percent']}%"
        if 'gpu_name' in metrics:
            line += f" | GPU {metrics['gpu_name']} {metrics['gpu_memory_used']}/{metrics['gpu_memory_total']} GB"
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')


