"""Central resource manifest and cached loading, independent of cwd."""

import pygame

from .config import PROJECT_ROOT
from .modes import Mode

MUSIC = {
    "intro": "sounds/music/generique.mp3",
    "menu": "sounds/music/Menu.wav",
    Mode.CLASSIC: "sounds/music/2joueurs.wav",
    Mode.PODER: "sounds/music/PODER.wav",
    Mode.AI: "sounds/music/VsIA.wav",
    Mode.WALL: "sounds/music/VsWall.wav",
    Mode.FOUR: "sounds/music/4joueurs.wav",
}
EFFECTS = {
    "paddle": "sounds/effects/reboundJoueur2.wav",
    "wall": "sounds/effects/reboundWallH.wav",
    "wall_point": "sounds/effects/reboundVsWall.wav",
    "game_over": "sounds/effects/losing.wav",
    "plus": "sounds/effects/plusOne.wav",
    "point": "sounds/effects/minusOne.wav",
    "miss": "sounds/effects/minusOne.wav",
    "speed": "sounds/effects/speed.wav",
    "attack": "sounds/effects/nani.wav",
}
IMAGES = {
    "logo": "px/images/logo.png",
    "title": "px/images/title.png",
    "menu_title": "px/images/Gtitle.png",
}
FONT = "px/fonts/WRESTLEMANIA.ttf"


def asset_path(relative):
    return str(PROJECT_ROOT / relative)


class Assets:
    def __init__(self):
        self.images = {name: pygame.image.load(asset_path(path)).convert_alpha()
                       for name, path in IMAGES.items()}
        self.images["logo"] = pygame.transform.scale(self.images["logo"], (200, 200))
        self.images["menu_title"] = pygame.transform.scale(self.images["menu_title"], (200, 75))
        self.fonts = {size: pygame.font.Font(asset_path(FONT), size) for size in (22, 28, 45, 72)}
