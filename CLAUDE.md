# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Freeclimber is a 2D climbing action game originally written in Python 2 (2008, Junta de Andalucia), now ported to Python 3 + pygame-ce. Released under GPLv3. Documentation and UI text are in Spanish.

## Running the Game

```bash
# Install in development mode
pip install -e .

# Run via entry point
freeclimber

# Run via module
python -m freeclimber
```

## Running Tests

```bash
python -m freeclimber.tests.test_engine
```

## Architecture

**Scene-based game loop** using a custom engine (in `freeclimber/engine/`) to transition between scenes:

```
config (console) -> Intro (fyshon-logo fade) -> Game -> quit
```

### Source Files (`freeclimber/`)

| File | Role |
|------|------|
| `freeclimber.py` | Entry point — initializes pygame, wires scenes together, runs director loop |
| `config.py` | Settings management — console prompts with autodetected defaults |
| `intro.py` | Splash screen with fade animation |
| `game.py` | Single-player game scene — layered rendering, collision detection |
| `actors.py` | `Climber` player class with sprite animation, `Status` HUD, movement |
| `building.py` | Procedural level generation — windows, obstacles, power-ups |
| `weather.py` | Cloud and particle weather effects |
| `engine/` | Custom pygame-ce SDL2 Renderer engine (director, scene, entity, actions, collision, resources, particles, font) |
| `tests/test_engine.py` | Engine smoke tests |

### Assets (`freeclimber/data/`)

- `images/` — sprite/texture files organized by category
- `music/` — OGG audio files (background music and sound effects)
- `fonts/` — Larabie TrueType fonts for UI rendering

### Key Frameworks

- **pygame-ce >= 2.4.0**: SDL2 Renderer, audio mixer, input handling
- Custom engine in `freeclimber/engine/` replacing the old pygext framework

### Input System

- Keyboard (WASD+IJKL or numpad)
- Dual-analog joystick/gamepad

### Configuration

Console-based configuration at startup. Auto-detects monitor resolution and aspect ratio (4:3, 16:10, 16:9, 10:16, 9:16).

## Important Notes

- Python 3.9+ required
- Uses relative imports throughout the package
- `LINUX_GAME_PATH` points to `freeclimber/data/` via `os.path.dirname(__file__)`
- Frame-rate independent animation via the engine's ticker system
