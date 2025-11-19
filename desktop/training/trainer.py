from typing import Dict, Any, Tuple

from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling

from desktop.training.config import TrainingConfig
from desktop.training.dataset import ConversationDataset
from desktop.training.utils import seed_everything
from desktop.training.reports.report_builder import ReportBuilder
from desktop.training.reports.plotter import ReportPlotter
from desktop.training.evaluation import EvaluationRunner


class FineTuningTrainer:
    def __init__(self, config: TrainingConfig):
        self.config = config
        seed_everything()
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_path, use_fast=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(self.config.model_path)
        self.peft_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            task_type="CAUSAL_LM"
        )
        self.model = get_peft_model(self.model, self.peft_config)
        self.dataset_loader = ConversationDataset(
            dataset_path=self.config.dataset_path,
            dataset_paths=self.config.dataset_paths
        )

    def build_training_arguments(self) -> TrainingArguments:
        return TrainingArguments(
            output_dir=self.config.output_dir,
            max_steps=self.config.max_steps,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            save_steps=self.config.save_steps,
            logging_steps=self.config.logging_steps,
            fp16=self.config.fp16,
            save_total_limit=2,
            report_to="none",
            remove_unused_columns=False,
        )

    def tokenize_function(self, sample: Dict[str, str]) -> Dict[str, Any]:
        input_text = f"Инструкция:\n{sample['instruction']}\nВвод:\n{sample['input']}\nОтвет:\n{sample['output']}"
        tokenized = self.tokenizer(
            input_text,
            truncation=True,
            max_length=self.config.max_seq_length,
            padding="max_length",
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized

    def _prepare_datasets(self) -> Tuple[Any, Any]:
        raw_dataset = self.dataset_loader.load()
        dataset_dict = None
        eval_dataset = None
        if self.config.eval_dataset_path:
            eval_loader = ConversationDataset(dataset_path=self.config.eval_dataset_path)
            eval_dataset = eval_loader.load()
        else:
            dataset_dict = raw_dataset.train_test_split(test_size=0.1)
        train_dataset = dataset_dict['train'] if dataset_dict else raw_dataset
        eval_dataset = dataset_dict['test'] if dataset_dict else eval_dataset
        tokenized_train = train_dataset.map(self.tokenize_function, remove_columns=train_dataset.column_names)
        tokenized_eval = None
        if eval_dataset:
            tokenized_eval = eval_dataset.map(self.tokenize_function, remove_columns=eval_dataset.column_names)
        return tokenized_train, tokenized_eval

    def _collect_history(self, log_history):
        metric_history: Dict[str, list] = {}
        for entry in log_history:
            step = entry.get('step')
            if step is None:
                continue
            for key in ('loss', 'eval_loss', 'eval_accuracy', 'eval_perplexity'):
                if key in entry and isinstance(entry[key], (int, float)):
                    metric_history.setdefault(key, []).append({'step': step, 'value': entry[key]})
        return metric_history

    def run(self):
        train_dataset, eval_dataset = self._prepare_datasets()
        data_collator = DataCollatorForLanguageModeling(self.tokenizer, mlm=False)
        trainer = Trainer(
            model=self.model,
            args=self.build_training_arguments(),
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )
        trainer.train()
        metrics = {}
        if eval_dataset:
            evaluator = EvaluationRunner(trainer, self.config.evaluation_metric)
            metrics = evaluator.run()
        trainer.save_model(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)
        report_dir = self.config.report_dir or self.config.output_dir
        builder = ReportBuilder(report_dir)
        report_meta = builder.save(metrics, {
            'max_steps': self.config.max_steps,
            'learning_rate': self.config.learning_rate,
            'dataset_paths': self.config.dataset_paths or [self.config.dataset_path],
            'eval_dataset_path': self.config.eval_dataset_path
        })
        history = self._collect_history(trainer.state.log_history)
        if history:
            plotter = ReportPlotter(report_dir)
            plot_name = f"metrics-{report_meta['timestamp']}.png"
            plot_path = plotter.plot_metrics(history, plot_name)
            report_meta['plot'] = plot_path

