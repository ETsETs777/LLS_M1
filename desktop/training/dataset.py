import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from datasets import Dataset, DatasetDict


class ConversationDataset:
    def __init__(self, dataset_path: Optional[str] = None, dataset_paths: Optional[List[str]] = None,
                 max_samples: int = 0):
        self.dataset_paths = [Path(dataset_path)] if dataset_path else []
        if dataset_paths:
            self.dataset_paths.extend([Path(path) for path in dataset_paths])
        self.max_samples = max_samples
        self.records: List[Dict[str, Any]] = []

    def load(self) -> Dataset:
        if not self.dataset_paths:
            raise ValueError("Не указан путь к датасету")
        for path in self.dataset_paths:
            if not path.exists():
                raise FileNotFoundError(f"Файл датасета {path} не найден")
            self._append_from_file(path)
        if not self.records:
            raise ValueError("Датасет не содержит записей")
        return Dataset.from_list(self.records)

    def _append_from_file(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                sample = json.loads(line)
                self.records.append(
                    {
                        "instruction": sample.get("instruction", ""),
                        "input": sample.get("input", ""),
                        "output": sample.get("output", ""),
                        "tags": sample.get("tags", []),
                    }
                )
                if self.max_samples and len(self.records) >= self.max_samples:
                    break

    def create_splits(self, eval_ratio: float = 0.1) -> DatasetDict:
        dataset = self.load()
        return dataset.train_test_split(test_size=eval_ratio)

