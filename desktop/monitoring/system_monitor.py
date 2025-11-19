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
        self._gpu_method = None  # Кешируем рабочий метод определения GPU
        self._gpu_errors_shown = False  # Флаг для однократного вывода ошибок
        
        # Очищаем лог-файл при запуске
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write('')  # Очищаем файл
        except Exception:
            pass  # Если не удалось очистить, продолжаем работу

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
        # Если уже нашли рабочий метод, используем его
        if self._gpu_method == 'torch':
            return self._get_gpu_torch()
        elif self._gpu_method == 'pynvml':
            return self._get_gpu_pynvml()
        elif self._gpu_method == 'wmi':
            return self._get_gpu_wmi()
        elif self._gpu_method == 'none':
            return {}
        
        # Пробуем найти рабочий метод
        errors = []
        
        # Способ 1: через PyTorch
        if TORCH_AVAILABLE and torch is not None:
            result = self._get_gpu_torch()
            if result:
                self._gpu_method = 'torch'
                return result
            else:
                errors.append("PyTorch: CUDA недоступен")
        
        # Способ 2: через pynvml (NVIDIA Management Library)
        if NVML_AVAILABLE and pynvml is not None:
            result = self._get_gpu_pynvml()
            if result:
                self._gpu_method = 'pynvml'
                return result
            else:
                errors.append("pynvml: NVML библиотека не найдена")
        
        # Способ 3: через WMI (только для Windows)
        if os.name == 'nt':
            result = self._get_gpu_wmi()
            if result:
                self._gpu_method = 'wmi'
                return result
            else:
                errors.append("WMI: не удалось получить информацию")
        
        # Если ничего не сработало, выводим ошибки один раз
        if not self._gpu_errors_shown:
            print("GPU не обнаружен. Попытки:")
            for error in errors:
                print(f"  - {error}")
            self._gpu_errors_shown = True
        
        self._gpu_method = 'none'
        return {}
    
    def _get_gpu_torch(self) -> Dict[str, Any]:
        """Получает информацию о GPU через PyTorch"""
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
        except Exception:
            pass
        return {}
    
    def _get_gpu_pynvml(self) -> Dict[str, Any]:
        """Получает информацию о GPU через pynvml"""
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
        except Exception:
            pass
        finally:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
        return {}
    
    def _get_gpu_wmi(self) -> Dict[str, Any]:
        """Получает информацию о GPU через WMI (Windows)"""
        try:
            import wmi
            c = wmi.WMI()
            
            for gpu in c.Win32_VideoController():
                name = gpu.Name if gpu.Name else "Unknown"
                
                # Пропускаем базовые/виртуальные адаптеры
                if "Basic" in name or "Microsoft" in name or "Virtual" in name:
                    continue
                
                # Пытаемся получить RAM разными способами
                ram = gpu.AdapterRAM if gpu.AdapterRAM else 0
                
                # Отладочная информация
                if not self._gpu_errors_shown:
                    print(f"  WMI нашел видеокарту: {name}")
                    print(f"    AdapterRAM: {ram} bytes")
                    if hasattr(gpu, 'AdapterDACType'):
                        print(f"    AdapterDACType: {gpu.AdapterDACType}")
                
                # Если RAM отрицательный или нулевой, это может быть переполнение или неопределенное значение
                if ram and int(ram) > 0:
                    total_mem = int(ram) / (1024 ** 3)
                elif ram and int(ram) < 0:
                    # Отрицательное значение может означать переполнение uint32
                    # Пробуем исправить (добавляем 2^32)
                    corrected_ram = int(ram) + (2 ** 32)
                    total_mem = corrected_ram / (1024 ** 3)
                    if not self._gpu_errors_shown:
                        print(f"    Исправленная память: {corrected_ram} bytes = {total_mem:.2f} GB")
                else:
                    # Не можем определить память, но видеокарта есть
                    # Для AMD RX 580 обычно 4 или 8 GB
                    if not self._gpu_errors_shown:
                        print(f"    Память не определена, используем значение по умолчанию")
                    total_mem = 0  # Не знаем точно
                
                # Возвращаем информацию о дискретной видеокарте
                if "AMD" in name or "NVIDIA" in name or "Radeon" in name or "GeForce" in name or "Intel Arc" in name:
                    return {
                        'gpu_name': name,
                        'gpu_memory_total': round(total_mem, 2) if total_mem > 0 else 0,
                        'gpu_memory_used': 0  # WMI не предоставляет используемую память
                    }
                
        except Exception as e:
            if not self._gpu_errors_shown:
                print(f"  WMI exception: {e}")
        return {}

    def _log(self, metrics: Dict[str, Any]):
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | CPU {metrics['cpu_percent']}% | RAM {metrics['memory_percent']}%"
        if 'gpu_name' in metrics:
            line += f" | GPU {metrics['gpu_name']} {metrics['gpu_memory_used']}/{metrics['gpu_memory_total']} GB"
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')


