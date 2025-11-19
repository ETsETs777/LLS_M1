class ThemeManager:
    def __init__(self):
        self.current_theme = 'light'
        
    def set_theme(self, theme):
        self.current_theme = theme
        
    def get_stylesheet(self, theme):
        if theme == 'dark':
            return """
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 10px;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #3d3d3d;
                    color: #808080;
                }
            """
        else:
            return """
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QTextEdit {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 10px;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: #ffffff;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #e0e0e0;
                    color: #808080;
                }
            """

