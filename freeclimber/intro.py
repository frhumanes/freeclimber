# -*- coding: utf-8 -*-

import pygame
import os
from pygame.locals import *
from .config import *
from .engine import *

SELECTED_RESOLUTION = get_game_resolution()


class Logo(Entity):

    image = os.path.join(LINUX_GAME_PATH, INTRO_PATH, "fyshon-logo.png")
    layer = "foreground"

    def init(self, fadein=2.0, pause=3.0, fadeout=1.5):
        scale = 1
        if self.width > min(SELECTED_RESOLUTION):
            scale = min(SELECTED_RESOLUTION) * 0.75 / self.width
        self.set(centerx=SELECTED_RESOLUTION[0] // 2, centery=SELECTED_RESOLUTION[1] // 2, scale=scale)
        self.set_alpha(0)
        self.place(Logo.layer)
        self.do(AlphaFade(255, secs=fadein) + Delay(pause) + AlphaFade(0, secs=fadeout))

    def isfinished(self):
        return len(self.current_actions) == 0


class Intro(Scene):

    def init(self, next_scene=None, previous_scene=None):
        self.next_scene = next_scene
        self.previous_scene = previous_scene

    def enter(self):
        self.new_static("bg")
        self.new_layer("foreground")

        screen.clear_color = (255, 255, 255, 255)

        if VOLUME:
            try:
                pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'menuintro.ogg'))
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(VOLUME * 0.01)
            except:
                formatExceptionInfo()

        self.logo = Logo()
        init_gamepad()

    def set_next_scene(self, new_scene):
        self.next_scene = new_scene

    def realtick(self):
        if self.logo.isfinished():
            self.end()

    def handle_keydown(self, ev):
        if ev.key in (K_ESCAPE, K_SPACE, K_RETURN):
            self.end()

    def handle_joybuttondown(self, ev):
        self.end()

    def end(self):
        if self.next_scene:
            director.set_scene(self.next_scene)
        else:
            director.quit()


def init_gamepad(dev=0):
    try:
        j = pygame.joystick.Joystick(dev)
    except:
        return 0
    else:
        j.init()


if __name__ == "__main__":
    screen.init(SELECTED_RESOLUTION, title="Intro Game")
    director.run(Intro)
    print("ticks per sec", director.ticks / director.secs)
    print("realticks per sec", director.realticks / director.secs)
