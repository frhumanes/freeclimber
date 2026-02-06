"""Node — base class with position, actions, and collision nodes."""


class Node:
    """Positional node with action and collision support.

    This is the base for Entity/TextEntity.  It tracks position, scale,
    angle, alpha, color, visibility, and manages the set of running
    actions and collision nodes attached to it.
    """

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.scale = 1.0
        self.angle = 0.0
        self.alpha = 255
        self.color = (255, 255, 255, 255)
        self.hidden = False
        self.deleted = False
        self._layer = None
        self.current_actions = set()
        self._collision_nodes = set()

    # ------------------------------------------------------------------
    # Chainable property setter
    # ------------------------------------------------------------------

    def set(self, **kw):
        """Set attributes by keyword; returns *self* for chaining.

        ``scale`` is applied first so that position properties
        (``centerx``, ``bottom``, etc.) compute with the correct
        dimensions.
        """
        if 'scale' in kw:
            self.scale = kw.pop('scale')
        for k, v in kw.items():
            setattr(self, k, v)
        return self

    def set_alpha(self, val):
        self.alpha = val

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def do(self, *actions):
        """Execute one or more actions on this node."""
        for action in actions:
            action.do(self)

    def get_actions(self, typefilter=None):
        """Return list of current actions, optionally filtered by type."""
        if typefilter is None:
            return list(self.current_actions)
        return [a for a in self.current_actions if isinstance(a, typefilter)]

    def abort_actions(self, typefilter=None):
        """Abort all current actions, optionally only those matching *typefilter*."""
        to_abort = list(self.current_actions)
        for a in to_abort:
            if typefilter is None or isinstance(a, typefilter):
                a.abort()

    # ------------------------------------------------------------------
    # Collision
    # ------------------------------------------------------------------

    def add_collnode(self, group, radius=0, x=0, y=0):
        """Register a collision circle on this node."""
        from .director import director
        scene = director.scene
        if scene is not None and scene.coll is not None:
            node = scene.coll.add_node(group, self, radius, x, y)
            self._collision_nodes.add(node)
            return node

    # ------------------------------------------------------------------
    # Layer / lifecycle
    # ------------------------------------------------------------------

    def place(self, layername):
        """Add this node to the named layer on the current scene."""
        from .director import director
        scene = director.scene
        if scene is not None:
            layer = scene.get_layer(layername)
            if layer is not None:
                # Remove from old layer first
                if self._layer is not None and self._layer is not layer:
                    self._layer.remove(self)
                layer.add(self)
                self._layer = layer
        return self

    def delete(self):
        """Mark as deleted, remove from layer, abort all actions, remove collision nodes."""
        self.deleted = True
        self.hidden = True
        if self._layer is not None:
            self._layer.remove(self)
            self._layer = None
        self.abort_actions()
        # Remove collision nodes
        from .director import director
        scene = director.scene
        if scene is not None and scene.coll is not None:
            for cn in list(self._collision_nodes):
                scene.coll.remove_node(cn)
        self._collision_nodes.clear()
