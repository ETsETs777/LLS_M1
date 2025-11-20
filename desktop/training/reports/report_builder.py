import json
import os
from datetime import datetime
from typing import Dict, Any


class ReportBuilder:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save(self, metrics: Dict[str, Any], config: Dict[str, Any]):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        json_path = os.path.join(self.output_dir, f'report-{timestamp}.json')
        md_path = os.path.join(self.output_dir, f'report-{timestamp}.md')
        payload = {
            'timestamp': timestamp,
            'metrics': metrics,
            'config': config
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._markdown(payload))
        return {'json': json_path, 'markdown': md_path, 'timestamp': timestamp}

    def _markdown(self, payload: Dict[str, Any]) -> str:
        lines = [
            f"# Отчет об обучении\n",
            f"**Время:** {payload['timestamp']}\n",
            f"\n## Метрики\n"
        ]
        for key, value in payload['metrics'].items():
            lines.append(f"- {key}: {value}")
        lines.append("\n## Конфигурация\n")
        for key, value in payload['config'].items():
            lines.append(f"- {key}: {value}")
        return '\n'.join(lines)


