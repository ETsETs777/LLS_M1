from typing import Dict

from desktop.config.settings import Settings
from desktop.core.model_manager import ModelManager


class NeuralNetwork:
    def __init__(self):
        self.settings = Settings()
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
