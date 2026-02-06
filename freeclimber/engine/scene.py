"""Scene and Layer classes — replaces pygext Scene/Layer system."""

import pygame
from .collision import RadialCollisions


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------

class Layer:
    """Unordered layer — entities drawn in arbitrary order (fast add/remove)."""

    def __init__(self, name):
        self.name = name
        self._entities = set()

    def add(self, entity):
        self._entities.add(entity)

    def remove(self, entity):
        self._entities.discard(entity)

    def draw(self, renderer):
        for e in list(self._entities):
            if not e.deleted:
                e.draw(renderer)

    def __iter__(self):
        return iter(set(self._entities))

    def __len__(self):
        return len(self._entities)

    def clear(self):
        self._entities.clear()


class StabileLayer:
    """Ordered layer — entities drawn in insertion order."""

    def __init__(self, name):
        self.name = name
        self._entities = []
        self._entity_set = set()

    def add(self, entity):
        if entity not in self._entity_set:
            self._entities.append(entity)
            self._entity_set.add(entity)

    def remove(self, entity):
        if entity in self._entity_set:
            self._entity_set.discard(entity)
            try:
                self._entities.remove(entity)
            except ValueError:
                pass

    def draw(self, renderer):
        for e in list(self._entities):
            if not e.deleted:
                e.draw(renderer)

    def __iter__(self):
        return iter(list(self._entities))

    def __len__(self):
        return len(self._entities)

    def clear(self):
        self._entities.clear()
        self._entity_set.clear()


class StaticLayer:
    """Static layer — renders entities once to a texture, then blits the cached result.

    Entities on static layers shouldn't change after creation.
    Falls back to normal rendering if the cache can't be built.
    """

    def __init__(self, name):
        self.name = name
        self._entities = []
        self._entity_set = set()
        self._dirty = True
        self._cache_texture = None

    def add(self, entity):
        if entity not in self._entity_set:
            self._entities.append(entity)
            self._entity_set.add(entity)
            self._dirty = True

    def remove(self, entity):
        if entity in self._entity_set:
            self._entity_set.discard(entity)
            try:
                self._entities.remove(entity)
            except ValueError:
                pass
            self._dirty = True

    def draw(self, renderer):
        if self._dirty:
            self._rebuild(renderer)
        if self._cache_texture is not None:
            from pygame._sdl2.video import Image
            img = Image(self._cache_texture)
            img.draw(dstrect=(0, 0, self._cache_texture.width, self._cache_texture.height))
        else:
            for e in list(self._entities):
                if not e.deleted:
                    e.draw(renderer)

    def _rebuild(self, renderer):
        """Render all entities into a cached texture."""
        try:
            from pygame._sdl2.video import Texture
            w, h = renderer.get_viewport().size
            tex = Texture(renderer, (w, h), target=True)
            # Render to texture
            old_target = renderer.target
            renderer.target = tex
            renderer.draw_color = (0, 0, 0, 0)
            renderer.clear()
            for e in list(self._entities):
                if not e.deleted:
                    e.draw(renderer)
            renderer.target = old_target
            self._cache_texture = tex
        except Exception:
            self._cache_texture = None
        self._dirty = False

    def __iter__(self):
        return iter(list(self._entities))

    def __len__(self):
        return len(self._entities)

    def clear(self):
        self._entities.clear()
        self._entity_set.clear()
        self._dirty = True
        self._cache_texture = None


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class Scene:
    """Base class for game scenes.

    Subclasses override ``init()``, ``enter()``, ``leave()``,
    ``realtick()``, and define ``handle_*`` event methods and
    ``collision_X_Y`` callbacks.
    """

    collengine = None  # Set to RadialCollisions on subclasses that need it

    def __init__(self, **kw):
        self._layers = {}       # name -> Layer
        self._layer_order = []  # insertion-ordered list of layer names
        self.event_handler = {}
        self.coll = None
        self._state = None
        self._state_realtick = None
        self._state_tick = None
        self._discover_handlers()
        self.init(**kw)

    def init(self, **kw):
        """User override — called during ``__init__``."""
        pass

    def _discover_handlers(self):
        """Auto-discover handle_* event methods and register them."""
        _event_map = {
            "handle_keydown": pygame.KEYDOWN,
            "handle_keyup": pygame.KEYUP,
            "handle_joybuttondown": pygame.JOYBUTTONDOWN,
            "handle_joybuttonup": pygame.JOYBUTTONUP,
            "handle_joyaxismotion": pygame.JOYAXISMOTION,
            "handle_mousebuttondown": pygame.MOUSEBUTTONDOWN,
            "handle_mousebuttonup": pygame.MOUSEBUTTONUP,
            "handle_mousemotion": pygame.MOUSEMOTION,
        }
        for method_name, event_type in _event_map.items():
            method = getattr(self, method_name, None)
            if method is not None:
                self.event_handler[event_type] = {"": method}

    def _discover_collision_handlers(self):
        """Find collision_X_Y methods and register them with the collision engine."""
        if self.coll is None:
            return
        prefix = "collision_"
        for name in dir(self):
            if name.startswith(prefix) and name.count("_") >= 2:
                parts = name[len(prefix):].split("_", 1)
                if len(parts) == 2:
                    group1, group2 = parts
                    callback = getattr(self, name)
                    self.coll.add_handler(group1, group2, callback)

    def _activate(self):
        """Called by Director when this scene becomes active."""
        # Create collision engine if needed
        if self.collengine is not None:
            self.coll = self.collengine()
        else:
            self.coll = RadialCollisions()
        # Reset layers
        self._layers.clear()
        self._layer_order.clear()
        self.event_handler.clear()
        self._state = None
        self._state_realtick = None
        self._state_tick = None
        self._discover_handlers()
        self.enter()
        self._discover_collision_handlers()

    def _deactivate(self):
        """Called by Director when leaving this scene."""
        self.leave()
        if self.coll is not None:
            self.coll.clear()

    def enter(self):
        """User override — called when the scene becomes active."""
        pass

    def leave(self):
        """User override — called when the scene is deactivated."""
        pass

    def realtick(self):
        """User override — called at fixed rate (FPS) by the Director."""
        pass

    def tick(self):
        """User override — called every frame."""
        pass

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------

    def set_state(self, name):
        """Activate a named state.

        Looks up ``state_{name}_realtick`` and ``state_{name}_tick``
        methods on this scene.  Pass ``None`` to clear state.
        """
        self._state = name
        if name is not None:
            self._state_realtick = getattr(self, "state_%s_realtick" % name, None)
            self._state_tick = getattr(self, "state_%s_tick" % name, None)
        else:
            self._state_realtick = None
            self._state_tick = None

    # ------------------------------------------------------------------
    # Layer management
    # ------------------------------------------------------------------

    def new_layer(self, name):
        layer = Layer(name)
        self._layers[name] = layer
        self._layer_order.append(name)
        return layer

    def new_static(self, name):
        layer = StaticLayer(name)
        self._layers[name] = layer
        self._layer_order.append(name)
        return layer

    def new_stabile(self, name):
        layer = StabileLayer(name)
        self._layers[name] = layer
        self._layer_order.append(name)
        return layer

    def get_layer(self, name):
        return self._layers.get(name)

    @property
    def ordered_layers(self):
        """Yield layers in creation order."""
        for name in self._layer_order:
            layer = self._layers.get(name)
            if layer is not None:
                yield layer

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def dispatch_event(self, event):
        """Route a pygame event to the appropriate handler."""
        handlers = self.event_handler.get(event.type)
        if handlers:
            for key, handler in handlers.items():
                handler(event)
