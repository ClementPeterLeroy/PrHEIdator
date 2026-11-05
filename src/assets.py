"""Central resource manifest and cached loading, independent of cwd."""

import pygame

from .config import PROJECT_ROOT
from .modes import Mode
from .powerups import POWERUP_FILES, RESERVED_FILE

MUSIC = {
    "intro": "assets/snd/music/generique.mp3",
    "menu": "assets/snd/music/Menu.wav",
    Mode.CLASSIC: "assets/snd/music/2joueurs.wav",
    Mode.FUN: "assets/snd/music/2joueurs.wav",
    Mode.PODER: "assets/snd/music/PODER.wav",
    Mode.AI: "assets/snd/music/VsIA.wav",
    Mode.WALL: "assets/snd/music/VsWall.wav",
    Mode.FOUR: "assets/snd/music/4joueurs.wav",
}
EFFECTS = {
    "paddle": "assets/snd/sfx/reboundJoueur2.wav",
    "wall": "assets/snd/sfx/reboundWallH.wav",
    "wall_point": "assets/snd/sfx/reboundVsWall.wav",
    "game_over": "assets/snd/sfx/losing.wav",
    "plus": "assets/snd/sfx/plusOne.wav",
    "point": "assets/snd/sfx/minusOne.wav",
    "miss": "assets/snd/sfx/minusOne.wav",
    "speed": "assets/snd/sfx/speed.wav",
    "pickup": "assets/snd/sfx/plusOne.wav",
    "shield": "assets/snd/sfx/reboundVsWall.wav",
    "attack": "assets/snd/sfx/nani.wav",
}
IMAGES = {
    "logo": "assets/px/branding/logo.png",
    "title": "assets/px/branding/title.png",
    "menu_title": "assets/px/branding/Gtitle.png",
}
FONT = "assets/px/fonts/WRESTLEMANIA.ttf"


def asset_path(relative):
    return str(PROJECT_ROOT / relative)


class Assets:
    def __init__(self):
        self.images = {name: pygame.image.load(asset_path(path)).convert_alpha()
                       for name, path in IMAGES.items()}
        self.images["logo"] = pygame.transform.scale(self.images["logo"], (200, 200))
        self.images["menu_title"] = pygame.transform.scale(self.images["menu_title"], (200, 75))
        self.fonts = {size: pygame.font.Font(None, size) for size in
                      (16, 18, 20, 22, 24, 26, 28, 32, 36, 40, 45, 48, 56, 64, 72, 96)}
        self.powerups = {kind: pygame.transform.smoothscale(
            pygame.image.load(asset_path("assets/px/powerups/" + filename)).convert_alpha(), (28, 28))
            for kind, filename in POWERUP_FILES.items()}
        self.reserved = pygame.image.load(asset_path("assets/px/powerups/" + RESERVED_FILE)).convert_alpha()
