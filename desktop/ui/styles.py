
from desktop.utils.constants import (
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_PRESSED,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_ERROR_DARK,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_TEXT_SECONDARY,
    BORDER_RADIUS, INPUT_PADDING, CHAT_PADDING,
    FONT_SIZE_NORMAL, FONT_SIZE_SMALL, FONT_SIZE_TINY
)


def get_chat_display_style(theme: str = 'light') -> str:
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    return f"QTextEdit {{ color: {color}; padding: {CHAT_PADDING}px; border: none; background: transparent; font-size: {FONT_SIZE_NORMAL}px; }}"


def get_input_field_style(theme: str = 'light') -> str:
    bg_alpha = "rgba(255, 255, 255, 0.1)" if theme == 'dark' else "rgba(0, 0, 0, 0.05)"
    bg_focus = "rgba(255, 255, 255, 0.15)" if theme == 'dark' else "rgba(0, 0, 0, 0.08)"
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    return f"QLineEdit {{ background: {bg_alpha}; border: none; border-radius: {BORDER_RADIUS}px; padding: {INPUT_PADDING}px; color: {color}; font-size: {FONT_SIZE_NORMAL}px; }} QLineEdit:focus {{ background: {bg_focus}; }}"


def get_send_button_style(theme: str = 'light') -> str:
    disabled_bg = "rgba(128, 128, 128, 0.3)" if theme == 'dark' else "rgba(128, 128, 128, 0.2)"
    disabled_color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_SECONDARY
    return f"QPushButton {{ background: {COLOR_ACCENT}; color: white; border: none; border-radius: {BORDER_RADIUS}px; padding: 8px 16px; font-size: {FONT_SIZE_NORMAL}px; font-weight: bold; }} QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }} QPushButton:pressed {{ background: {COLOR_ACCENT_PRESSED}; }} QPushButton:disabled {{ background: {disabled_bg}; color: {disabled_color}; }}"


def get_tag_button_style(theme: str = 'light') -> str:
    bg_normal = "rgba(255, 255, 255, 0.1)" if theme == 'dark' else "rgba(0, 0, 0, 0.05)"
    bg_hover = "rgba(255, 255, 255, 0.2)" if theme == 'dark' else "rgba(0, 0, 0, 0.1)"
    border = "rgba(255, 255, 255, 0.2)" if theme == 'dark' else "rgba(0, 0, 0, 0.2)"
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    return f"QPushButton {{ background: {bg_normal}; color: {color}; border: 1px solid {border}; border-radius: {BORDER_RADIUS}px; padding: 4px 8px; font-size: {FONT_SIZE_SMALL}px; }} QPushButton:hover {{ background: {bg_hover}; }}"


def get_icon_button_style() -> str:
    return f"QPushButton {{ background: transparent; border: none; border-radius: {BORDER_RADIUS}px; }} QPushButton:hover {{ background: rgba(0, 0, 0, 0.1); }} QPushButton:pressed {{ background: rgba(0, 0, 0, 0.2); }}"


def get_loading_label_style(theme: str = 'light') -> str:
    color = COLOR_TEXT_DARK if theme == 'dark' else COLOR_TEXT_LIGHT
    return f"color: {color};"
