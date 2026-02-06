"""Particle system — replaces pygext.gl.particles.

Provides BitmapParticleSystem and RingEmitter used by weather/fireworks.
"""

import math
import random
import pygame
from .entity import Entity
from .resources import resources


class _Particle:
    """Single particle state."""
    __slots__ = ("x", "y", "vx", "vy", "life", "age", "alpha", "scale",
                 "scale_delta", "color", "fade_time", "fade_in", "shape",
                 "_texture")

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.life = 1.0
        self.age = 0.0
        self.alpha = 255
        self.scale = 1.0
        self.scale_delta = 0.0
        self.color = (255, 255, 255, 255)
        self.fade_time = 0.5
        self.fade_in = 0.0
        self.shape = None
        self._texture = None


class BitmapParticleSystem(Entity):
    """Manages a collection of image-based particles.

    Subclass and set ``image``, ``layer``, and ``mutators`` class attributes.
    """

    image = None
    layer = None
    mutators = []

    def __init__(self, **kw):
        self._particles = []
        self._emitters = []
        super().__init__(**kw)

    def init(self, **kw):
        pass

    def new_emitter(self, emitter_cls, node):
        """Create an emitter of *emitter_cls* attached to *node*."""
        emitter = emitter_cls()
        emitter._system = self
        emitter._node = node
        emitter._timer = 0.0
        self._emitters.append(emitter)
        # Register with reactor so tick() is called
        from .director import director
        director.reactor.add(emitter)
        return emitter

    def _add_particle(self, p):
        self._particles.append(p)

    def tick(self, delta):
        """Update all particles."""
        dead = []
        for p in self._particles:
            p.age += delta
            if p.age >= p.life:
                dead.append(p)
                continue
            p.x += p.vx * delta
            p.y += p.vy * delta
            p.scale += p.scale_delta * delta
            # Fade out
            if p.fade_time > 0 and p.age > p.life - p.fade_time:
                frac = (p.life - p.age) / p.fade_time
                p.alpha = int(255 * max(0, frac))
            # Fade in
            elif p.fade_in > 0 and p.age < p.fade_in:
                frac = p.age / p.fade_in
                p.alpha = int(255 * min(1, frac))
        for p in dead:
            self._particles.remove(p)

    def draw(self, renderer):
        if self.hidden or self.deleted:
            return
        for p in self._particles:
            if p.shape is None:
                continue
            # Ensure texture
            if p._texture is None:
                try:
                    from pygame._sdl2.video import Texture
                    p._texture = Texture.from_surface(renderer, p.shape.surface)
                except Exception:
                    continue
            w = int(p.shape.width * p.scale)
            h = int(p.shape.height * p.scale)
            if w <= 0 or h <= 0:
                continue
            dest = pygame.Rect(int(p.x - w / 2), int(p.y - h / 2), w, h)
            p._texture.alpha = max(0, min(255, int(p.alpha)))
            if p.color and len(p.color) >= 3:
                p._texture.color = p.color[:3]
            renderer.blit(p._texture, dest)


class RingEmitter:
    """Emits particles in a ring pattern from a parent node.

    Subclass and set class attributes: delay, num_particles, life,
    fade_time, fade_in, scale, scale_delta, color, velocity, radius,
    tangent, angle, direction.
    """

    delay = 0.05
    num_particles = 1
    life = 1.0
    fade_time = 0.5
    fade_in = 0.0
    scale = 0.1
    scale_delta = 0.0
    alfa = 255
    color = (255, 255, 255, 255)
    velocity = 100
    radius = 50
    tangent = False
    angle = 0
    direction = 0

    def __init__(self):
        self._system = None
        self._node = None
        self._timer = 0.0

    def tick(self, delta):
        if self._node is None or self._node.deleted:
            return
        if self._node.hidden:
            return
        self._timer += delta
        while self._timer >= self.delay:
            self._timer -= self.delay
            self.emit()

    def emit(self):
        """Emit particles in a ring."""
        for _ in range(self.num_particles):
            p = _Particle()
            # Resolve scale (may be a Random lazy value)
            sc = self.scale
            if callable(sc):
                sc = sc()
            elif hasattr(sc, 'value'):
                sc = sc.value()

            a = random.uniform(0, 2 * math.pi)
            cx = self._node.x
            cy = self._node.y

            p.x = cx + self.radius * math.cos(a)
            p.y = cy + self.radius * math.sin(a)

            if self.tangent:
                # Velocity tangent to circle
                p.vx = -self.velocity * math.sin(a)
                p.vy = self.velocity * math.cos(a)
            else:
                p.vx = self.velocity * math.cos(a)
                p.vy = self.velocity * math.sin(a)

            p.life = self.life
            p.fade_time = self.fade_time
            p.fade_in = self.fade_in
            p.scale = float(sc)
            p.scale_delta = self.scale_delta
            p.color = self.color
            p.alpha = self.alfa

            # Use system's default shape
            if self._system and self._system.shape:
                p.shape = self._system.shape
            p._texture = None

            self._tweak(p)
            self._system._add_particle(p)

    def _tweak(self, p):
        """Override to customize individual particles."""
        pass


class Random:
    """Lazy random value — replacement for pygext.lazy.Random.

    Returns a random float between lo and hi each time it's called.
    """

    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __call__(self):
        return random.uniform(self.lo, self.hi)

    def value(self):
        return random.uniform(self.lo, self.hi)
