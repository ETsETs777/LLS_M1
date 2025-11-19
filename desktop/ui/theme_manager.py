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
                QWidget {{
                    background-color: #1e1e1e;
                    color: #ffffff;
                }}
                QMenuBar {{
                    background-color: #252526;
                    color: #cccccc;
                    border-bottom: 1px solid #3e3e42;
                }}
                QMenuBar::item {{
                    background-color: transparent;
                    padding: 4px 8px;
                }}
                QMenuBar::item:selected {{
                    background-color: #2a2d2e;
                }}
                QMenu {{
                    background-color: #252526;
                    color: #cccccc;
                    border: 1px solid #3e3e42;
                }}
                QMenu::item:selected {{
                    background-color: #094771;
                }}
                QToolBar {{
                    background-color: #2d2d2d;
                    border: none;
                    spacing: 5px;
                    padding: 5px;
                }}
                QStatusBar {{
                    background-color: {accent};
                    color: #ffffff;
                }}
                QTextEdit {{
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                }}
                QLineEdit {{
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 2px solid {accent};
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {accent_focus};
                }}
                QPushButton {{
                    background-color: {accent};
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {accent_hover};
                }}
                QPushButton:pressed {{
                    background-color: {accent_pressed};
                }}
                QPushButton:disabled {{
                    background-color: #3d3d3d;
                    color: #808080;
                }}
                QLabel {{
                    color: #ffffff;
                    font-size: 13px;
                }}
            """
        else:
            return f"""
                QMainWindow {{
                    background-color: #ffffff;
                    color: #000000;
                }}
                QWidget {{
                    background-color: #ffffff;
                    color: #000000;
                }}
                QMenuBar {{
                    background-color: #f3f3f3;
                    color: #000000;
                    border-bottom: 1px solid #d0d0d0;
                }}
                QMenuBar::item {{
                    background-color: transparent;
                    padding: 4px 8px;
                }}
                QMenuBar::item:selected {{
                    background-color: #e8e8e8;
                }}
                QMenu {{
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                }}
                QMenu::item:selected {{
                    background-color: #e8f4f8;
                }}
                QToolBar {{
                    background-color: #f5f5f5;
                    border: none;
                    spacing: 5px;
                    padding: 5px;
                }}
                QStatusBar {{
                    background-color: {accent};
                    color: #ffffff;
                }}
                QTextEdit {{
                    background-color: #fafafa;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                }}
                QLineEdit {{
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid {accent};
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {accent_focus};
                }}
                QPushButton {{
                    background-color: {accent};
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {accent_hover};
                }}
                QPushButton:pressed {{
                    background-color: {accent_pressed};
                }}
                QPushButton:disabled {{
                    background-color: #e0e0e0;
                    color: #808080;
                }}
                QLabel {{
                    color: #000000;
                    font-size: 13px;
                }}
            """
