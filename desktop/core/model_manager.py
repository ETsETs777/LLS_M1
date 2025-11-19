import os
from typing import Dict, Any

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
    from transformers.generation import GenerationMixin
    TRANSFORMERS_AVAILABLE = True
except Exception:
    torch = None  # type: ignore
    GenerationConfig = None  # type: ignore
    GenerationMixin = object  # type: ignore
    TRANSFORMERS_AVAILABLE = False


class ModelManager:
    def __init__(self, model_path: str, generation_params: Dict[str, Any]):
        self.model_path = model_path
        self.generation_params = generation_params or {}
        self.device = None
        self.tokenizer = None
        self.model: GenerationMixin = None
        self.is_fallback = not TRANSFORMERS_AVAILABLE
        self.fallback_history = []
        if not self.is_fallback:
            try:
                self._load_resources()
            except Exception:
                self.is_fallback = True

    def _load_resources(self):
        resolved_path = os.path.abspath(self.model_path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f'Модель не найдена по пути {resolved_path}')

        self.tokenizer = AutoTokenizer.from_pretrained(resolved_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(resolved_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()

    def generate(self, prompt: str) -> str:
        if not prompt:
            return 'Пожалуйста, введите вопрос.'
        if self.is_fallback or not TRANSFORMERS_AVAILABLE:
            return self._fallback_generate(prompt)

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

    def update_generation_params(self, params: Dict[str, Any]):
        self.generation_params.update(params or {})

    def get_metadata(self) -> Dict[str, Any]:
        if self.is_fallback or not self.model:
            return {
                'model_path': 'fallback',
                'device': 'cpu',
                'dtype': 'N/A',
                'context_length': 0,
                'vocab_size': 0,
                'fallback': True
            }
        config = getattr(self.model, 'config', None)
        context = None
        if config is not None:
            context = getattr(config, 'n_positions', None) or getattr(config, 'max_position_embeddings', None)
        return {
            'model_path': os.path.abspath(self.model_path),
            'device': str(self.device),
            'dtype': str(getattr(self.model, 'dtype', 'unknown')),
            'context_length': context,
            'vocab_size': getattr(config, 'vocab_size', None),
            'fallback': False
        }

    def _fallback_generate(self, prompt: str) -> str:
        prompt = prompt.strip()
        if not prompt:
            return 'Пожалуйста, введите вопрос.'
        last_user_prompt = prompt.split('Пользователь:')[-1].strip().split('\n')[0]
        self.fallback_history.append(last_user_prompt)
        if len(self.fallback_history) > 5:
            self.fallback_history.pop(0)
        return f"Извините, полноценная модель сейчас недоступна. Ваш вопрос: \"{last_user_prompt}\". Сообщение сохранено для последующей обработки."

