# Changelog

## v2.1 — Arcade Renaissance (unreleased)

- Renamed the modern game Predator while preserving PrHEIdator/HEI history,
  original authorship, emblem and v2.0 records.
- Rebuilt the interface as a cohesive retro-neon arcade presentation: six
  English home actions, shared outlined buttons, hover/keyboard/press feedback,
  clean typography, restrained animated branding, arenas and score panels.
- Added resizable/fullscreen display with a logical 800?450 surface,
  aspect-preserving scaling, letterboxes and correctly mapped mouse input.
- Added a controls briefing and 3?2?1 countdown for every mode, universal Esc
  pause/resume/restart/menu, focus-loss pause and deliberate results choices.
- Preserved VS COMPUTER, VS WALL, Classic, Poder and renamed Free-for-All;
  added playable Fun with six rally power-ups and explicit ownership/expiry.
- Implemented Giant Paddle, Sabotage, Hyperball, Phantom Ball, Straight Shot
  and Shield. Preserved the supplied icons unchanged; excluded reserved Lightning.
- Added collision substeps for fast shots and reversible temporary effects.
- Replaced disruptive full-screen flashes and forced hit pauses with local,
  nonblocking feedback; added reduced flash.
- Added real music/SFX volumes, mute, display controls and validated local JSON
  settings with graceful save failure. Improved pause/restart/audio transitions.
- Consolidated all 57 media files under assets/, preserved 60 checksum records
  including historical scripts, and retained uncertain legacy resources.
- Retained/adapted the 45 regression tests for intended lifecycle changes and
  added coverage for Fun, scaling, lifecycle, settings and visual regressions.
- Added renderer previews, reproducible validation scripts and updated docs.
- Refined v2.1 menus: removed persistent slogans/control hints, retained
  pre-match controls and the version label, and placed the revised credits on
  a padded opaque panel with BACK below the text.
- Recorded owner-supplied visual provenance, preserving applicable licensing
  and attribution requirements and separate sound/font review.
- No new dependencies, network features, neural AI or Git operations.

## v2.0 â€” Game Rebirth (unreleased)

- Replaced nested global gameplay/menu loops with one application loop and
  explicit screens, reusable entities, shared collisions and separate mode rules.
- Preserved AI, wall, two-player Classic, Poder and four-player Classic;
  preserved the school branding, controls, intro, music and game-over display.
- Disabled the unimplemented Fun and DeepIA choices and repaired mouse/keyboard
  navigation, including the previously inactive credits/quit choice.
- Fixed wall game-over progression and prevented score/movement updates after
  match completion. Added consistent return-to-menu and clean shutdown behavior.
- Fixed signed paddle speed asymmetry and repeated overlap collisions; clamped
  movement to the field and normalized corner margins. Preserved the intended
  three-zone paddle response and documented behavioral differences.
- Preserved Poder centre-hit charge, charge loss on a missed point, and
  close-range horizontal attacks for both players.
- Converted original per-frame speeds to a 100 Hz fixed simulation step and
  retained the 150 ms collision flashes without blocking event processing.
- Replaced AI's numerical integral with the equivalent normal CDF.
- Centralized project-relative asset paths; corrected intro/menu filenames;
  cached images/fonts and streamed background music independently of effects.
- Added mute and silent operation when audio hardware cannot initialize.
- Reorganized assets into sounds/ and px/. Preserved all 50 asset files and
  archived all three original scripts as text with a checksum migration record.
- Removed NumPy, Flask, Kafka and controller infrastructure from the active
  application. Pygame is the sole third-party requirement.
- Added meaningful simulation and headless integration tests, project
  documentation and a list of asset provenance questions for manual review.

The original comments describe school-project iterations v1â€“v5 and proposed
v6 work. No historical release dates or verified Git history are available;
see docs/PROJECT_HISTORY.txt. No commits, tags or releases were created here.
