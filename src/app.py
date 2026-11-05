"""One event loop with fixed simulation and explicit match lifecycle screens."""
import pygame
from .assets import Assets
from .audio import Audio
from .config import (ATTACK_KEYS, CONTROLS, COUNTDOWN_SECONDS, FPS, HEIGHT,
                     INTRO_SECONDS, MAX_FRAME_TIME, STEP, WIDTH)
from .modes import Match, Mode
from .navigation import Navigation, Screen, mode_parent
from .rendering import Renderer
from .settings import Settings


class Application:
    def __init__(self, audio=True, settings=None, persist=True, settings_file=None):
        pygame.display.init()
        pygame.font.init()
        if audio:
            try:
                pygame.mixer.init()
            except pygame.error:
                audio = False
        self.settings_file = settings_file
        self.settings = settings if settings is not None else Settings.load(settings_file)
        self.persist = persist
        self.settings_saved = True
        self.window_size = (1120, 630)
        self.window = None
        self._set_display()
        self.screen = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Predator - v2.1 - Arcade Renaissance")
        self.assets = Assets()
        self.audio = Audio(audio, self.settings)
        self.renderer = Renderer(self.screen, self.assets)
        self.navigation = Navigation()
        self.clock = pygame.time.Clock()
        self.running = True
        self.match = None
        self.pending_mode = None
        self.elapsed = 0
        self.state_time = 0
        self.accumulator = 0
        self.feedback = []
        self._resume_screen = Screen.PLAYING
        self._resume_time = 0
        self.audio.music("intro")

    def _set_display(self, size=None):
        if size is not None:
            self.window_size = (max(400, size[0]), max(225, size[1]))
        try:
            self.window = pygame.display.set_mode((0, 0) if self.settings.fullscreen else self.window_size,
                                                 pygame.FULLSCREEN if self.settings.fullscreen else pygame.RESIZABLE)
        except pygame.error:
            self.settings.fullscreen = False
            self.window = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)

    @property
    def viewport(self):
        width, height = self.window.get_size()
        scale = min(width / WIDTH, height / HEIGHT)
        size = (max(1, round(WIDTH * scale)), max(1, round(HEIGHT * scale)))
        return pygame.Rect((width - size[0]) // 2, (height - size[1]) // 2, *size)

    def to_logical(self, position):
        rect = self.viewport
        if not rect.collidepoint(position):
            return None
        return ((position[0] - rect.x) * WIDTH / rect.width,
                (position[1] - rect.y) * HEIGHT / rect.height)

    def save_settings(self):
        if self.persist:
            self.settings_saved = self.settings.save(self.settings_file)

    def transition(self, target):
        if isinstance(target, Mode):
            self.pending_mode = target
            self.match = None
            target = Screen.PRE_MATCH
        self.navigation.go(target)
        self.state_time = 0
        self.accumulator = 0
        self.feedback.clear()
        if target == Screen.GAME_OVER:
            self.audio.stop_effects()
            self.audio.pause(False)
            self.audio.music(None)
            self.audio.effect("game_over")
        elif target == Screen.PLAYING:
            self.audio.pause(False)
            self.audio.music(self.match.mode)
        elif target == Screen.COUNTDOWN:
            self.audio.stop_effects()
            self.audio.pause(False)
            self.audio.music(None)
        elif target not in (Screen.PAUSED, Screen.INTRO):
            self.audio.stop_effects()
            self.audio.pause(False)
            self.audio.music("menu")
            if target != Screen.PRE_MATCH:
                self.pending_mode = None
            self.match = None

    def start_match(self):
        if self.pending_mode is None:
            return
        self.match = Match(self.pending_mode)
        self.transition(Screen.COUNTDOWN)

    def pause(self):
        self._resume_screen = self.navigation.screen
        self._resume_time = self.state_time
        self.navigation.go(Screen.PAUSED)
        self.accumulator = 0
        self.audio.pause(True)

    def resume(self):
        self.navigation.go(self._resume_screen)
        self.state_time = self._resume_time
        self.accumulator = 0
        self.audio.pause(False)

    def back(self):
        screen = self.navigation.screen
        if screen == Screen.PAUSED:
            self.resume()
        elif screen in (Screen.PLAYING, Screen.COUNTDOWN):
            self.pause()
        elif screen == Screen.PRE_MATCH:
            self.transition(mode_parent(self.pending_mode))
        elif screen == Screen.MAIN:
            self.running = False
        else:
            self.transition(Screen.MAIN)

    def option(self, name, direction=1):
        if name in ("music_volume", "sfx_volume"):
            value = getattr(self.settings, name)
            setattr(self.settings, name, round(max(0, min(1, value + direction * .1)), 1))
            self.audio.apply_volumes()
            if name == "sfx_volume":
                self.audio.effect("paddle")
        elif name == "mute":
            self.audio.toggle_mute()
        elif name == "fullscreen":
            self.settings.fullscreen = not self.settings.fullscreen
            self._set_display()
        elif name == "reduced_flash":
            self.settings.reduced_flash = not self.settings.reduced_flash
        self.save_settings()

    def activate(self, target):
        if target == "quit":
            self.running = False
        elif target == "play" or target == "restart":
            self.start_match()
        elif target == "resume":
            self.resume()
        elif target == "back":
            self.back()
        elif isinstance(target, str):
            self.option(target)
        elif target is not None:
            self.transition(target)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.VIDEORESIZE and not self.settings.fullscreen:
            self._set_display(event.size)
            return
        if event.type == pygame.WINDOWFOCUSLOST and self.navigation.screen in (Screen.PLAYING, Screen.COUNTDOWN):
            self.pause()
            return
        if event.type == pygame.KEYDOWN:
            if getattr(event, "repeat", False):
                return
            if event.key == pygame.K_m:
                self.option("mute")
                return
            if event.key == pygame.K_F11:
                self.option("fullscreen")
                return
            if event.key == pygame.K_ESCAPE:
                self.back()
                return
            if self.navigation.screen == Screen.INTRO and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.transition(Screen.MAIN)
                return
            if self.navigation.screen == Screen.OPTIONS and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                target = self.navigation.items[self.navigation.selected].target
                if target in ("music_volume", "sfx_volume"):
                    self.option(target, -1 if event.key == pygame.K_LEFT else 1)
                return
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            # Hitboxes are always in logical coordinates; letterbox clicks miss.
            position = self.to_logical(event.pos)
            event = pygame.event.Event(event.type, {**event.dict, "pos": position or (-1, -1)})
            if self.navigation.screen == Screen.OPTIONS and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for i, rect in enumerate(self.navigation.rects()[:2]):
                    if position and rect.collidepoint(position) and self.navigation.pressed == i:
                        value = round(max(0, min(1, (position[0] - (rect.x + 178)) / 120)), 1)
                        setattr(self.settings, self.navigation.items[i].target, value)
                        self.audio.apply_volumes()
                        self.save_settings()
                        self.navigation.pressed = None
                        return
        self.activate(self.navigation.handle(event))

    def _feedback(self, events):
        for name, player in events:
            sound = "plus" if name == "point" and self.match.mode == Mode.AI and player == 0 else name
            self.audio.effect(sound)
            self.feedback.append([name, player, .4])
        self.feedback = self.feedback[-8:]

    def update(self, dt, keys=None):
        dt = max(0, min(dt, MAX_FRAME_TIME))
        self.elapsed += dt
        screen = self.navigation.screen
        self.renderer.animate(self.navigation, dt, self.settings.reduced_flash)
        if screen == Screen.PAUSED:
            return
        self.state_time += dt
        if screen == Screen.INTRO and self.state_time >= INTRO_SECONDS:
            self.transition(Screen.MAIN)
        elif screen == Screen.COUNTDOWN:
            if self.state_time >= COUNTDOWN_SECONDS:
                self.transition(Screen.PLAYING)
        elif screen == Screen.PLAYING:
            keys = pygame.key.get_pressed() if keys is None else keys
            directions = {i: int(bool(keys[positive])) - int(bool(keys[negative]))
                          for i, (negative, positive) in enumerate(CONTROLS)}
            attacks = [i for i, key in enumerate(ATTACK_KEYS) if keys[key]]
            self.feedback = [[name, player, life - dt] for name, player, life in self.feedback if life > dt]
            self.accumulator += dt
            while self.accumulator + 1e-9 >= STEP:
                self.accumulator = max(0, self.accumulator - STEP)
                self._feedback(self.match.step(STEP, directions, attacks))
                if self.match.finished:
                    self.transition(Screen.GAME_OVER)
                    break

    def draw(self):
        self.renderer.draw(self)
        rect = self.viewport
        self.window.fill((0, 0, 0))
        self.window.blit(pygame.transform.smoothscale(self.screen, rect.size), rect)
        pygame.display.flip()

    def run(self, max_frames=None):
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
