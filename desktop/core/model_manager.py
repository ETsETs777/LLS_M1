"""
Менеджер модели для загрузки и управления языковыми моделями.
Поддерживает валидацию, загрузку и генерацию текста.
"""
import os
from typing import Dict, Any, Optional

from desktop.utils.logger import get_logger

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
    from transformers.generation import GenerationMixin
    TRANSFORMERS_AVAILABLE = True
except Exception as e:
    torch = None  # type: ignore
    GenerationConfig = None  # type: ignore
    GenerationMixin = object  # type: ignore
    TRANSFORMERS_AVAILABLE = False
    logger = get_logger('desktop.core.model_manager')
    logger.warning(f"Transformers недоступны: {e}")

logger = get_logger('desktop.core.model_manager')


class ModelManager:
    """
    Менеджер для управления языковой моделью.
    
    Отвечает за валидацию, загрузку модели и генерацию текста.
    Поддерживает fallback режим при отсутствии transformers.
    """
    
    def __init__(self, model_path: str, generation_params: Dict[str, Any]):
        """
        Инициализирует менеджер модели.
        
        Args:
            model_path: Путь к директории с моделью
            generation_params: Параметры генерации (temperature, top_p, etc.)
        """
        self.model_path = model_path
        self.generation_params = generation_params or {}
        self.device: Optional[torch.device] = None
        self.tokenizer = None
        self.model: Optional[GenerationMixin] = None
        self.is_fallback = not TRANSFORMERS_AVAILABLE
        self.fallback_history: list = []
        self.load_error: Optional[str] = None
        
        if not self.is_fallback:
            try:
                # Проверяем модель перед загрузкой
                validation_result = self._validate_model()
                if not validation_result['valid']:
                    self.load_error = validation_result['error']
                    logger.error(f"Ошибка проверки модели: {validation_result['error']}")
                    self.is_fallback = True
                else:
                    self._load_resources()
            except Exception as e:
                self.load_error = str(e)
                logger.exception(f"Ошибка загрузки модели: {e}")
                self.is_fallback = True
        else:
            logger.warning("Используется fallback режим - transformers недоступны")

    def _validate_model(self) -> Dict[str, Any]:
        """
        Проверяет целостность модели перед загрузкой.
        
        Returns:
            Словарь с ключами 'valid' (bool) и 'error' (str или None)
        """
        resolved_path = os.path.abspath(self.model_path)
        logger.debug(f"Валидация модели по пути: {resolved_path}")
        
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
    
    def _load_resources(self) -> None:
        """
        Загружает токенизатор и модель в память.
        
        Raises:
            FileNotFoundError: Если модель не найдена
            Exception: При ошибках загрузки
        """
        resolved_path = os.path.abspath(self.model_path)
        if not os.path.exists(resolved_path):
            error_msg = f'Модель не найдена по пути {resolved_path}'
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Загрузка модели из: {resolved_path}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(resolved_path, trust_remote_code=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                logger.debug("Установлен pad_token = eos_token")
        except Exception as e:
            logger.exception(f"Ошибка загрузки токенизатора: {e}")
            raise

        logger.info("Загрузка модели (это может занять время)...")
        try:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            device_map = 'auto' if torch.cuda.is_available() else None
            logger.debug(f"Параметры загрузки: dtype={dtype}, device_map={device_map}")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                resolved_path,
                trust_remote_code=True,
                torch_dtype=dtype,
                device_map=device_map
            )
        except Exception as e:
            logger.exception(f"Ошибка загрузки модели: {e}")
            raise
        
        if not torch.cuda.is_available() or self.model.device.type == 'cpu':
            self.device = torch.device('cpu')
            self.model = self.model.to(self.device)
            logger.info("Модель загружена на CPU")
        else:
            self.device = next(self.model.parameters()).device
            logger.info(f"Модель загружена на устройство: {self.device}")
        
        self.model.eval()
        logger.info(f"Модель успешно загружена и готова к использованию на {self.device}")

    def generate(self, prompt: str) -> str:
        """
        Генерирует ответ на основе промпта.
        
        Args:
            prompt: Текст промпта для генерации
        
        Returns:
            Сгенерированный текст
        """
        if not prompt:
            logger.warning("Попытка генерации с пустым промптом")
            return 'Пожалуйста, введите вопрос.'
        
        if self.is_fallback or not TRANSFORMERS_AVAILABLE:
            logger.debug("Использование fallback генерации")
            return self._fallback_generate(prompt)
        
        logger.debug(f"Генерация ответа для промпта длиной {len(prompt)} символов")

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

        try:
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    generation_config=gen_config
                )

            generated_part = output_ids[0][inputs.input_ids.shape[1]:]
            text = self.tokenizer.decode(generated_part, skip_special_tokens=True)
            result = text.strip() or 'Модель не смогла сформировать ответ.'
            logger.debug(f"Сгенерирован ответ длиной {len(result)} символов")
            return result
        except Exception as e:
            logger.exception(f"Ошибка при генерации: {e}")
            return f'Произошла ошибка при генерации ответа: {str(e)}'

    def update_generation_params(self, params: Dict[str, Any]) -> None:
        """
        Обновляет параметры генерации.
        
        Args:
            params: Словарь с новыми параметрами
        """
        if params:
            self.generation_params.update(params)
            logger.debug(f"Обновлены параметры генерации: {params}")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Возвращает метаданные о загруженной модели.
        
        Returns:
            Словарь с информацией о модели (путь, устройство, dtype, etc.)
        """
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
        """
        Генерирует ответ в fallback режиме (без реальной модели).
        
        Args:
            prompt: Текст промпта
        
        Returns:
            Сообщение о недоступности модели
        """
        from desktop.utils.constants import FALLBACK_HISTORY_LIMIT
        
        prompt = prompt.strip()
        if not prompt:
            return 'Пожалуйста, введите вопрос.'
        
        last_user_prompt = prompt.split('Пользователь:')[-1].strip().split('\n')[0]
        self.fallback_history.append(last_user_prompt)
        if len(self.fallback_history) > FALLBACK_HISTORY_LIMIT:
            self.fallback_history.pop(0)
        
        error_msg = ""
        if self.load_error:
            error_msg = f"\n\nПричина: {self.load_error}"
            logger.warning(f"Fallback режим: {self.load_error}")
        
        return f"Извините, полноценная модель сейчас недоступна. Ваш вопрос: \"{last_user_prompt}\". Сообщение сохранено для последующей обработки.{error_msg}"

