import os
from typing import Dict, Any

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from transformers.generation import GenerationMixin


class ModelManager:
    def __init__(self, model_path: str, generation_params: Dict[str, Any]):
        self.model_path = model_path
        self.generation_params = generation_params or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.model: GenerationMixin = None
        self._load_resources()

    def _load_resources(self):
        resolved_path = os.path.abspath(self.model_path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f'Модель не найдена по пути {resolved_path}')

        self.tokenizer = AutoTokenizer.from_pretrained(resolved_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(resolved_path)
        self.model.to(self.device)
        self.model.eval()

    def generate(self, prompt: str) -> str:
        if not prompt:
            return 'Пожалуйста, введите вопрос.'

        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        gen_config = GenerationConfig(
            max_new_tokens=self.generation_params.get('max_new_tokens', 200),
            temperature=self.generation_params.get('temperature', 0.8),
            top_p=self.generation_params.get('top_p', 0.95),
            do_sample=self.generation_params.get('do_sample', True),
            repetition_penalty=self.generation_params.get('repetition_penalty', 1.05),
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                generation_config=gen_config
            )

        generated_part = output_ids[0][inputs.input_ids.shape[1]:]
        text = self.tokenizer.decode(generated_part, skip_special_tokens=True)
        return text.strip() or 'Модель не смогла сформировать ответ.'

