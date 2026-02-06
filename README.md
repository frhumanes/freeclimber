# FreeClimber

Juego de escalada 2D desarrollado originalmente en 2008 para la Junta de Andalucia.
Portado a Python 3 y pygame-ce con motor propio basado en SDL2 Renderer.

## Requisitos

- Python 3.9+
- pygame-ce >= 2.4.0

## Instalacion

```bash
pip install -e .
```

## Ejecucion

```bash
# Mediante entry point
freeclimber

# Mediante modulo
python -m freeclimber
```

Al iniciar se muestra una configuracion por consola con valores autodetectados.
Modos de video soportados: 4:3 (por defecto) y 16:9.

## Flujo del juego

Intro (logo) → Menu principal → Juego → Menu principal

El menu permite empezar una partida o salir. Tras 40 segundos de
inactividad se lanza un modo demo automatico.

## Controles

- **Teclado**: S+I / W+K (subir derecha/izquierda), D+L / A+J (derecha/izquierda), S+K (bajar). Tambien numpad (4, 6, 7, 9, 2).
- **Gamepad**: Ejes analogicos.
- **P**: Pausar.
- **Escape**: Volver al menu / Salir.

## Tests

```bash
python -m freeclimber.tests.test_engine
```

## Creditos

- **Programacion**: Fernando Ruiz, Javier Munoz
- **Diseno grafico**: Nieves Pantion
- **Musica y FX**: German Hurtado, Banco de imagenes y sonidos del MEC

## Licencia

GPLv3 - Ver archivo LICENSE.
