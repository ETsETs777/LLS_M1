from typing import List, Dict


class PaletteManager:
    def __init__(self):
        self._options = [
            {'name': 'Azure', 'value': '#0078d4'},
            {'name': 'Emerald', 'value': '#10b981'},
            {'name': 'Sunrise', 'value': '#ff9800'},
            {'name': 'Ruby', 'value': '#e53935'},
            {'name': 'Lavender', 'value': '#9c27b0'},
            {'name': 'Slate', 'value': '#64748b'},
        ]

    def options(self) -> List[Dict[str, str]]:
        return self._options

    def find_name(self, value: str) -> str:
        for option in self._options:
            if option['value'].lower() == (value or '').lower():
                return option['name']
        return 'Custom'

