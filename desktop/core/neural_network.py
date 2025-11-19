from typing import Dict, Any, Optional

from desktop.config.settings import Settings
from desktop.core.model_manager import ModelManager


class NeuralNetwork:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self._init_model_manager()

    def _init_model_manager(self):
        self.model_manager = ModelManager(
            model_path=self.settings.get_model_path(),
            generation_params=self.settings.get_generation_config()
        )

    def _build_prompt(self, user_input: str) -> str:
        system_prompt = self.settings.get_prompt().strip()
        return f'{system_prompt}\nПользователь: {user_input}\nАссистент:'

    def generate_response(self, user_input: str) -> str:
        prompt = self._build_prompt(user_input)
        return self.model_manager.generate(prompt)

    def refresh_from_settings(self):
        self.settings.reload()
        self.model_manager.update_generation_params(self.settings.get_generation_config())

    def reload_model(self):
        self.settings.reload()
        self._init_model_manager()

    def update_prompt(self, prompt: str):
        self.settings.set_prompt(prompt)

    def update_generation_params(self, params: Dict[str, Any]):
        self.settings.update_generation_config(params)
        self.model_manager.update_generation_params(params)

    def get_model_info(self) -> Dict[str, Any]:
        metadata = self.model_manager.get_metadata()
        metadata['theme'] = self.settings.get_theme()
        return metadata
