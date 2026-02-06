# -*- coding: utf-8 -*-

import os
import threading
import pygame
from pygame.locals import *
from .engine import *
from .config import *

SELECTED_RESOLUTION = get_game_resolution()

_MENU_PATH = os.path.join(LINUX_GAME_PATH, 'images', 'menu')
_ANIM_PATH = os.path.join(_MENU_PATH, 'animation')
_FONT_BUNDLED = os.path.join(LINUX_GAME_PATH, 'fonts', 'BASIF.TTF')
_FONT_SYSTEM = "/usr/share/fonts/truetype/ttf-larabie-deco/baveuse3.ttf"

DEMO_IDLE_SECS = 40.0
DEMO_PLAY_SECS = 180.0


def _font_spec(size):
    if os.path.isfile(_FONT_SYSTEM):
        return (_FONT_SYSTEM, size)
    return (_FONT_BUNDLED, size)


class MenuAnimation(Entity):
    """Cycling climber animation."""

    image = os.path.join(_ANIM_PATH, 'climber_00.png')
    layer = "animation"

    def init(self, anim_scale=1.0, **kw):
        frames = []
        for i in range(15):
            bmp = resources.get_bitmap(
                os.path.join(_ANIM_PATH, 'climber_%02d.png' % i))
            if bmp:
                frames.append(bmp)
        self.set(centerx=SELECTED_RESOLUTION[0] // 2,
                 centery=int(SELECTED_RESOLUTION[1] * 0.55),
                 scale=anim_scale, alpha=0)
        if frames:
            self.do(Animate(frames, secs=1.5, mode=RepeatMode))
        self.do(AlphaFade(255, 1.5))


class Menu(Scene):

    def init(self, **kw):
        self._selected = 0
        self._options = ["EMPEZAR", "SALIR"]
        self._idle_timer = None
        self._demo_timer = None

    def enter(self):
        # Cancel leftover demo timer from previous run
        self._cancel_demo_timer()
        self._selected = 0

        self.new_layer("bg")
        self.new_stabile("animation")
        self.new_stabile("ui")

        screen.clear_color = (255, 255, 255, 255)

        # Music
        if VOLUME:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.set_volume(VOLUME * 0.01)
                pygame.mixer.music.load(
                    os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'menuintro.ogg'))
                pygame.mixer.music.play(-1)
            except Exception:
                formatExceptionInfo()

        W, H = SELECTED_RESOLUTION

        # Background — cover mode (fill screen, crop excess)
        self._bg = Entity(os.path.join(_MENU_PATH, 'main-bg.jpg'))
        bg_scale = max(W / float(self._bg._base_width),
                       H / float(self._bg._base_height))
        self._bg.set(centerx=W // 2, centery=H // 2,
                     scale=bg_scale, alpha=0).place("bg")
        self._bg.do(AlphaFade(255, 1.0))

        # Climbing animation (60% of screen height)
        anim_scale = H * 0.6 / 1400.0  # climber sprite is 1400px tall
        self._anim = MenuAnimation(anim_scale=anim_scale)

        # Title image — 50% of screen width, above center
        self._title = Entity(os.path.join(_MENU_PATH, 'freeclimber.png'))
        title_scale = W * 0.5 / float(self._title._base_width)
        self._title.set(centerx=W // 2,
                        centery=int(H * 0.15),
                        scale=title_scale, alpha=0).place("animation")
        self._title.do(AlphaFade(255, 3.0))

        # Options inline: EMPEZAR    SALIR
        opt_size = W // 24
        self._opt_entities = []
        cy = int(H * 0.92)
        gap = W // 4
        positions = [W // 2 - gap // 2, W // 2 + gap // 2]
        for i, label in enumerate(self._options):
            color = (100, 200, 0) if i == self._selected else (80, 80, 80)
            font = GLFont(_font_spec(opt_size), color)
            te = TextEntity(font, label)
            te.set(centerx=positions[i], centery=cy, alpha=0).place("ui")
            te.do(Delay(1.0) + AlphaFade(255, 1.0))
            self._opt_entities.append(te)

        # Idle timer → demo
        self._reset_idle_timer()

    def leave(self):
        self._cancel_idle_timer()

    # ------------------------------------------------------------------
    # Timers
    # ------------------------------------------------------------------

    def _cancel_idle_timer(self):
        if self._idle_timer is not None:
            self._idle_timer.cancel()
            self._idle_timer = None

    def _reset_idle_timer(self):
        self._cancel_idle_timer()
        self._idle_timer = threading.Timer(DEMO_IDLE_SECS, self._start_demo)
        self._idle_timer.daemon = True
        self._idle_timer.start()

    def _cancel_demo_timer(self):
        if self._demo_timer is not None:
            self._demo_timer.cancel()
            self._demo_timer = None

    def _start_demo(self):
        self._idle_timer = None
        from .game import Game
        juego = Game(previous_scene=self)
        juego.demo_mode = True
        self._demo_timer = threading.Timer(DEMO_PLAY_SECS, self._end_demo)
        self._demo_timer.daemon = True
        self._demo_timer.start()
        director.set_scene(juego)

    def _end_demo(self):
        self._demo_timer = None
        director.set_scene(self)

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def _update_colors(self):
        opt_size = SELECTED_RESOLUTION[0] // 24
        for i, te in enumerate(self._opt_entities):
            color = (100, 200, 0) if i == self._selected else (80, 80, 80)
            font = GLFont(_font_spec(opt_size), color)
            te._font = font
            te.set_text(self._options[i])

    def _select(self):
        self._cancel_idle_timer()
        if self._selected == 0:
            play_audio('ok.ogg', 0.75)
            if VOLUME:
                try:
                    pygame.mixer.music.fadeout(2500)
                except Exception:
                    formatExceptionInfo()
            from .game import Game
            juego = Game(previous_scene=self)
            for te in self._opt_entities:
                te.do(AlphaFade(0, 1.0))
            self._title.do(AlphaFade(0, 1.5))
            self._bg.do(AlphaFade(0, 2.0)
                        + CallFunc(director.set_scene, juego))
        else:
            self._quit()

    def _quit(self):
        self._cancel_idle_timer()
        if VOLUME:
            try:
                pygame.mixer.music.fadeout(1500)
            except Exception:
                formatExceptionInfo()
        for te in self._opt_entities:
            te.do(AlphaFade(0, 1.0))
        self._title.do(AlphaFade(0, 1.0))
        self._bg.do(AlphaFade(0, 1.0) + CallFunc(director.quit))

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_keydown(self, ev):
        self._reset_idle_timer()
        if ev.key in (K_LEFT, K_a):
            self._selected = (self._selected - 1) % len(self._options)
            self._update_colors()
            play_audio('cliki.ogg', 0.5)
        elif ev.key in (K_RIGHT, K_d):
            self._selected = (self._selected + 1) % len(self._options)
            self._update_colors()
            play_audio('cliki.ogg', 0.5)
        elif ev.key in (K_RETURN, K_SPACE):
            self._select()
        elif ev.key == K_ESCAPE:
            self._quit()

    def handle_joybuttondown(self, ev):
        self._reset_idle_timer()
        if ev.button in (0, 1):
            self._select()
        elif ev.button == 8:
            self._quit()

    def handle_joyaxismotion(self, ev):
        self._reset_idle_timer()
