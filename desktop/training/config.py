from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class TrainingConfig:
    model_path: str
    output_dir: str
    dataset_path: Optional[str] = None
    dataset_paths: Optional[List[str]] = None
    eval_dataset_path: Optional[str] = None
    max_steps: int = 1000
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    warmup_steps: int = 50
    save_steps: int = 100
    logging_steps: int = 10
    fp16: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    max_seq_length: int = 1024
    report_dir: Optional[str] = None
    evaluation_metric: str = 'perplexity'
    status_file: Optional[str] = None

    @classmethod
    def from_dict(cls, values: Dict[str, Any]) -> "TrainingConfig":
        return cls(
            model_path=values.get("model_path"),
            output_dir=values.get("output_dir"),
            dataset_path=values.get("dataset_path"),
            dataset_paths=values.get("dataset_paths"),
            eval_dataset_path=values.get("eval_dataset_path"),
            max_steps=values.get("max_steps", 1000),
            per_device_train_batch_size=values.get("per_device_train_batch_size", 2),
            gradient_accumulation_steps=values.get("gradient_accumulation_steps", 4),
            learning_rate=values.get("learning_rate", 2e-5),
            warmup_steps=values.get("warmup_steps", 50),
            save_steps=values.get("save_steps", 100),
            logging_steps=values.get("logging_steps", 10),
            fp16=values.get("fp16", False),
            lora_r=values.get("lora_r", 8),
            lora_alpha=values.get("lora_alpha", 16),
            lora_dropout=values.get("lora_dropout", 0.05),
            max_seq_length=values.get("max_seq_length", 1024),
            report_dir=values.get("report_dir"),
            evaluation_metric=values.get("evaluation_metric", 'perplexity'),
            status_file=values.get("status_file"),
        )

