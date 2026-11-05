"""One music stream, cached effects, volume controls and pause lifecycle."""
import pygame
from .assets import EFFECTS, MUSIC, asset_path
from .settings import Settings


class Audio:
    def __init__(self, enabled=True, settings=None):
        self.enabled = enabled and pygame.mixer.get_init() is not None
        self.settings = settings or Settings()
        self.current = None
        self.paused = False
        self.effects = {}
        if self.enabled:
            try:
                cache = {path: pygame.mixer.Sound(asset_path(path)) for path in set(EFFECTS.values())}
                self.effects = {name: cache[path] for name, path in EFFECTS.items()}
            except (pygame.error, OSError):
                self.enabled = False
        self.apply_volumes()

    @property
    def muted(self):
        return self.settings.muted

    def apply_volumes(self):
        if self.enabled:
            pygame.mixer.music.set_volume(0 if self.muted else self.settings.music_volume)
            for sound in self.effects.values():
                sound.set_volume(0 if self.muted else self.settings.sfx_volume)

    def music(self, name):
        if name == self.current:
            return
        if self.enabled:
            try:
                pygame.mixer.music.stop()
                if name is not None:
                    pygame.mixer.music.load(asset_path(MUSIC[name]))
                    pygame.mixer.music.play(0 if name == "intro" else -1)
                    if self.paused:
                        pygame.mixer.music.pause()
            except (pygame.error, OSError):
                self.enabled = False
        self.current = name

    def effect(self, name):
        if self.enabled and not self.muted and not self.paused:
            self.effects[name].play()

    def toggle_mute(self):
        self.settings.muted = not self.settings.muted
        self.apply_volumes()
        if self.enabled and self.muted:
            pygame.mixer.stop()

    def pause(self, paused):
        self.paused = paused
        if self.enabled:
            if paused:
                pygame.mixer.music.pause()
                pygame.mixer.pause()
            else:
                pygame.mixer.music.unpause()
                pygame.mixer.unpause()

    def stop_effects(self):
        if pygame.mixer.get_init():
            pygame.mixer.stop()

    def close(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.stop()
