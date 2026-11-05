"""Explicit screen routing and edge-triggered mouse/keyboard menus."""
from dataclasses import dataclass
from enum import Enum, auto
import pygame
from .modes import Mode
from .ui.buttons import button_rects


class Screen(Enum):
    INTRO = auto()
    MAIN = auto()
    ONE_PLAYER = auto()
    TWO_PLAYER = auto()
    FOUR_PLAYER = auto()
    OPTIONS = auto()
    CREDITS = auto()
    PRE_MATCH = auto()
    COUNTDOWN = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


@dataclass(frozen=True)
class MenuItem:
    label: str
    target: Screen | Mode | str

    @property
    def enabled(self):
        return True


MENUS = {
    Screen.MAIN: (MenuItem("SOLO", Screen.ONE_PLAYER), MenuItem("VERSUS", Screen.TWO_PLAYER),
                  MenuItem("FREE-FOR-ALL", Screen.FOUR_PLAYER), MenuItem("OPTIONS", Screen.OPTIONS),
                  MenuItem("CREDITS", Screen.CREDITS), MenuItem("EXIT", "quit")),
    Screen.ONE_PLAYER: (MenuItem("VS COMPUTER", Mode.AI), MenuItem("VS WALL", Mode.WALL), MenuItem("BACK", Screen.MAIN)),
    Screen.TWO_PLAYER: (MenuItem("CLASSIC", Mode.CLASSIC), MenuItem("PODER", Mode.PODER), MenuItem("FUN", Mode.FUN), MenuItem("BACK", Screen.MAIN)),
    Screen.FOUR_PLAYER: (MenuItem("FREE-FOR-ALL", Mode.FOUR), MenuItem("BACK", Screen.MAIN)),
    Screen.OPTIONS: (MenuItem("MUSIC", "music_volume"), MenuItem("SOUND EFFECTS", "sfx_volume"),
                     MenuItem("MUTE", "mute"), MenuItem("DISPLAY", "fullscreen"),
                     MenuItem("REDUCED FLASH", "reduced_flash"), MenuItem("BACK", Screen.MAIN)),
    Screen.CREDITS: (MenuItem("BACK", Screen.MAIN),),
    Screen.PRE_MATCH: (MenuItem("PLAY", "play"), MenuItem("BACK", "back")),
    Screen.PAUSED: (MenuItem("RESUME", "resume"), MenuItem("RESTART", "restart"), MenuItem("MAIN MENU", Screen.MAIN)),
    Screen.GAME_OVER: (MenuItem("PLAY AGAIN", "restart"), MenuItem("MAIN MENU", Screen.MAIN)),
}


def mode_parent(mode):
    return Screen.ONE_PLAYER if mode in (Mode.AI, Mode.WALL) else Screen.FOUR_PLAYER if mode == Mode.FOUR else Screen.TWO_PLAYER


class Navigation:
    def __init__(self):
        self.screen = Screen.INTRO
        self.selected = 0
        self.hover = None
        self.pressed = None

    @property
    def items(self):
        return MENUS.get(self.screen, ())

    def go(self, screen):
        self.screen = screen
        self.selected = 0
        self.hover = None
        self.pressed = None

    def move(self, direction):
        if self.items:
            self.selected = (self.selected + direction) % len(self.items)
            self.hover = None

    def rects(self, font=None):
        if self.screen == Screen.CREDITS:
            layout = "credits"
        elif self.screen == Screen.PRE_MATCH:
            layout = "bottom"
        elif self.screen in (Screen.PAUSED, Screen.GAME_OVER):
            layout = "overlay"
        else:
            layout = "side"
        return button_rects(len(self.items), layout)

    def handle(self, event, font=None):
        if not self.items:
            return None
        if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                self.move(-1 if event.key == pygame.K_UP else 1)
            elif event.key == pygame.K_RETURN:
                return self.items[self.selected].target
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.hover = next((i for i, rect in enumerate(self.rects()) if rect.collidepoint(event.pos)), None)
            if self.hover is not None:
                self.selected = self.hover
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.pressed = self.hover
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pressed, self.pressed = self.pressed, None
                if pressed is not None and pressed == self.hover:
                    return self.items[pressed].target
        return None
