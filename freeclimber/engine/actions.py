"""Action system — replaces pygext action classes with chaining support."""

import copy
import pygame


# ---------------------------------------------------------------------------
# Interpolation modes
# ---------------------------------------------------------------------------

def StopMode(t):
    """Clamp to [0,1], action ends when t >= 1."""
    return min(max(t, 0.0), 1.0)


def RepeatMode(t):
    """Loop: t wraps around via modulo."""
    return t % 1.0


def PingPongMode(t):
    """Bounce: 0→1→0→1…"""
    t = t % 2.0
    return t if t <= 1.0 else 2.0 - t


# ---------------------------------------------------------------------------
# Base Action
# ---------------------------------------------------------------------------

class Action:
    """Base class for all actions."""

    _next = None  # chained action

    def __add__(self, other):
        """Chain two actions: ``a + b`` means *b* runs after *a* ends."""
        a = copy.copy(self)
        # Walk to end of chain
        tail = a
        while tail._next is not None:
            tail = tail._next
        tail._next = copy.copy(other)
        return a

    def do(self, entity):
        """Start this action on *entity*.  Called by Entity.do()."""
        c = copy.copy(self)
        c.entity = entity
        c._start(entity)
        entity.current_actions.add(c)
        from .director import director
        director.reactor.add(c)
        return c

    def _start(self, entity):
        """Override to capture starting state."""
        self.init()

    def init(self):
        """User override — called when the action starts on an entity."""
        pass

    def tick(self, delta):
        """Called every frame by the Reactor."""
        pass

    def end(self):
        """Called when the action finishes normally."""
        self.abort()
        if self._next is not None:
            self._next.do(self.entity)

    def abort(self):
        """Remove this action from entity + reactor."""
        try:
            self.entity.current_actions.discard(self)
        except AttributeError:
            pass
        from .director import director
        director.reactor.remove(self)

    # Convenience for Repeat / chain building
    def _deep_copy_chain(self):
        c = copy.copy(self)
        if c._next is not None:
            c._next = c._next._deep_copy_chain()
        return c


# ---------------------------------------------------------------------------
# IntervalAction — time‑based with interpolation
# ---------------------------------------------------------------------------

class IntervalAction(Action):
    """Action that runs over a fixed *secs* duration with a *mode*."""

    def __init__(self, secs=1.0, mode=StopMode):
        self.secs = float(secs)
        self.mode = mode

    def _start(self, entity):
        self._elapsed = 0.0
        self.start(entity)

    def start(self, entity):
        """Override: capture starting values."""
        pass

    def tick(self, delta):
        self._elapsed += delta
        if self.secs <= 0:
            raw_t = 1.0
        else:
            raw_t = self._elapsed / self.secs
        t = self.mode(raw_t)
        self.update(t)
        if self.mode is StopMode and raw_t >= 1.0:
            self.end()

    def update(self, t):
        """Override: apply interpolated value (t in [0,1])."""
        pass


# ---------------------------------------------------------------------------
# Concrete actions
# ---------------------------------------------------------------------------

class MoveTo(IntervalAction):
    """Move entity to absolute (x, y) over *secs*."""

    def __init__(self, x, y, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.target_x = float(x)
        self.target_y = float(y)

    def start(self, entity):
        self.start_x = float(entity.x)
        self.start_y = float(entity.y)
        self.dx = self.target_x - self.start_x
        self.dy = self.target_y - self.start_y

    def update(self, t):
        self.entity.x = self.start_x + self.dx * t
        self.entity.y = self.start_y + self.dy * t


class MoveDelta(IntervalAction):
    """Move entity by (dx, dy) relative to starting position over *secs*."""

    def __init__(self, dx, dy, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.move_dx = float(dx)
        self.move_dy = float(dy)

    def start(self, entity):
        self.start_x = float(entity.x)
        self.start_y = float(entity.y)

    def update(self, t):
        self.entity.x = self.start_x + self.move_dx * t
        self.entity.y = self.start_y + self.move_dy * t


class Move(Action):
    """Continuous velocity-based movement — moves (vx, vy) pixels/sec every frame."""

    def __init__(self, vx, vy=0):
        self.vx = float(vx)
        self.vy = float(vy)

    def _start(self, entity):
        pass

    def tick(self, delta):
        self.entity.x += self.vx * delta
        self.entity.y += self.vy * delta


class AlphaFade(IntervalAction):
    """Interpolate entity alpha to *target* over *secs*."""

    def __init__(self, target, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.target_alpha = float(target)

    def start(self, entity):
        self.start_alpha = float(entity.alpha)
        self.dalpha = self.target_alpha - self.start_alpha

    def update(self, t):
        self.entity.alpha = int(self.start_alpha + self.dalpha * t)


class ColorFade(IntervalAction):
    """Interpolate entity color tuple to *target_color* over *secs*."""

    def __init__(self, target_color, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.target_color = tuple(float(c) for c in target_color)

    def start(self, entity):
        self.start_color = tuple(float(c) for c in entity.color)
        n = len(self.target_color)
        sc = self.start_color[:n]
        self.dcolor = tuple(self.target_color[i] - sc[i] for i in range(n))

    def update(self, t):
        sc = self.start_color
        n = len(self.dcolor)
        self.entity.color = tuple(int(sc[i] + self.dcolor[i] * t) for i in range(n))


class Scale(IntervalAction):
    """Interpolate entity scale to *target* over *secs*."""

    def __init__(self, target, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.target_scale = float(target)

    def start(self, entity):
        self.startscale = float(entity.scale)
        self.dscale = self.target_scale - self.startscale

    def update(self, t):
        self.entity.scale = self.startscale + self.dscale * t

    # Expose limited() alias used by building.py's CenteredScale subclass
    def limited(self, t):
        self.update(t)


class CenteredScale(Scale):
    """Scale while keeping a fixed center point.

    The game redefines this in building.py, but we provide the base
    version here so it's available from the engine import.
    """

    def __init__(self, target, secs=1.0, center=None, mode=StopMode):
        super().__init__(target, secs, mode)
        self.center = center

    def start(self, entity):
        super().start(entity)

    def update(self, t):
        self.entity.scale = self.startscale + self.dscale * t
        if self.center:
            self.entity.set(centerx=self.center[0], centery=self.center[1])


class Animate(IntervalAction):
    """Cycle through a list of bitmap frames over *secs*."""

    def __init__(self, frames, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.frames = list(frames)

    def start(self, entity):
        self._frame_idx = -1

    def update(self, t):
        if not self.frames:
            return
        idx = int(t * len(self.frames))
        idx = min(idx, len(self.frames) - 1)
        if idx != self._frame_idx:
            self._frame_idx = idx
            self.entity.shape = self.frames[idx]
            self.entity._texture_dirty = True

    def cleanup(self):
        """Override point — Wait subclass overrides this to skip resetting."""
        if self.frames:
            self.entity.shape = self.frames[0]
            self.entity._texture_dirty = True

    def end(self):
        # Don't reset frame on normal end if mode loops
        if self.mode is StopMode:
            self.cleanup()
        super().end()


class Delay(IntervalAction):
    """Wait for *secs* then chain to next action."""

    def __init__(self, secs=1.0):
        super().__init__(secs, StopMode)

    def update(self, t):
        pass


class CallFunc(Action):
    """Call func(*args) immediately, then chain."""

    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        c.func(*c.args)
        c._finish_chain(entity)
        return c

    def _finish_chain(self, entity):
        if self._next is not None:
            self._next.do(entity)


class CallFuncE(Action):
    """Call func(entity, *args) immediately, then chain."""

    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        c.func(entity, *c.args)
        c._finish_chain(entity)
        return c

    def _finish_chain(self, entity):
        if self._next is not None:
            self._next.do(entity)


class Delete(Action):
    """Delete the entity immediately, then chain."""

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        entity.delete()
        if c._next is not None:
            c._next.do(entity)
        return c


class Hide(Action):
    """Hide the entity immediately, then chain."""

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        entity.hidden = True
        if c._next is not None:
            c._next.do(entity)
        return c


class Show(Action):
    """Show the entity immediately, then chain."""

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        entity.hidden = False
        if c._next is not None:
            c._next.do(entity)
        return c


class Blink(IntervalAction):
    """Toggle hidden on/off.

    Signatures found in game code:
    - ``Blink(on_time, off_time=None, repeats=None)``
    - ``Blink(on_time)`` — blinks indefinitely with on==off time
    """

    def __init__(self, on_time, off_time=None, repeats=None):
        self.on_time = float(on_time)
        self.off_time = float(off_time) if off_time is not None else self.on_time
        self.cycle = self.on_time + self.off_time
        if repeats is not None:
            secs = self.cycle * repeats
            mode = StopMode
        else:
            secs = 1e9  # effectively infinite
            mode = RepeatMode
        super().__init__(secs, mode)
        self.repeats = repeats

    def start(self, entity):
        self._prev_hidden = entity.hidden

    def update(self, t):
        elapsed = t * self.secs
        phase = elapsed % self.cycle
        self.entity.hidden = phase >= self.on_time

    def end(self):
        self.entity.hidden = False
        super().end()

    def abort(self):
        try:
            self.entity.hidden = False
        except AttributeError:
            pass
        super().abort()


class RotateDelta(IntervalAction):
    """Rotate entity by *angle* degrees over *secs*."""

    def __init__(self, angle, secs=1.0, mode=StopMode):
        super().__init__(secs, mode)
        self.target_angle = float(angle)

    def start(self, entity):
        self.start_angle = float(entity.angle)

    def update(self, t):
        self.entity.angle = self.start_angle + self.target_angle * t


class Repeat(Action):
    """Repeat an action chain *times* times (None = infinite)."""

    def __init__(self, action, times=None):
        self.inner_action = action
        self.times = times

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        c._count = 0
        c._run_inner(entity)
        return c

    def _run_inner(self, entity):
        if self.times is not None and self._count >= self.times:
            # Done repeating — chain to next
            if self._next is not None:
                self._next.do(entity)
            return
        self._count += 1
        # Build a copy of the inner action chain with a sentinel at the end
        inner = self.inner_action._deep_copy_chain()
        # Find tail of inner chain
        tail = inner
        while tail._next is not None:
            tail = tail._next
        # Append a CallFunc that triggers the next repetition
        sentinel = _RepeatSentinel(self)
        tail._next = sentinel
        inner.do(entity)

    def _on_iteration_done(self):
        self._run_inner(self.entity)


class _RepeatSentinel(Action):
    """Internal helper — signals that one repeat iteration has finished."""

    def __init__(self, repeat_action):
        self._repeat = repeat_action

    def _start(self, entity):
        pass

    def do(self, entity):
        c = copy.copy(self)
        c.entity = entity
        c._repeat._on_iteration_done()
        return c
