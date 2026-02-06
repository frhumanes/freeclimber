#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth floor, Boston,
#       MA 02110-1301, USA.

#!/usr/bin/python
# -*- coding: utf-8 -*-

from pygame.locals import *
from .engine import *
from .config import *
from .intro import Intro
from .menu import Menu
from .building import Escalable


SELECTED_RESOLUTION = get_game_resolution()


def set_ticker(ticker, resolution):
    ticker.resolution = float(resolution)
    ticker.tick_delay = 1000.0 / resolution
    ticker.now = pygame.time.get_ticks()
    ticker.prev_tick = ticker.now
    ticker.prev_realtick = ticker.now
    ticker.next_realtick = ticker.now + ticker.tick_delay
    ticker.delta = 0.0
    ticker.tick_delta = 0.0
    ticker.realtick_delta = 0.0
    ticker.realtick = False

def main():

    pygame.mixer.pre_init(44100, -16, 2, 3702)
    screen.init(SELECTED_RESOLUTION, fullscreen=FULLSCREEN, title="FreeClimber")
    try:
        icon = pygame.transform.scale(pygame.image.load(os.path.join(LINUX_GAME_PATH, 'images', 'climber', 'female', 'miniclimber_10.png')).convert_alpha(), (32, 32))
        screen._window.set_icon(icon)
    except Exception:
        pass
    if VOLUME:
        try:
            pygame.mixer.music.set_volume(VOLUME * 0.01)
        except:
            formatExceptionInfo()

    set_ticker(director.ticker, FPS)
    menu = Menu()
    intro = Intro(next_scene=menu, previous_scene=None)
    director.run(intro)
    try:
        pygame.mixer.music.stop()
    except:
        pass
    try:
        print("ticks per sec", director.ticks / director.secs)
        print("realticks per sec", director.realticks / director.secs)
        print("desired ticks per sec", director.ticker.resolution)
        print("accuracy rate %d%%" % ((director.realticks * 100) / (director.secs * director.ticker.resolution)))
    except ZeroDivisionError:
        formatExceptionInfo()
    pygame.quit()
    director.quit()
    director.running = True


if __name__ == "__main__":
    main()
