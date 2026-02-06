"""GLFont wrapper — replaces pygext's OpenGL font with pygame.font."""

import pygame
from .resources import _Bitmap


class GLFont:
    """Font wrapper compatible with pygext's GLFont API.

    Usage::

        font = GLFont(("/path/to/font.ttf", 24), (255, 255, 255))
        surface = font.render("Hello")
    """

    def __init__(self, font_spec, color):
        """
        Parameters
        ----------
        font_spec : tuple
            ``(font_path, font_size)``
        color : tuple
            ``(r, g, b)`` or ``(r, g, b, a)``
        """
        path, size = font_spec
        self.color = color[:3]
        self.alpha = color[3] if len(color) > 3 else 255
        try:
            self._font = pygame.font.Font(path, int(size))
        except Exception:
            self._font = pygame.font.Font(None, int(size))

    def render(self, text):
        """Render *text* and return a _Bitmap."""
        surf = self._font.render(str(text), True, self.color)
        if self.alpha < 255:
            surf.set_alpha(self.alpha)
        return _Bitmap(surf, hotspot=None)
