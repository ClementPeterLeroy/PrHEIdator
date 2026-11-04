# Architecture

`main.py` calls `src.app.main()`. Importing modules does not open a window,
initialize audio, contact a service or start a game. The main function creates
the application, runs it and closes Pygame in `finally`, including after an
initialization or runtime failure.

## Responsibilities

| Module | Responsibility |
| --- | --- |
| config | Project root, dimensions, timing, colours and keyboard constants |
| entities | Floating-point ball position/velocity and clamped paddle movement |
| collisions | Direction-aware paddle and top/bottom collision responses |
| modes | Match ownership, reactive AI, mode-specific exits/scoring and Poder |
| navigation | Explicit screen enum, menu contents, keyboard/mouse selection |
| assets | Project-relative resource manifest and cached images/fonts |
| audio | Streamed music, loaded effects, mute and shutdown |
| rendering | Drawing original assets, scores, paddles, flashes and game over |
| app | Event dispatch, state transitions, simulation timing and lifecycle |

## One central loop

Every rendered frame:

1. Read elapsed time from the Pygame clock, limited to 100 ms to avoid an
   unbounded catch-up after a stalled window.
2. Consume every queued event exactly once. Handle quit, menu selection,
   back/skip and mute. Menu input comes from events, never a stale event variable.
3. Update the active screen's timer. During gameplay, sample held movement and
   attack keys and advance a fixed 10 ms simulation accumulator.
4. Each simulation step moves the paddles and reactive AI, evaluates held Poder
   attacks, moves the ball, resolves boundaries/paddles and applies mode rules.
5. Consume simulation events as sound effects and colour flashes. A flash
   pauses simulation for the original 150 ms while frame/event processing
   continues. Match completion transitions to GAME_OVER once.
6. Draw the active screen and flip the display.

Intro, menus, gameplay and game over use this same loop. There are no blocking
animation loops, delayed waits, worker threads or network services. The clock
limits rendering to 100 FPS. Simulation positions retain subpixel precision;
Pygame rectangles are rounded collision/rendering bounds.

## State and ownership

`Navigation` owns one `Screen` and the selected menu index. `Application`
owns a `Match` only while playing or showing game over. Selecting a mode
creates a fresh match, resetting scores, charge, ball, paddles and last touch.
Leaving a match drops it. Entering GAME_OVER stops music, plays the losing
effect once, freezes simulation and starts a 2.8-second return timer.

`Match` owns its ball, paddles, scores, RNG and rules. It returns small
`(event_name, player)` tuples and never plays sound or draws. `Mode` contains
only the five implemented modes; Fun and DeepIA have no selectable target.
The reactive AI uses an injectable RNG for deterministic verification.

The school game's presentation is drawn by `Renderer`. Game-over paddle
falling is visual only and does not mutate the stopped match. The old
inconsistent ball/paddle draw-before-move ordering is replaced with drawing
the current simulation state.

## Resources and dependencies

`PROJECT_ROOT` comes from the config module's location. All active resources
are declared in assets.py and resolved against that root. Images and fonts
are cached at startup. Effects are loaded once; music uses Pygame's streaming
channel and changes on state transitions. Effects cannot accidentally restart
menu music through a global mixer-busy test.

Pygame is the only third-party dependency. Python's math.erf replaces the
AI integral; plain tuples replace NumPy's colour array. Audio initialization
failure permits a silent game. Missing/corrupt active files still raise an
error. Archived source is text and is never imported.

## Verification

Tests isolate entities, collisions and rules, then use real Pygame with dummy
SDL drivers to exercise application state transitions, input, every mode's
game-over path, resource decoding and lifecycle cleanup. A subprocess runs
the real entry point from docs/ with socket connection methods blocked.
See VALIDATION.md for observed results and testing limits.
