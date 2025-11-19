import os
import time
from pathlib import Path
from typing import Dict, Any

import psutil

try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    TORCH_AVAILABLE = False
    torch = None
    print(f"PyTorch недоступен: {e}")

# Альтернативный способ проверки GPU через pynvml (NVIDIA) или других библиотек
try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    pynvml = None


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
        
        # Пытаемся получить информацию о GPU
        gpu_info = self._get_gpu_info()
        if gpu_info:
            metrics.update(gpu_info)
        
        self._log(metrics)
        return metrics
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Получает информацию о GPU разными способами"""
        # Способ 1: через PyTorch
        if TORCH_AVAILABLE and torch is not None:
            try:
                if torch.cuda.is_available():
                    gpu_index = torch.cuda.current_device()
                    total_mem = torch.cuda.get_device_properties(gpu_index).total / (1024 ** 3)
                    free_mem, total = torch.cuda.mem_get_info()
                    used_mem = (total - free_mem) / (1024 ** 3)
                    return {
                        'gpu_name': torch.cuda.get_device_name(gpu_index),
                        'gpu_memory_total': round(total_mem, 2),
                        'gpu_memory_used': round(used_mem, 2)
                    }
            except Exception as e:
                print(f"Ошибка при получении информации через PyTorch: {e}")
        
        # Способ 2: через pynvml (NVIDIA Management Library)
        if NVML_AVAILABLE and pynvml is not None:
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    name = pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode('utf-8')
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    total_mem = mem_info.total / (1024 ** 3)
                    used_mem = mem_info.used / (1024 ** 3)
                    pynvml.nvmlShutdown()
                    return {
                        'gpu_name': name,
                        'gpu_memory_total': round(total_mem, 2),
                        'gpu_memory_used': round(used_mem, 2)
                    }
            except Exception as e:
                print(f"Ошибка при получении информации через pynvml: {e}")
                try:
                    pynvml.nvmlShutdown()
                except:
                    pass
        
        # Способ 3: через WMI (только для Windows)
        if os.name == 'nt':
            try:
                import wmi
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    if gpu.AdapterRAM and int(gpu.AdapterRAM) > 0:
                        total_mem = int(gpu.AdapterRAM) / (1024 ** 3)
                        return {
                            'gpu_name': gpu.Name,
                            'gpu_memory_total': round(total_mem, 2),
                            'gpu_memory_used': 0  # WMI не предоставляет используемую память
                        }
            except Exception as e:
                print(f"Ошибка при получении информации через WMI: {e}")
        
        return {}

    def _log(self, metrics: Dict[str, Any]):
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | CPU {metrics['cpu_percent']}% | RAM {metrics['memory_percent']}%"
        if 'gpu_name' in metrics:
            line += f" | GPU {metrics['gpu_name']} {metrics['gpu_memory_used']}/{metrics['gpu_memory_total']} GB"
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')


