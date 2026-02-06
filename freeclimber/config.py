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

import os
import sys
import traceback
from time import time
import pygame
pygame.mixer.pre_init(44100, -16, 2, 3702)

VERSION = '0.9.1'

import gettext

# Multi-lingual support
_ = gettext.gettext
gettext.textdomain("freeclimber")
gettext.bindtextdomain("freeclimber", "./translations")

# --- Fixed paths ---
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LINUX_GAME_PATH = os.path.join(_PACKAGE_DIR, "data")
INTRO_PATH = os.path.join("images", "intro")
MUSIC_PATH = os.path.join("music")

# --- Resolution tables ---
RESOLUTIONS = {
    "4:3":  {"low": (800, 600),  "medium": (1024, 768), "high": (1280, 1024)},
    "16:9": {"low": (1280, 720), "medium": (1366, 768), "high": (1920, 1080)},
}

# --- Fixed defaults ---
FPS = 40.0
CONTROLLER = 'keyboard'


def _detect_aspect(w, h):
    """Return the closest aspect ratio string for the given resolution."""
    ratio = w / h
    aspects = {
        "4:3":  4 / 3,
        "16:9": 16 / 9,
    }
    best = min(aspects, key=lambda k: abs(aspects[k] - ratio))
    return best


def _detect_detail(w, h, aspect):
    """Pick the best detail level that fits within the detected resolution."""
    for detail in ("high", "medium", "low"):
        rw, rh = RESOLUTIONS[aspect][detail]
        if rw <= w and rh <= h:
            return detail
    return "low"


def _ask(prompt, default, validator=None):
    """Ask a question on the console. Enter accepts default."""
    try:
        raw = input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raw = ""
    if not raw:
        return default
    if validator:
        result = validator(raw)
        if result is not None:
            return result
        print("  Valor no valido, usando default: %s" % default)
        return default
    return raw


def _configure():
    """Ask the user for settings via console, with sensible defaults."""
    global ASPECT, DETAIL, FULLSCREEN, VOLUME, DIFFICULTY, DIF, LEVELS

    # Autodetect resolution
    pygame.display.init()
    info = pygame.display.Info()
    det_w, det_h = info.current_w, info.current_h
    pygame.display.quit()

    ASPECT = "4:3"
    DETAIL = _detect_detail(det_w, det_h, ASPECT)

    print("\n=== FreeClimber - Configuracion ===")
    print("  Pantalla detectada: %dx%d (%s, %s)" % (det_w, det_h, ASPECT, DETAIL))

    res = RESOLUTIONS[ASPECT][DETAIL]
    ans = _ask("  Resolucion %dx%d? [S/n]: " % res, "s")
    if ans.lower().startswith("n"):
        # Let user pick aspect
        aspects = list(RESOLUTIONS.keys())
        print("  Relaciones de aspecto: %s" % ", ".join(aspects))
        def valid_aspect(v):
            return v if v in aspects else None
        ASPECT = _ask("  Aspecto [%s]: " % ASPECT, ASPECT, valid_aspect)
        # Let user pick detail
        details = list(RESOLUTIONS[ASPECT].keys())
        print("  Detalles disponibles: %s" % ", ".join(details))
        def valid_detail(v):
            return v if v in details else None
        DETAIL = _ask("  Detalle [%s]: " % DETAIL, DETAIL, valid_detail)

    # Fullscreen
    def valid_bool(v):
        if v.lower() in ("s", "si", "y", "yes", "1", "true"):
            return True
        if v.lower() in ("n", "no", "0", "false"):
            return False
        return None
    FULLSCREEN = _ask("  Pantalla completa? [s/N]: ", False, valid_bool)

    # Volume
    def valid_volume(v):
        try:
            n = int(v)
            if 0 <= n <= 100:
                return n
        except ValueError:
            pass
        return None
    VOLUME = _ask("  Volumen 0-100 [80]: ", 80, valid_volume)

    # Difficulty
    diff_map = {"easy": 1, "normal": 2, "hard": 3}
    def valid_diff(v):
        return v if v in diff_map else None
    DIFFICULTY = _ask("  Dificultad (easy/normal/hard) [normal]: ", "normal", valid_diff)
    DIF = diff_map[DIFFICULTY]

    # Levels
    def valid_levels(v):
        try:
            n = int(v)
            if 1 <= n <= 100:
                return n
        except ValueError:
            pass
        return None
    LEVELS = _ask("  Niveles 1-100 [25]: ", 25, valid_levels)

    print("  Configuracion lista: %dx%d %s\n" % (RESOLUTIONS[ASPECT][DETAIL][0], RESOLUTIONS[ASPECT][DETAIL][1], "fullscreen" if FULLSCREEN else "windowed"))


# --- Run configuration on import ---
_configure()


def define_difficulty():
    global DIF
    if DIFFICULTY == 'hard':
        DIF = 3
    elif DIFFICULTY == 'normal':
        DIF = 2
    else:
        DIF = 1


def debug(msg):
    if "--debug" in sys.argv:
        if pygame.time.get_ticks():
            now = pygame.time.get_ticks() / 1000.0
        else:
            now = time()
        print("[%.3f] %s" % (now, msg))


def get_game_resolution():
    return RESOLUTIONS[ASPECT][DETAIL]


def formatExceptionInfo(inst=None, maxTBlevel=15):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = inst and inst or "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    tb = '\n'
    for l in excTb:
        tb += '     -' + l + '\n'
    debug("<<<Exception>>>\n    Type: %s\n    Error: %s\n    TraceBack: %s\n    " % (excName, excArgs, tb))
    return (excName, excArgs, excTb)


def available_controllers():
    controllers = ['keyboard']
    try:
        pygame.init()
    except:
        pass
    else:
        pygame.joystick.init()
        n = pygame.joystick.get_count()
        for i in range(n):
            j = pygame.joystick.Joystick(i)
            j.init()
            if j.get_numaxes() > 4:
                controllers.append('gamepad' + str(i))
    return controllers


def play_audio(file, f=1.0, d=None):
    if d is not None and d >= 0:
        f = f * (0.8 - d / (max(get_game_resolution()) * 2 // 3))
    if VOLUME and f > 0:
        try:
            fx = pygame.mixer.Sound(os.path.join(LINUX_GAME_PATH, MUSIC_PATH, file))
            fx.set_volume(VOLUME * 0.01 * f)
            fx.play()
        except:
            formatExceptionInfo()
