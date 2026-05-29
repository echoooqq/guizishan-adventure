import os
import pygame


_font_cache = {}


def get_font(size):
    if size in _font_cache:
        return _font_cache[size]

    chinese_font_paths = [
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "simhei.ttf"),
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "msyh.ttc"),
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "simsun.ttc"),
    ]

    for font_path in chinese_font_paths:
        if os.path.exists(font_path):
            try:
                font = pygame.font.Font(font_path, size)
                _font_cache[size] = font
                return font
            except Exception:
                continue

    font = pygame.font.Font(None, size)
    _font_cache[size] = font
    return font
