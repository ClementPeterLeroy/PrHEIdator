"""Local mode rules, score ownership and Poder special attacks."""

from enum import Enum
from math import erf, sqrt
import random

import pygame

from .collisions import bounce_paddle, bounce_walls, exit_side
from .config import AI_SPEED, HEIGHT, HORIZONTAL_SPEED, PADDLE_SPEED, WIDTH, WINNING_SCORE
from .entities import Ball, Paddle


class Mode(Enum):
    AI = "Ia"
    WALL = "Wall"
    CLASSIC = "Classic"
    PODER = "Poder"
    FOUR = "4 joueurs Classic"


class Match:
    """Own a single match. Events describe sounds/flashes for the application."""

    def __init__(self, mode, rng=None):
        self.mode = Mode(mode)
        self.rng = rng if rng is not None else random.Random()
        self.ball = Ball()
        self.paddles = [Paddle(pygame.Rect(10, 200, 10, 100), 0)]
        if self.mode != Mode.WALL:
            self.paddles.append(Paddle(pygame.Rect(780, 200, 10, 100), 1))
        if self.mode == Mode.FOUR:
            self.paddles.extend((Paddle(pygame.Rect(375, 10, 100, 10), 2, True),
                                 Paddle(pygame.Rect(375, 430, 100, 10), 3, True)))
        self.scores = [0] * len(self.paddles)
        self.last_touch = None
        self.finished = False
        self.winner = None
        self.ai_detection = 0.9

    def move_players(self, directions, dt):
        for paddle in self.paddles:
            if self.mode == Mode.AI and paddle.player == 1:
                continue
            speed = HORIZONTAL_SPEED if paddle.horizontal else PADDLE_SPEED
            # Keep four-player paddles clear of the corner paddles.
            margin = 20 if self.mode == Mode.FOUR else 0
            paddle.move(directions.get(paddle.player, 0), speed, dt, margin)
        if self.mode == Mode.AI and self.ball.position.x > WIDTH * self.ai_detection:
            paddle = self.paddles[1]
            distance = self.ball.position.y - paddle.rect.centery
            direction = max(-1, min(1, distance / (AI_SPEED * dt))) if dt else 0
            paddle.move(direction, AI_SPEED, dt)

    def _next_ai_detection(self):
        # Exact normal CDF replaces the legacy 2,000-step integral. Preserve
        # the effective original arguments (mu=.1, sigma=.4), including rounding.
        value = abs(self.rng.random() - self.rng.random())
        cdf = lambda x: 0.5 * (1 + erf((x - 0.1) / (0.4 * sqrt(2))))
        return min(round(cdf(value) - cdf(0), 2) + 0.15, 0.95)

    def attack(self, player):
        if self.finished or self.mode != Mode.PODER or player not in (0, 1):
            return False
        paddle = self.paddles[player]
        near = self.ball.position.x < 30 if player == 0 else self.ball.position.x > 760
        aligned = paddle.rect.top < self.ball.position.y < paddle.rect.bottom
        if paddle.charge < 2 or not near or not aligned:
            return False
        paddle.charge = 0
        self.ball.position.x = (paddle.rect.right + self.ball.radius if player == 0
                                else paddle.rect.left - self.ball.radius)
        self.ball.velocity.update(1000 if player == 0 else -1000, 0)
        return True

    def _award(self, player):
        self.scores[player] += 1
        if self.mode != Mode.WALL and self.scores[player] >= WINNING_SCORE:
            self.finished = True
            self.winner = player

    def step(self, dt, directions=None, attacks=()):
        if self.finished:
            return []
        self.move_players(directions or {}, dt)
        events = []
        for player in attacks:
            if self.attack(player):
                events.append(("attack", player))
        self.ball.move(dt)
        if self.mode != Mode.FOUR and bounce_walls(self.ball):
            events.append(("wall", None))
        for paddle in self.paddles:
            zone = bounce_paddle(self.ball, paddle, zoned=self.mode != Mode.FOUR)
            if zone is not None:
                self.last_touch = paddle.player
                if self.mode == Mode.PODER and zone == "center":
                    paddle.charge = min(2, paddle.charge + 1)
                if self.mode == Mode.AI and paddle.player == 1:
                    self.ai_detection = self._next_ai_detection()
                events.append(("paddle" if zone in ("center", "plain") else "speed", paddle.player))

        side = exit_side(self.ball)
        if self.mode == Mode.WALL:
            if side == "right":
                self.ball.position.x = WIDTH - self.ball.radius
                self.ball.velocity.x = -abs(self.ball.velocity.x)
                self._award(0)
                events.append(("wall_point", 0))
            elif side == "left":
                self.finished = True
                events.append(("miss", None))
        elif self.mode == Mode.FOUR:
            if side is not None:
                if self.last_touch is not None:
                    self._award(self.last_touch)
                    events.append(("point", self.last_touch))
                else:
                    events.append(("miss", None))
                self.last_touch = None
                self.ball.reset()
        elif side in ("left", "right"):
            scorer = 1 if side == "left" else 0
            self._award(scorer)
            if self.mode == Mode.PODER:
                self.paddles[1 - scorer].charge = 0
            events.append(("point", scorer))
            self.ball.reset()
        return events
