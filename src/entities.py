"""Reusable simulation objects; drawing and mode rules live elsewhere."""

from dataclasses import dataclass, field

import pygame

from .config import BALL_RADIUS, HEIGHT, WIDTH


@dataclass
class Ball:
    position: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(400, 240))
    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(100, 300))
    radius: int = BALL_RADIUS

    @property
    def rect(self):
        return pygame.Rect(round(self.position.x) - self.radius,
                           round(self.position.y) - self.radius,
                           self.radius * 2, self.radius * 2)

    def move(self, dt):
        self.position += self.velocity * dt

    def reset(self):
        self.position.update(WIDTH / 2, 200)
        self.velocity.update(100, 300)


@dataclass
class Paddle:
    rect: pygame.Rect
    player: int
    horizontal: bool = False
    charge: int = 0
    position: float = field(init=False)

    def __post_init__(self):
        self.position = float(self.rect.x if self.horizontal else self.rect.y)

    def move(self, direction, speed, dt, margin=0):
        length = self.rect.width if self.horizontal else self.rect.height
        limit = WIDTH if self.horizontal else HEIGHT
        self.position = max(margin, min(limit - length - margin,
                                       self.position + direction * speed * dt))
        if self.horizontal:
            self.rect.x = round(self.position)
        else:
            self.rect.y = round(self.position)
