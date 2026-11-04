"""Streaming background music and separate effect channels."""

import pygame

from .assets import EFFECTS, MUSIC, asset_path


class Audio:
    def __init__(self, enabled=True):
        self.enabled = enabled and pygame.mixer.get_init() is not None
        self.muted = False
        self.current = None
        self.effects = ({name: pygame.mixer.Sound(asset_path(path)) for name, path in EFFECTS.items()}
                        if self.enabled else {})

    def music(self, name):
        if name == self.current:
            return
        if self.enabled:
            pygame.mixer.music.stop()
            if name is not None:
                pygame.mixer.music.load(asset_path(MUSIC[name]))
                pygame.mixer.music.play(0 if name == "intro" else -1)
        self.current = name

    def effect(self, name):
        if self.enabled and not self.muted:
            self.effects[name].play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.enabled:
            pygame.mixer.music.set_volume(0 if self.muted else 1)
            if self.muted:
                pygame.mixer.stop()

    def close(self):
        if self.enabled:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
