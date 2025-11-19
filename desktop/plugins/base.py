from typing import Dict, Any


class Plugin:
    id: str = 'base'
    name: str = 'Base Plugin'
    description: str = ''

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = False

    def activate(self):
        self.enabled = True

    def deactivate(self):
        self.enabled = False

    def execute(self, query: str) -> str:
        raise NotImplementedError

