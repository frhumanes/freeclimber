##
## requires pygext 0.9.1 or newer
##

import pygame
import os
import glob
from pygame.locals import *
from .engine import *
from random import uniform, choice, randint, random
## First we'll define some constants so we can
## easily alter any game parameters.
from .config import *
from time import sleep





SELECTED_RESOLUTION = get_game_resolution()


## We'll subclass the Entity class for our Cloud objects
class Cloud(Entity):
    nubes = glob.glob(os.path.join(LINUX_GAME_PATH, 'images', 'stages', 'default', 'cloud*.png'))
    image = choice(nubes)
    layer = "weather_b"
    # Pools sorted by image width: small → background, large → foreground
    _pool_bg = []
    _pool_fg = []
    _pool_theme = None

    @classmethod
    def _build_pools(cls, theme):
        paths = glob.glob(os.path.join(LINUX_GAME_PATH, 'images', 'stages', theme, 'cloud*.png'))
        sized = []
        for p in paths:
            bmp = resources.get_bitmap(p, hotspot=None)
            if bmp:
                sized.append((bmp.width, p))
        sized.sort(key=lambda x: x[0])
        mid = max(1, len(sized) // 2)
        cls._pool_bg = [p for _, p in sized[:mid]]
        cls._pool_fg = [p for _, p in sized[mid:]]
        # Fallback: if one pool is empty, use all
        if not cls._pool_bg:
            cls._pool_bg = [p for _, p in sized]
        if not cls._pool_fg:
            cls._pool_fg = [p for _, p in sized]
        cls._pool_theme = theme

    def init(self, theme='default', capa="weather_b"):
        if Cloud._pool_theme != theme:
            Cloud._build_pools(theme)
        pool = Cloud._pool_bg if capa == 'weather_b' else Cloud._pool_fg
        self.shape = resources.get_bitmap(choice(pool), hotspot=None)
        if self.shape is not None:
            self._base_width = self.shape.width
            self._base_height = self.shape.height
            self._texture_dirty = True
        self.place(capa)
        speed = randint(15,60)
        d = choice((-1,1))
        self.ow = self.width # original width
        if capa=='weather_b':
            self.maxw = SELECTED_RESOLUTION[0]/3.0
            self.minw = SELECTED_RESOLUTION[0]/8.0
            self.recolocate(SELECTED_RESOLUTION[1]*3//2)
        else:
            self.maxw = SELECTED_RESOLUTION[0]/2.0
            self.minw = SELECTED_RESOLUTION[0]/6.0
            self.recolocate(-SELECTED_RESOLUTION[1])
        ## Save a reference to the movement action so we can alter it
        ## later on.
        self.do(Move(d*speed,0))
        #self.do(MoveDelta(d*SELECTED_RESOLUTION[0],0, secs= SELECTED_RESOLUTION[0]/speed, mode=RepeatMode))
        #self.move.add_velocity(self.move.vx*0.5, self.move.vy*0.5)

    def check_bounds(self, maxy=0):
        maxy = min(maxy, SELECTED_RESOLUTION[1])
        if self.right < 0:
            self.recolocate(maxy)
            self.left = SELECTED_RESOLUTION[0]
        elif self.left >= SELECTED_RESOLUTION[0]:
            self.recolocate(maxy)
            self.right = 0

    def recolocate(self, maxy=None):
        maxy = int(maxy) if maxy is not None else 0
        x = randint(0,SELECTED_RESOLUTION[0])
        if maxy <= 0:
            y = -randint(abs(maxy), abs(maxy*2))
        else:
            y = randint(0, maxy)
        self.set(x=x, y=y)

class Sky(Scene):

    def init(self, theme="default"):
        self.bg = Entity(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, ASPECT, 'tile.jpg'), hotspot=(0,0))

    def enter(self):

        pygame.event.set_grab(True)
        ## Create a static layer for the non-animated background.
        ## Entities on static layers can't be altered in any way,
        ## they are rendered more efficiently.
        self.new_static("bg")

        ## The actors layer contains the ship and bullets.
        self.new_layer("weather_b")

        self.new_layer("particles")

        ## Load the background.
        self.bg.set(x=0,y=0).place("bg")

        self.system = TestSystem()
        activate_fireworks(None, self.system, 4)

        ## Since the background image covers the whole screen, set
        ## the clear_color to None to save time in screen updates.
        screen.clear_color = None

        for x in range(10):
            Cloud()

    ## This callback is called by the director on every "realtick"
    ## aka. "engine tick". While frames are drawn as fast as possible,
    ## engine ticks happen at a constant time of FPS times per second.
    def realtick(self):
        self.check_bounds()

    def check_bounds(self):
        for e in self.get_layer("weather_b"):
            e.check_bounds()

    def handle_keydown(self, ev):
        if ev.key == K_ESCAPE:
            director.quit()


class TestSystem(BitmapParticleSystem):
    image = os.path.join(LINUX_GAME_PATH, 'images',"common","star.png")
    layer = "particles"
    mutators = []

class Fireworks(RingEmitter):
    delay = 0.01
    num_particles = 1
    life = 0.70
    fade_time = 0.5
    fade_in = 0.1
    scale = Random(0.1, 0.2)
    scale_delta = 0.2
    alfa = 255
    color = (255,255,255,alfa)
    velocity = SELECTED_RESOLUTION[0]//10

    radius = SELECTED_RESOLUTION[0]//16
    tangent = True
    angle = 0
    direction = 0

    colores=[(255,0,0,alfa),(0,255,0,alfa),(30,144,255,alfa), (255,255,0,alfa),(160,32,240,alfa),(0,255,255,alfa),(255,165,0,alfa)]

    def _tweak(self, p):
        if not randint(0,55):
            self.color = choice(Fireworks.colores)
            self.radius = randint(SELECTED_RESOLUTION[0]//20,SELECTED_RESOLUTION[0]//12)
            self.velocity = randint(SELECTED_RESOLUTION[0]//12,SELECTED_RESOLUTION[0]//8)

def activate_fireworks(parent, system, n = 1):
    if parent and isinstance(parent, Entity):
        parent.do(Delete())
    play_audio('silbido%s.ogg' % randint(0,1),0.75)
    for i in range(n):
        node = Entity()
        node.set(realx=randint(0,SELECTED_RESOLUTION[0]), realy=randint(0,SELECTED_RESOLUTION[1]//3))
        system.new_emitter(Fireworks, node)
        delay = uniform(1.2,2.0)
        node.do(Hide()+Delay(delay*i)+CallFunc(play_audio, 'fireworks.ogg', 0.55)+Show()+Delay(delay)+AlphaFade(0,delay/2)+Delay(delay*2)+CallFuncE(activate_fireworks, system, n-2))



if __name__ == "__main__":
    screen.init(SELECTED_RESOLUTION, title="Weather layer")
    #director.ticker = Ticker(60)
    #director.ticker.tick()
    #director.reactor.add(director.ticker)
    #set_ticker(director.ticker, 60)
    director.run(Sky)
    print("ticks per sec", director.ticks/director.secs)
    print("realticks per sec", director.realticks/director.secs)
    print("desired ticks per sec", director.ticker.resolution)
    print("accurace ticks %d%%" % ((director.realticks*100)/(director.secs*director.ticker.resolution)))
