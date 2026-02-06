"""Radial collision detection — replaces pygext RadialCollisions."""


class CollisionNode:
    """A circle attached to a parent node (Entity)."""

    __slots__ = ("group", "parent", "radius", "offset_x", "offset_y")

    def __init__(self, group, parent, radius, offset_x=0, offset_y=0):
        self.group = group
        self.parent = parent
        self.radius = float(radius)
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)

    @property
    def x(self):
        return self.parent.x + self.offset_x

    @property
    def y(self):
        return self.parent.y + self.offset_y


class RadialCollisions:
    """Simple brute-force radial collision engine.

    Used as ``collengine = RadialCollisions`` on Scene subclasses.
    The Scene instantiates it and the Director calls
    ``check_collisions()`` each realtick.
    """

    def __init__(self):
        # group_name -> set of CollisionNode
        self._groups = {}
        # list of (group1, group2, callback)
        self._handlers = []

    def add_node(self, group, parent, radius, offset_x=0, offset_y=0):
        node = CollisionNode(group, parent, radius, offset_x, offset_y)
        self._groups.setdefault(group, set()).add(node)
        return node

    def remove_node(self, node):
        group_set = self._groups.get(node.group)
        if group_set is not None:
            group_set.discard(node)

    def add_handler(self, group1, group2, callback):
        self._handlers.append((group1, group2, callback))

    def check_collisions(self):
        for g1_name, g2_name, callback in self._handlers:
            g1 = self._groups.get(g1_name)
            g2 = self._groups.get(g2_name)
            if not g1 or not g2:
                continue
            for n1 in list(g1):
                if n1.parent.deleted or n1.parent.hidden:
                    continue
                for n2 in list(g2):
                    if n2.parent.deleted or n2.parent.hidden:
                        continue
                    if n1.parent is n2.parent:
                        continue
                    dx = n1.x - n2.x
                    dy = n1.y - n2.y
                    dist_sq = dx * dx + dy * dy
                    r_sum = n1.radius + n2.radius
                    if dist_sq < r_sum * r_sum:
                        callback(n1.parent, n2.parent)

    def clear(self):
        self._groups.clear()
        self._handlers.clear()
