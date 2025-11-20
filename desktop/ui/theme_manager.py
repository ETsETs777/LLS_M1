class ThemeManager:
    def __init__(self):
        self.current_theme = 'light'
        self.accent_color = '#0078d4'

    def set_theme(self, theme):
        self.current_theme = theme

    def set_accent_color(self, color: str):
        if color:
            self.accent_color = color

    def _shade(self, color: str, factor: float) -> str:
        hex_value = color.lstrip('#')
        if len(hex_value) != 6:
            return self.accent_color
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f'#{r:02x}{g:02x}{b:02x}'

    def get_stylesheet(self, theme):
        accent = self.accent_color
        accent_hover = self._shade(accent, 1.1)
        accent_pressed = self._shade(accent, 0.85)
        accent_focus = self._shade(accent, 1.2)
        if theme == 'dark':
            return f"""
            QMainWindow {{
                background-color: #1e1e1e;
                color: #ffffff;
            }}
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {accent_pressed};
            }}
            QPushButton:focus {{
                outline: 2px solid {accent_focus};
            }}
            """
        else:
            return f"""
            QMainWindow {{
                background-color: #ffffff;
                color: #000000;
            }}
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {accent_pressed};
            }}
            QPushButton:focus {{
                outline: 2px solid {accent_focus};
            }}
            """
