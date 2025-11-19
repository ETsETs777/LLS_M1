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
        self.load_error = None
        if not self.is_fallback:
            try:
                # Проверяем модель перед загрузкой
                validation_result = self._validate_model()
                if not validation_result['valid']:
                    self.load_error = validation_result['error']
                    print(f"Ошибка проверки модели: {validation_result['error']}")
                    self.is_fallback = True
                else:
                    self._load_resources()
            except Exception as e:
                self.load_error = str(e)
                print(f"Ошибка загрузки модели: {e}")
                self.is_fallback = True

    def _validate_model(self) -> Dict[str, Any]:
        """Проверяет целостность модели перед загрузкой"""
        resolved_path = os.path.abspath(self.model_path)
        
        if not os.path.exists(resolved_path):
            return {
                'valid': False,
                'error': f'Путь к модели не существует: {resolved_path}'
            }
        
        if not os.path.isdir(resolved_path):
            return {
                'valid': False,
                'error': f'Путь к модели не является директорией: {resolved_path}'
            }
        
        # Проверяем наличие обязательных файлов
        required_files = ['config.json', 'tokenizer.json']
        missing_files = []
        for file in required_files:
            file_path = os.path.join(resolved_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            return {
                'valid': False,
                'error': f'Отсутствуют обязательные файлы: {", ".join(missing_files)}'
            }
        
        # Проверяем sharded модели (разбитые на части)
        index_file = os.path.join(resolved_path, 'model.safetensors.index.json')
        if os.path.exists(index_file):
            try:
                import json
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                weight_map = index_data.get('weight_map', {})
                if weight_map:
                    # Получаем уникальные имена файлов из weight_map
                    required_shards = set(weight_map.values())
                    existing_files = set(os.listdir(resolved_path))
                    
                    missing_shards = []
                    for shard in required_shards:
                        if shard not in existing_files:
                            missing_shards.append(shard)
                    
                    if missing_shards:
                        return {
                            'valid': False,
                            'error': f'Модель неполная. Отсутствуют файлы: {", ".join(sorted(missing_shards)[:5])}{"..." if len(missing_shards) > 5 else ""} ({len(missing_shards)} из {len(required_shards)})'
                        }
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Ошибка при проверке индекса модели: {str(e)}'
                }
        
        # Проверяем наличие хотя бы одного файла модели
        model_files = [f for f in os.listdir(resolved_path) 
                      if f.endswith(('.safetensors', '.bin')) or f.startswith('pytorch_model')]
        if not model_files:
            return {
                'valid': False,
                'error': 'Не найдены файлы весов модели (.safetensors или .bin)'
            }
        
        return {'valid': True, 'error': None}
    
    def _load_resources(self):
        resolved_path = os.path.abspath(self.model_path)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f'Модель не найдена по пути {resolved_path}')

        print(f"Загрузка модели из: {resolved_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(resolved_path, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print("Загрузка модели (это может занять время)...")
        self.model = AutoModelForCausalLM.from_pretrained(
            resolved_path,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map='auto' if torch.cuda.is_available() else None
        )
        
        if not torch.cuda.is_available() or self.model.device.type == 'cpu':
            self.device = torch.device('cpu')
            self.model = self.model.to(self.device)
        else:
            self.device = next(self.model.parameters()).device
        
        self.model.eval()
        print(f"Модель успешно загружена на устройство: {self.device}")

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
        
        error_msg = ""
        if self.load_error:
            error_msg = f"\n\nПричина: {self.load_error}"
        
        return f"Извините, полноценная модель сейчас недоступна. Ваш вопрос: \"{last_user_prompt}\". Сообщение сохранено для последующей обработки.{error_msg}"

