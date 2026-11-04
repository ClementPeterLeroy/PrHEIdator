# Validation results

Environment: Windows, existing .venv_pong, Python 3.11.15, Pygame 2.6.1,
SDL 2.28.4. The tests use SDL dummy video and audio drivers. No packages were
installed or uninstalled during implementation.

## Automated suite

```powershell
.venv_pong\Scripts\python.exe -m unittest discover -s tests -v
```

Observed final result: **45 tests passed**, 0 failures, 0 errors.
The suite completed in approximately 3.6 seconds on the development machine.

Covered behaviors:

- Ball movement/reset and subpixel integration; vertical and horizontal
  paddle bounds; four-player corner margins.
- Top/bottom reflections, all four paddle directions, mirrored paddle
  zones, bounded edge acceleration and prevention of repeated overlap flips.
- Fresh initialization of all five modes; rejection of Fun/DeepIA as modes.
- Classic point ownership, first-to-five completion and frozen finished matches.
- Wall right-side scoring beyond five and left-miss completion.
- Four-player last-touch scoring for all players on all exits and no points
  before the first touch.
- AI detection/tracking boundaries and equivalence of the exact CDF to the
  effective historical numerical integral for a deterministic sample.
- Poder centre-hit charges, charge cap, proximity/alignment requirements,
  both attack directions, charge loss on a missed point and collision of a
  high-speed shot with an aligned opponent.
- Keyboard mode selection, initial mouse click before rendering, skipped
  disabled choices, empty-event frames and all menu renders.
- All four paddle controls, both attack keys, Esc navigation, intro expiry/
  skip, game-over expiry in every mode and responsive quit during flashes.
- Fixed-step equivalence across frame batching, music reuse and mute.
- Quit handling in every screen and application-loop quit processing.
- Real decoder loading of all 19 unique active assets and all 50 retained
  media files, including unused and retired variants.
- SHA-256 verification of all 53 relocated files against the migration record.
- Real main.py invocation from docs/ in a subprocess, with connection APIs
  blocked and SDL cleanup asserted after exit.
- Silent operation when mixer initialization fails, and main-function
  cleanup after both initialization and runtime exceptions.

An initial run had 42 passing tests and a Windows permission error removing
a test-only temporary directory. The entry-point test now uses the existing
docs/ working directory, requires no temporary filesystem cleanup and passes.

## Additional checks

- Before refactoring, each original implemented gameplay loop ran for 15
  frames headlessly with no exception. This was a short baseline, not full
  verification of the old game's functionality.
- Six rendered screen captures were generated under the ignored
  .diagnostics/ directory. Main, two-player, credits, Poder and four-player
  captures were visually inspected; the original visual arrangement is retained.
- Active source was checked for debug prints, Flask, Kafka, NumPy, remote
  URLs and external controller references; none remain in src/ or main.py.
- Original scripts remain text snapshots. No third-party asset was generated,
  overwritten or discarded.

## Testing limits

No physical-keyboard multiplayer session, human audio listening, long-form
interactive balance comparison, installer test, fresh environment install or
macOS/Linux run was performed. Headless tests establish code paths and decoder
compatibility, not perceived gameplay quality or physical audio output.

In particular, review the documented collision symmetry/corner-margin fixes
against desired gameplay feel. Unimplemented modes remain disabled. Provenance
and redistribution rights remain a manual task and are not validated by tests.
