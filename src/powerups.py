"""Fun rally pickups and reversible effects; no display/audio initialization."""

from dataclasses import dataclass
from enum import Enum

import pygame

from .config import HEIGHT, WIDTH


class PowerUp(Enum):
    GIANT = "Giant Paddle"
    SABOTAGE = "Sabotage"
    HYPERBALL = "Hyperball"
    PHANTOM = "Phantom Ball"
    STRAIGHT = "Straight Shot"
    SHIELD = "Shield"


POWERUP_FILES = {
    PowerUp.GIANT: "power_up_magic_bean.png",
    PowerUp.SABOTAGE: "power_up_sabotage.png",
    PowerUp.HYPERBALL: "power_up_flaming_ball.png",
    PowerUp.PHANTOM: "power_up_ghost.png",
    PowerUp.STRAIGHT: "power_up_laser.png",
    PowerUp.SHIELD: "power_up_shield.png",
}
RESERVED_FILE = "power_up_lightning.png"


@dataclass
class Pickup:
    kind: PowerUp
    position: pygame.Vector2

    @property
    def rect(self):
        return pygame.Rect(round(self.position.x) - 16, round(self.position.y) - 16, 32, 32)


@dataclass
class Effect:
    kind: PowerUp
    owner: int
    age: float = 0
    previous_vertical: float = 0


class PowerUps:
    def __init__(self, rng):
        self.rng = rng
        self.pickup = None
        self.active = None
        self.spawn_in = rng.uniform(6, 12)

    def clear(self, match):
        self.expire(match)
        self.pickup = None
        self.spawn_in = self.rng.uniform(6, 12)

    def expire(self, match):
        effect = self.active
        if effect is None:
            return
        if effect.kind == PowerUp.GIANT:
            match.paddles[effect.owner].resize(100)
        elif effect.kind == PowerUp.SABOTAGE:
            match.paddles[1 - effect.owner].resize(100)
        elif effect.kind == PowerUp.HYPERBALL:
            match.ball.velocity /= 1.5
        elif effect.kind == PowerUp.STRAIGHT:
            # Preserve the direction of the opponent's return while restoring a
            # nonzero vertical component; horizontal rallies cannot get stuck.
            sign = 1 if match.ball.velocity.x >= 0 else -1
            match.ball.velocity.x = sign * min(500, max(100, abs(match.ball.velocity.x) / 1.25))
            if not match.ball.velocity.y:
                match.ball.velocity.y = effect.previous_vertical or 300
        self.active = None
        self.spawn_in = self.rng.uniform(6, 12)

    def activate(self, match, kind, owner):
        if self.active is not None:
            return False
        kind = PowerUp(kind)
        self.pickup = None
        self.active = Effect(kind, owner, previous_vertical=match.ball.velocity.y)
        if kind == PowerUp.GIANT:
            match.paddles[owner].resize(150)
        elif kind == PowerUp.SABOTAGE:
            match.paddles[1 - owner].resize(65)
        elif kind == PowerUp.HYPERBALL:
            match.ball.velocity *= 1.5
        elif kind == PowerUp.STRAIGHT:
            speed = min(750, max(200, abs(match.ball.velocity.x) * 1.25))
            match.ball.velocity.update(speed if owner == 0 else -speed, 0)
        return True

    def on_return(self, match, player):
        if self.active and self.active.owner != player and self.active.kind != PowerUp.SHIELD:
            self.expire(match)

    def save(self, match, side):
        effect = self.active
        if effect is None or effect.kind != PowerUp.SHIELD:
            return None
        loser = 0 if side == "left" else 1
        if effect.owner != loser:
            return None
        owner = effect.owner
        self.expire(match)
        match.ball.position.x = 30 if owner == 0 else WIDTH - 30
        match.ball.position.y = max(20, min(HEIGHT - 20, match.ball.position.y))
        match.ball.velocity.update(300 if owner == 0 else -300, match.ball.velocity.y or 200)
        match.last_touch = owner
        return owner

    def update(self, match, dt):
        if self.active:
            self.active.age += dt
            return []
        if self.pickup is not None:
            if match.ball.rect.colliderect(self.pickup.rect):
                owner = match.last_touch if match.last_touch is not None else match.serving_player
                self.activate(match, self.pickup.kind, owner)
                return [("pickup", owner)]
        else:
            self.spawn_in -= dt
            if self.spawn_in <= 0:
                self.pickup = Pickup(self.rng.choice(tuple(PowerUp)),
                                     pygame.Vector2(self.rng.uniform(350, 450), self.rng.uniform(85, 365)))
        return []

    def ball_visible(self, match):
        effect = self.active
        if effect is None or effect.kind != PowerUp.PHANTOM or effect.age < 0.6:
            return True
        # Only hide while travelling toward the other player.
        return not (match.ball.velocity.x > 0 if effect.owner == 0 else match.ball.velocity.x < 0)
