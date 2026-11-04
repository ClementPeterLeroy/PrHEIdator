"""Explicit screens and reusable menus, with disabled unfinished features."""

from dataclasses import dataclass
from enum import Enum, auto

import pygame

from .modes import Mode


class Screen(Enum):
    INTRO = auto()
    MAIN = auto()
    ONE_PLAYER = auto()
    TWO_PLAYER = auto()
    FOUR_PLAYER = auto()
    OPTIONS = auto()
    CREDITS = auto()
    PLAYING = auto()
    GAME_OVER = auto()


@dataclass(frozen=True)
class MenuItem:
    label: str
    target: Screen | Mode | str | None

    @property
    def enabled(self):
        return self.target is not None


MENUS = {
    Screen.MAIN: (
        MenuItem("1 joueur", Screen.ONE_PLAYER),
        MenuItem("2 joueurs", Screen.TWO_PLAYER),
        MenuItem("4 joueurs", Screen.FOUR_PLAYER),
        MenuItem("Option", Screen.OPTIONS),
        MenuItem("Credit & Quit", Screen.CREDITS),
    ),
    Screen.ONE_PLAYER: (
        MenuItem("Ia", Mode.AI), MenuItem("Wall", Mode.WALL), MenuItem("Return", Screen.MAIN),
    ),
    Screen.TWO_PLAYER: (
        MenuItem("Classic", Mode.CLASSIC), MenuItem("Poder", Mode.PODER),
        MenuItem("Fun (unavailable)", None), MenuItem("Return", Screen.MAIN),
    ),
    Screen.FOUR_PLAYER: (MenuItem("Classic", Mode.FOUR), MenuItem("Return", Screen.MAIN)),
    Screen.OPTIONS: (MenuItem("DeepIA: unavailable", None), MenuItem("Return", Screen.MAIN)),
    Screen.CREDITS: (MenuItem("Return", Screen.MAIN), MenuItem("Quit", "quit")),
}


class Navigation:
    def __init__(self):
        self.screen = Screen.INTRO
        self.selected = 0

    @property
    def items(self):
        return MENUS.get(self.screen, ())

    def go(self, screen):
        self.screen = screen
        self.selected = next((i for i, item in enumerate(self.items) if item.enabled), 0)

    def move(self, direction):
        if not self.items:
            return
        for offset in range(1, len(self.items) + 1):
            candidate = (self.selected + offset * direction) % len(self.items)
            if self.items[candidate].enabled:
                self.selected = candidate
                return

    def rects(self, font):
        return [font.render(item.label, True, (255, 255, 255)).get_rect(topleft=(550, 50 + i * 50))
                for i, item in enumerate(self.items)]

    def handle(self, event, font):
        if not self.items:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.move(-1 if event.key == pygame.K_UP else 1)
            elif event.key == pygame.K_RETURN:
                return self.items[self.selected].target
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.rects(font)):
                if rect.collidepoint(event.pos) and self.items[index].enabled:
                    self.selected = index
                    return self.items[index].target
        return None
