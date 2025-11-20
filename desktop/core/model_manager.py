import os
from typing import Dict, Any, Optional

from desktop.utils.logger import get_logger

# Импорт logger после проверки torch, чтобы избежать проблем с DLL
TRANSFORMERS_AVAILABLE = False
torch = None
GenerationConfig = None
GenerationMixin = object

try:
    # Пытаемся импортировать torch отдельно
    import torch
    # Если torch импортирован успешно, пробуем transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
    from transformers.generation import GenerationMixin
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    # Если модуль не найден - это нормально для fallback режима
    pass
except Exception as e:
    # Другие ошибки (включая DLL ошибки) - логируем, но продолжаем работу
    pass

# Создаем logger после попытки импорта
logger = get_logger('desktop.core.model_manager')

if not TRANSFORMERS_AVAILABLE:
    logger.warning(f"Transformers недоступны - приложение будет работать в fallback режиме. "
                   f"Модель не будет загружаться до решения проблемы с torch/transformers.")


class ModelManager:
    def __init__(self, model_path: str, generation_params: Dict[str, Any]):
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
        
        # Проверка доступной памяти
        try:
            import psutil
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            total_memory_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"Проверка памяти: {available_memory_gb:.2f} GB доступно из {total_memory_gb:.2f} GB")
            
            # Для модели ~20B параметров в float16 нужно минимум ~40GB в памяти
            # С оффлоадингом на диск можно работать с минимальной памятью (4GB для системы + буферы)
            # Снижаем требования до минимума для работы с оффлоадингом
            min_required_gb = 4.0  # Минимум для работы с оффлоадингом (4GB для системы + буферы)
            if available_memory_gb < min_required_gb:
                return {
                    'valid': False,
                    'error': f'Недостаточно памяти. Доступно: {available_memory_gb:.2f} GB, требуется минимум: {min_required_gb} GB для работы с оффлоадингом на диск. Закройте другие приложения.'
                }
            else:
                # Предупреждаем, что работа будет медленной, если памяти мало
                if available_memory_gb < 8.0:
                    logger.warning(f"Мало доступной памяти ({available_memory_gb:.2f} GB). Загрузка модели будет очень медленной с оффлоадингом на диск.")
        except Exception as e:
            logger.warning(f"Не удалось проверить память: {e}")
        index_file = os.path.join(resolved_path, 'model.safetensors.index.json')
        if os.path.exists(index_file):
            try:
                import json
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                weight_map = index_data.get('weight_map', {})
                if weight_map:
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
        model_files = [f for f in os.listdir(resolved_path) 
                      if f.endswith(('.safetensors', '.bin')) or f.startswith('pytorch_model')]
        if not model_files:
            return {
                'valid': False,
                'error': 'Не найдены файлы весов модели (.safetensors или .bin)'
            }
        
        return {'valid': True, 'error': None}
    
    def _load_resources(self) -> None:
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
            # Оптимизация для работы с ограниченной памятью
            import psutil
            available_memory_gb = psutil.virtual_memory().available / (1024**3)
            total_memory_gb = psutil.virtual_memory().total / (1024**3)
            logger.info(f"Доступная память: {available_memory_gb:.2f} GB из {total_memory_gb:.2f} GB")
            
            # Для модели ~20B параметров в float16 нужно ~40GB
            # С оффлоадингом можно работать с меньшей памятью (минимум 4GB для системы)
            # Рекомендуем использовать float16 и оффлоадинг на диск
            dtype = torch.float16
            device_map = 'auto' if torch.cuda.is_available() else 'cpu'
            
            # Параметры для экономии памяти
            load_kwargs = {
                'trust_remote_code': True,
                'dtype': dtype,  # Используем dtype вместо устаревшего torch_dtype
                'low_cpu_mem_usage': True,  # Критично для экономии памяти
            }
            
            if not torch.cuda.is_available():
                # Для CPU: не используем device_map и offload_folder, 
                # позволяем transformers самому управлять загрузкой с low_cpu_mem_usage
                # Это может быть медленно, но более надежно
                logger.warning(f"ВНИМАНИЕ: Модель очень большая (~82GB). Загрузка на CPU может быть очень медленной.")
                logger.warning(f"Рекомендуется минимум 32GB RAM для комфортной работы.")
                logger.info("Используется low_cpu_mem_usage для минимизации использования памяти.")
            else:
                load_kwargs['device_map'] = device_map
            
            logger.debug(f"Параметры загрузки: {load_kwargs}")
            logger.info("Начало загрузки модели... Это может занять много времени и памяти!")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                resolved_path,
                **load_kwargs
            )
        except Exception as e:
            logger.exception(f"Ошибка загрузки модели: {e}")
            raise
        
        if not torch.cuda.is_available() or (hasattr(self.model, 'device') and self.model.device.type == 'cpu'):
            self.device = torch.device('cpu')
            if not hasattr(self.model, 'device') or self.model.device.type != 'cpu':
                # Модель может использовать device_map с оффлоадингом
                logger.info("Модель загружена на CPU с оффлоадингом")
            else:
                logger.info("Модель загружена на CPU")
        else:
            self.device = next(self.model.parameters()).device if hasattr(self.model, 'parameters') else torch.device('cpu')
            logger.info(f"Модель загружена на устройство: {self.device}")
        
        self.model.eval()
        logger.info(f"Модель успешно загружена и готова к использованию на {self.device}")

    def generate(self, prompt: str) -> str:
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
        if params:
            self.generation_params.update(params)
            logger.debug(f"Обновлены параметры генерации: {params}")

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

