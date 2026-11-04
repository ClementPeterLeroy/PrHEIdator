# Changelog

## v2.0 — Game Rebirth (unreleased)

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

The original comments describe school-project iterations v1–v5 and proposed
v6 work. No historical release dates or verified Git history are available;
see docs/PROJECT_HISTORY.txt. No commits, tags or releases were created here.
