"""Original black field, coloured paddles, branding and menu placement."""

import pygame

from .config import (BLACK, CHARGE_COLORS, GAME_OVER_SECONDS, GRAY,
                     PLAYER_COLORS, SCORE_GRAY, WHITE, YELLOW)
from .modes import Mode
from .navigation import Screen


class Renderer:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets

    def text(self, text, size, color, position, centered=False):
        surface = self.assets.fonts[size].render(text, True, color)
        rect = surface.get_rect(center=position) if centered else surface.get_rect(topleft=position)
        self.screen.blit(surface, rect)

    def intro(self, elapsed):
        self.screen.fill(BLACK)
        # Preserve the original two-stage, deliberately faint logo/title fade.
        for name, alpha, pos in (
            ("logo", min(45, elapsed * 10), (300, 50)),
            ("title", max(0, min(45, (elapsed - 4.6) * 10)), (250, 250)),
        ):
            image = self.assets.images[name].copy()
            image.set_alpha(round(alpha))
            self.screen.blit(image, pos)

    def menu(self, navigation):
        self.screen.fill(BLACK)
        self.screen.blit(self.assets.images["logo"], (75, 100))
        self.screen.blit(self.assets.images["menu_title"], (75, 300))
        for i, (item, rect) in enumerate(zip(navigation.items, navigation.rects(self.assets.fonts[45]))):
            color = GRAY if not item.enabled else YELLOW if i == navigation.selected else WHITE
            # Long disabled explanations use the same font at a readable smaller size.
            self.text(item.label, 28 if not item.enabled else 45, color, rect.topleft)
        if navigation.screen == Screen.CREDITS:
            self.text("Clement LEROY", 28, WHITE, (500, 220))
            self.text("HEI school project", 22, WHITE, (500, 260))
            self.text("v2.0 - Game Rebirth", 22, WHITE, (500, 300))

    def match(self, match, flash=None, elapsed=0, game_over=None):
        self.screen.fill(flash if flash is not None else BLACK)
        for paddle in match.paddles:
            rect = paddle.rect.copy()
            if game_over is not None and paddle.player != match.winner:
                # Retain the losing paddles' fall without changing simulation state.
                rect.y += round(min(game_over, GAME_OVER_SECONDS) * 300)
            pygame.draw.rect(self.screen, PLAYER_COLORS[paddle.player], rect)
        pygame.draw.circle(self.screen, WHITE, match.ball.position, match.ball.radius)
        if match.mode == Mode.FOUR:
            for i, pos in enumerate(((350, 200), (450, 200), (400, 150), (400, 250))):
                self.text(str(match.scores[i]), 72, PLAYER_COLORS[i], pos)
        else:
            self.text("  ".join(map(str, match.scores)), 72, SCORE_GRAY, (375, 20))
        if match.mode == Mode.PODER:
            for i, x in enumerate((10, 730)):
                charge = match.paddles[i].charge
                color = CHARGE_COLORS[int(elapsed * 100) % len(CHARGE_COLORS)] if charge == 2 else PLAYER_COLORS[i]
                pygame.draw.rect(self.screen, color, (x, 400, 25 * charge, 10))
        if game_over is not None:
            pos = (250, 350) if match.mode == Mode.FOUR else (250, 150)
            self.text("GAME OVER", 72, SCORE_GRAY, pos)
