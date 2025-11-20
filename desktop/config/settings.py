"""
Менеджер настроек приложения.
Управляет загрузкой, сохранением и валидацией конфигурации.
"""
import json
import os
import shutil
from typing import Dict, Any, Optional

from desktop.utils.logger import get_logger
from desktop.utils.constants import CONFIG_INDENT, CONFIG_ENSURE_ASCII

logger = get_logger('desktop.config.settings')


class SettingsError(Exception):
    """Исключение для ошибок настроек."""
    pass


class Settings:
    def __init__(self):
        """
        Инициализирует менеджер настроек.
        
        Raises:
            SettingsError: При критических ошибках загрузки конфигурации
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(base_dir, 'config')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.backup_file = os.path.join(self.config_dir, 'config.json.backup')
        self._save_pending = False
        self._save_timer = None
        self._cache = {}  # Кэш для часто используемых значений
        self.ensure_config_dir()
        self.load_config()
        
    def ensure_config_dir(self) -> None:
        """Создает директорию конфигурации, если она не существует."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logger.info(f"Создана директория конфигурации: {self.config_dir}")
            
    def load_config(self) -> None:
        """
        Загружает конфигурацию из файла.
        
        При ошибках пытается восстановить из резервной копии или создает новую.
        
        Raises:
            SettingsError: Если не удалось загрузить или восстановить конфигурацию
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.debug("Конфигурация успешно загружена")
                # Валидируем загруженную конфигурацию
                self._validate_config()
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON в конфигурации: {e}")
                if self._restore_from_backup():
                    logger.info("Конфигурация восстановлена из резервной копии")
                else:
                    logger.warning("Создана новая конфигурация по умолчанию")
                    self.config = self.default_config()
                    self.save_config()
            except Exception as e:
                logger.exception(f"Неожиданная ошибка при загрузке конфигурации: {e}")
                if self._restore_from_backup():
                    logger.info("Конфигурация восстановлена из резервной копии")
                else:
                    raise SettingsError(f"Не удалось загрузить конфигурацию: {e}")
        else:
            logger.info("Файл конфигурации не найден, создается конфигурация по умолчанию")
            self.config = self.default_config()
            self.save_config()
    
    def _validate_config(self) -> None:
        """
        Валидирует структуру конфигурации.
        
        Raises:
            SettingsError: Если конфигурация невалидна
        """
        if not isinstance(self.config, dict):
            raise SettingsError("Конфигурация должна быть словарем")
        
        # Проверяем наличие обязательных ключей
        required_keys = ['model_path', 'theme', 'prompt', 'generation']
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            logger.warning(f"Отсутствуют ключи в конфигурации: {missing_keys}")
            # Восстанавливаем недостающие ключи из дефолтной конфигурации
            defaults = self.default_config()
            for key in missing_keys:
                self.config[key] = defaults[key]
            self.save_config()
    
    def _restore_from_backup(self) -> bool:
        """
        Пытается восстановить конфигурацию из резервной копии.
        
        Returns:
            True если восстановление успешно, False иначе
        """
        if os.path.exists(self.backup_file):
            try:
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self._validate_config()
                # Сохраняем восстановленную конфигурацию
                self.save_config()
                return True
            except Exception as e:
                logger.error(f"Ошибка при восстановлении из резервной копии: {e}")
        return False

    def reload(self) -> None:
        """Перезагружает конфигурацию из файла."""
        logger.debug("Перезагрузка конфигурации")
        self.load_config()
            
    def default_config(self) -> Dict[str, Any]:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        knowledge_path = os.path.join(base_dir, 'desktop', 'knowledge', 'articles.json')
        return {
            'model_path': os.path.join(base_dir, 'models'),
            'theme': 'light',
            'prompt': 'Вы являетесь полезным русскоязычным ассистентом, отвечающим кратко и по делу.',
            'generation': {
                'max_new_tokens': 200,
                'temperature': 0.8,
                'top_p': 0.95,
                'do_sample': True,
                'repetition_penalty': 1.05
            },
            'presets': {},
            'history': {
                'export_dir': os.path.join(data_dir, 'exports'),
                'retention_days': 90,
                'default_tags': []
            },
            'training': {
                'reports_dir': os.path.join(data_dir, 'reports'),
                'runs_dir': os.path.join(base_dir, 'training_runs'),
                'status_file': os.path.join(data_dir, 'reports', 'training_status.json')
            },
            'appearance': {
                'accent_color': '#0078d4'
            },
            'backup': {
                'dir': os.path.join(data_dir, 'backups')
            },
            'plugins': {
                'enabled': [],
                'available': {
                    'web_search': {
                        'module': 'desktop.plugins.examples.web_search',
                        'class': 'WebSearchPlugin',
                        'name': 'Поиск в сети',
                        'description': 'Стартовый плагин для интеграции веб-поиска.',
                        'config': {},
                        'allowed_roles': ['admin']
                    },
                    'knowledge_base': {
                        'module': 'desktop.plugins.examples.knowledge_base',
                        'class': 'KnowledgeBasePlugin',
                        'name': 'База знаний',
                        'description': 'Ответы на основе локальной коллекции статей.',
                        'config': {
                            'data_path': knowledge_path
                        },
                        'allowed_roles': ['analyst', 'admin']
                    }
                }
            },
            'updater': {
                'auto_check': True,
                'channel': 'stable',
                'verify_models_on_start': True
            },
            'database': {
                'path': os.path.join(base_dir, 'data', 'database', 'app.db')
            },
            'current_user_id': None
        }
            
    def save_config(self, immediate: bool = False) -> None:
        """
        Сохраняет конфигурацию в файл.
        
        Использует батчинг для уменьшения количества операций записи.
        
        Args:
            immediate: Если True, сохраняет немедленно, иначе использует батчинг
        
        Raises:
            SettingsError: При ошибках сохранения
        """
        if immediate:
            self._do_save()
        else:
            # Батчинг: откладываем сохранение
            self._save_pending = True
            if self._save_timer is None:
                from PyQt5.QtCore import QTimer
                self._save_timer = QTimer()
                self._save_timer.setSingleShot(True)
                self._save_timer.timeout.connect(self._do_save)
                self._save_timer.start(500)  # Сохраняем через 500мс после последнего изменения
            else:
                # Перезапускаем таймер
                self._save_timer.stop()
                self._save_timer.start(500)
    
    def _do_save(self) -> None:
        """
        Выполняет фактическое сохранение конфигурации.
        
        Raises:
            SettingsError: При ошибках сохранения
        """
        if not self._save_pending:
            return
        
        try:
            # Создаем резервную копию перед сохранением
            if os.path.exists(self.config_file):
                try:
                    shutil.copy2(self.config_file, self.backup_file)
                    logger.debug("Создана резервная копия конфигурации")
                except Exception as e:
                    logger.warning(f"Не удалось создать резервную копию: {e}")
            
            # Сохраняем конфигурацию
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=CONFIG_ENSURE_ASCII, indent=CONFIG_INDENT)
            logger.debug("Конфигурация сохранена")
            self._save_pending = False
            self._cache.clear()  # Очищаем кэш при сохранении
        except Exception as e:
            logger.exception(f"Ошибка при сохранении конфигурации: {e}")
            raise SettingsError(f"Не удалось сохранить конфигурацию: {e}")
            
    def get_model_path(self) -> str:
        return self.config.get('model_path') or self.default_config()['model_path']

    def set_model_path(self, path: str):
        self.config['model_path'] = path
        self.save_config()

    def get_database_path(self) -> str:
        database = self.config.get('database', self.default_config()['database'])
        path = database.get('path')
        if not path:
            path = self.default_config()['database']['path']
        self.config['database'] = database
        self.save_config()
        return path
        
    def get_theme(self) -> str:
        """Возвращает текущую тему с использованием кэша."""
        cache_key = 'theme'
        if cache_key not in self._cache:
            self._cache[cache_key] = self.config.get('theme', 'light')
        return self._cache[cache_key]
        
    def set_theme(self, theme: str) -> None:
        """Устанавливает тему."""
        self.config['theme'] = theme
        self._cache['theme'] = theme  # Обновляем кэш
        self.save_config()

    def get_generation_config(self) -> Dict[str, Any]:
        return self.config.get('generation', self.default_config()['generation'])

    def get_prompt(self) -> str:
        return self.config.get('prompt', self.default_config()['prompt'])

    def set_prompt(self, prompt: str):
        self.config['prompt'] = prompt
        self.save_config()

    def update_generation_config(self, updates: Dict[str, Any]):
        generation = self.config.get('generation', self.default_config()['generation'])
        generation.update(updates)
        self.config['generation'] = generation
        self.save_config()

    def get_presets(self) -> Dict[str, Any]:
        return self.config.get('presets', {})

    def save_preset(self, name: str, data: Dict[str, Any]):
        presets = self.config.get('presets', {})
        presets[name] = data
        self.config['presets'] = presets
        self.save_config()

    def delete_preset(self, name: str):
        presets = self.config.get('presets', {})
        if name in presets:
            del presets[name]
            self.config['presets'] = presets
            self.save_config()

    def apply_preset(self, name: str):
        presets = self.config.get('presets', {})
        data = presets.get(name)
        if not data:
            return
        self.config['prompt'] = data.get('prompt', self.get_prompt())
        self.config['generation'] = data.get('generation', self.get_generation_config())
        if data.get('model_path'):
            self.config['model_path'] = data['model_path']
        self.save_config()

    def get_history_config(self) -> Dict[str, Any]:
        defaults = self.default_config()['history']
        history = self.config.get('history', defaults)
        defaults.update(history)
        self.config['history'] = defaults
        self.save_config()
        return defaults

    def update_history_config(self, updates: Dict[str, Any]):
        history = self.get_history_config()
        history.update(updates)
        self.config['history'] = history
        self.save_config()

    def get_backup_config(self) -> Dict[str, Any]:
        defaults = self.default_config()['backup']
        backup = self.config.get('backup', defaults)
        defaults.update(backup)
        self.config['backup'] = defaults
        self.save_config()
        return defaults

    def update_backup_config(self, updates: Dict[str, Any]):
        backup = self.get_backup_config()
        backup.update(updates)
        self.config['backup'] = backup
        self.save_config()

    def get_training_config(self) -> Dict[str, Any]:
        defaults = self.default_config()['training']
        training = self.config.get('training', defaults)
        defaults.update(training)
        self.config['training'] = defaults
        self.save_config()
        return defaults

    def get_appearance(self) -> Dict[str, Any]:
        defaults = self.default_config()['appearance']
        appearance = self.config.get('appearance', defaults)
        defaults.update(appearance)
        self.config['appearance'] = defaults
        self.save_config()
        return defaults

    def update_appearance(self, updates: Dict[str, Any]):
        appearance = self.get_appearance()
        appearance.update(updates)
        self.config['appearance'] = appearance
        self.save_config()

    def get_accent_color(self) -> str:
        appearance = self.get_appearance()
        return appearance.get('accent_color', '#0078d4')

    def get_plugin_config(self) -> Dict[str, Any]:
        return self.config.get('plugins', self.default_config()['plugins'])

    def update_plugin_config(self, data: Dict[str, Any]):
        plugins = self.get_plugin_config()
        plugins.update(data)
        self.config['plugins'] = plugins
        self.save_config()

    def get_updater_config(self) -> Dict[str, Any]:
        defaults = self.default_config()['updater']
        updater = self.config.get('updater', defaults)
        defaults.update(updater)
        self.config['updater'] = defaults
        self.save_config()
        return defaults

    def update_updater_config(self, data: Dict[str, Any]):
        updater = self.get_updater_config()
        updater.update(data)
        self.config['updater'] = updater
        self.save_config()

    def set_current_user_id(self, user_id: int):
        self.config['current_user_id'] = user_id
        self.save_config()

    def get_current_user_id(self) -> Optional[int]:
        """Возвращает ID текущего пользователя."""
        return self.config.get('current_user_id')

