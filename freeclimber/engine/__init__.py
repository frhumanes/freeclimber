"""Freeclimber engine — pygame-ce replacement for pygext.gl.all.

Usage (replaces ``from pygext.gl.all import *``)::

    from engine import *
"""

from .director import director, screen, Ticker
from .scene import Scene
from .entity import Entity, TextEntity
from .node import Node
from .actions import (
    Action, IntervalAction,
    MoveTo, MoveDelta, Move,
    AlphaFade, ColorFade,
    Scale, CenteredScale,
    Animate, Delay,
    CallFunc, CallFuncE,
    Delete, Hide, Show,
    Blink, RotateDelta, Repeat,
    StopMode, RepeatMode, PingPongMode,
)
from .collision import RadialCollisions
from .resources import resources
from .particles import BitmapParticleSystem, RingEmitter, Random
from .font import GLFont

__all__ = [
    # Director & screen
    "director", "screen", "Ticker",
    # Scene
    "Scene",
    # Entities
    "Entity", "TextEntity", "Node",
    # Actions
    "Action", "IntervalAction",
    "MoveTo", "MoveDelta", "Move",
    "AlphaFade", "ColorFade",
    "Scale", "CenteredScale",
    "Animate", "Delay",
    "CallFunc", "CallFuncE",
    "Delete", "Hide", "Show",
    "Blink", "RotateDelta", "Repeat",
    "StopMode", "RepeatMode", "PingPongMode",
    # Collision
    "RadialCollisions",
    # Resources
    "resources",
    # Particles
    "BitmapParticleSystem", "RingEmitter", "Random",
    # Font
    "GLFont",
]
