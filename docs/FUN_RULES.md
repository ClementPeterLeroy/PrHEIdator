# Fun mode rules ? v2.1

Fun uses Classic's two paddles, three collision zones, rightward reset serve
and first-to-five target. Only Fun owns a PowerUps controller. All durations
use active simulation time; pause, countdown and results advance none of them.

## Spawn, collection and ownership

A fresh uniform 6?12 second interval starts at match/rally start and after any
effect ends. One pickup appears at x=350?450, y=85?365, away from paddles and
score panels. Icons are shown at 28?28 inside a 32?32 ball-overlap hitbox.
An uncollected pickup stays until collection or rally end; it cannot multiply.

The last paddle to touch the ball owns a pickup. Before a contact, the serving
player owns it: default player 1, who serves toward the right under the
preserved reset rule. Collection removes the icon, plays the existing plusOne
sound, highlights ownership and enables one effect. There is no stacking and
no new collectible while an effect is active. Lightning is never in the pool.

## Effects

| Name | Supplied file | Implementation |
| --- | --- | --- |
| Giant Paddle | power_up_magic_bean.png | Owner's height 100 ? 150; centre preserved where bounds permit. |
| Sabotage | power_up_sabotage.png | Opponent's height 100 ? 65; centre preserved and field-clamped. |
| Hyperball | power_up_flaming_ball.png | Current velocity ?1.5; divide out on expiry. Direction is retained; movement is substepped for collisions. |
| Phantom Ball | power_up_ghost.png | Warn for 0.6 active seconds, then hide only while travelling toward the opponent. Physics remain active. |
| Straight Shot | power_up_laser.png | Aim horizontally toward opponent at max(200, 1.25? horizontal speed), capped at 750 px/s. On expiry remove the boost and restore vertical motion if zero. |
| Shield | power_up_shield.png | One protected goal. On the owner's missed side, prevent scoring, consume, place ball x=30/770 within safe vertical bounds and send it inward at 300 px/s with nonzero vertical velocity. |

Non-Shield effects remain until the opponent successfully returns the ball or
the rally ends. Own returns do not expire them. Shield ignores opponent
returns and lasts until consumed or rally end. If its owner scores instead,
it is cleared with the rally; it never protects the other player.

Restoring a paddle keeps its current centre and clamps it again; it does not
teleport back to its pre-effect location. Ball speed may evolve through ordinary
zone collisions, so removing a multiplier acts on the current reflected
velocity. All points subsequently use the normal ball reset (100, 300 px/s).
Straight Shot cannot leave a rally permanently horizontal after the opponent's
return. Phantom reappears on that return or reset and is never intangible.

## Feedback and balance

Active effects display a player-coloured name; Shield draws a protected goal
line. Collection, points, attacks and defensive saves reuse existing sounds and
short local labels/outlines. Phantom provides its explicit warning. Trails and
transient feedback are removed by reduced flash; essential indicators remain.

Initial magnitudes/intervals follow the brief's suggested values. v2.1 does not
claim competitive balance; long human matches should inform any v2.2 tuning.
The six supplied placeholder images are unchanged. The seventh supplied
power_up_lightning.png is preserved and decoded but has no gameplay effect.
