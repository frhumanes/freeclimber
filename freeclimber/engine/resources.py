"""Resource loading and caching — replaces pygext resource system."""

import os
import pygame


class _Bitmap:
    """Wrapper around pygame.Surface that mimics pygext's compiled bitmap.

    In the original pygext, bitmaps had an OpenGL display-list id
    (``_listid``) and a ``compile()`` method.  Game code sometimes checks
    ``shape._listid is None`` and calls ``shape.compile()`` — both are
    now harmless no-ops because we use SDL2 textures at draw time.
    """

    def __init__(self, surface, hotspot=None):
        self.surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()
        # hotspot: fractional anchor (0-1, 0-1) or None for center
        self.hotspot = hotspot
        # Compatibility stub — game code checks this
        self._listid = True

    def compile(self):
        """No-op kept for API compatibility."""
        pass

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height


class ResourceHandler:
    """Loads and caches image surfaces."""

    def __init__(self):
        self._cache = {}

    def get_surface(self, path, hotspot=None):
        key = (path, hotspot if hotspot is not None else "default")
        if key not in self._cache:
            try:
                surf = pygame.image.load(path)
            except Exception:
                return None
            bmp = _Bitmap(surf, hotspot)
            self._cache[key] = bmp
        return self._cache[key]

    def get_bitmap(self, path, hotspot=None):
        """Alias for get_surface — matches pygext API."""
        return self.get_surface(path, hotspot)

    def clear(self):
        self._cache.clear()


resources = ResourceHandler()
