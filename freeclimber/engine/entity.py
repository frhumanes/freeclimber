"""Entity and TextEntity — sprite rendering via SDL2 Renderer."""

import os
import pygame
from .node import Node
from .resources import resources, _Bitmap


class Entity(Node):
    """Visible game object with image, position, scale, alpha, rotation.

    In pygext, ``(x, y)`` referred to the entity's *hotspot* position,
    not the top-left corner.  The default hotspot is ``(0.5, 0.5)``
    (center), so ``x, y`` is the center of the sprite.  When
    ``hotspot=(0, 0)`` is passed, ``x, y`` is the top-left corner.

    Class attributes that subclasses typically set:

    - ``image``: default image path (string)
    - ``layer``: default layer name — entity auto-places on this layer

    Keyword arguments to the constructor are forwarded to ``init()``.
    """

    image = None
    layer = None

    def __init__(self, image=None, hotspot="default", **kw):
        super().__init__()
        # Resolve image
        img = image or self.__class__.image
        self.shape = None           # _Bitmap or None
        self._texture = None        # pygame._sdl2 Texture (lazy)
        self._texture_dirty = True  # need to (re)create texture
        self._base_width = 1
        self._base_height = 1

        # Hotspot: (hx, hy) fractions where 0=left/top, 0.5=center, 1=right/bottom
        # Default is center (0.5, 0.5) matching pygext behavior
        if isinstance(hotspot, (tuple, list)) and len(hotspot) >= 2:
            self._hx = float(hotspot[0])
            self._hy = float(hotspot[1])
        else:
            # "default", None, or anything else → center
            self._hx = 0.5
            self._hy = 0.5

        if img is not None:
            if isinstance(img, str):
                bmp = resources.get_bitmap(img)
                if bmp is not None:
                    self.shape = bmp
            elif isinstance(img, _Bitmap):
                self.shape = img

        if self.shape is not None:
            self._base_width = self.shape.width
            self._base_height = self.shape.height

        # Auto-place on layer
        self.init(**kw)
        if self.__class__.layer and self._layer is None:
            self.place(self.__class__.layer)

    def init(self, **kw):
        """User override — called during ``__init__``."""
        pass

    # ------------------------------------------------------------------
    # Dimension properties (account for scale)
    # ------------------------------------------------------------------

    @property
    def width(self):
        return int(self._base_width * self.scale)

    @width.setter
    def width(self, val):
        if self._base_width:
            self.scale = val / self._base_width

    @property
    def height(self):
        return int(self._base_height * self.scale)

    @height.setter
    def height(self, val):
        if self._base_height:
            self.scale = val / self._base_height

    # ------------------------------------------------------------------
    # Hotspot-aware position helpers
    #
    # (x, y) is the hotspot position.  With default hotspot (0.5, 0.5),
    # x is the horizontal center and y is the vertical center.
    # Named properties (left, right, centerx, top, bottom, centery)
    # always refer to the actual edges/center regardless of hotspot.
    # ------------------------------------------------------------------

    @property
    def left(self):
        return self.x - self._hx * self.width

    @left.setter
    def left(self, val):
        self.x = val + self._hx * self.width

    @property
    def right(self):
        return self.x + (1 - self._hx) * self.width

    @right.setter
    def right(self, val):
        self.x = val - (1 - self._hx) * self.width

    @property
    def centerx(self):
        return self.x + (0.5 - self._hx) * self.width

    @centerx.setter
    def centerx(self, val):
        self.x = val - (0.5 - self._hx) * self.width

    @property
    def top(self):
        return self.y - self._hy * self.height

    @top.setter
    def top(self, val):
        self.y = val + self._hy * self.height

    @property
    def bottom(self):
        return self.y + (1 - self._hy) * self.height

    @bottom.setter
    def bottom(self, val):
        self.y = val - (1 - self._hy) * self.height

    @property
    def centery(self):
        return self.y + (0.5 - self._hy) * self.height

    @centery.setter
    def centery(self, val):
        self.y = val - (0.5 - self._hy) * self.height

    # Compatibility aliases used by weather.py particles
    @property
    def realx(self):
        return self.x

    @realx.setter
    def realx(self, val):
        self.x = val

    @property
    def realy(self):
        return self.y

    @realy.setter
    def realy(self, val):
        self.y = val

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _ensure_texture(self, renderer):
        """Create / recreate SDL2 Texture from the current shape surface."""
        if self.shape is None:
            self._texture = None
            return
        try:
            from pygame._sdl2.video import Texture
            surf = self.shape.surface
            self._texture = Texture.from_surface(renderer, surf)
            self._base_width = self.shape.width
            self._base_height = self.shape.height
        except Exception:
            self._texture = None
        self._texture_dirty = False

    def draw(self, renderer):
        if self.hidden or self.deleted:
            return
        if self.shape is None:
            return
        if self._texture is None or self._texture_dirty:
            self._ensure_texture(renderer)
        if self._texture is None:
            return

        w = int(self._base_width * self.scale)
        h = int(self._base_height * self.scale)
        if w <= 0 or h <= 0:
            return

        # Draw position is always top-left, computed from hotspot
        draw_x = int(self.x - self._hx * w)
        draw_y = int(self.y - self._hy * h)
        dest = pygame.Rect(draw_x, draw_y, w, h)

        # Apply alpha
        alpha = max(0, min(255, int(self.alpha)))
        self._texture.alpha = alpha

        # Apply color modulation
        if self.color and len(self.color) >= 3:
            self._texture.color = self.color[:3]

        if self.angle != 0:
            from pygame._sdl2.video import Image
            img = Image(self._texture)
            img.angle = self.angle
            img.draw(dstrect=dest)
        else:
            renderer.blit(self._texture, dest)


class TextEntity(Entity):
    """Entity that renders text via a GLFont.

    Usage::

        font = GLFont(("path.ttf", 24), (255, 255, 255))
        te = TextEntity(font, "Hello")
        te.set(centerx=400, centery=300).place("info")
    """

    def __init__(self, font, text="", **kw):
        self._font = font
        self._text = str(text)
        # Render to bitmap
        bmp = font.render(self._text)
        # Set up as Entity with that bitmap
        super().__init__(image=bmp, **kw)

    def set_text(self, text):
        """Re-render with new text content."""
        self._text = str(text)
        bmp = self._font.render(self._text)
        self.shape = bmp
        self._base_width = bmp.width
        self._base_height = bmp.height
        self._texture_dirty = True
