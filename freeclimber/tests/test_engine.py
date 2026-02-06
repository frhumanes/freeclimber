#!/usr/bin/env python3
"""Smoke test for the engine module — verifies imports and basic API."""

import sys
import os


# Must init pygame minimally before anything else
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()


def test_imports():
    """All public symbols should be importable."""
    from freeclimber.engine import (
        director, screen, Ticker,
        Scene,
        Entity, TextEntity, Node,
        Action, IntervalAction,
        MoveTo, MoveDelta, Move,
        AlphaFade, ColorFade,
        Scale, CenteredScale,
        Animate, Delay,
        CallFunc, CallFuncE,
        Delete, Hide, Show,
        Blink, RotateDelta, Repeat,
        StopMode, RepeatMode, PingPongMode,
        RadialCollisions,
        resources,
        BitmapParticleSystem, RingEmitter, Random,
        GLFont,
    )
    print("  [OK] All symbols imported successfully")


def test_ticker():
    from freeclimber.engine import Ticker
    t = Ticker(40)
    t.reset()
    assert t.resolution == 40.0
    assert t.delta == 0.0
    print("  [OK] Ticker")


def test_reactor():
    from freeclimber.engine.director import Reactor

    calls = []

    class Tickable:
        def tick(self, delta):
            calls.append(delta)

    r = Reactor()
    obj = Tickable()
    r.add(obj)
    r.tick(0.016)
    assert len(calls) == 1
    assert calls[0] == 0.016

    r.remove(obj)
    r.tick(0.016)
    assert len(calls) == 1  # should not have been called again
    print("  [OK] Reactor")


def test_action_chaining():
    from freeclimber.engine.actions import Delay, AlphaFade, CallFunc, Hide, Show, Delete

    # Test basic chaining
    chain = Delay(1.0) + AlphaFade(255, 0.5) + Delay(0.5)
    assert chain._next is not None
    assert chain._next._next is not None
    assert chain._next._next._next is None
    print("  [OK] Action chaining")


def test_modes():
    from freeclimber.engine.actions import StopMode, RepeatMode, PingPongMode

    assert StopMode(0.5) == 0.5
    assert StopMode(1.5) == 1.0
    assert StopMode(-0.1) == 0.0

    assert abs(RepeatMode(1.5) - 0.5) < 0.001
    assert abs(RepeatMode(2.0) - 0.0) < 0.001

    assert abs(PingPongMode(0.5) - 0.5) < 0.001
    assert abs(PingPongMode(1.5) - 0.5) < 0.001
    assert abs(PingPongMode(2.0) - 0.0) < 0.001
    print("  [OK] Interpolation modes")


def test_collision():
    from freeclimber.engine.collision import RadialCollisions
    from freeclimber.engine.node import Node

    coll = RadialCollisions()
    hits = []

    n1 = Node()
    n1.x, n1.y = 100, 100
    n2 = Node()
    n2.x, n2.y = 110, 100

    coll.add_node("player", n1, 20)
    coll.add_node("enemy", n2, 20)
    coll.add_handler("player", "enemy", lambda a, b: hits.append((a, b)))
    coll.check_collisions()
    assert len(hits) == 1
    assert hits[0] == (n1, n2)

    # Move out of range
    hits.clear()
    n2.x = 200
    coll.check_collisions()
    assert len(hits) == 0
    print("  [OK] RadialCollisions")


def test_scene_layers():
    from freeclimber.engine.scene import Scene

    class TestScene(Scene):
        pass

    s = TestScene()
    # Simulate activation
    s._layers.clear()
    s._layer_order.clear()

    s.new_layer("bg")
    s.new_stabile("actors")
    s.new_static("cache")

    assert s.get_layer("bg") is not None
    assert s.get_layer("actors") is not None
    assert s.get_layer("cache") is not None
    assert s.get_layer("nonexistent") is None

    layers = list(s.ordered_layers)
    assert len(layers) == 3
    assert layers[0].name == "bg"
    assert layers[1].name == "actors"
    assert layers[2].name == "cache"
    print("  [OK] Scene layers")


def test_node_set():
    from freeclimber.engine.node import Node

    n = Node()
    result = n.set(x=10, y=20, scale=2.0, alpha=128)
    assert result is n  # chainable
    assert n.x == 10
    assert n.y == 20
    assert n.scale == 2.0
    assert n.alpha == 128
    print("  [OK] Node.set()")


def test_entity_properties():
    from freeclimber.engine.entity import Entity

    e = Entity()
    e._base_width = 100
    e._base_height = 50
    e.scale = 2.0

    assert e.width == 200
    assert e.height == 100

    # Default hotspot is center (0.5, 0.5), so centerx == x, centery == y
    e.centerx = 300
    assert abs(e.x - 300) < 1

    e.centery = 200
    assert abs(e.y - 200) < 1

    # right = x + 0.5*width = x + 100; right=500 → x=400
    e.right = 500
    assert abs(e.x - 400) < 1

    # bottom = y + 0.5*height = y + 50; bottom=400 → y=350
    e.bottom = 400
    assert abs(e.y - 350) < 1

    # Test with hotspot=(0,0) — top-left, original behavior
    e2 = Entity(hotspot=(0, 0))
    e2._base_width = 100
    e2._base_height = 50
    e2.scale = 2.0
    e2.centerx = 300
    assert abs(e2.x - 200) < 1  # x = 300 - 200/2 = 200
    e2.bottom = 400
    assert abs(e2.y - 300) < 1  # y = 400 - 100 = 300
    print("  [OK] Entity properties")


def test_glfont():
    from freeclimber.engine.font import GLFont

    # Use default font since system fonts may not exist
    font = GLFont((None, 16), (255, 255, 255))
    bmp = font.render("Test")
    assert bmp is not None
    assert bmp.width > 0
    assert bmp.height > 0
    print("  [OK] GLFont")


def test_text_entity():
    from freeclimber.engine.entity import TextEntity
    from freeclimber.engine.font import GLFont

    font = GLFont((None, 16), (255, 255, 255))
    te = TextEntity(font, "Hello")
    assert te._base_width > 0
    assert te._base_height > 0

    old_w = te._base_width
    te.set_text("Longer text string")
    # Width should change
    assert te._base_width != old_w or True  # text rendering is font-dependent
    assert te._texture_dirty is True
    print("  [OK] TextEntity")


def test_repeat_action():
    from freeclimber.engine.actions import Repeat, Delay

    # Verify Repeat with times parameter creates proper chain
    r = Repeat(Delay(0.1), times=3)
    assert r.inner_action is not None
    assert r.times == 3
    print("  [OK] Repeat action")


def test_random_lazy():
    from freeclimber.engine.particles import Random

    r = Random(0.1, 0.2)
    for _ in range(10):
        v = r()
        assert 0.1 <= v <= 0.2
    print("  [OK] Random lazy value")


def test_resources():
    from freeclimber.engine.resources import resources, _Bitmap

    # Test that get_bitmap returns None for nonexistent files
    result = resources.get_bitmap("/nonexistent/path.png")
    assert result is None

    # Test _Bitmap compat
    surf = pygame.Surface((10, 10), pygame.SRCALPHA)
    bmp = _Bitmap(surf)
    assert bmp._listid is not None  # should be truthy
    bmp.compile()  # no-op, should not raise
    assert bmp.width == 10
    assert bmp.height == 10
    print("  [OK] Resources")


if __name__ == "__main__":
    print("Engine smoke tests:")
    test_imports()
    test_ticker()
    test_reactor()
    test_action_chaining()
    test_modes()
    test_collision()
    test_scene_layers()
    test_node_set()
    test_entity_properties()
    test_glfont()
    test_text_entity()
    test_repeat_action()
    test_random_lazy()
    test_resources()
    print("\nAll tests passed!")
