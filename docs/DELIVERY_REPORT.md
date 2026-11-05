# Predator v2.1 — Arcade Renaissance: delivery report

## 1. Executive summary

One cumulative local patch implements the requested arcade redesign, asset
consolidation, lifecycle screens and six-effect Fun mode. All five prior modes
remain, giving six playable modes. No intermediate version, Git operation,
dependency installation, online feature, neural AI or Lightning gameplay was
introduced. The owner retains version control and publication responsibility.

The UI/credits refinement remains within this same v2.1 entry: persistent menu
control hints/slogans are removed, the requested credits have their own opaque
right-side panel and a BACK button below it, and pre-match explanations remain.
Owner-supplied visual provenance is recorded without assigning blanket public
domain status or inventing terms. Sound/font provenance stays separate.
The refinement adds docs/CREDITS.md and tests/test_menu_refinement.py to the
maintained tree below.

## 2. Final maintained repository tree

```text
Predator/
├── main.py
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── assets.py
│   ├── audio.py
│   ├── entities.py
│   ├── collisions.py
│   ├── modes.py
│   ├── navigation.py
│   ├── rendering.py
│   ├── powerups.py
│   ├── settings.py
│   └── ui/
│       ├── __init__.py
│       ├── buttons.py
│       ├── menus.py
│       └── overlays.py
├── assets/
│   ├── px/
│   │   ├── branding/          3 original logo/title files
│   │   ├── powerups/          7 supplied unchanged placeholder icons
│   │   ├── fonts/             Original font + preserved legacy duplicate
│   │   └── legacy/            Unused images/ and previous legacy/ groups
│   └── snd/
│       ├── music/             8 original music files
│       ├── sfx/               14 original effects
│       └── legacy/            6 separate tracks + 4 retired encodings
├── scripts/
│   ├── capture_previews.py
│   └── smoke_desktop.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ASSET_MIGRATION.json
│   ├── ASSET_REVIEW.md
│   ├── AUDIT.md
│   ├── AUDIT_V2_0.md
│   ├── DELIVERY_REPORT.md
│   ├── DELIVERY_REPORT_V2_0.md
│   ├── FUN_RULES.md
│   ├── PROJECT_HISTORY.txt
│   ├── ROADMAP.md
│   ├── VALIDATION.md
│   ├── VALIDATION_V2_0.md
│   ├── previews/              12 actual renderer captures
│   └── legacy/                3 original script snapshots as text
├── tests/
│   ├── test_application.py
│   ├── test_simulation.py
│   ├── test_powerups.py
│   └── test_lifecycle.py
├── README.md
├── CHANGELOG.md
├── requirements.txt
└── .gitignore
```

The existing workspace folder is not renamed. Local environments, editor files,
caches, diagnostics and Git metadata are omitted from this maintained tree.
No empty ui asset directory is created: UI is rendered programmatically.

## 3. Architecture

The existing independent simulation and single fixed-step loop are retained.
Explicit PRE_MATCH, COUNTDOWN, PAUSED and result ownership replace direct mode
activation/automatic ending. One pending mode supplies clean restart behavior.
Shared UI geometry aligns rendering and input. A logical surface separates
window scaling from physics. Settings persistence and Fun effects have small,
separate modules. See ARCHITECTURE.md and AUDIT.md for design decisions.

## 4. Menu and graphical improvements

Home has SOLO, VERSUS, FREE-FOR-ALL, OPTIONS, CREDITS and EXIT. English labels,
outlined panel buttons, keyboard/hover/pressed feedback, original fleur-de-lis,
clean typography and restrained grid/ring decoration form one theme. Match
arenas use neon paddle edges, a readable high-contrast ball, player-associated
scores, short trails and nonblocking local feedback. Full-screen hit flashes
are removed; reduced flash is functional. Window resizing/fullscreen preserve
16:9 and mouse alignment. Free-for-All score panels leave the top paddle visible.

## 5. Modes

VS COMPUTER (tracking bot), VS WALL (unbounded survival), Classic, Poder,
Fun and Free-for-All (four-player last-touch scoring). Existing bindings,
base dimensions/speeds, zone responses and win conditions remain recognizable.
Competitive modes end at five; wall runs end on the first left miss.

## 6. Fun

Seeded/random 6–12 second spawn intervals, one centre pickup at a time,
last-hitter or serving ownership, one reversible effect and safe rally cleanup.
Giant Paddle, Sabotage, Hyperball, Phantom Ball, Straight Shot and Shield all
operate. Shield explicitly survives opposing returns and prevents a point
before consuming itself. Collision substeps protect fast shots. Lightning is
retained and decoded but excluded. See FUN_RULES.md for exact behavior/tuning.

## 7. Match lifecycle

Each mode shows actual default controls, player assignments, rules, PLAY/BACK,
then a frozen 3–2–1 countdown. Esc/focus loss pauses; RESUME/RESTART/MAIN MENU
work by mouse or keyboard. Pause freezes match timers/physics/effects, with
no catch-up. Results show outcome/final scores and PLAY AGAIN/MAIN MENU.
Restart/Play Again reset all scores, charge, entities and Fun state.

## 8. Assets and sound

All **57 media files** now live under assets/. All **60 checksum records**
(including three historical scripts) pass verification. The manifest retains
old paths and adds previous_path/current locations. The seven supplied icons
are unchanged. Unused originals and the old duplicate font remain for review;
no new duplicate assets are introduced.

Music/SFX have real volume controls, mute and pause lifecycle. One background
stream prevents unintended overlap; effects are cached and reused. Preferences
use a validated atomic JSON save, without a database. Audio failure can fall
back to silence. Pygame 2.6.1 remains the only third-party requirement.

## 9. Tests

**100 passing tests** after UI refinement, including 45 retained/adapted
regressions and 55 new checks. The suite covers mode rules, lifecycle, Fun, scaling, options,
resources, offline startup and cleanup. A separate native Windows main.py
launch ran 410 frames through briefing/countdown/gameplay/pause with connections
blocked and clean shutdown. Commands and limitations are in VALIDATION.md.

## 10. Previews

See [home](previews/home.png), [Fun briefing](previews/fun-briefing.png),
[Fun pickup](previews/fun-pickup.png), [pause](previews/pause.png),
[results](previews/results.png) and [Free-for-All](previews/free-for-all.png).
There are 12 reproducible renderer captures; scripts/capture_previews.py uses
explicit fixture states rather than implying they came from human matches.

## 11. Limitations

Physical keyboard rollover, listening on real audio hardware, long-form Fun
balance, other operating systems, multi-monitor fullscreen and clean installs
need review. The bot remains simple. Controls are not remappable in this patch.
Asset rights and a code license remain unresolved. No Lightning, online play,
neural AI or v2.2 work is included.

## 12. Manual owner review

- Launch main.py and inspect home, all briefings, overlays and display sizes.
- Play all six modes; review Fun ownership/expiry, Shield saves, speed and balance.
- Test four simultaneous players and Poder actions on the intended keyboard.
- Check audible music/SFX levels, mute, pause and persistent settings on real hardware.
- Review assets and ASSET_REVIEW.md for provenance/rights, and select a code license.
- Review CHANGELOG.md, historical records, README and local changes before
  manually performing any version-control/publication steps.

## 13. v2.2 recommendations

Prioritize playtest-led tuning, remappable controls, accessibility review,
platform/packaging validation and asset permissions. Add CI only through the
owner's chosen workflow. ROADMAP.md describes proposals; development has not begun.
