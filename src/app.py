"""One responsive application loop: input, fixed simulation, audio, drawing."""

import pygame

from .assets import Assets
from .audio import Audio
from .config import (ATTACK_KEYS, CONTROLS, FLASH_SECONDS, FPS, GAME_OVER_SECONDS,
                     GRAY, HEIGHT, INTRO_SECONDS, MAX_FRAME_TIME, PLAYER_COLORS,
                     STEP, WHITE, WIDTH)
from .modes import Match, Mode
from .navigation import Navigation, Screen
from .rendering import Renderer


class Application:
    def __init__(self, audio=True):
        # Initialize only the subsystems used by the local game. Missing audio
        # hardware may disable sound; missing or corrupt assets still raise.
        pygame.display.init()
        pygame.font.init()
        if audio:
            try:
                pygame.mixer.init()
            except pygame.error:
                audio = False
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("PrHEIdator - Game Rebirth")
        self.assets = Assets()
        self.audio = Audio(audio)
        self.renderer = Renderer(self.screen, self.assets)
        self.navigation = Navigation()
        self.clock = pygame.time.Clock()
        self.running = True
        self.match = None
        self.elapsed = 0
        self.state_time = 0
        self.accumulator = 0
        self.flash = None
        self.flash_time = 0
        self.audio.music("intro")

    def transition(self, target):
        if isinstance(target, Mode):
            self.match = Match(target)
            self.navigation.go(Screen.PLAYING)
            self.audio.music(target)
        else:
            self.navigation.go(target)
            if target == Screen.GAME_OVER:
                self.audio.music(None)
                self.audio.effect("game_over")
            elif target in (Screen.MAIN, Screen.ONE_PLAYER, Screen.TWO_PLAYER,
                            Screen.FOUR_PLAYER, Screen.OPTIONS, Screen.CREDITS):
                self.audio.music("menu")
                self.match = None
        self.state_time = 0
        self.accumulator = 0
        self.flash = None
        self.flash_time = 0

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                self.audio.toggle_mute()
                return
            if event.key == pygame.K_ESCAPE:
                if self.navigation.screen == Screen.MAIN:
                    self.running = False
                else:
                    self.transition(Screen.MAIN)
                return
            if self.navigation.screen == Screen.INTRO and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.transition(Screen.MAIN)
                return
            if self.navigation.screen == Screen.GAME_OVER and event.key == pygame.K_RETURN:
                self.transition(Screen.MAIN)
                return
        target = self.navigation.handle(event, self.assets.fonts[45])
        if target == "quit":
            self.running = False
        elif target is not None:
            self.transition(target)

    def _feedback(self, events):
        for name, player in events:
            sound = ("plus" if name == "point" and self.match.mode == Mode.AI and player == 0 else name)
            self.audio.effect(sound)
            if name == "point":
                self.flash = PLAYER_COLORS[player]
            elif name == "speed":
                self.flash = WHITE
            elif name == "paddle":
                self.flash = WHITE if self.match.mode == Mode.FOUR else GRAY
            else:
                continue
            self.flash_time = FLASH_SECONDS

    def update(self, dt, keys=None):
        dt = max(0, min(dt, MAX_FRAME_TIME))
        self.elapsed += dt
        self.state_time += dt
        screen = self.navigation.screen
        if screen == Screen.INTRO:
            if self.state_time >= INTRO_SECONDS:
                self.transition(Screen.MAIN)
        elif screen == Screen.GAME_OVER:
            if self.state_time >= GAME_OVER_SECONDS:
                self.transition(Screen.MAIN)
        elif screen == Screen.PLAYING:
            keys = pygame.key.get_pressed() if keys is None else keys
            directions = {i: int(bool(keys[positive])) - int(bool(keys[negative]))
                          for i, (negative, positive) in enumerate(CONTROLS)}
            attacks = [i for i, key in enumerate(ATTACK_KEYS) if keys[key]]
            # Legacy collision flashes paused movement for 150 ms. Keep that
            # pause while still polling events and rendering every frame.
            if self.flash_time > 0:
                self.flash_time = max(0, self.flash_time - dt)
                if not self.flash_time:
                    self.flash = None
                return
            self.accumulator += dt
            while self.accumulator + 1e-9 >= STEP:
                self.accumulator = max(0, self.accumulator - STEP)
                self._feedback(self.match.step(STEP, directions, attacks))
                if self.match.finished:
                    self.transition(Screen.GAME_OVER)
                    break
                if self.flash_time:
                    self.accumulator = 0
                    break

    def draw(self):
        screen = self.navigation.screen
        if screen == Screen.INTRO:
            self.renderer.intro(self.state_time)
        elif screen in (Screen.PLAYING, Screen.GAME_OVER):
            self.renderer.match(self.match, self.flash, self.elapsed,
                                self.state_time if screen == Screen.GAME_OVER else None)
        else:
            self.renderer.menu(self.navigation)
        pygame.display.flip()

    def run(self, max_frames=None):
        """Optional frame bound supports smoke tests without a second loop."""
        frames = 0
        while self.running and (max_frames is None or frames < max_frames):
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                self.handle_event(event)
                if not self.running:
                    break
            if not self.running:
                break
            self.update(dt)
            self.draw()
            frames += 1

    def close(self):
        self.running = False
        self.audio.close()
        pygame.quit()


def main():
    app = None
    try:
        app = Application()
        app.run()
    finally:
        if app is not None:
            app.close()
        else:
            pygame.quit()
