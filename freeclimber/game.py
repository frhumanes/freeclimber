#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## requires pygext 0.9.1 or newer
##

from pygame.locals import *
from .engine import *
from .config import *
from .weather import *
from .building import *
from .actors import *
import threading

SELECTED_RESOLUTION = get_game_resolution()

_GPUTEK_FONT = os.path.join(LINUX_GAME_PATH, 'fonts', 'GPUTEKSR.TTF')

ENDMUSICEVENT = USEREVENT + 2

class Game(Scene):
    init_gamepad()
    nfloors = 25
    if ASPECT == '4:3' or ASPECT == "9:6" or ASPECT == "10:16":
        columns = 8
    else:
        columns = 10

    ## Use the RadialCollisions engine, since all our sprites fit
    ## nicely inside a circle.
    collengine = RadialCollisions

    def init(self, next_scene = None, previous_scene = None):
        self.next_scene = next_scene
        self.previous_scene = previous_scene
        self.demo_mode = False
        self.paused = False
        self.game_finished = False
        self.color_player = None
        self.secs = []


    def enter(self, theme = 'default'):
        self.theme = theme
        self.set_state("loading")
        self.i = 0
        self.game_finished = False
        self.new_stabile("load")
        self.msgbg = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'paused.png'), hotspot=(0,0))
        self.msgbg.set(x=0,y=0,scale=max(SELECTED_RESOLUTION), alpha=220).place('load')
        self.msg = TextEntity(GLFont((_GPUTEK_FONT, SELECTED_RESOLUTION[0]//20),(255,255,255)), "Cargando...")
        self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
        if self.demo_mode:
            debug("Modo demostración")


    def state_loading_realtick(self):
        debug("Cargando juego...")
        theme = self.theme

        if self.i == 0:
            self.msg.set_text("Cargando capas...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")

            self.new_static("bg")

            ## The actors layer contains the ship and bullets.
            self.new_layer("city")
            self.new_layer("weather_b")
            self.new_layer("particles")
            self.new_layer("dummy")
            self.new_layer("room")
            self.new_layer("glass")
            self.new_stabile("building")
            self.new_stabile("actors")

            self.new_layer("weather_f")
            self.new_stabile("info")
            self.new_layer("points")
            self.new_stabile("pausa")
            self.new_stabile('load')
            self.msgbg.place("load")
            self.msg.place("load")

        elif self.i == 1:
            ## Load the background.

            self.msg.set_text("Cargando fondo...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            e = Entity(os.path.join(LINUX_GAME_PATH, 'images','stages', theme,  ASPECT, 'tile.jpg'), hotspot=(0,0))
            e.set(x=0,y=0,scale=SELECTED_RESOLUTION[0]/float(e.width)).place("bg")
            screen.clear_color = None
            debug("Capas creadas")

        elif self.i == 2:
            self.msgbg.place("load")
            self.msg.set_text("Cargando musica...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            if VOLUME:
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.set_volume(VOLUME * 0.01)
                    pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'juego0.ogg'))
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_endevent(ENDMUSICEVENT)
                    self.event_handler[ENDMUSICEVENT] = {"":getattr(self, "handle_endmusicevent")}
                except:
                    formatExceptionInfo()

            debug("Musica cargada")

        elif self.i == 3:
            self.msg.set_text("Cargando escenario...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            self.system = TestSystem()

            for x in range(6):
                Cloud(theme = theme)
                Cloud(capa = "weather_f", theme = theme)

            columns = Game.columns
            levels = int(LEVELS)
            self.escenario = Stage((levels, columns), theme)

            debug("Escenario creado")

        elif self.i == 4:
            self.msg.set_text("Cargando jugador...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            self.player = Climber(x = SELECTED_RESOLUTION[0]//2, y = SELECTED_RESOLUTION[1]//2, width = self.escenario.width_unit, height = self.escenario.height_unit, color_player = self.color_player)
            debug("Jugador creado")
            self.set_player()

        elif self.i == 5:
            self.msg.set_text("Cargando menu...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            self.pausedbg = Entity(os.path.join(LINUX_GAME_PATH, 'images','common', 'paused.png'), hotspot=(0,0))
            self.pausedbg.set(x=0,y=0,scale=max(SELECTED_RESOLUTION), alpha=165).place('pausa')
            self.pausedbg.do(Hide())
            self.pausedmsg = TextEntity(GLFont((_GPUTEK_FONT, SELECTED_RESOLUTION[0]//10),(255,255,255)), "PAUSA")
            self.pausedmsg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("pausa")
            self.pausedmsg.do(Hide())

            debug("Pausa preparada")

        elif self.i == 6:
            self.msg.set_text("Cargando controles...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            if CONTROLLER.startswith("gamepad"):
                init_gamepad(int(CONTROLLER[-1]))

            debug("Controles configurados")

        elif self.i == 7 and self.demo_mode:
            self.msg.set_text("Cargando IA...")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            self.mensaje = TextEntity(GLFont((_GPUTEK_FONT, SELECTED_RESOLUTION[0]//24),(255,165,0)), "Modo DEMO")
            self.mensaje.set(right=SELECTED_RESOLUTION[0]*39//40, bottom=SELECTED_RESOLUTION[1]*39//40).place("info")
            self.mensaje.do(Blink(0.5, 0.25))
            now = pygame.time.get_ticks()
            self.prev_movement = now
            self.next_movement = now
            debug("Demo preparada")

        elif self.i == 8:
            self.enter_netGame()#FFA500

        elif self.i == 9:
            self.msg.set_text("Juego cargado")
            self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
            director.set_state(None)
            for e in self.get_layer('load'):
                e.do(Hide())
        self.i +=1

    def enter_netGame(self):
        self.msg.set_text("Cargando cuenta atras...")
        self.msg.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2).place("load")
        self.countdown(True)

    def countdown(self, start = False):
        center = (SELECTED_RESOLUTION[0]//2,SELECTED_RESOLUTION[1]//2)
        path = os.path.join(LINUX_GAME_PATH, 'images','common')
        if start:
            self.secs = [Entity(os.path.join(path,str(s)+'.png')) for s in range(4)]
            for e in self.secs:
                e.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2, scale=float(SELECTED_RESOLUTION[0])/e.width).place("info")
                e.do(Hide())
        if len(self.secs) :
            self.secs.pop().do(Show()+Delay(0.1)+CenteredScale(0,0.9,center)+Delete())
            self.timer = threading.Timer(1.25, self.countdown)
            self.timer.start()

    def collision_player_bonus(self, player, item):
        if item.destroyed or self.is_paused():
            return 0
        item.destroyed = True
        item.do(MoveTo(player.scoreboard.centerx, player.scoreboard.centery, 1.0))
        item.do(Delay(0.9) + CallFunc(play_audio, 'puntos.ogg', 0.75) + CallFunc(self.increase_score))
        item.do(Delay(0.7) + CallFunc(item.destroy))

    def increase_score(self):
        self.player.score += 500
        self.player.update()

    def life1up(self):
        self.player.lifes += 1
        self.player.update()

    def subir(self):
        self.escenario.bajar(-self.player.height, secs= 0.25)
        self.player.do(MoveDelta(0, -self.player.height, secs= 0.25))
        for e in self.get_layer("weather_f"):
            e.do(MoveDelta(0,-self.player.height, secs= 0.50))
        for e in self.get_layer("city"):
            e.do(MoveDelta(0,-self.player.height//16, secs= 0.50))

    def bajar(self):
        self.escenario.subir(SELECTED_RESOLUTION[1]//2, secs= 0.50)
        self.player.do(MoveDelta(0, SELECTED_RESOLUTION[1]//2, secs= 0.50))
        for e in self.get_layer("weather_f"):
            e.do(MoveDelta(0,SELECTED_RESOLUTION[1]//2, secs= 0.50))
        for e in self.get_layer("city"):
            e.do(MoveDelta(0,SELECTED_RESOLUTION[1]//20, secs= 0.50))

    def collision_player_life1up(self, player, item):
        debug("Colision: vida extra")
        if item.destroyed or self.is_paused() or not player.lifes:
            return 0
        play_audio('bien.ogg',0.75)
        item.destroyed = True
        item.do(MoveTo(player.lifeboard.right, player.lifeboard.centery, 1.0))
        item.do(Delay(0.9) + CallFunc(self.life1up))
        item.do(Delay(0.7) + CallFunc(item.destroy))

    def collision_player_enemy(self, player, item):
        debug("Colision: enemigo")
        if item.destroyed or self.is_paused() or not player.lifes:
            return 0
        if item.active:
            if not self.player.invencible():
                player.move('hit')
                item.destroy(distance(player,item))

    def collision_player_invincibility(self, player, item):
        debug("Colision: invencibilidad")
        if item.destroyed or self.is_paused() or not player.lifes:
            return 0
        item.destroy()
        player.score += 500
        player.update()
        Supertirititran(scale = player.scale)
        play_audio('supertirititran.ogg',0.75)
        #play_audio('lema.wav')
        player.do(Repeat(AlphaFade(200,0.5)+AlphaFade(128, 0.5), times=10)+AlphaFade(255,1.0))


    def collision_player_bomb(self, player, item):
        debug("Colision: Explosion")
        if item.destroyed or self.is_paused() or not player.lifes:
            return 0
        play_audio('bomb.ogg')
        for e in self.get_layer('actors'):
            if isinstance(e,Plant) and e.y <= player.y+min(SELECTED_RESOLUTION)//3 and e.y >= player.y-min(SELECTED_RESOLUTION)//3:
                d = distance(e,item)
                e.do(Delay(d*0.0025)+CallFunc(e.destroy,d+50))
        item.destroy()

    def collision_ground_player(self, g, player):
        debug("Colision: suelo")
        player.abort_actions(MoveDelta)

    def collision_ground_enemy(self, g, item):
        debug("Colision: suelo")
        if item.destroyed or self.is_paused():
            return 0
        if item.active:
            item.destroy(distance(self.player,item))

    def is_paused(self):
        return  len(self.secs) or self.paused or self.game_finished

    def end_game(self):
        self.game_finished = True
        if self.player.level >= self.escenario.dim[0]:
            self.player.move('winner')
            activate_fireworks(None,self.system,5)
            if VOLUME:
                try:
                    pygame.mixer.music.fadeout(1500)
                    pygame.mixer.music.set_endevent()
                except:
                    formatExceptionInfo()

            play_audio('victoria.ogg')

            Status(x = SELECTED_RESOLUTION[0]//2, y = SELECTED_RESOLUTION[1]//2, color_player = self.player.color_player, width = min(SELECTED_RESOLUTION)//3, type = 'static')
            self.cd = Entity(os.path.join(LINUX_GAME_PATH, 'images', 'common', 'winner.png'))
            self.cd.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]*3//4, scale = SELECTED_RESOLUTION[0]/(2*float(self.cd.width))).place("info")
            self.cd.do(ColorFade(colormap[self.player.color_player], 0.5))
            scale = self.cd.scale
            self.cd.do(Repeat(Delay(0.4)+CenteredScale(scale*1.1, 0.5, (SELECTED_RESOLUTION[0]//2, SELECTED_RESOLUTION[1]*3//4))+CenteredScale(scale, 0.1, (SELECTED_RESOLUTION[0]//2, SELECTED_RESOLUTION[1]*3//4)), times=10)+CallFunc(self.exit_game))
        else:
            if VOLUME:
                try:
                    pygame.mixer.music.fadeout(1500)
                    pygame.mixer.music.set_endevent()
                except:
                    formatExceptionInfo()

            play_audio('perdedor.ogg')
            self.player.levelboard.loser()
            self.cd = Entity(os.path.join(LINUX_GAME_PATH, 'images', 'common', 'gameover.png'))
            self.cd.set(centerx=SELECTED_RESOLUTION[0]//2, centery=SELECTED_RESOLUTION[1]//2, scale = SELECTED_RESOLUTION[0]/(2*float(self.cd.width))).place("info")
            scale = self.cd.scale
            self.cd.do(Repeat(Delay(0.4)+CenteredScale(scale*1.1, 0.5, (SELECTED_RESOLUTION[0]//2, SELECTED_RESOLUTION[1]//2))+CenteredScale(scale, 0.1, (SELECTED_RESOLUTION[0]//2, SELECTED_RESOLUTION[1]//2)), times=10)+CallFunc(self.exit_game))


    def set_previous_scene(self, scene):
        self.previous_scene = scene

    def pause(self):
        if self.paused:
            self.pausedbg.do(Hide())
            self.pausedmsg.do(Hide())
            self.paused = False
            for e in self.interrupted:
                e.close_window(True)
                self.interrupted.remove(e)
        else:
            self.interrupted = []
            for e in self.get_layer("dummy"):
                if isinstance(e, MetaWindow):
                    if e.close_window(False):
                        self.interrupted.append(e)
            self.pausedbg.do(Show())
            self.pausedmsg.do(Show())
            self.paused = True
        try:
            pygame.mixer.music.fadeout(2000)
        except:
            formatExceptionInfo()


    def exit_game(self):
        debug("Saliendo del juego...")
        if self.previous_scene is not None:
            director.set_scene(self.previous_scene)
        else:
            director.quit()

    ## This callback is called by the director on every "realtick"
    ## aka. "engine tick". While frames are drawn as fast as possible,
    ## engine ticks happen at a constant time of FPS times per second.
    def realtick(self):
        debug("Realtick")

        if self.is_paused():
            debug("Juego pausado")
            return 1

        if self.demo_mode:
            debug("Decidiendo movimiento...")
            self.ia()

        if not self.player.ismoving(): # scroll
            debug("Comprobación de estados")

            if self.player.last_movement == "fall":
                #recolocar
                self.set_player()

            elif isinstance(self.escenario.escenario[-self.player.level][self.player.window], MetaWindow) and self.escenario.escenario[-self.player.level][self.player.window].is_closed() and not self.player.invencible():
                self.player.move("fall")
                play_audio('ups.ogg')

            elif self.player.y < SELECTED_RESOLUTION[1]//4 and self.player.manos == 2:
                self.bajar()

            elif self.player.y > SELECTED_RESOLUTION[1]*5//6 and self.player.manos == 2:
                self.subir()

            elif not self.game_finished and (self.player.level >= self.escenario.dim[0] and self.player.manos == 2) or self.player.lifes == 0: # game over
                self.end_game()

            else:
                self.escenario.check_windows(self.player.x)
        elif not self.player.lifes:
            self.end_game()


        for e in self.get_layer("weather_b"):
            e.check_bounds(self.escenario.get_middle_level())
        for e in self.get_layer("weather_f"):
            e.check_bounds(self.escenario.get_middle_level())

    def set_player(self):
        punto_partida = self.escenario.escenario[-self.player.level][self.player.window]
        while not punto_partida.isescalable():
            if self.player.level > 2:
                self.player.level -= 1
            else:
                self.player.window = (self.player.window + 1) % self.escenario.dim[1]
            punto_partida = self.escenario.escenario[-self.player.level][self.player.window]
        self.player.set_in_window(punto_partida, self.player.level==2)

    def handle_keydown(self, ev):
        if ev.key == K_ESCAPE or (self.demo_mode and (ev.key == K_SPACE or ev.key == K_RETURN)):
            self.demo_mode = False
            self.exit_game()
        elif ev.key == K_p:
            self.pause()
        if self.is_paused():
            return 0
        keys = pygame.key.get_pressed()
        if ((ev.key == K_s and keys[K_k]) or (ev.key == K_KP2)):
            self.player.move('down', stage = self.escenario.escenario)
        elif ((ev.key == K_i and keys[K_s]) or (ev.key == K_s and keys[K_i]) or (ev.key == K_KP9)):
            self.player.move('up_right', stage = self.escenario.escenario)
        elif ((ev.key == K_w and keys[K_k]) or (ev.key == K_k and keys[K_w]) or (ev.key == K_KP7)):
            self.player.move('up_left', stage = self.escenario.escenario)
        elif ((ev.key == K_d and keys[K_l]) or (ev.key == K_l and keys[K_d]) or (ev.key == K_KP6)):
            self.player.move('right', stage = self.escenario.escenario)
        elif ((ev.key == K_a and keys[K_j]) or (ev.key == K_j and keys[K_a]) or (ev.key == K_KP4)):
            self.player.move('left', stage = self.escenario.escenario)

    def handle_joybuttondown(self, ev):
        if ev.button == 9:
            self.pause()
        if self.is_paused():
            return 0
        if ev.button == 8:
            self.demo_mode = False
            print("Exit joybutton")
            self.exit_game()

    def handle_joyaxismotion(self, ev):
        if self.is_paused() or self.demo_mode:
            return 0
        if ev.axis == 3 and ev.value < -0.2:
            self.player.move('up_right', stage = self.escenario.escenario)
        elif ev.axis == 1 and ev.value < -0.9:
            self.player.move('up_left', stage = self.escenario.escenario)
        elif ev.axis == 0 and ev.value < -0.9:
            self.player.move('left', stage = self.escenario.escenario)
        elif ev.axis == 4 and ev.value > 0.8:
            self.player.move('right', stage = self.escenario.escenario)
        if (ev.axis == 3 and ev.value > 0.5) or (ev.axis == 1 and ev.value > 0.9):
            self.player.move('down', stage = self.escenario.escenario)


    def handle_endmusicevent(self, ev):
        if VOLUME:
            try:
                if not pygame.mixer.music.get_busy():
                    if self.paused:
                        pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'pause.ogg'))
                    elif self.player.level >= self.escenario.dim[0]*3//4:
                        pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'juego3.ogg'))
                    elif self.player.level >= self.escenario.dim[0]//2:
                        pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'juego2.ogg'))
                    else:
                        pygame.mixer.music.load(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, 'juego1.ogg'))
                    pygame.mixer.music.set_volume(VOLUME * 0.01)
                    pygame.mixer.music.play()
            except:
                formatExceptionInfo()

    def ia(self):
        now = pygame.time.get_ticks()
        if now > self.next_movement:
            self.prev_movement = now
            self.next_movement += self.player.auto_move(self.escenario.escenario)
            debug("Next movement at: %.2f" % (self.next_movement/1000.0))

def init_gamepad(dev = 0):
    try:
        j = pygame.joystick.Joystick(dev)
    except:
        return 0
    else:
        j.init()

def main():
    screen.init(SELECTED_RESOLUTION, fullscreen= FULLSCREEN, title="Free Climber")
    juego = Game()
    #director.visible_collision_nodes = True
    director.run(juego)
    print("ticks per sec", director.ticks/director.secs)
    print("realticks per sec", director.realticks/director.secs)

if __name__ == "__main__":
    main()
