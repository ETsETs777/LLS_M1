from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class QuickAction:
    label: str
    description: str
    handler: Callable[[Optional[str]], None]
    requires_input: bool = False


class QuickActionsManager:
    def __init__(self):
        self._actions: List[QuickAction] = []

    def register(self, action: QuickAction):
        self._actions.append(action)

    def list_actions(self) -> List[QuickAction]:
        return self._actions

