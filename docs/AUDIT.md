# v2.1 audit ? Arcade Renaissance

## Starting point

The v2.0 implementation had one event loop, independent match simulation,
project-relative resource paths and 45 passing tests. The baseline suite was
run before editing: all 45 passed. Its audit, validation and delivery report
remain in AUDIT_V2_0.md, VALIDATION_V2_0.md and DELIVERY_REPORT_V2_0.md.

The runtime consisted of nine game modules plus a package initializer, main.py
and two test files. Audio and images were split across root sounds/ and px/.
Seven supplied power_up_*.png files had been added under px/images/ since the
v2.0 inventory; all were found before implementation and preserved unchanged.
No dependencies beyond Pygame are needed or added.

## Maintainability and reliability findings

- Simulation was already testable without a display. This boundary is retained.
- App transitioned directly from mode choice to simulation; it needed explicit
  briefing/countdown/pause/results states and clean restart ownership.
- Navigation computed hitboxes by rendering text; layout was coupled to fonts
  and renderer placement. Shared rectangular button geometry now drives both.
- Rendering and physics assumed one fixed-size display; a separate logical
  surface plus inverse input mapping now handles scaling and letterboxes.
- Game-over returned automatically and Esc abandoned matches. These intentionally
  become a result choice and pause/resume, with previous gameplay rules retained.
- Full-screen 150 ms flashes blocked simulation despite continued event polling.
  They are replaced with local feedback and an optional reduced-flash setting.
- Assets and audio were centrally declared but split across root folders; all
  runtime resources now live under assets/, retaining hashes and provenance.
- Audio had mute but no volume settings, persistence or pause lifecycle. These
  now share one Settings instance, while tests inject isolated preferences.
- Fixed steps alone could miss collisions after new speed boosts; movement
  now uses collision substeps and direction-aware separation.
- Fun was disabled with no implementation. Its six effects are isolated in
  powerups.py; Lightning remains outside its enum and random pool.

## Preserved and changed behavior

Preserved: logical 800?450 arena, initial ball/paddle positions, default control
bindings, 100 Hz fixed simulation, existing paddle zones and base speeds,
Poder charge/attack mechanics, first-to-five competitive scoring, wall survival
and Free-for-All last-touch scoring. Existing AI remains a reactive tracking bot.

Changed deliberately: English UI and Predator branding; neon panels/arena;
scalable window/fullscreen; nonblocking feedback replacing old full-screen
flashes; pre-match/countdown; Esc pause; manual result choices; new Fun effects;
functional options/persistence. Free-for-All replaces the four-player UI name.
DeepIA is not displayed as an option. No other game modes or network/AI systems
were introduced.

## Visual inspection findings

Rendered previews exposed overlapping horizontal paddle diagrams/control
labels and a scoreboard hiding the Free-for-All top paddle. The label layout
and scoreboard were corrected. A regression test checks top-paddle visibility.
The final UI uses one shared button geometry, clean bundled Pygame typography,
the existing emblem and supplied placeholder icons, with restrained decoration.

## Asset and historical integrity

The migration manifest retains original school paths/hashes, adds previous_path
for the v2.1 move, and records all seven supplied placeholders. All 57 media
files and three archived scripts are accounted for in 60 checksum records.
The original duplicate font is kept in legacy storage because ownership/use
questions remain unresolved; no new duplicate assets were introduced.
Unused/retired resources remain available for owner review. No user environment,
ignored diagnostics or editor settings were deleted. No Git operations occurred.

No licensing, asset rights, historical release dates or human contributors are
invented. See ASSET_REVIEW.md and PROJECT_HISTORY.txt.
