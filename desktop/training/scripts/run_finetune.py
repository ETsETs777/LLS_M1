import json
import os
from pathlib import Path

from desktop.training.pipeline import FineTuningPipeline


def run_from_config(config_path: str):
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Конфигурация {config_path} не найдена")
    with path.open("r", encoding="utf-8") as f:
        config_data = json.load(f)
    pipeline = FineTuningPipeline(config_data)
    pipeline.run()


if __name__ == "__main__":
    default_config = os.path.join(os.path.dirname(__file__), "..", "configs", "example.json")
    run_from_config(default_config)

