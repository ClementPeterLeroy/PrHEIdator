# Predator v2.1 ? Arcade Renaissance: architecture

The minimal main.py calls src.app.main(). Imports do not initialize a display
or connect to a service. main() owns predictable cleanup in a finally block,
including initialization/runtime failures. Pygame is the sole external dependency.

## Responsibilities

| Module | Responsibility |
| --- | --- |
| app | Lifecycle transitions, one event loop, fixed-step scheduling, window scaling |
| config | Logical dimensions, timing, palette and actual control bindings |
| entities | Ball/paddle state and reversible paddle resizing |
| collisions | Direction-aware reflection, separation and paddle zones |
| modes | Six mode identifiers, match state, tracking bot, scoring and Poder |
| powerups | Seeded Fun spawning, ownership, temporary transformations and expiry |
| navigation | Explicit screen enum, shared button hitboxes, edge-triggered input |
| ui/buttons | Button geometry and common selected/hover/pressed rendering |
| ui/menus | Mode explanations and controls derived from configuration |
| ui/overlays | Shared translucent countdown/pause/result panels |
| rendering | Cached backdrop/text, branding, briefings, arenas and feedback |
| assets | One project-relative runtime resource manifest and caches |
| audio | One music stream, cached/aliased effects, volume, pause and cleanup |
| settings | Validated JSON preferences, atomic save and graceful save failure |

The small ui/ package separates presentation from navigation without a widget
framework. Settings has its own module because filesystem persistence is
independent of game configuration. No empty proposed modules were added.

## Screens and transitions

INTRO ? MAIN ? SOLO / VERSUS / FREE-FOR-ALL / OPTIONS / CREDITS.
Selecting any Mode stores pending_mode and opens PRE_MATCH, without simulating
or creating transient effects. PLAY creates a new Match and opens COUNTDOWN.
After three seconds COUNTDOWN transitions to PLAYING. Back from PRE_MATCH
returns to the branch the mode belongs to.

PLAYING or COUNTDOWN ? PAUSED on Esc/focus loss. RESUME/Esc restores the exact
previous screen and countdown time. RESTART creates a fresh Match/countdown;
MAIN MENU drops all transient state. A finished match enters GAME_OVER once.
That results screen waits for PLAY AGAIN or MAIN MENU rather than timing out.

A Match owns its ball, paddles, scores, RNG, play time, last-touch/serve ownership
and optional Fun controller. It does not load files, play sounds or draw.
Selecting a mode is distinct from starting a match; rendering/input share
explicit state rather than overloading one gameplay flag.

## One central loop and simulation

Each frame polls all queued events once, dispatches lifecycle/navigation,
updates the active screen and draws one logical frame. Menu activation uses
KEYDOWN edges or matching mouse press/release, and ignores key repeats.
No nested animation loops or blocking waits are used.

The original gameplay coordinate space remains 800?450. Rendering is limited
to 100 FPS; a 10 ms fixed-step accumulator advances gameplay. Frame input above
100 ms is discarded to bound stall catch-up. Collision processing further
substeps ball movement to at most four pixels per slice for in-game speed
ranges, budgeting for Hyperball collection midway through a step. A point ends
that simulation step so an old trajectory cannot score twice. Paddle float
positions avoid losing movement precision during substeps.

Pause never calls Match.step(), advances an effect or consumes spawn time.
The simulation accumulator is cleared on pause/resume. Rendering/menu easing
may continue while match state stays frozen. Countdown similarly advances only
its own screen timer. Results freeze match state until a deliberate action.

Simulation returns small (event_name, player) tuples for audio/visual feedback.
Feedback has a bounded history, is nonblocking and uses local outlines/labels
rather than full-screen flashes. Reduced-flash preferences suppress decorative
motion/trails and transient feedback, preserving necessary effect indicators.

## Fun state

A PowerUps controller exists only for FUN. It owns one Pickup or one Effect,
never a stack. Its seeded RNG supplies a fresh 6?12 second interval and safe
centre-arena placement. Collection uses the ball rectangle and last hitter;
serving_player supplies ownership before first contact.

Transformations use reversible scale factors or centre-preserving paddle
resizes. Non-Shield effects expire after the opposing paddle's valid return.
Shield instead intercepts the protected player's goal before score assignment,
consumes itself and sends the ball back into the court. Rally end clears all
pickups/effects before the standard reset. Straight Shot restores a nonzero
vertical component on expiry. Phantom modifies rendering only, with a 0.6 s
warning and continuing collision detection. Lightning is a retained image,
not an enum member or random choice. See FUN_RULES.md for exact rules.

## Display and resources

A logical surface is scaled to the largest 16:9 viewport inside the real window.
Black bars fill unused space. Mouse events are inverse-mapped through that same
viewport; clicks in letterboxes miss all widgets. Both mouse hitboxes and button
rendering use ui.buttons.button_rects(). Resizing and fullscreen update the
window without changing physics coordinates or the match.

All runtime files live under assets/. Images, supplied icons and fonts load
once; fonts use Pygame's bundled default for clean interface typography.
Original font files remain preserved. The gradient/grid backdrop and rendered
text are cached; text caching is bounded to 256 entries. Music streams on one
channel while aliased sound events reuse decoded Sound instances. Transitions
stop inappropriate effects/music; pause/resume use the mixer pause controls.

Settings are saved only when changed. Values/types are validated; invalid JSON
loads defaults. Atomic replacement reduces partial saves. A write failure keeps
the session functional and is reported inside Options, without blocking play.
Tests inject Settings and disable persistence to avoid modifying user choices.
