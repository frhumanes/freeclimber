# -*- coding: utf-8 -*-
##
## requires pygext 0.9.1 or newer
##

import pygame
import os
from glob import glob
from pygame.locals import *
from pygext.gl.all import *
from math import cos
from config import *
import threading


SELECTED_RESOLUTION = get_game_resolution()

ENDMUSICEVENT = pygame.USEREVENT + 2

class Option(Entity):

    image = os.path.join(LINUX_GAME_PATH, MENU_PATH, "default.png")
    layer = "icon"

    def init(self, pos , center, name = "", icon = None, action = None):
        if icon and os.path.exists(icon):
            shape = resources.get_bitmap(icon, None)
            shape.compile()
            self.shape = shape
        self.angle = 0
        self.ref = center
        self.new_scale = lambda x: 1.0/(1+x**2)
        self.new_alpha = lambda x: abs(x) <= 1 and 255/(1+abs(x)) or 0
        self.new_x = lambda x: abs(x) == 1 and SELECTED_RESOLUTION[0]*(2+x)/4 or SELECTED_RESOLUTION[0]/2
        self.new_y = lambda x: abs(x) <= 1 and self.ref*(7-abs(x))/6 or self.ref*5/6

        self.pos = pos

        self.set(centerx = self.new_x(self.pos), \
                 centery = self.new_y(self.pos), \
                 alpha = 0)
        self.font = font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/baveuse3.ttf", SELECTED_RESOLUTION[0]/20),(100,200,0))
        if icon and os.path.exists(icon):
            self.shape = resources.get_bitmap(icon, None)
            shape.compile()
        self.name = TextEntity(self.font, name)
        self.name.set(centerx=SELECTED_RESOLUTION[0]/2, top=self.ref*(7.0/6)+50, alpha = 0).place("text")
        self.action = action
        self.set(scale = self.new_scale(self.pos))
        self.do(AlphaFade(self.new_alpha(self.pos), 2))
        if self.pos == 0:
            self.name.do(AlphaFade(self.new_alpha(self.pos), 2))

    def move_left(self, active = False):
        self.pos += 1
        dx = self.new_x(self.pos) - self.centerx
        dy = self.new_y(self.pos) - self.centery
        self.do(MoveTo(self.x+dx,self.y+dy, secs = 1))
        self.do(AlphaFade(self.new_alpha(self.pos), 1))
        self.do(Scale(self.new_scale(self.pos), 1))



        if self.pos == 0:
            self.name.do(Delay(0.25) + AlphaFade(255, 0.75))
        else:
            self.name.do(AlphaFade(0, 0.75))


    def move_right(self, active = False):
        self.pos -= 1
        dx = self.new_x(self.pos) - self.centerx
        dy = self.new_y(self.pos) - self.centery
        self.do(MoveTo(self.x+dx,self.y+dy, secs = 1))
        self.do(AlphaFade(self.new_alpha(self.pos), 1))
        self.do(Scale(self.new_scale(self.pos), 1))


        if self.pos == 0:
             self.name.do(Delay(0.25) + AlphaFade(255, 0.75))
        else:
            self.name.do(AlphaFade(0, 0.75))

    def run(self):
        if self.action:
            self.action()
        else:
            self.not_available()

    def not_available(self):
        font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/cranberr.ttf", SELECTED_RESOLUTION[0]/30),(240,0,0))
        adv = TextEntity(font, "Opcion no disponible")
        adv.set(centerx=SELECTED_RESOLUTION[0]/2, centery=SELECTED_RESOLUTION[1]/2, alpha=0).place("text")
        adv.do(AlphaFade(255,0.25)+Delay(0.75)+AlphaFade(0,0.25)+Delete())

class Animation(Entity):

    image = os.path.join(LINUX_GAME_PATH, MENU_PATH, 'animation', 'climber_00.png')
    layer = "animation"

    def init(self, scale, x=None, y=None):
        if not x: x = SELECTED_RESOLUTION[0]/2
        if not y: y = SELECTED_RESOLUTION[1]/2
        #base = Entity(Animation.image)
        #base.set(centerx = x, centery=y, scale = scale).place(Animation.layer)
        self.set(centerx = x, centery=y, scale = scale, alpha = 0).place(Animation.layer)
        animpath = os.path.join(LINUX_GAME_PATH, MENU_PATH, 'animation')
        #count = glob(os.path.join(LINUX_GAME_PATH, MENU_PATH, 'animation', 'climber_*.png'))
        #count.sort()
        self.dedos = 3
        tres = Animate([resources.get_bitmap(e) for e in[os.path.join(animpath, 'climber_00.png')]],0.15)
        dos = Animate([resources.get_bitmap(e) for e in[os.path.join(animpath, 'climber_01.png'), os.path.join(animpath, 'climber_02.png'), os.path.join(animpath, 'climber_04.png'), os.path.join(animpath, 'climber_04.png')]],0.15)
        uno = Animate([resources.get_bitmap(e) for e in[os.path.join(animpath, 'climber_05.png'), os.path.join(animpath, 'climber_06.png'), os.path.join(animpath, 'climber_07.png'), os.path.join(animpath, 'climber_08.png')]],0.15)
        cero = Animate([resources.get_bitmap(e) for e in[os.path.join(animpath, 'climber_09.png'), os.path.join(animpath, 'climber_10.png'), os.path.join(animpath, 'climber_11.png'), os.path.join(animpath, 'climber_12.png'), os.path.join(animpath, 'climber_13.png'), os.path.join(animpath, 'climber_14.png')]],0.15)
        self.do(tres)
        self.anims = [cero, uno, dos, tres]
        self.timer = threading.Timer(1.0, self.count)
        self.timer.start()
        self.do(AlphaFade(255,1.5))

    def count(self):
        if self.dedos:
            self.dedos -= 1
        else:
            self.dedos = 3
        self.do(self.anims[self.dedos])
        self.timer = threading.Timer(1.0, self.count)
        self.timer.start()


class MainMenu(Scene):

    def init(self):
        #director.wiimote = None
        self.next_scene = {}
        pass

    def enter(self):
        #pygame.event.set_grab(True)
        director.netFrame = None
        init_gamepad()
        self.set_state("loading")
        self.i = 0
        self.new_stabile("load")
        self.msgbg = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'paused.png'), hotspot=(0,0))
        self.msgbg.set(x=0,y=0,scale=max(SELECTED_RESOLUTION), alpha=220).place('load')
        self.msg = TextEntity(GLFont(("/usr/share/fonts/truetype/ttf-larabie-deco/qswitcha.ttf", SELECTED_RESOLUTION[0]/20),(255,255,255)), "Cargando...")
        self.msg.set(centerx=SELECTED_RESOLUTION[0]/2, centery=SELECTED_RESOLUTION[1]/2).place("load")
        self.timer = threading.Timer(30.0, self.load_demo, '1')
        self.timer.start()

    def state_loading_realtick(self):
        if self.i == 0:
            self.msg.set_text("Cargando.")
            self.new_layer("bg")
            self.new_stabile("animation")
            self.new_layer("about")
            self.new_layer("info")
            self.new_stabile('load')
            self.msgbg.place("load")
            self.msg.place("load")

        elif self.i == 1:
            self.msg.set_text("Cargando..")
            if VOLUME:
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.set_volume(VOLUME*0.01)
                    pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'menuintro.ogg'))
                    #pygame.mixer.music.queue(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'menuloop.ogg'))
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_endevent(ENDMUSICEVENT)
                    self.event_handler[ENDMUSICEVENT] = {"":getattr(self, "handle_endmusicevent")}
                except:
                    formatExceptionInfo()

        elif self.i == 2:
            self.msg.set_text("Cargando...")
            ## Load the background.
            self.bg = Entity(os.path.join(LINUX_GAME_PATH, MENU_PATH, "main-bg.jpg"))
            self.bg.set(centerx=SELECTED_RESOLUTION[0]/2,centery=SELECTED_RESOLUTION[1]/2, scale=SELECTED_RESOLUTION[1]/float(self.bg.height)).place("bg")
            self.bg.do(AlphaFade(255,1.0))

        elif self.i == 3:
            self.msg.set_text("Cargando.")
            self.aboutbg = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'credits.png'), hotspot=(0,0))
            self.aboutbg.set(x=0,y=0,scale=max(SELECTED_RESOLUTION), alpha=0).place('about')

        elif self.i == 4:
            self.msg.set_text("Cargando..")
            self.anim = Animation(scale = self.bg.scale)

            screen.clear_color = (255,255,255,255)

        elif self.i == 5:
            self.msg.set_text("Cargando...")
            self.title = Entity(os.path.join(LINUX_GAME_PATH, MENU_PATH, "freeclimber.png"))
            self.title.set(centerx=SELECTED_RESOLUTION[0]/2,centery=self.anim.top, alpha=0, scale=SELECTED_RESOLUTION[0]*7/(8*float(self.title.width))).place("animation")
            self.title.do(AlphaFade(255,5.0))
            #glmouse.pointer = glmouse.default_pointer
            #{"name":"OPCIONES", "action":None, "icon":os.path.join(LINUX_GAME_PATH, MENU_PATH,"option.png")}, \
            options = [{"name":"NUEVO JUEGO", "action":self.load_game , "icon":os.path.join(LINUX_GAME_PATH, MENU_PATH,"new.png")}, \
                       {"name":"JUEGO EN RED", "action":self.load_netgame, "icon":os.path.join(LINUX_GAME_PATH, MENU_PATH,"net.png")}, \
                       {"name":"DEMO", "action":self.load_demo_cont, "icon":os.path.join(LINUX_GAME_PATH, MENU_PATH,"demo.png")}, \
                       {"name":"CREDITOS", "action":self.show_credits, "icon":None}, \
                       {"name":"SALIR","action":self.quit, "icon":os.path.join(LINUX_GAME_PATH, MENU_PATH,"exit.png")}
                       ]
            self.menu_bar(options)

        elif self.i == 6:
            self.msg.set_text("Cargando.")
            if director.wiimote:
                try:
                    self.new_layer('points')
                    director.wiimote.draw_hands()
                    director.wiimote.rpt_mode=9
                except:
                    director.wiimote = None

        elif self.i == 7:
            self.msg.set_text("Carga finalizada")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]/2, centery=SELECTED_RESOLUTION[1]/2).place("load")
            director.set_state(None)
            for e in self.get_layer('load'):
                e.do(Hide())
        self.i +=1

    def load(self, new_scene):
        self.anim.timer.cancel()
        self.timer.cancel()
        try:
            if isinstance(new_scene, Scene):
                #if director.wiimote:
                #    new_scene.wiimote = director.wiimote
                director.set_scene(new_scene)
        except Exception, inst:
            debug("Error %s en la carga del juego: %s" % (type(inst), inst))
            formatExceptionInfo()
            director.set_scene(self)


    def load_netgame(self):
        #if director.wiimote:
        #    self.next_scene['netgame'].wiimote = director.wiimote
        if VOLUME:
            try:
                pygame.mixer.music.fadeout(2300)
            except:
                formatExceptionInfo()
        play_audio('ok.ogg',0.75)
        self.anim.timer.cancel()
        self.title.do(AlphaFade(0,2))
        for e in self.get_layer('bg'): e.do(AlphaFade(0,2.15)+CallFunc(self.load, self.next_scene['netgame']))
        for e in self.get_layer('icon'): e.do(AlphaFade(0,2))
        for e in self.get_layer('text'): e.do(AlphaFade(0,2))

    def quit(self):
        if VOLUME:
            try:
                pygame.mixer.music.fadeout(1500)
            except:
                formatExceptionInfo()
        self.timer.cancel()
        self.anim.timer.cancel()
        self.title.do(AlphaFade(0,2))
        for e in self.get_layer('bg'): e.do(AlphaFade(0,1.15)+CallFunc(director.quit))
        for e in self.get_layer('icon'): e.do(AlphaFade(0,1))
        for e in self.get_layer('text'): e.do(AlphaFade(0,1))

    def load_game(self):
        #if director.wiimote:
        #    self.next_scene['game'].wiimote = director.wiimote
        play_audio('ok.ogg',0.75)
        if VOLUME:
            try:
                pygame.mixer.music.fadeout(2500)
            except:
                formatExceptionInfo()
        self.anim.timer.cancel()
        self.title.do(AlphaFade(0,2))
        for e in self.get_layer('bg'): e.do(AlphaFade(0,2.15)+CallFunc(self.load, self.next_scene['game']))
        for e in self.get_layer('icon'): e.do(AlphaFade(0,2))
        for e in self.get_layer('text'): e.do(AlphaFade(0,2))

    def load_demo_cont(self):
        self.load_demo(modo = True)

    def load_demo(self, modo = True):
        #if director.wiimote:
        #    self.next_scene['game'].wiimote = director.wiimote
        play_audio('ok.ogg',0.5)
        if VOLUME:
            try:
                pygame.mixer.music.fadeout(2500)
            except:
                formatExceptionInfo()
        self.anim.timer.cancel()
        try:
            self.next_scene['game'].demo_mode = modo
        except:
            pass
        else:
            self.title.do(AlphaFade(0,2))
            for e in self.get_layer('bg'): e.do(AlphaFade(0,2.15)+CallFunc(self.load, self.next_scene['game']))
            for e in self.get_layer('icon'): e.do(AlphaFade(0,2))
            for e in self.get_layer('text'): e.do(AlphaFade(0,2))

    def show_credits(self):
        try:
            f = open("../ABOUT",'r')
        except:
            pass
        else:
            font = GLFont(("/usr/share/fonts/truetype/ttf-larabie-straight/zekton__.ttf", SELECTED_RESOLUTION[0]/32),(0,0,0))
            n = 0
            self.aboutbg.do(AlphaFade(165,1.0))
            for l in f.readlines():
                adv = TextEntity(font, l)
                adv.set(centerx=SELECTED_RESOLUTION[0]/2, centery=SELECTED_RESOLUTION[1], alpha=0).place("credits")
                adv.do(Delay(n*0.60)+AlphaFade(255,2)+Delay(10.0)+AlphaFade(0,2)+Delete())
                adv.do(Delay(n*0.60)+MoveDelta(0,-SELECTED_RESOLUTION[1]+32, 14.0))
                n += 1
            self.aboutbg.do(Delay(n*0.60+12)+AlphaFade(0,1.0))
            f.close()
            self.timer.cancel()
            self.timer = threading.Timer(n*0.60+42, self.load_demo, '1')
            self.timer.start()


    def clear_credits(self):
        for e in self.get_layer('credits'):
            e.abort_actions()
            e.do(Delete())

    def set_next_scene(self, new_scene, name):
        self.next_scene[name] = new_scene


    def menu_bar(self, options):
        self.new_layer("icon")
        self.new_layer("text")
        self.new_layer("credits")
        #self.font = font = GLFont(("BASIF.TTF", 16))
        self.selected_option = 0
        self.options = []
        i = 0
        for o in options:
            opt = Option(pos = i, center=SELECTED_RESOLUTION[1]*4/6, name=o["name"], icon=o["icon"], action=o["action"])
            self.options.append(opt)
            i += 1

    def realtick(self):
        self.handle_input()
        if director.wiimote:
            director.wiimote.get_status()
            self.handle_wiimote_movements()
        #for e in self.get_layer("icon"):
        #    e.set_title()

    def handle_input(self):
        if not self.moving():
            keys = pygame.key.get_pressed()
            if keys[K_UP]:
                pass
            if keys[K_DOWN]:
                pass
            if keys[K_ESCAPE]:
                self.clear_credits()
            if keys[K_LEFT]:
                if self.selected_option > 0:
                    self.previous()
            if keys[K_RIGHT]:
                if self.selected_option < len(self.options)-1:
                    self.next()
            if keys[K_RETURN]:
                self.options[self.selected_option].run()

    def showing_credits(self):
        return len(self.get_layer("credits"))

    def handle_wiimote_movements(self):

        if not self.moving() and director.wiimote and director.wiimote.initialized:
            #director.wiimote.get_status()
            mov = director.wiimote.get_movement()
            event = None
            if mov:
                self.timer.cancel()
                self.timer = threading.Timer(30.0, self.load_demo, '1')
                self.timer.start()
            if mov == "ll":
                if self.selected_option > 0:
                    self.previous()
            elif mov == "ul":
                pass
            elif mov == "dl":
                self.options[self.selected_option].run()
            elif mov == "rr":
                if self.selected_option < len(self.options)-1:
                    self.next()
            elif mov == "ur":
                pass
            elif mov == "dr":
                self.options[self.selected_option].run()

    def handle_endmusicevent(self, ev):
        if VOLUME:
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'menuloop.ogg'))
                    pygame.mixer.music.play()
            except:
                formatExceptionInfo()


    def previous(self):
        self.selected_option -= 1
        play_audio('cliki.ogg',0.5)
        for i in range(len(self.options)):
            self.options[i].move_left()

    def moving(self):
        return len(self.options[0].get_actions()) + self.showing_credits()


    def next(self):
        self.selected_option += 1
        play_audio('cliki.ogg',0.5)
        for i in range(len(self.options)):
            self.options[i].move_right()


    def handle_keydown(self, ev):
        """if ev.key == K_ESCAPE:
            director.quit()
        if ev.key == K_LEFT:
            if self.selected_option > 0: self.previous()
        elif ev.key == K_RIGHT:
            if self.selected_option < len(self.options)-1: self.next()
        elif ev.key == K_RETURN:
            self.options[self.selected_option].run()"""
        self.timer.cancel()
        self.timer = threading.Timer(30.0, self.load_demo, '1')
        self.timer.start()
        pass

    def handle_joyaxismotion(self, ev):
        self.timer.cancel()
        self.timer = threading.Timer(30.0, self.load_demo, '1')
        self.timer.start()
        if not self.moving():
            if ev.axis == 0 and ev.value == 1:
                if self.selected_option < len(self.options)-1: self.next()
            elif ev.axis == 0 and ev.value == -1:
                if self.selected_option > 0: self.previous()

    def handle_joybuttondown(self, ev):
        self.timer.cancel()
        self.timer = threading.Timer(30.0, self.load_demo, '1')
        self.timer.start()
        if not self.moving() and ev.button < 4:
            self.options[self.selected_option].run()


def init_gamepad(dev = 0):
    try:
        j = pygame.joystick.Joystick(dev)
    except:
        return 0
    else:
        j.init()

if __name__ == "__main__":
    screen.init(SELECTED_RESOLUTION, title="Menu Test")
    director.wiimote = None
    director.run(MainMenu)
    print "ticks per sec", director.ticks/director.secs
    print "realticks per sec", director.realticks/director.secs
