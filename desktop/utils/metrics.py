
import time
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime

from desktop.utils.logger import get_logger

logger = get_logger('desktop.utils.metrics')


class MetricsCollector:
    
    
    def __init__(self, max_history: int = 100):
        
        self.max_history = max_history
        self.response_times: deque = deque(maxlen=max_history)
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self.request_history: List[Dict] = []
        self._start_time = time.time()
    
    def record_response(self, response_time: float, success: bool = True, 
                       error: Optional[str] = None) -> None:
        
        timestamp = datetime.now().isoformat()
        metric = {
            'timestamp': timestamp,
            'response_time': response_time,
            'success': success,
            'error': error
        }
        
        self.response_times.append(response_time)
        self.request_history.append(metric)
        
        if len(self.request_history) > self.max_history:
            self.request_history.pop(0)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error:
                logger.warning(f"Запрос завершился с ошибкой: {error}")
    
    def get_stats(self) -> Dict:
        
        if not self.response_times:
            return {
                'total_requests': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'min_response_time': 0.0,
                'max_response_time': 0.0,
                'uptime': time.time() - self._start_time
            }
        
        total = self.successful_requests + self.failed_requests
        success_rate = (self.successful_requests / total * 100) if total > 0 else 0.0
        
        return {
            'total_requests': total,
            'successful': self.successful_requests,
            'failed': self.failed_requests,
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(sum(self.response_times) / len(self.response_times), 3),
            'min_response_time': round(min(self.response_times), 3),
            'max_response_time': round(max(self.response_times), 3),
            'uptime': round(time.time() - self._start_time, 2)
        }
    
    def reset(self) -> None:
        
        self.response_times.clear()
        self.successful_requests = 0
        self.failed_requests = 0
        self.request_history.clear()
        self._start_time = time.time()
        logger.info("Метрики сброшены")


_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


