"""
Стили для UI компонентов.
Централизованное хранение стилей для устранения дублирования.
"""
from desktop.utils.constants import (
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_PRESSED,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_ERROR_DARK,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_TEXT_SECONDARY,
    BORDER_RADIUS, INPUT_PADDING, CHAT_PADDING,
    FONT_SIZE_NORMAL, FONT_SIZE_SMALL, FONT_SIZE_TINY
)


def get_chat_display_style(theme: str = 'light') -> str:
    """
    Возвращает стиль для области чата.
    
    Args:
        theme: Тема ('light' или 'dark')
    
    Returns:
        CSS стиль для QTextEdit
    """
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    return f"""
        QTextEdit {{
            background-color: transparent;
            color: {color};
            border: none;
            padding: {CHAT_PADDING}px;
        }}
    """


def get_input_field_style(theme: str = 'light') -> str:
    """
    Возвращает стиль для поля ввода.
    
    Args:
        theme: Тема ('light' или 'dark')
    
    Returns:
        CSS стиль для QLineEdit
    """
    bg_alpha = "rgba(255, 255, 255, 0.1)" if theme == 'dark' else "rgba(0, 0, 0, 0.05)"
    bg_focus = "rgba(255, 255, 255, 0.15)" if theme == 'dark' else "rgba(0, 0, 0, 0.08)"
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    
    return f"""
        QLineEdit {{
            background-color: {bg_alpha};
            color: {color};
            border: none;
            border-bottom: 2px solid {COLOR_ACCENT};
            padding: {INPUT_PADDING}px;
            font-size: {FONT_SIZE_NORMAL}px;
        }}
        QLineEdit:focus {{
            border-bottom: 2px solid {COLOR_ACCENT};
            background-color: {bg_focus};
        }}
    """


def get_send_button_style(theme: str = 'light') -> str:
    """
    Возвращает стиль для кнопки отправки.
    
    Args:
        theme: Тема ('light' или 'dark')
    
    Returns:
        CSS стиль для QPushButton
    """
    disabled_bg = "#666" if theme == 'dark' else "#ccc"
    disabled_color = COLOR_TEXT_DARK if theme == 'dark' else "#666"
    
    return f"""
        QPushButton {{
            background-color: {COLOR_ACCENT};
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS}px;
            padding: 6px 16px;
            font-size: {FONT_SIZE_TINY}px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {COLOR_ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {COLOR_ACCENT_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {disabled_bg};
            color: {disabled_color};
        }}
    """


def get_tag_button_style(theme: str = 'light') -> str:
    """
    Возвращает стиль для кнопки тегов.
    
    Args:
        theme: Тема ('light' или 'dark')
    
    Returns:
        CSS стиль для QPushButton
    """
    bg_normal = "rgba(255, 255, 255, 0.1)" if theme == 'dark' else "rgba(0, 0, 0, 0.05)"
    bg_hover = "rgba(255, 255, 255, 0.2)" if theme == 'dark' else "rgba(0, 0, 0, 0.1)"
    border = "rgba(255, 255, 255, 0.2)" if theme == 'dark' else "rgba(0, 0, 0, 0.2)"
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    
    return f"""
        QPushButton {{
            background-color: {bg_normal};
            color: {color};
            border: 1px solid {border};
            border-radius: {BORDER_RADIUS}px;
            padding: 6px 12px;
            font-size: {FONT_SIZE_TINY}px;
        }}
        QPushButton:hover {{
            background-color: {bg_hover};
        }}
        QPushButton:checked {{
            background-color: {COLOR_ACCENT};
            color: white;
            border: 1px solid {COLOR_ACCENT};
        }}
    """


def get_icon_button_style() -> str:
    """
    Возвращает стиль для иконок-кнопок.
    
    Returns:
        CSS стиль для QPushButton
    """
    return f"""
        QPushButton {{
            background-color: rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(0, 0, 0, 0.2);
            border-radius: {BORDER_RADIUS}px;
            padding: 4px;
        }}
        QPushButton:hover {{
            background-color: rgba(0, 0, 0, 0.1);
        }}
        QPushButton:pressed {{
            background-color: rgba(0, 0, 0, 0.15);
        }}
    """


def get_loading_label_style(theme: str = 'light') -> str:
    """
    Возвращает стиль для метки загрузки.
    
    Args:
        theme: Тема ('light' или 'dark')
    
    Returns:
        CSS стиль для QLabel
    """
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    return f"color: {color};"

