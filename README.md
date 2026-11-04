# PrHEIdator

PrHEIdator is a local Pong game created by **Clement LEROY** as a school project.
Its name combines Predator with HEI, the school's name. **v2.0 — Game Rebirth**
rehabilitates the original game with a modular application, reliable resource
paths and automated tests. It keeps the original branding, 800×450 window,
black playing field, coloured paddles, menus, sounds and keyboard mappings.

This is a modernization of the school game. The historical source's v1–v5
labels are explained in [the project history](docs/PROJECT_HISTORY.txt);
they are not a verified release history for this repository.

## Play

Use Python **3.11 or later**. The development checks used Python 3.11.15 and
Pygame 2.6.1 on Windows. From the project directory:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

On macOS/Linux, use `.venv/bin/python` in place of `.venv\Scripts\python.exe`.
If you already use this project's `.venv_pong`, launch it with:

```powershell
.venv_pong\Scripts\python.exe main.py
```

You can also run `python /absolute/path/to/PrHEIdator/main.py` from another
folder. Assets are located relative to the project, never your working directory.
The new entry point is **main.py**; the old scripts are preserved as text in
`docs/legacy/` for reference.

Pygame is the only third-party runtime dependency. No NumPy, Flask, Kafka,
database, account, server, controller app or network connection is needed.
If no audio device is available, the game runs silently. Asset loading errors
are still reported instead of being silently ignored.

## Supported modes

| Mode | Rules |
| --- | --- |
| 1 joueur → Ia | Left paddle versus the original style of reactive computer opponent. First to five. |
| 1 joueur → Wall | One left paddle; each hit on the right wall earns a point. Missing on the left ends the run. No five-point limit. |
| 2 joueurs → Classic | Two local players. First to five. |
| 2 joueurs → Poder | Classic plus charge bars: two centre-zone returns charge an attack. First to five. |
| 4 joueurs → Classic | One paddle per side. When the ball leaves any side, the last player to touch it earns a point. First to five. |

**Fun** and **DeepIA** are visibly disabled. The original source contains no Fun
gameplay and no neural-network implementation. Enabling the old DeepIA option
merely stopped the reactive bot from moving.

## Controls

| Action | Keys |
| --- | --- |
| Menu selection | ↑ / ↓, then Enter; or left mouse click |
| Player 1, left paddle | A up / Q down (original mapping) |
| Player 2, right paddle | ↑ / ↓ |
| Player 3, top paddle | T left / Y right |
| Player 4, bottom paddle | V left / B right |
| Poder attack, player 1 | Hold S while charged and the ball is nearby and aligned with the paddle |
| Poder attack, player 2 | Hold ← under the same conditions |
| Skip intro | Enter / Space |
| Return to main menu | Esc; also Enter during GAME OVER |
| Quit | Window close, Esc on main menu, or Credit & Quit → Quit |
| Mute/unmute | M |

A Poder attack consumes both charges and sends a horizontal shot at the original
10 pixels per simulation step. A point clears the losing player's charge. The
GAME OVER display returns to the main menu after 2.8 seconds. The original
colour flashes and short collision pauses remain, but window events continue
to be handled during them.

## Repository layout

```text
main.py                    Minimal entry point
src/
  app.py                   One application loop and lifecycle
  config.py                Shared dimensions, timing and controls
  entities.py              Ball and Paddle
  collisions.py            Boundaries and paddle hit zones
  modes.py                 Match simulation, AI and mode rules
  navigation.py            Screens, menus and disabled choices
  assets.py                Resource manifest and image/font cache
  audio.py                 Streaming music and sound effects
  rendering.py             Original presentation
sounds/
  music/                   School game's music
  effects/                 School game's effects, including unused originals
  legacy/                  Separate Games_files audio and retired variants
px/
  images/                  School game's images, including unused originals
  fonts/                   Font and preserved duplicate under legacy/
  legacy/                  Separate Games_files images
docs/                      Audit, architecture, history, roadmap and delivery report
  legacy/                  Original scripts archived as .py.txt
tests/                     Standard-library unittest tests
README.md
CHANGELOG.md
requirements.txt
.gitignore
```

## Validation

```powershell
.venv_pong\Scripts\python.exe -m unittest discover -s tests -v
```

Tests select SDL's dummy video/audio drivers for headless checks. They cover
movement, boundaries, collision responses, scoring, charges and attacks,
mode initialization, navigation, game-over transitions, asset decoding, clean
shutdown and an offline entry-point run from another directory. No testing
dependency beyond Pygame is required.

## Known limitations and next work

- The reactive AI has no learning or training system. Fun remains unfinished.
- Fixed-step timing and corrected collision handling make some edge cases
  behave differently from the buggy source. Changes are detailed in
  [the audit](docs/AUDIT.md#gameplay-corrections).
- The original faint intro, flashing effects, fixed window and keyboard layout
  are retained. There are no saved settings or remappable controls.
- Four people on one keyboard may encounter hardware key rollover limits.
- Automated checks use headless SDL. Human gameplay feel, physical keyboard
  combinations, audio listening and other operating systems still need review.
- Asset redistribution rights and a source-code license have not been
  established. See [asset review](docs/ASSET_REVIEW.md) before public distribution.

The [roadmap](docs/ROADMAP.md) prioritizes playtesting, accessibility and input
configuration for v2.1, with packaging and carefully scoped maintenance for
v2.2. No online multiplayer or neural AI is included in this release.
