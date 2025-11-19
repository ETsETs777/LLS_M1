import json
import os
from typing import Dict, Any


class Settings:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(base_dir, 'config')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.ensure_config_dir()
        self.load_config()
        
    def ensure_config_dir(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config()
            self.save_config()

    def reload(self):
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
                'runs_dir': os.path.join(base_dir, 'training_runs')
            },
            'plugins': {
                'enabled': [],
                'available': {
                    'web_search': {
                        'module': 'desktop.plugins.examples.web_search',
                        'class': 'WebSearchPlugin',
                        'name': 'Поиск в сети',
                        'description': 'Стартовый плагин для интеграции веб-поиска.',
                        'config': {}
                    },
                    'knowledge_base': {
                        'module': 'desktop.plugins.examples.knowledge_base',
                        'class': 'KnowledgeBasePlugin',
                        'name': 'База знаний',
                        'description': 'Ответы на основе локальной коллекции статей.',
                        'config': {
                            'data_path': knowledge_path
                        }
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
            
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
            
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
        return self.config.get('theme', 'light')
        
    def set_theme(self, theme: str):
        self.config['theme'] = theme
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

    def get_training_config(self) -> Dict[str, Any]:
        defaults = self.default_config()['training']
        training = self.config.get('training', defaults)
        defaults.update(training)
        self.config['training'] = defaults
        self.save_config()
        return defaults

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

    def get_current_user_id(self) -> Any:
        return self.config.get('current_user_id')

