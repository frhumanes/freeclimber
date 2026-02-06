##
## requires pygext 0.9.1 or newer
##

import pygame
import os
import glob
from pygame.locals import *

## First we'll define some constants so we can
## easily alter any game parameters.
from .config import *

from .engine import *
from random import uniform, randrange as randint, random
from random import choice

SELECTED_RESOLUTION = get_game_resolution()

closed_windows = 0

class Escalable(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','dummy.png')
    layer = "dummy"

    def init(self, x, y, width = None, height = None, theme='default'):
        self.entities = {}
        self.theme = theme
        self.escala = 1
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'dummy.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        if width:
            self.escala = float(width)/self.width
        self.set(x=x, y=y, scale=self.escala) # also set the drawing scale here

    def isescalable(self):
        # Method to be override
        return True

    escalable = property(isescalable)

    def move(self, dx, dy, secs):
        try:
            self.do(MoveDelta(dx, dy, secs))
            for name, e in self.entities.items():
                e.abort_actions()
                if e.bottom >= 0 or e.top <= SELECTED_RESOLUTION[1]:
                    e.do(MoveDelta(dx, dy, secs))
                else:
                    e.set(x = e.x +dx, y = e.y+dy)
        except:
            formatExceptionInfo()

    def ismoving(self):
        return False

    def abort_actions(self, typefilter=None):
        for name, ent in self.entities.items():
            ent.abort_actions(typefilter)

class MetaWindow(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=Window(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        self.entities['glass']=Glass(x=self.x, y=self.y-0.5*self.height, escala=self.escala, theme=self.theme)
        self.entities['glass'].do(Hide())
        self.entities['room']=Room(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        if not randint(0,5):
            self.entities['item']=Plant(x=self.centerx, y=self.top+self.height*0.40, escala=self.escala/1.75, theme=self.theme)
        elif not randint(0,15):
            self.entities['item']=Bonus(x=self.centerx, y=self.top+self.height*0.35, escala=self.escala, theme=self.theme)
        elif not randint(0,50):
            self.entities['item']=Bomb(x=self.centerx, y=self.top+self.height*0.35, escala=self.escala, theme=self.theme)
        elif not randint(0,50):
            self.entities['item']=Invincibility(x=self.centerx, y=self.top+self.height*0.35, escala=self.escala, theme=self.theme)
        elif not randint(0,55):
            self.entities['item']=Life1up(x=self.centerx, y=self.top+self.height*0.35, escala=self.escala, theme=self.theme)

    def has_dangeorus_plant(self):
        return 'item' in self.entities and isinstance(self.entities['item'], Plant) and self.entities.active

    def close_window(self, cerrar = True):
        if cerrar and not self.ismoving() or self.is_closed():
            if self.entities['glass'].top > self.top:
                self.entities['glass'].y = self.y-0.5*self.height
            self.entities['glass'].do(Show()+MoveTo(self.x, self.y, uniform(2.0,5.0)) + CallFunc(self.set_num_closed, 1) + Delay(uniform(2.0,4.0)) + CallFunc(self.set_num_closed, -1) + MoveTo(self.x, self.y-self.height//2, uniform(2.0,5.0))+Hide())
            #self.entities['glass'].do( Delay(uniform(2.0,4.0) ))
            #self.entities['glass'].do( MoveDelta(0, -self.height/2, uniform(2.0,5.0) ))
        else:
            interrupted = self.entities['glass'].moving
            self.entities['glass'].abort_actions()
            return interrupted


    def ismoving(self):
        return self.entities['glass'].moving

    def set_num_closed(self, value):
        global closed_windows
        closed_windows += value

    moving = property(ismoving)

    def is_closed(self):
        c = self.entities['glass'].y == self.entities['window'].y
        return c

    def lights(self):
        if randint(2):
            self.entities['room'].do(ColorFade((150,150,150,255),2.0))
        else:
            self.entities['room'].do(ColorFade((255,255,175,255),1.0))

    def isescalable(self):
        return not self.is_closed()

    close = property(is_closed, close_window)

    def move(self, dx, dy, secs):
        interrupted = self.ismoving()
        self.do(MoveDelta(dx, dy, secs))
        for name, e in self.entities.items():
            if (isinstance(e,Bonus) or isinstance(e,Life1up)) and e.destroyed:
                continue
            else:
                e.abort_actions(MoveTo)
                e.abort_actions(Delay)
                e.abort_actions(CallFunc)
                e.abort_actions(Hide)
                if interrupted and name == 'glass':
                    e.do(MoveDelta(dx, dy, secs))
                    self.do(Delay(secs+0.15)+CallFunc(self.close_window))
                else:
                    e.do(MoveDelta(dx, dy, secs))


## We'll subclass the Entity class for our Window objects
class Window(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','window.png')
    layer = "building"

    def init(self, x, y, escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'window.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

class Glass(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','glass.png')
    layer = "glass"

    def init(self, x, y, escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'glass.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(scale = escala)
        self.set(x=x, y=y) # also set the drawing scale here

    def ismoving(self):
        return len(self.current_actions)

    moving = property(ismoving)

class Room(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','room.png')
    layer = "room"

    def init(self, x, y, escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'room.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale = escala)


class MetaLBorder(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=LeftBorder(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        #self.entities['glass']=Glass(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        #self.entities['room']=Window(self.x, self.y, self.escala, self.theme)

    def isescalable(self):
        return 'glass' in self.entities

class MetaRBorder(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=RightBorder(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        #self.entities['glass']=Glass(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        #self.entities['room']=Window(self.x, self.y, self.escala, self.theme)

    def isescalable(self):
        return 'glass' in self.entities

class MetaTop(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default', borde = ""):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=CentralTop(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        if borde == 'left':
            self.entities['glass'] = LeftBorder(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        elif borde == 'right':
            self.entities['glass'] = RightBorder(x=self.x, y=self.y, escala=self.escala, theme=self.theme)

class CentralTop(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','ctop.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'ctop.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

class MetaLTop(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=LeftTop(x=self.x, y=self.y, escala=self.escala, theme=self.theme)

class LeftTop(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','ltop.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'ltop.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

class MetaRTop(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=RightTop(x=self.x, y=self.y, escala=self.escala, theme=self.theme)

class RightTop(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','rtop.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'rtop.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

class MetaBottom(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=CentralBottom(x=self.x, y=self.y, escala=self.escala, theme=self.theme)

    def isescalable(self):
        return False

class CentralBottom(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','cbottom.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'cbottom.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here


class MetaObstacle(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window'] = StaticOsbtacle(x=self.x, y=self.y, escala=self.escala, theme=self.theme)
        self.entities['item'] = StaticOsbtacleEffect(x=self.x, y=self.y, escala=self.escala, theme=self.theme, step=self.width, vstep=self.height)

    def isescalable(self):
        return False

    def move(self, dx, dy, secs):
        try:
            self.do(MoveDelta(dx, dy, secs))
            for name, e in self.entities.items():
                if e.bottom >= 0 or e.top <= SELECTED_RESOLUTION[1]:
                    e.do(MoveDelta(dx, dy, secs))
                else:
                    e.set(x = e.x +dx, y = e.y+dy)
        except:
            formatExceptionInfo()

class MetaLBottom(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=LeftBottom(x=self.x, y=self.y, escala=self.escala, theme=self.theme)

    def isescalable(self):
        return False

class LeftCity(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','left-city.png')
    layer = "city"

    def init(self, width, bottom=0, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'left-city.png'), hotspot = (0.5,1))
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        escala = float(width)/self.width
        self.set(left=0, bottom=SELECTED_RESOLUTION[1]-bottom//2, scale=escala) # also set the drawing scale here

class RightCity(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','right-city.png')
    layer = "city"

    def init(self, width, bottom=0, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'right-city.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        escala = float(width)/self.width
        self.set(right=SELECTED_RESOLUTION[0], bottom=SELECTED_RESOLUTION[1]-bottom//2, scale=escala) # also set the drawing scale here

class LeftBottom(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','lbottom.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'lbottom.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

class MetaRBottom(Escalable):

    def __init__(self, x, y, width = None, height = None, theme='default'):
        Escalable.__init__(self, x=x, y=y, width=width, height=height, theme=theme)
        self.entities['window']=RightBottom(x=self.x, y=self.y, escala=self.escala, theme=self.theme)

    def isescalable(self):
        return False

class RightBottom(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','rbottom.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'rbottom.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here


class LeftBorder(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','lborder.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'lborder.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

    def move(self, dx, dy, secs):
        if self.bottom >= 0 or self.top <= SELECTED_RESOLUTION[1]:
            self.do(MoveDelta(dx, dy, secs))
        else:
            self.set(x = self.x +dx, y = self.y+dy)

class RightBorder(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','rborder.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'rborder.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here

    def move(self, dx, dy, secs):
        if self.bottom >= 0 or self.top <= SELECTED_RESOLUTION[1]:
            self.do(MoveDelta(dx, dy, secs))
        else:
            self.set(x = self.x +dx, y = self.y+dy)

class Ground(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','ground.png')
    layer = "building"

    def init(self, width = SELECTED_RESOLUTION[0], theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'ground.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        escala = float(width)/self.width
        self.set(centerx=SELECTED_RESOLUTION[0]//2, bottom=SELECTED_RESOLUTION[1], scale=escala) # also set the drawing scale here
        for i in range(-4,5):
            if i:
                d = i * SELECTED_RESOLUTION[0]//6
            else:
                d = 0
            self.add_collnode("ground", radius = escala*self.height/2, x = d, y = 0)
        self.bin = Entity(os.path.join(LINUX_GAME_PATH, 'images','stages','default','bin.png'))
        self.bin.set(x=SELECTED_RESOLUTION[0]*3//4,centery=self.centery,scale=escala).place('actors')
        self.banco = Entity(os.path.join(LINUX_GAME_PATH, 'images','stages','default','banco.png'))
        self.banco.set(x=SELECTED_RESOLUTION[0]*9//10,centery=self.centery-20,scale=escala).place('actors')

    def move(self, dx, dy, secs):
        if self.bottom >= 0 or self.top <= SELECTED_RESOLUTION[1]:
            self.do(MoveDelta(dx, dy, secs))
            self.bin.do(MoveDelta(dx, dy, secs))
            self.banco.do(MoveDelta(dx, dy, secs))
        else:
            self.set(x = self.x +dx, y = self.y+dy)
            self.bin.set(x = self.x +dx, y = self.y+dy)
            self.banco.set(x = self.x +dx, y = self.y+dy)

class StaticOsbtacle(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','dummy.png')
    layer = "building"

    def init(self, x, y,escala = 1, theme='default'):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'staticenemy_00.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here
        anim = glob.glob(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'staticenemy_*.png'))
        anim.sort()
        self.do(Animate([resources.get_bitmap(e) for e in anim],10, mode=RepeatMode))


class StaticOsbtacleEffect(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','dummy.png')
    layer = "actors"

    # Sentido horario: N, NE, E, SE, S, SW, W, NW
    _DIRECTIONS = ((0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1))

    def init(self, x, y, escala=1, theme='default', step=0, vstep=0):
        self.set(x=x, y=y, scale=escala)
        self.step = step
        self.vstep = vstep
        self.escala = escala
        anim = glob.glob(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'sefx_*.png'))
        anim.sort()
        anim.append(StaticOsbtacleEffect.image)
        self._sefx_frames = [resources.get_bitmap(e) for e in anim]
        ray_files = glob.glob(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'ray_*.png'))
        ray_files.sort()
        self._ray_frames = [resources.get_bitmap(e) for e in ray_files]
        self._dir_idx = 0
        self._cycle(0)

    def _cycle(self, n=0):
        speeds = [0.55, 0.40, 0.25]
        speed = speeds[min(n, 2)]
        if n >= 2:
            self.do(Animate(self._sefx_frames, speed)
                    + CallFunc(self._spawn_ray)
                    + Delay(0.5)
                    + CallFunc(self._cycle, 0))
        else:
            self.do(Animate(self._sefx_frames, speed)
                    + CallFunc(self._cycle, n + 1))

    def _spawn_ray(self):
        if not self._ray_frames or not self.step:
            return
        dx, dy = self._DIRECTIONS[self._dir_idx]
        self._dir_idx = (self._dir_idx + 1) % 8
        ray = Entity()
        ray.set(x=self.x + dx * self.step, y=self.y + dy * self.vstep, scale=self.escala)
        ray.place("actors")
        ray.active = True
        ray.destroyed = False
        ray.destroy = lambda d=0: _destroy_ray(ray)
        ray.add_collnode("enemy", radius=56 * self.escala)
        ray.do(Animate(self._ray_frames, 0.55) + Delete())

    def fx(self):
        pass


def _destroy_ray(ray):
    ray.destroyed = True
    ray.abort_actions()
    ray.do(AlphaFade(0, 0.2) + Delete())


class Bonus(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','bonus_00.png')
    layer = "actors"

    def init(self, x, y, escala=1, theme="default"):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'bonus_00.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here
        self.add_collnode("bonus", 56*self.scale)
        self.destroyed = False
        anim = glob.glob(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'bonus_*.png'))
        anim.sort()
        self.do(Animate([resources.get_bitmap(e) for e in anim],1.8, mode=PingPongMode))


    def destroy(self):
        self.destroyed = True
        self.do(AlphaFade(0, 0.9))
        self.do(Scale(1.5,1.0)+Delete())

class Life1up(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','1up.png')
    layer = "actors"

    def init(self, x, y, escala=1, theme="default"):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, '1up.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here
        self.add_collnode("life1up", 56*self.scale)
        self.destroyed = False

    def destroy(self):
        self.destroyed = True
        self.do(AlphaFade(0, 0.9))
        self.do(Scale(1.5,1.0)+Delete())

class Plant(Entity):

    macetas = glob.glob(os.path.join(LINUX_GAME_PATH, 'images', 'stages', 'default', 'maceta*.png'))
    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','maceta1.png')
    layer = "actors"

    def init(self, x, y, escala=1, theme="default"):
        Plant.macetas = glob.glob(os.path.join(LINUX_GAME_PATH, 'images', 'stages', theme, 'maceta*.png'))
        self.shape = resources.get_bitmap(choice(Plant.macetas), hotspot = None)
        self.active = False
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here
        self.add_collnode("enemy", 56*self.scale)
        self.destroyed = False

    def destroy(self, d = 0):
        self.destroyed = True
        self.abort_actions()
        self.do(CallFunc(play_audio, 'maceta.ogg', 1.0, d)+AlphaFade(0, 0.4))
        self.do(Scale(0.5,0.4)+CallFunc(self.abort_actions, RotateDelta)+Delete())

    def activate(self):
        if self.y > 0 and self.y < SELECTED_RESOLUTION[1] and not self.destroyed and not self.active:
            self.active = True
            self.do(RotateDelta(20,0.16,PingPongMode))
            self.do(Delay(2.5)+Move(0,SELECTED_RESOLUTION[1]//7))
            self.do(Delay(10)+Delete())


class Invincibility(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','invincibility_00.png')
    layer = "actors"

    def init(self, x, y, escala=1, theme="default"):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'invincibility_00.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here
        self.add_collnode("invincibility", 56*self.scale)
        self.destroyed = False
        anim = glob.glob(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'invincibility_*.png'))
        anim.sort()
        self.do(Animate([resources.get_bitmap(e) for e in anim],1.6, mode=RepeatMode))

    def destroy(self):
        self.destroyed = True
        self.do(AlphaFade(0, 0.9))
        self.do(Scale(1.5,1.0)+Delete())

class Bomb(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','stages','default','bomb_00.png')
    layer = "actors"

    def init(self, x, y, escala=1, theme="default"):
        self.shape = resources.get_bitmap(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'bomb_00.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()
        self.set(x=x, y=y, scale=escala) # also set the drawing scale here
        self.add_collnode("bomb", 56*self.scale)
        self.destroyed = False
        anim = glob.glob(os.path.join(LINUX_GAME_PATH, 'images','stages', theme, 'bomb_*.png'))
        anim.sort()
        self.do(Animate([resources.get_bitmap(e) for e in anim],1.8, mode=RepeatMode))

    def destroy(self):
        self.destroyed = True
        onda = Entity(os.path.join(LINUX_GAME_PATH,'images','common', 'onda.png'))
        onda.set(centerx=self.centerx, centery=self.centery, scale=self.width/float(onda.width)).place('building')
        onda.do(CenteredScale(1.5,1.5,(onda.centerx,onda.centery))+Delete())
        self.do(AlphaFade(0, 0.9))
        self.do(Scale(1.5,1.0)+Delete())

class Stage:

    def __init__(self, dim, theme="default"):
        self.escenario = []
        self.dim = dim
        self.theme = theme
        define_difficulty()
        self.initialize()

        if self.escenario:
            width_object = (SELECTED_RESOLUTION[0]//(self.dim[1]+3))
            self.width_unit = width_object
            l = list(range(dim[0]))
            l.reverse()
            h = 0
            self.ground = Ground()
            offset = [(SELECTED_RESOLUTION[0]-width_object*self.dim[1])//2, SELECTED_RESOLUTION[1]-self.ground.height*4//3]
            for planta in l:
                offset[0] = (SELECTED_RESOLUTION[0]-width_object*self.dim[1])/1.5
                for pos in range(dim[1]):
                    e = self.escenario[planta][pos]
                    if not e is None and int(e) in range(10):
                        if e == 1:
                            objeto = MetaLBorder(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 2:
                            objeto = MetaRBorder(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 3:
                            objeto = MetaWindow(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 4:
                            objeto = MetaTop(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 4.1:
                            objeto = MetaTop(x = offset[0], y = offset[1], width= width_object, theme = theme, borde = "left")
                        elif e == 4.2:
                            objeto = MetaTop(x = offset[0], y = offset[1], width= width_object, theme = theme, borde = "right")
                        elif e == 5:
                            objeto = MetaLTop(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 6:
                            objeto = MetaRTop(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 7:
                            objeto = MetaLBottom(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 8:
                            objeto = MetaRBottom(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        elif e == 9:
                            objeto = MetaBottom(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        else:
                            objeto = MetaObstacle(x = offset[0], y = offset[1], width= width_object, theme = theme)
                        self.escenario[planta][pos] = objeto
                        if e>=7 and e <=9:
                            h = objeto.height*1.15
                        else:
                            self.height_unit = h = objeto.height
                        offset[0] += objeto.width
                    else:
                        offset[0] += width_object
                offset[1] -= h
            LeftCity(width=self.width_unit*1.75, theme = theme)
            RightCity(width=self.width_unit*2, theme = theme)

    def subir(self, desp = SELECTED_RESOLUTION[1]//10, secs= 0.5):
        self.ground.move(0, desp, secs = secs)
        for p in self.escenario:
            for e in p:
                if e and isinstance(e, Escalable):
                    #e.abort_actions()
                    #desp = desp and desp or e.height
                    e.move(0, desp, secs = secs)

    def bajar(self, desp = -SELECTED_RESOLUTION[1]//10, secs = 0.5):
        self.ground.move(0, desp, secs = secs)
        for p in self.escenario:
            for e in p:
                if e and isinstance(e, Escalable):
                    #e.abort_actions()
                    #desp = desp and desp or -e.height
                    e.move(0, desp, secs = secs)

    def initialize(self):
        #inicializar escenario:
        #1 => borde izquierdo
        #2 => borde derecho
        #3 => ventana
        #4 => tejado
        #5 => tejado izquierdo
        #6 => tejado derecho
        #7 => planta baja izq
        #8 => planta baja der
        #9 => planta baja central
        #0 => reservado
        #self.escenario = [map((lambda x: 0), range(self.dim[1])),map((lambda x: 0), range(self.dim[1]))]
        self.escenario = []
        dif = DIFFICULTY
        if dif == "easy":
            r = self.dim[0]
            l = self.dim[0]
        elif dif == "normal":
            r = 4
            l = 6
        elif dif == "hard":
            r = 4
            l = 3
        else:
            r = 5
            l = 5
        for j in reversed(range(self.dim[0])):
            floor = []
            no_mas_obstaculos = 0
            for i in range(self.dim[1]):
                if i == 0 and j >= self.dim[0]//l:
                    if j == self.dim[0]-1:
                        floor.append(7)
                    elif j == self.dim[0]//l:
                        floor.append(5)
                    else:
                        floor.append(1)
                elif i == self.dim[1]-1 and j >= self.dim[0]//r:
                    if j == self.dim[0]-1:
                        floor.append(8)
                    elif j == self.dim[0]//r:
                        floor.append(6)
                    else:
                        floor.append(2)
                elif i == 1 and j <= self.dim[0]//l:
                    if j == 0:
                        floor.append(5)
                    elif j == self.dim[0]//l:
                        floor.append(4.1)
                    else:
                        floor.append(1)
                elif i == self.dim[1]-2 and j <= self.dim[0]//r:
                    if j == 0:
                        floor.append(6)
                    elif j == self.dim[0]//r:
                        floor.append(4.2)
                    else:
                        floor.append(2)
                elif j > self.dim[0]//r and i in range(2,self.dim[1]-1):
                    if j == self.dim[0]-1:
                        floor.append(9)
                    else:
                        if not no_mas_obstaculos and 3 <= i <= self.dim[1]-3 and not randint(self.dim[1]*(24//DIF)):
                            floor.append(0)
                            no_mas_obstaculos = True
                        else:
                            floor.append(3)
                elif j <= self.dim[0]//r and i in range(1,self.dim[1]-2):
                    if j == 0:
                        floor.append(4)
                    else:
                        if not no_mas_obstaculos and 2 <= i <= self.dim[1]-4 and not randint(self.dim[1]*(12//DIF)):
                            floor.append(0)
                            no_mas_obstaculos = True
                        else:
                            floor.append(3)
                elif j > self.dim[0]//l and i in range(1,self.dim[1]-2):
                    if j == self.dim[0]-1:
                        floor.append(9)
                    else:
                        floor.append(3)
                elif j <= self.dim[0]//l and i in range(2,self.dim[1]-1):
                    if j == 0:
                        floor.append(4)
                    else:
                        if not no_mas_obstaculos and 3 <= i <= self.dim[1]-3 and not randint(self.dim[1]*(12//DIF)):
                            floor.append(0)
                            no_mas_obstaculos = True
                        else:
                            floor.append(3)
                else:
                    floor.append(None)

            self.escenario.insert(0,floor)
        #for p in self.escenario:
        #   print p

    def get_middle_level(self):
        return self.escenario[self.dim[0]//2][self.dim[1]//2].centery

    def check_windows(self, x):
        for p in self.escenario:
            for e in p:
                if isinstance(e, MetaWindow) and (e.y > 0 and e.y < SELECTED_RESOLUTION[1]):
                    if (e.x == x and not randint(0,250) or not randint(0,2700//DIF)): # random close window
                        e.close_window(True)
                    elif 'item' in e.entities and isinstance(e.entities['item'], Plant) and e.x == x and not randint(0,300//DIF):
                        e.entities['item'].activate()
                    if not randint(0,2000):
                        e.lights()


class Building(Scene):

    nfloors = 25
    theme = "testing"
    if ASPECT.startswith('16'):
        columns = 10
    else:
        columns = 8

    ## Use the RadialCollisions engine, since all our sprites fit
    ## nicely inside a circle.
    collengine = RadialCollisions

    def enter(self):

        #pygame.event.set_grab(True)

        ## Create a static layer for the non-animated background.
        ## Entities on static layers can't be altered in any way,
        ## they are rendered more efficiently.
        self.new_static("bg")

        self.new_layer("city")

        ## The actors layer contains the ship and bullets.
        self.new_layer("dummy")
        self.new_layer("room")
        self.new_layer("glass")
        self.new_stabile("building")
        self.new_stabile("actors")

        ## Load the background.
        e = Entity(os.path.join(LINUX_GAME_PATH, 'images','stages', Building.theme, ASPECT, 'tile.jpg'), hotspot=(0,0))
        e.set(x=0,y=0,scale=SELECTED_RESOLUTION[0]/float(e.width)).place("bg")

        ## Since the background image covers the whole screen, set
        ## the clear_color to None to save time in screen updates.
        screen.clear_color = None

        self.escenario = Stage((Building.nfloors, Building.columns), Building.theme)
        #self.initialize()



    ## This callback is called by the director on every "realtick"
    ## aka. "engine tick". While frames are drawn as fast as possible,
    ## engine ticks happen at a constant time of FPS times per second.
    def realtick(self):
        self.escenario.check_windows(randint(SELECTED_RESOLUTION[1]))

    def handle_keydown(self, ev):
        if ev.key == K_ESCAPE:
            director.quit()
        if ev.key == K_DOWN:
            self.escenario.bajar()
            for e in self.get_layer("city"):
                e.do(MoveDelta(0,-20, secs= 0.50))
        elif ev.key == K_UP:
            self.escenario.subir()
            for e in self.get_layer("city"):
                e.do(MoveDelta(0,+20, secs= 0.50))

    def handle_joyaxismotion(self, ev):
        if ev.axis == 1 and ev.value == 1:
            self.escenario.bajar()
            for e in self.get_layer("city"):
                e.do(MoveDelta(0,-20, secs= 0.50))
        elif ev.axis == 1 and ev.value == -1:
            self.escenario.subir()
            for e in self.get_layer("city"):
                e.do(MoveDelta(0, +20, secs= 0.50))

def init_gamepad(dev = 0):
    try:
        j = pygame.joystick.Joystick(dev)
    except:
        return 0
    else:
        j.init()


if __name__ == "__main__":
    screen.init(SELECTED_RESOLUTION, title="Building layer")
    #director.ticker = Ticker(60)
    #director.visible_collision_nodes = True
    init_gamepad()
    director.run(Building)
    print("ticks per sec", director.ticks/director.secs)
    print("realticks per sec", director.realticks/director.secs)
