# v2.1 — Arcade Renaissance: validation

Environment: Windows, existing .venv_pong, Python 3.11.15, Pygame 2.6.1,
SDL 2.28.4. No dependencies were installed or uninstalled. No Git operations
were performed. v2.0 results are retained in VALIDATION_V2_0.md.

## Automated results

```powershell
.venv_pong\Scripts\python.exe -m unittest discover -s tests -q
```

Latest result after UI refinement: **100 tests passed**, 0 failures/errors,
approximately 12.7 seconds. All 45 v2.0 regression tests were retained/adapted
for the intentional v2.1 behavior changes; 55 further tests cover new work.
Tests use SDL dummy drivers. Simulation tests do not open a window.

Four added refinement checks verify the supplied credits wording, opaque panel,
text bounds/overlap at landscape and portrait sizes, BACK by keyboard/scaled
mouse, removed persistent menu hints, retained version label and pre-match
instructions. Gameplay simulation and rules are unchanged by this refinement.

Deliberate regression expectation updates: mode choice opens a briefing rather
than immediate gameplay; Fun becomes selectable and DeepIA is absent; Esc
pauses instead of abandoning; results wait for a choice; feedback no longer
pauses physics; click activation uses matching press/release. Substep paddle
positions are compared with floating-point tolerance. No gameplay regression
was removed to hide a failing implementation.

Coverage includes:

- All six home actions, Solo/Versus/Free-for-All branches, Options/Credits/Exit,
  mouse and keyboard selection, initial clicks, wrapping, hover consistency,
  ignored key repeats, matching click edges and Back navigation.
- Briefing and countdown for every mode; simulation frozen until countdown
  completes; pause/resume, focus loss, paused countdown time, restart, results,
  Play Again, score/charge/effect resets and dropping matches on menu return.
- All existing mode movement, boundaries, collision directions/zones, bot,
  scoring, wall survival, first-to-five, Poder attacks and last-touch scoring.
- Randomized/seeded Fun spawning and intervals, safe positioning, overlap
  collection, last-touch/serve ownership, no stacking, no spawning during active
  effects and fresh delays after expiry.
- Giant/Sabotage resize and restoration, Hyperball direction/scale/tunneling,
  Phantom warning/visibility/physical returns, Straight Shot aim and restored
  vertical motion, Shield survival/consumption/no-point behavior on both sides,
  expiry, rally cleanup, paused timers and reserved Lightning exclusion.
- Resizing, 16:9 viewports, inverse mouse mapping at three window sizes,
  letterbox rejection and fullscreen/windowed toggles with dummy SDL.
- Actual music/effect volume values, slider input, mute, reduced flash, audio
  pause/resume/restart, silent audio initialization/decoder failure and settings
  save/load validation, corrupt preferences and save-permission failure.
- Real asset decoders for all retained media, all 60 migration hashes,
  image-cache reuse during rendering, every gameplay overlay and top-paddle
  visibility under the Free-for-All scoreboard.
- Actual main.py execution from another working directory with connection APIs
  blocked; quit in every screen and cleanup after initialization/runtime errors.

## Native application launch

```powershell
.venv_pong\Scripts\python.exe scripts/smoke_desktop.py
```

Observed: **native SDL driver windows**, 410 frames, no network access, clean
display/mixer shutdown. Visited INTRO, MAIN, ONE_PLAYER, PRE_MATCH, COUNTDOWN,
PLAYING and PAUSED. The scripted native run is muted and does not save user
preferences. It executes the real main.py rather than a replacement loop.
This is an actual desktop-window launch, separate from dummy-driver tests.

## Visual previews

```powershell
.venv_pong\Scripts\python.exe scripts/capture_previews.py
```

Twelve previews are generated from explicit fixtures using the actual renderer,
not concept art or claimed recordings of human matches:

- home.png, options.png, credits.png
- fun-briefing.png, poder-briefing.png, free-for-all-briefing.png
- countdown.png, pause.png, results.png
- fun-arena.png, fun-pickup.png, free-for-all.png

Visual inspection covered home, briefings, options, credits, Fun arena/pickup,
pause, results and Free-for-All. It found and prompted fixes for overlapping
horizontal control diagrams and the score panel obscuring the top paddle.
Previews are in docs/previews/; generation changes no runtime assets.

## Remaining manual validation

The v2.1 UI refinement previews were refreshed and inspected: home, Options,
Credits and the Free-for-All briefing. Credits were additionally inspected at
800x450, 1120x630 and 600x800 (portrait letterboxing). Section text is fully
inside an opaque panel; the grid does not cross it, and BACK is below it.
The logo, version label and pre-match instructions remain. Physical high-DPI
readability and other operating systems were not visually verified.

- Long interactive games, competitive Fun balance and human gameplay feel.
- Physical four-player key rollover and simultaneous Poder key combinations.
- Audible output and subjective levels on real audio devices; native smoke is muted.
- Fullscreen behavior on physical multi-monitor setups and macOS/Linux.
- Clean-machine dependency installation and packaging.
- Provenance, attribution, redistribution permissions and a source-code license.

Headless tests and a scripted native launch do not replace these owner checks.
