# -*- coding: utf-8 -*-
##
## requires pygext 0.9.1 or newer
##

import pygame
import os
from pygame.locals import *
#from menu import MainMenu
from math import sqrt

## First we'll define some constants so we can
## easily alter any game parameters.
from .config import *

from .engine import *
from random import random, randint, choice
from glob import glob
from math import ceil, floor
from base64 import b64encode
#import socket
from .building import Escalable, MetaWindow

SELECTED_RESOLUTION= get_game_resolution()

colormap={
    'red':(255,0,0,255) ,\
    'blue':(0,0,255,255) ,\
    'green':(0,255,0,255) ,\
    'violet':(160,32,240,255) ,\
    'white':(255,255,255,255) ,\
    'yellow':(255,255,0,255) ,\
    'orange':(255,165,0,255) ,\
    'pink':(255,128,255,255) ,\
}

class Wait(Animate):

    def cleanup(self):
        pass

class Status(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','climber','mini_shadow.png')
    layer = 'info'

    def init(self, width, sex = 'female', color_player = None, type = 'normal', x = 0, y = 0):
        anim = glob(os.path.join(LINUX_GAME_PATH, 'images','climber',sex,'miniclimber_*.png'))
        anim.sort()

        self.ent = []
        self.type = type

        icon = Entity(os.path.join(LINUX_GAME_PATH, 'images','climber', sex ,'miniclimber_00.png'))
        shadow = Entity(os.path.join(LINUX_GAME_PATH, 'images','climber','mini_shadow.png'))

        if self.type == 'ghost':
            bg = Entity(os.path.join(LINUX_GAME_PATH, 'images','climber', 'mini_ghost.png'))
        elif color_player:
            bg = Entity(os.path.join(LINUX_GAME_PATH, 'images','climber', 'mini_b_'+color_player+'.png'))
        else:
            bg = Entity(os.path.join(LINUX_GAME_PATH, 'images','climber', 'mini_b_red.png'))

        if width:
            self.escala = float(width)/self.width

        alpha = 256
        if self.type == "mini":
            x, y, alpha = width, SELECTED_RESOLUTION[1]-width, 256
        elif self.type == "normal":
            x, y, alpha = int(width/1.5)+x, int(width/1.5)+y, 256
        elif self.type == "ghost":
            alpha, self.escala = 192, self.escala

        if self.type == "normal":
            self.escala = self.escala*1.15

        self.set(centerx=x, centery=y, scale=self.escala, alpha = alpha) # also set the drawing scale here
        if self.type == "mini":
            self.marco = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'status.png'))
            self.marco.set(left=self.left-self.width//10, centery=self.centery, scale=self.escala*1.1).place("info")
            self.marco.do(ColorFade(colormap[color_player],1.0,mode=PingPongMode))

        bg.set(scale = self.escala, centerx=self.x,centery=self.y, alpha = alpha).place('info')
        shadow.set(scale = self.escala, centerx=self.x,centery=self.y, alpha = alpha).place('info')

        if self.type == 'normal':
            r,g,b,a = colormap[color_player]
            invcolor = (255-r, 255-g, 255-b, 192)
            self.position_font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/planetbe.ttf", int(width*0.5)),invcolor)
            self.position = TextEntity(self.position_font, "01")
            self.position.set(centerx= self.centerx, centery=self.centery ).place("info")
        elif self.type == 'mini':
            self.position_font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/planetbe.ttf", int(width*0.45)),(225,225,255,192))
            self.position = TextEntity(self.position_font, "01")
            self.position.set(left = int(self.right*1.05), centery = self.centery+1).place("info")
        self.place('info')
        self.do(Animate([resources.get_bitmap(e) for e in anim], 0.75, mode = PingPongMode))
        anim = glob(os.path.join(LINUX_GAME_PATH, 'images','climber',sex,'miniclimberloser_*.png'))
        anim.sort()
        self.loser_anim = Animate([resources.get_bitmap(e) for e in anim], 0.75, mode = PingPongMode)
        if self.type == 'normal':
            effect = AlphaFade(255,0.75)+Delay(3.0)+AlphaFade(0,0.5)+Delay(1.0)
            self.do(Repeat(effect))
        elif self.type == 'ghost':
            self.do(ColorFade(colormap[color_player],2.0)+AlphaFade(alpha,1.5))
            bg.do(ColorFade(colormap[color_player],2.0)+AlphaFade(alpha,1.5)+RotateDelta(360,4.0,RepeatMode))
            shadow.do(ColorFade(colormap[color_player],2.0)+AlphaFade(alpha//2,1.5))

        self.ent += [shadow, bg]

    def set_status(self, position = None):
        if self.type == "static":
            pass
        elif position:
            self.position.set_text("%.2d" % (int(position)-1))
        if self.type == 'normal':
            self.position.set(centerx = self.centerx, centery = self.centery)

    def loser(self):
        self.abort_actions(AlphaFade)
        self.abort_actions(Delay)
        self.abort_actions(Animate)
        self.do(AlphaFade(255,1.0))
        self.do(self.loser_anim)

    def erase(self):
        if self.type == 'normal' or self.type == 'mini':
            self.position.do(Delete())

        if self.type == 'mini':
            self.marco.do(Delete())
        for e in self.ent:
            e.do(Delete())
        self.do(Delete())

    def escalar(self, escala):
        for e in self.ent:
            e.set(scale = escala)
        self.set(scale = escala)

    def moveTo(self, x, y, secs=0.25, escala = None, alpha=None):
        self.do(MoveTo(x, y, secs))
        if self.type == 'normal' or self.type == 'mini':
            self.position.do((MoveTo(self.position.x, y-self.position.height//2, secs)))
            if self.type == "mini":
                dx = self.x - self.marco.x
                self.marco.do((MoveTo(x-dx, y, secs)))
        for e in self.ent:
            e.do(MoveTo(x, y, secs))
            if escala: e.do(Scale(escala*self.escala, secs))
            if alpha: e.do(AlphaFade(alpha, secs))
        if escala:
            self.do(Scale(escala*self.escala, secs))
            self.position.do(Scale(escala, secs))
        if alpha:
            self.do(AlphaFade(alpha, secs))
            self.position.do(AlphaFade(alpha, secs))


class Level_board(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','common','miniclimber.png')
    layer = "info"

class LifeBoard(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','common','climber.png')
    layer = "info"

    def init(self, x, y, width = None, lifes = None, theme='default'):
        self.num = lifes and lifes or 3
        if width:
            self.escala = float(width)/self.width
        self.set(x=x, y=y, scale=self.escala)
        self.marco = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'status.png'))
        self.marco.set(centerx=self.right, centery=self.centery, scale=self.escala*1.1,alpha=190).place(LifeBoard.layer)
        self.place(LifeBoard.layer)
        self.lifeboard = TextEntity(GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/worldofw.ttf", self.width//2),(255,0,0)), "x %d" % self.num)
        self.lifeboard.set(centerx= self.right+self.width//3, centery = self.centery).place(LifeBoard.layer)

    def set_lifes(self, num):
        if self.num == 2 and num == 1:
            self.lifeboard.do(Blink(0.25))
        elif self.num == 1 and num == 2:
            self.lifeboard.abort_actions(Blink)
        self.num = num
        self.lifeboard.set_text("x %d" % self.num)
        self.lifeboard.set(centerx = self.right+self.width//3, centery = self.centery)


def distance(a, b):
    if not(isinstance(a, Entity) and isinstance(b, Entity)):
        return 0
    else:
        return sqrt((a.x-b.x)**2+(a.y-b.y)**2)

class Climber(Entity):

    image = os.path.join(LINUX_GAME_PATH, 'images','climber','female','climber.png')
    layer = "actors"

    def init(self, x, y, width = None, height = None, sex = 'female', color_player = None, ghost = False):
        self.id = b64encode(str(randint(10**5,10**7)).encode()).decode()
        self.name = self.id
        self.escala = 1
        self.lifes = 3
        self.level = 2
        self.window = 2
        self.score = 0
        self.color_player = color_player and color_player or choice(list(colormap.keys()))
        self.ghost = ghost

        self.climber_path = os.path.join(LINUX_GAME_PATH, 'images', 'climber', sex)

        self.shape = resources.get_bitmap(os.path.join(self.climber_path, 'climber.png'), hotspot = None)
        if self.shape is not None and self.shape._listid is None:
            self.shape.compile()

        if width:
            self.escala = float(width)/self.width

        self.altura = height and height or self.height
        self.set(x=x, y=y, scale=self.escala) # also set the drawing scale here

        self.last_movement=None
        self.manos = 2
        #self.escudo = Escudo()
        #self.escudo.set(centerx = self.centerx, centery = self.centery, scale = self.escala/2)
        #self.escudo.do(Hide())

        up1left = glob(self.climber_path+'/*_up1left_*.png')
        up1left.sort()

        up2left = glob(self.climber_path+'/*_up2left_*.png')
        up2left.sort()

        up3left = glob(self.climber_path+'/*_up3left_*.png')
        up3left.sort()

        up1right = glob(self.climber_path+'/*_up1right_*.png')
        up1right.sort()

        up2right = glob(self.climber_path+'/*_up2right_*.png')
        up2right.sort()

        up3right = glob(self.climber_path+'/*_up3right_*.png')
        up3right.sort()

        left = glob(self.climber_path+'/*_left_*.png')
        left.sort()

        right = glob(self.climber_path+'/*_right_*.png')
        right.sort()

        down = glob(self.climber_path+'/*_down_*.png')
        down.sort()

        fall = glob(self.climber_path+'/*_fall_*.png')
        fall.sort()

        parachute = glob(self.climber_path+'/*_parachute_*.png')
        parachute.sort()

        wait = glob(self.climber_path+'/*_wait_*.png')
        wait.sort()

        waitleft = glob(self.climber_path+'/*_waitleft_*.png')
        waitleft.sort()

        waitright = glob(self.climber_path+'/*_waitright_*.png')
        waitright.sort()

        final = glob(self.climber_path+'/*_final_*.png')
        final.sort()

        winner = glob(self.climber_path+'/*_winner_*.png')
        winner.sort()

        self.animations={'up1left': Animate([resources.get_bitmap(e) for e in up1left], 0.5),\
                        'up1right': Animate([resources.get_bitmap(e) for e in up1right], 0.5),\
                        'up2left': Animate([resources.get_bitmap(e) for e in up2left], 0.7),\
                        'up2right': Animate([resources.get_bitmap(e) for e in up2right], 0.7),\
                        'up3left': Animate([resources.get_bitmap(e) for e in up3left], 0.5),\
                        'up3right': Animate([resources.get_bitmap(e) for e in up3right], 0.5),\
                        'down':  Animate([resources.get_bitmap(e) for e in down], 0.5),\
                        'left': Animate([resources.get_bitmap(e) for e in left], 0.95),\
                        'right': Animate([resources.get_bitmap(e) for e in right], 0.95),\
                        'wait': Wait([resources.get_bitmap(e) for e in wait], 1.0, mode = PingPongMode),\
                        'waitleft': Wait([resources.get_bitmap(e) for e in waitleft], 0.5, mode = PingPongMode),\
                        'waitright': Wait([resources.get_bitmap(e) for e in waitright], 0.5, mode = PingPongMode),\
                        'fall': Animate([resources.get_bitmap(e) for e in fall], 0.5, mode = PingPongMode),\
                        'winner': Animate([resources.get_bitmap(e) for e in final], 0.5)+Animate([resources.get_bitmap(e) for e in winner], 0.5, mode = PingPongMode),\
                        'parachute': Repeat(Animate([resources.get_bitmap(e) for e in fall], 0.5),times = 2) + Animate([resources.get_bitmap(e) for e in parachute], 0.5) + RotateDelta(20,0.5,PingPongMode)
                        }

        self.movements={'up1left': MoveDelta(0, ceil(-self.altura/2.0), 0.4)+Delay(0.1),\
                        'up1right': MoveDelta(0, ceil(-self.altura/2.0), 0.4)+Delay(0.1),\
                        'up2left': Delay(0.1)+MoveDelta(0, floor(-self.altura/2.0), 0.5)+Delay(0.1),\
                        'up2right': Delay(0.1)+MoveDelta(0, floor(-self.altura/2.0), 0.5)+Delay(0.1),\
                        'up3left': Delay(0.5),\
                        'up3right': Delay(0.5),\
                        'halfdown': MoveDelta(0, self.altura//2, 0.25),\
                        'down': MoveDelta(0, self.altura, 0.5),\
                        'left': Delay(0.25)+MoveDelta(-self.width,0, 0.50)+Delay(0.20),\
                        'right': Delay(0.25)+MoveDelta(self.width,0, 0.50)+Delay(0.20),\
                        'wait': None,\
                        'waitleft': None,\
                        'waitright': None,\
                        'fall': MoveDelta(0,10,1.0)+MoveDelta(0,SELECTED_RESOLUTION[1]//2,1.0),\
                        'parachute': MoveDelta(0,10,0.9)+MoveDelta(0,30,0.5)+MoveDelta(self.x,SELECTED_RESOLUTION[1]+self.height*2,6.0),\
                        'winner': MoveDelta(0, ceil(-self.altura//3), 0.15)+Delay(0.1)+MoveDelta(0, ceil(-self.altura//3), 0.1)+Delay(0.25),\
                        }

        if ghost:
            if color_player:
                c = list(colormap[color_player])
                c[-1] = 128
                self.set(alpha = 0)
                self.do(ColorFade(c,1.0))
            else:
                self.set(alpha=128)
            #self.do(AlphaFade(160,0.5))
        else:
            score_font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-uncommon/endless.ttf", self.width//2),(225,225,30))
            shadow_font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-uncommon/endless.ttf", self.width//2),(0,0,0,160))
            #score_font = GLFont(("Wargames", self.width/2),(225,225,30))
            #shadow_font = GLFont(("Wargames", self.width/2),(0,0,0,160))
            position_font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/baveuse3.ttf", int(self.width*0.9)),(255,255,255))

            self.scoreboard = TextEntity(score_font, "0")
            self.scoreshadow = TextEntity(shadow_font, "0")
            self.scoremarco = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'status.png'))

            self.scoremarco.place('info')
            self.scoreshadow.place("info")
            self.scoreboard.set(right= SELECTED_RESOLUTION[0]*20//21, centery = self.scoreboard.height).place("info")
            self.scoremarco.set(scale=self.scoreboard.height/float(self.scoremarco.height/1.7),alpha=190)
            self.scoremarco.set(right=SELECTED_RESOLUTION[0], centery=self.scoreboard.centery)
            self.scoreshadow.set(x= self.scoreboard.x+2, y = self.scoreboard.y+2)

            self.lifeboard = LifeBoard(x = SELECTED_RESOLUTION[0]-self.width*1.25, y = self.scoreboard.bottom+self.scoreboard.height*6//5, width = int(self.width*0.75))

            self.levelboard= Status(width=width*1.15, color_player = self.color_player, type = 'normal')
            #self.ghost = Status(x=SELECTED_RESOLUTION[0]-100,y=500,width=width, color_player = 'blue', type = 'ghost')
            #self.mini =  Status(width=int(width*0.75), color_player = 'green', type = 'mini')

            self.add_collnode("player", radius=30*self.scale, x=0, y=int(-160*self.scale))

            self.update()

    def set_in_window(self, window, first = None):
        self.altura = window.height
        self.last_movement = None
        self.move()
        if self.lifes > 0:
            if self.ghost:
                c = list(colormap[self.color_player])
                c[-1] = 128
                self.do(ColorFade(c,0.5))
                self.do(MoveTo(window.x, window.y + window.height*3//5, secs=0.5))
            else:
                self.set(x= window.x, y=window.y + window.height*3//5)
                if first:
                    self.do(Blink(0.35,0.15,repeats=20))
                else:
                    self.do(Blink(0.35,0.15,repeats=10))
        else:
            self.set(x= SELECTED_RESOLUTION[0]//2, y=SELECTED_RESOLUTION[1]//2, alpha = 0)
        #self.escudo.set(centerx = self.centerx, centery = self.centery)

    def update(self):
        self.refresh_boards()

    def refresh_boards(self):
        #self.level.set_text("%d" % (self.level-1))
        #self.level.set(centerx=SELECTED_RESOLUTION[0]/12)
        self.scoreboard.set_text("%d" % self.score)
        self.scoreboard.set(centerx = self.scoremarco.centerx)
        self.scoreshadow.set_text("%d" % self.score)
        self.scoreshadow.set(x = self.scoreboard.x + 2)
        self.levelboard.set_status(self.level)
        self.lifeboard.set_lifes(self.lifes)

    def move(self, movement="wait", stage = None):
        debug("Requested %s" % movement)
        if (self.ismoving() and not movement == 'hit') or self.last_movement == "fall":
            debug("Movimiento descartado")
            return None
        elif stage:
            f, w = self.level, self.window
            if movement == 'down' and not (self.manos == 1 or (f > 1 and isinstance(stage[-f+1][w], Escalable) and stage[-f+1][w].isescalable())):
                debug("Movimiento descartado")
                return None
            elif movement == 'up_right' and not (self.manos == 1 or (f < len(stage) and isinstance(stage[-f-1][w], Escalable) and stage[-f-1][w].isescalable())):
                debug("Movimiento descartado")
                return None
            elif movement == 'up_left' and not (self.manos == 1 or (f < len(stage) and isinstance(stage[-f-1][w], Escalable) and stage[-f-1][w].isescalable())):
                debug("Movimiento descartado")
                return None
            elif movement == 'right' and not(w < len(stage[1])-1 and isinstance(stage[-f][w+1], Escalable) and stage[-f][w+1].isescalable()):
                debug("Movimiento descartado")
                return None
            elif movement == 'left' and not(w > 1 and isinstance(stage[-f][w-1], Escalable) and stage[-f][w-1].isescalable()):
                debug("Movimiento descartado")
                return None
        debug("Movimiento aceptado")
        self.abort_actions(Wait)
        if movement.startswith('wait'):
            self.abort_actions()
            self.do(self.animations[movement])
            self.last_movement = None
            self.manos = 2
        elif (movement == "left" or movement == 'right'):
            if self.last_movement:
                movement = None
            else:
                if movement == 'left':
                    self.window -= 1
                else:
                    self.window += 1
                self.do(self.animations[movement]+self.animations['wait'])
                self.last_movement = None
                self.score += 50
                self.update()
                self.manos = 2
        elif movement == "down":
            self.do(self.animations[movement]+self.animations['wait'])
            if self.last_movement and self.last_movement.startswith("up1"):
                movement = "halfdown"
            else:
                self.level -= 1
            self.update()
            self.last_movement = None
            self.manos = 2
        elif movement == "fall":
            self.lifes -= 1
            self.update()
            self.manos = 0
            if self.lifes == 0:
                movement = 'parachute'
            self.do(self.animations[movement])
            self.last_movement = "fall"
        elif movement == "up_right":
            if self.last_movement == None:
                movement = "up1right"
                self.do(self.animations[movement]+self.animations['waitright'])
                self.last_movement = movement
                self.manos = 1
            elif self.last_movement == 'up1left':
                movement = "up2right"
                self.do(self.animations[movement]+self.animations['waitright'])
                self.last_movement = movement
                self.level += 1
                self.manos = 1
            elif self.last_movement == 'up2left' or self.last_movement == "hit":
                movement = "up3right"
                self.do(self.animations[movement]+self.animations['wait'])
                self.last_movement = None
                self.score += 100
                self.update()
                self.manos = 2
        elif movement == "up_left":
            if self.last_movement == None:
                movement = "up1left"
                self.do(self.animations[movement]+self.animations['waitleft'])
                self.last_movement = movement
                self.manos = 1
            elif self.last_movement == 'up1right':
                movement = "up2left"
                self.do(self.animations[movement]+self.animations['waitleft'])
                self.last_movement = movement
                self.level += 1
                self.manos = 1
            elif self.last_movement == 'up2right' :
                movement = "up3left"
                self.do(self.animations[movement]+self.animations['wait'])
                self.last_movement = None
                self.score += 100
                self.update()
                self.manos = 2
        elif movement == 'hit':
            if self.manos == 2:
                self.do(self.animations['waitleft'])
                self.last_movement = 'hit'
                self.score -= 200
                self.update()
                self.manos = 1
            elif self.manos == 1:
                movement = None
                self.move('fall', stage)
                #self.last_movement = "fall"
                #self.do(self.animations[movement])
                #self.lifes -= 1
                #self.update()
                #self.manos = 0
        elif movement == 'winner':
            self.do(self.animations[movement])
            self.last_movement = None
        if movement in self.movements and self.movements[movement]:
            self.do(self.movements[movement])
            #self.escudo.do(self.movements[movement])

    def ismoving(self):
        return len(self.get_actions(MoveDelta))+len(self.get_actions(Delay))

    moving = property(ismoving)

    def invencible(self):
       for a in list(self.current_actions):
           if isinstance(a, Blink) or isinstance(a, AlphaFade):
               return True

    def auto_move(self, stage):
        f, w = self.level, self.window
        delay = randint(750,1500)
        if self.last_movement == 'up1right' and f < len(stage) and stage[-f-1][w].isescalable():
            if stage[-f][w].ismoving():
                self.move('down')
            else:
                self.move('up_left')
            delay = randint(625,900)
        elif self.last_movement == 'up1left' and f < len(stage) and stage[-f-1][w].isescalable():
            if stage[-f][w].ismoving():
                self.move('down')
            else:
                self.move('up_right')
            delay = randint(625,900)
        elif isinstance(stage[-f][w], MetaWindow) and stage[-f][w].ismoving():
            if not self.last_movement and w < len(stage[1])-1 and stage[-f][w+1].isescalable():
                self.move('right')
                delay = randint(900,1500)
            elif not self.last_movement and w > 1 and stage[-f][w-1].isescalable():
                self.move('left')
                delay = randint(900,1500)
            elif f > 1 and isinstance(stage[-f+1][w], Escalable) and stage[-f+1][w].isescalable():
                self.move('down')
                delay = randint(750,1300)
        elif self.last_movement == 'up2right':
            self.move('up_left')
            delay = randint(750,1500)
        elif self.last_movement == 'up2left' or self.last_movement == 'hit':
            self.move('up_right')
            delay = randint(750,1500)
        elif self.last_movement is None:
            if f < len(stage) and isinstance(stage[-f-1][w], Escalable) and stage[-f-1][w].isescalable() and not stage[-f-1][w].ismoving():
                self.move('up_right')
                delay = randint(550,900)
            elif w > 1 and isinstance(stage[-f][w-1], Escalable) and stage[-f][w-1].isescalable():
                self.move('left')
                delay = randint(900,1500)
            elif w < len(stage[1])-1 and isinstance(stage[-f][w+1], Escalable) and stage[-f][w+1].isescalable():
                self.move('right')
                delay = randint(900,1500)
            elif f > 1 and isinstance(stage[-f+1][w], Escalable) and isinstance(stage[-f+1][w], Escalable) and stage[-f+1][w].isescalable():
                self.move('down')
                delay = randint(750,1300)
        elif self.last_movement == 'fall':
            pass
        return delay

class Supertirititran(Entity):
    image=os.path.join(LINUX_GAME_PATH, 'images', 'common','super.png')
    layer="actors"

    def init(self, scale):
        self.set(x = SELECTED_RESOLUTION[0]*11//12, y = SELECTED_RESOLUTION[1]+self.height,scale=scale)
        self.do(MoveTo(self.x-self.width//2,SELECTED_RESOLUTION[1]*2//3,0.75)+MoveTo(self.x+self.width//3,SELECTED_RESOLUTION[1]//3,1.05)+MoveTo(self.x,-self.height, 0.85)+Delete())


if __name__ == "__main__":
    screen.init(SELECTED_RESOLUTION, fullscreen= FULLSCREEN, title="Actor's test")
    #director.visible_collision_nodes = True
    director.run(Test)
    print("ticks per sec", director.ticks/director.secs)
    print("realticks per sec", director.realticks/director.secs)


