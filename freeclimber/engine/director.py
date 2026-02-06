"""Director singleton, Ticker, Reactor, Screen — game loop."""

import pygame
from .scene import Scene


# ---------------------------------------------------------------------------
# Ticker — frame-rate management
# ---------------------------------------------------------------------------

class Ticker:
    """Fixed-rate tick generator matching pygext's Ticker API."""

    def __init__(self, resolution=40):
        self.resolution = float(resolution)
        self.tick_delay = 1000.0 / self.resolution
        self.now = 0.0
        self.prev_tick = 0.0
        self.prev_realtick = 0.0
        self.next_realtick = 0.0
        self.delta = 0.0            # seconds since last tick() call
        self.tick_delta = 0.0       # same as delta (compat)
        self.realtick_delta = 0.0   # time since last realtick
        self.realtick = False       # True on frames where a realtick fires

    def tick(self):
        """Call once per frame.  Updates timing and sets ``realtick`` flag."""
        self.now = pygame.time.get_ticks()
        elapsed = self.now - self.prev_tick
        self.prev_tick = self.now
        self.delta = elapsed / 1000.0
        self.tick_delta = self.delta

        if self.now >= self.next_realtick:
            self.realtick = True
            self.realtick_delta = (self.now - self.prev_realtick) / 1000.0
            self.prev_realtick = self.now
            self.next_realtick = self.now + self.tick_delay
        else:
            self.realtick = False
            self.realtick_delta = 0.0

    def reset(self):
        self.now = pygame.time.get_ticks()
        self.prev_tick = self.now
        self.prev_realtick = self.now
        self.next_realtick = self.now + self.tick_delay
        self.delta = 0.0
        self.tick_delta = 0.0
        self.realtick_delta = 0.0
        self.realtick = False


# ---------------------------------------------------------------------------
# Reactor — manages tickable objects
# ---------------------------------------------------------------------------

class Reactor:
    """Set of tickable objects with safe add/remove during iteration."""

    def __init__(self):
        self._objects = set()
        self._to_add = set()
        self._to_remove = set()

    def add(self, obj):
        self._to_add.add(obj)
        self._to_remove.discard(obj)

    def remove(self, obj):
        self._to_remove.add(obj)
        self._to_add.discard(obj)

    def tick(self, delta):
        # Apply deferred adds/removes
        if self._to_add:
            self._objects |= self._to_add
            self._to_add.clear()
        if self._to_remove:
            self._objects -= self._to_remove
            self._to_remove.clear()

        for obj in list(self._objects):
            if obj not in self._to_remove:
                obj.tick(delta)

    def clear(self):
        self._objects.clear()
        self._to_add.clear()
        self._to_remove.clear()


# ---------------------------------------------------------------------------
# Screen — compatibility object for screen.init() / screen.clear_color
# ---------------------------------------------------------------------------

class Screen:
    """Compatibility wrapper for ``screen.init()`` and ``screen.clear_color``."""

    def __init__(self):
        self.clear_color = (0, 0, 0, 255)
        self._window = None
        self._renderer = None

    def init(self, resolution, fullscreen=False, title=""):
        """Initialize the display via SDL2 Renderer.

        Creates a ``pygame._sdl2.Window`` + ``Renderer``.
        """
        pygame.init()

        from pygame._sdl2.video import Window, Renderer
        self._window = Window(title, resolution)
        if fullscreen:
            self._window.set_fullscreen(True)
        self._renderer = Renderer(self._window)

        # Wire into director
        director._renderer = self._renderer
        director._window = self._window
        director._resolution = resolution

    @property
    def renderer(self):
        return self._renderer


# ---------------------------------------------------------------------------
# Director singleton
# ---------------------------------------------------------------------------

class _Director:
    """Game loop and scene management singleton."""

    def __init__(self):
        self.ticker = Ticker(40)
        self.reactor = Reactor()
        self.scene = None
        self._next_scene = None
        self._renderer = None
        self._window = None
        self._resolution = (800, 600)
        self.running = True
        self.ticks = 0
        self.realticks = 0
        self.secs = 0.0
        self._clock = None

    def run(self, scene_or_class):
        """Main game loop.  Accepts a Scene instance or Scene subclass."""
        if isinstance(scene_or_class, type) and issubclass(scene_or_class, Scene):
            scene = scene_or_class()
        else:
            scene = scene_or_class

        self.running = True
        self.ticks = 0
        self.realticks = 0
        self.secs = 0.0
        self._clock = pygame.time.Clock()

        self._set_scene_immediate(scene)

        self.ticker.reset()

        while self.running:
            # --- Draw ---
            if self._renderer is not None:
                cc = screen.clear_color
                if cc is not None:
                    self._renderer.draw_color = cc
                    self._renderer.clear()
                if self.scene is not None:
                    for layer in self.scene.ordered_layers:
                        layer.draw(self._renderer)
                self._renderer.present()

            # --- Timing ---
            self.ticker.tick()
            delta = self.ticker.delta
            self.ticks += 1
            self.secs += delta

            # --- Realtick (fixed-rate logic) ---
            if self.ticker.realtick:
                self.realticks += 1
                if self.scene is not None:
                    # Collision checks
                    if self.scene.coll is not None:
                        self.scene.coll.check_collisions()
                    # Pygame events
                    self._handle_events()
                    # State-specific realtick
                    if self.scene._state_realtick is not None:
                        self.scene._state_realtick()
                    else:
                        self.scene.realtick()

            # --- Per-frame tick ---
            if self.scene is not None:
                if self.scene._state_tick is not None:
                    self.scene._state_tick()
                else:
                    self.scene.tick()

            # --- Reactor (actions, particles) ---
            self.reactor.tick(delta)

            # --- Deferred scene switch ---
            if self._next_scene is not None:
                next_s = self._next_scene
                self._next_scene = None
                self._set_scene_immediate(next_s)

            # Cap frame rate loosely (don't burn CPU)
            if self._clock:
                self._clock.tick(0)  # no cap — just track time

        # Leaving run loop
        if self.scene is not None:
            self.scene._deactivate()
            self.scene = None

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if self.scene is not None:
                self.scene.dispatch_event(event)

    def set_scene(self, scene_or_class, *args, **kw):
        """Deferred scene switch — takes effect at end of current frame."""
        if isinstance(scene_or_class, type) and issubclass(scene_or_class, Scene):
            scene = scene_or_class(*args, **kw)
        else:
            scene = scene_or_class
        self._next_scene = scene

    def _set_scene_immediate(self, scene):
        """Activate *scene* now."""
        if self.scene is not None:
            self.scene._deactivate()
        self.scene = scene
        # Clear reactor — old scene's actions should not persist
        self.reactor.clear()
        if scene is not None:
            scene._activate()

    def set_state(self, name):
        """Set state on the current scene."""
        if self.scene is not None:
            self.scene.set_state(name)

    def quit(self):
        self.running = False


# Module-level singletons
director = _Director()
screen = Screen()
