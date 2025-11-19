import os
from pathlib import Path
from typing import Dict, Any

from desktop.training.config import TrainingConfig
from desktop.training.trainer import FineTuningTrainer


class FineTuningPipeline:
    def __init__(self, config_data: Dict[str, Any]):
        self.config = TrainingConfig.from_dict(config_data)
        self.ensure_directories()

    def ensure_directories(self):
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        if self.config.report_dir:
            Path(self.config.report_dir).mkdir(parents=True, exist_ok=True)

    def run(self):
        trainer = FineTuningTrainer(self.config)
        trainer.run()

