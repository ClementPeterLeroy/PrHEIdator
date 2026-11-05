"""Cached arcade backdrop, shared buttons and lightweight gameplay effects."""
from functools import lru_cache
from math import sin
import pygame
from .config import (BACKGROUND, CYAN, HEIGHT, MUTED_TEXT, PANEL, PLAYER_COLORS,
                     PURPLE, TEXT, WHITE, WIDTH)
from .modes import Mode
from .navigation import Screen
from .powerups import PowerUp
from .ui.buttons import draw_button
from .ui.menus import MODE_RULES, player_controls
from .ui.overlays import overlay


class Renderer:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.hover_levels = [0] * 6
        self.backdrop = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            pygame.draw.line(self.backdrop, (8 + int(t * 6), 11 + int(t * 3), 25 + int(t * 14)), (0, y), (WIDTH, y))
        for x in range(-400, 1201, 100):
            pygame.draw.line(self.backdrop, (30, 25, 57), (400 + (x - 400) * .15, 285), (x, HEIGHT))
        for y in (292, 307, 330, 365, 415):
            pygame.draw.line(self.backdrop, (30, 25, 57), (0, y), (WIDTH, y))

    @lru_cache(maxsize=256)
    def _text(self, value, size, color):
        return self.assets.fonts[size].render(str(value), True, color)

    def text(self, value, size, color, pos, center=False):
        surface = self._text(str(value), size, tuple(color))
        rect = surface.get_rect(center=pos) if center else surface.get_rect(topleft=pos)
        self.screen.blit(surface, rect)

    def animate(self, navigation, dt, reduced=False):
        for i in range(6):
            target = 1 if navigation.selected == i else 0
            # A brief easing transition never changes the actual hitboxes.
            self.hover_levels[i] += (target - self.hover_levels[i]) * min(1, dt * (40 if reduced else 12))

    def panel(self, rect, color=PURPLE):
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, color, rect, 1, border_radius=8)

    def branding(self, elapsed=0, reduced=False):
        pulse = 0 if reduced else 3 * sin(elapsed * 1.5)
        center = (204, 217)
        pygame.draw.circle(self.screen, (29, 30, 65), center, round(110 + pulse), 1)
        pygame.draw.circle(self.screen, (25, 58, 77), center, 98, 1)
        pygame.draw.line(self.screen, CYAN, (54, 108), (126, 108), 2)
        pygame.draw.line(self.screen, PURPLE, (278, 326), (350, 326), 2)
        logo = self.assets.images["logo"]
        self.screen.blit(logo, logo.get_rect(center=center))
        self.text("PREDATOR", 56, TEXT, (204, 351), True)

    def buttons(self, app):
        navigation = app.navigation
        for i, (item, rect) in enumerate(zip(navigation.items, navigation.rects())):
            label = item.label
            if navigation.screen == Screen.OPTIONS:
                labels = {
                    "music_volume": "MUSIC", "sfx_volume": "SOUND EFFECTS",
                    "mute": "MUTE   " + ("ON" if app.settings.muted else "OFF"),
                    "fullscreen": "DISPLAY   " + ("FULLSCREEN" if app.settings.fullscreen else "WINDOWED"),
                    "reduced_flash": "REDUCED FLASH   " + ("ON" if app.settings.reduced_flash else "OFF"),
                }
                label = labels.get(item.target, label)
            is_slider = navigation.screen == Screen.OPTIONS and i < 2
            draw_button(self.screen, rect, "" if is_slider else label,
                        self.assets.fonts[22 if navigation.screen == Screen.OPTIONS else 24],
                        i == navigation.selected, self.hover_levels[i], i == navigation.pressed,
                        not (navigation.screen == Screen.MAIN and i >= 3))
            if is_slider:
                self.text(label, 18, TEXT, (rect.x + 12, rect.y + 7))
                value = getattr(app.settings, item.target)
                track = pygame.Rect(rect.x + 178, rect.y + 16, 120, 6)
                pygame.draw.rect(self.screen, (44, 56, 82), track, border_radius=3)
                pygame.draw.rect(self.screen, CYAN, (track.x, track.y, round(120 * value), 6), border_radius=3)
                pygame.draw.circle(self.screen, TEXT, (track.x + round(120 * value), track.centery), 5)
                self.text(f"{value:.0%}", 16, MUTED_TEXT, (rect.x + 12, rect.y + 23))

    def menu(self, app):
        navigation = app.navigation
        self.screen.blit(self.backdrop, (0, 0))
        self.branding(app.elapsed, app.settings.reduced_flash)
        titles = {Screen.MAIN: "ENTER THE ARENA", Screen.ONE_PLAYER: "SOLO",
                  Screen.TWO_PLAYER: "VERSUS", Screen.FOUR_PLAYER: "FREE-FOR-ALL",
                  Screen.OPTIONS: "OPTIONS", Screen.CREDITS: "CREDITS"}
        if navigation.screen == Screen.CREDITS:
            self.panel(pygame.Rect(408, 48, 352, 296), (47, 62, 88))
        self.text(titles[navigation.screen], 28, TEXT, (424, 62))
        self.buttons(app)
        if navigation.screen == Screen.CREDITS:
            self.credits()
        if navigation.screen == Screen.OPTIONS:
            if not app.settings_saved:
                self.text("Settings apply now; local save unavailable.", 16, CYAN, (424, 411))
        self.text("v2.1", 18, CYAN, (709, 427))

    def credits(self):
        sections = (
            ("ORIGINAL PROJECT", "HEI School Project",
             "Original concept and foundational development"),
            ("CURRENT DEVELOPMENT", "Peter Clement LEROY",
             "Game design, redevelopment and programming"),
            ("VISUAL IDENTITY", "Original Predator branding", None),
        )
        for i, (heading, name, description) in enumerate(sections):
            y = 110 + i * 84
            self.text(heading, 18, CYAN, (424, y))
            self.text(name, 24, TEXT, (424, y + 24))
            if description:
                self.text(description, 16, MUTED_TEXT, (424, y + 48))

    def pre_match(self, app):
        self.screen.blit(self.backdrop, (0, 0))
        mode = app.pending_mode
        self.text("MATCH BRIEFING", 18, CYAN, (44, 30))
        self.text(mode.value, 48, TEXT, (44, 57))
        for i, line in enumerate(MODE_RULES[mode]):
            self.text(line, 24, MUTED_TEXT, (44, 111 + i * 26))
        controls = player_controls(mode)
        for i, role, keys, attack in controls:
            rect = pygame.Rect(44 + i * 181, 183, 165, 144)
            color = PLAYER_COLORS[i]
            self.panel(rect, color)
            self.text(f"PLAYER {i + 1} / {role}", 18, color, (rect.x + 13, rect.y + 14))
            paddle = pygame.Rect(rect.x + 16, rect.y + 50, 7, 45)
            if i >= 2:
                paddle.size = (45, 7)
            pygame.draw.rect(self.screen, color, paddle, border_radius=3)
            key_position = (rect.x + 16, rect.y + 75) if i >= 2 else (rect.x + 35, rect.y + 56)
            self.text(keys, 24, TEXT, key_position)
            self.text("ATTACK: " + attack if attack else "MOVE PADDLE", 18, MUTED_TEXT, (rect.x + 13, rect.y + 114))
        if mode == Mode.AI:
            self.panel(pygame.Rect(225, 183, 165, 144), PLAYER_COLORS[1])
            self.text("COMPUTER / RIGHT", 18, PLAYER_COLORS[1], (238, 197))
            self.text("TRACKING BOT", 22, TEXT, (238, 244))
        if mode == Mode.FUN:
            self.text("SIX RALLY MODIFIERS", 18, CYAN, (424, 186))
            for i, kind in enumerate(PowerUp):
                x, y = 424 + (i % 2) * 170, 216 + (i // 2) * 36
                self.screen.blit(self.assets.powerups[kind], (x, y - 5))
                self.text(kind.value, 18, TEXT, (x + 33, y + 2))
            self.text("Expires on return. Shield saves once.", 16, MUTED_TEXT, (424, 324))
        self.text("ESC: PAUSE     M: MUTE     F11: DISPLAY", 18, MUTED_TEXT, (44, 341))
        self.buttons(app)

    def arena(self, app):
        match = app.match
        self.screen.fill(BACKGROUND)
        pygame.draw.rect(self.screen, (38, 54, 77), (4, 4, 792, 442), 1, border_radius=4)
        if match.mode != Mode.FOUR:
            for y in range(70, 430, 22):
                pygame.draw.line(self.screen, (25, 40, 59), (400, y), (400, y + 8))
            pygame.draw.circle(self.screen, (25, 40, 59), (400, 225), 47, 1)
        for paddle in match.paddles:
            color = PLAYER_COLORS[paddle.player]
            pygame.draw.rect(self.screen, tuple(c // 4 for c in color), paddle.rect.inflate(6, 6), border_radius=4)
            pygame.draw.rect(self.screen, color, paddle.rect, border_radius=3)
            if match.mode == Mode.PODER:
                x = 28 if paddle.player == 0 else 716
                for charge in range(2):
                    rect = pygame.Rect(x + charge * 28, 414, 22, 6)
                    pygame.draw.rect(self.screen, color if charge < paddle.charge else (40, 48, 67), rect, border_radius=2)
                self.text("READY" if paddle.charge == 2 else "CHARGE", 16, color, (x, 397))
        count = len(match.scores)
        start = (WIDTH - count * 86) // 2
        score_y = 44 if match.mode == Mode.FOUR else 10
        for i, score in enumerate(match.scores):
            rect = pygame.Rect(start + i * 86, score_y, 78, 42)
            self.panel(rect, (41, 53, 75))
            self.text("P" + str(i + 1), 16, PLAYER_COLORS[i], (rect.x + 10, score_y + 13))
            self.text(score, 36, TEXT, (rect.x + 53, score_y + 22), True)
        self.text(match.mode.value, 16, MUTED_TEXT, (28, 20))
        self.text("ESC PAUSE", 16, MUTED_TEXT, (706, 20))
        powers = match.powerups
        visible = not powers or powers.ball_visible(match)
        if visible:
            color = WHITE
            if powers and powers.active:
                color = PLAYER_COLORS[powers.active.owner]
            position = match.ball.position
            if not app.settings.reduced_flash:
                direction = match.ball.velocity.normalize() if match.ball.velocity.length_squared() else pygame.Vector2()
                for index in (3, 2, 1):
                    pygame.draw.circle(self.screen, tuple(c // (index + 3) for c in color),
                                       position - direction * index * 6, max(1, 5 - index))
                pygame.draw.circle(self.screen, tuple(c // 4 for c in color), position, 9)
            pygame.draw.circle(self.screen, color, position, match.ball.radius)
        if powers:
            if powers.pickup:
                pickup = powers.pickup
                rect = pickup.rect
                self.panel(rect.inflate(8, 8), CYAN)
                self.screen.blit(self.assets.powerups[pickup.kind], rect.move(2, 2))
            if powers.active:
                effect = powers.active
                color = PLAYER_COLORS[effect.owner]
                self.text(f"P{effect.owner + 1}  {effect.kind.value.upper()}", 18, color, (280, 425))
                if effect.kind == PowerUp.SHIELD:
                    x = 5 if effect.owner == 0 else 793
                    pygame.draw.line(self.screen, color, (x, 60), (x, 390), 3)
                if effect.kind == PowerUp.PHANTOM and effect.age < .6:
                    self.text("PHANTOM INCOMING", 20, CYAN, (400, 77), True)
                if effect.kind == PowerUp.STRAIGHT:
                    x = round(match.ball.position.x)
                    pygame.draw.line(self.screen, color, (x - 14, round(match.ball.position.y)), (x + 14, round(match.ball.position.y)), 1)
        if not app.settings.reduced_flash:
            for name, player, life in app.feedback:
                if player is not None:
                    color = PLAYER_COLORS[player]
                    if name in ("pickup", "shield", "attack", "point"):
                        label = {"pickup": "POWER UP", "shield": "SAVED", "attack": "PODER!", "point": "+1"}[name]
                        self.text(label, 28, color, (140 if player == 0 else 660, 110), True)
                    elif name in ("paddle", "speed"):
                        paddle = match.paddles[player]
                        pygame.draw.rect(self.screen, color, paddle.rect.inflate(10, 10), 1, border_radius=5)
                elif name == "wall":
                    pygame.draw.line(self.screen, CYAN, (370, 5), (430, 5), 2)

    def draw(self, app):
        state = app.navigation.screen
        if state == Screen.INTRO:
            self.screen.blit(self.backdrop, (0, 0))
            self.branding(app.elapsed, app.settings.reduced_flash)
            self.text("WELCOME TO THE ARENA", 28, CYAN, (570, 170), True)
            self.text("THE RALLY BEGINS AGAIN", 22, TEXT, (570, 215), True)
            self.text("ENTER / SPACE TO CONTINUE", 18, MUTED_TEXT, (570, 295), True)
        elif state == Screen.PRE_MATCH:
            self.pre_match(app)
        elif state in (Screen.PLAYING, Screen.COUNTDOWN, Screen.PAUSED, Screen.GAME_OVER):
            self.arena(app)
            if state != Screen.PLAYING:
                overlay(self.screen)
                if state == Screen.COUNTDOWN:
                    self.text("GET READY", 32, TEXT, (400, 128), True)
                    self.text(max(1, 3 - int(app.state_time)), 96, CYAN, (400, 230), True)
                    self.text(app.match.mode.value, 22, MUTED_TEXT, (400, 330), True)
                elif state == Screen.PAUSED:
                    self.text("PAUSED", 48, CYAN, (400, 128), True)
                    self.text("RALLY FROZEN / ESC TO RESUME", 18, MUTED_TEXT, (400, 175), True)
                    self.buttons(app)
                else:
                    title = "RUN COMPLETE" if app.match.mode == Mode.WALL else f"PLAYER {app.match.winner + 1} WINS"
                    self.text(title, 36, CYAN, (400, 128), True)
                    self.text("FINAL SCORE   " + " : ".join(map(str, app.match.scores)), 24, TEXT, (400, 175), True)
                    self.buttons(app)
        else:
            self.menu(app)
