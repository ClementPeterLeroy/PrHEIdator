"""Credits layout, presentation boundaries and retained menu input."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest
from unittest.mock import patch
import pygame

from src.app import Application
from src.modes import Mode
from src.navigation import Screen
from src.settings import Settings


class MenuRefinementTests(unittest.TestCase):
    def setUp(self):
        self.app = Application(audio=False, settings=Settings(), persist=False)

    def tearDown(self):
        self.app.close()

    def rendered_text(self):
        with patch.object(self.app.renderer, "text", wraps=self.app.renderer.text) as draw:
            self.app.draw()
        return [call.args for call in draw.call_args_list]

    def test_general_menus_omit_persistent_hints_and_keep_version(self):
        forbidden = ("UP / DOWN", "UP/DOWN", "MOUSE TO SELECT", "LOCAL PLAY.",
                     "ARCADE RENAISSANCE", "LEFT / RIGHT: volume")
        for screen in (Screen.MAIN, Screen.ONE_PLAYER, Screen.TWO_PLAYER,
                       Screen.FOUR_PLAYER, Screen.OPTIONS, Screen.CREDITS):
            with self.subTest(screen=screen):
                self.app.transition(screen)
                texts = [str(args[0]) for args in self.rendered_text()]
                self.assertIn("v2.1", texts)
                self.assertFalse(any(phrase in text for phrase in forbidden for text in texts))

    def test_credits_content_fits_opaque_panel_and_back_is_below(self):
        expected = {"ORIGINAL PROJECT", "HEI School Project",
                    "Original concept and foundational development",
                    "CURRENT DEVELOPMENT", "Peter Clement LEROY",
                    "Game design, redevelopment and programming",
                    "VISUAL IDENTITY", "Original Predator branding"}
        for size in ((800, 450), (1120, 630), (600, 800)):
            self.app._set_display(size)
            self.app.transition(Screen.CREDITS)
            calls = self.rendered_text()
            texts = {args[0] for args in calls}
            self.assertTrue(expected <= texts)
            self.assertFalse(any(phrase in text for text in texts for phrase in
                                 ("Codex", "owner-directed", "docs/", "migration")))
            rects = []
            for text, font_size, color, position, *rest in calls:
                if text in expected:
                    rect = self.app.assets.fonts[font_size].render(text, True, color).get_rect(topleft=position)
                    self.assertTrue(pygame.Rect(424, 100, 320, 228).contains(rect), text)
                    rects.append(rect)
            for i, rect in enumerate(rects):
                self.assertFalse(any(rect.colliderect(other) for other in rects[i + 1:]))
            self.assertGreater(self.app.navigation.rects()[0].top, 344)
            # The grid is masked by a solid panel under the lowest text section.
            self.assertEqual(self.app.screen.get_at((418, 330))[:3], (17, 23, 43))

    def test_credits_back_works_with_keyboard_and_scaled_mouse(self):
        self.app.transition(Screen.CREDITS)
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)
        for size in ((800, 450), (600, 800)):
            self.app._set_display(size)
            self.app.transition(Screen.CREDITS)
            center = self.app.navigation.rects()[0].center
            viewport = self.app.viewport
            pos = (round(viewport.x + center[0] * viewport.width / 800),
                   round(viewport.y + center[1] * viewport.height / 450))
            for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self.app.handle_event(pygame.event.Event(kind, button=1, pos=pos))
            self.assertEqual(self.app.navigation.screen, Screen.MAIN)

    def test_pre_match_retains_player_and_special_controls(self):
        for mode in Mode:
            self.app.transition(mode)
            texts = [args[0] for args in self.rendered_text()]
            self.assertIn("A / Q", texts)
            self.assertIn("ESC: PAUSE     M: MUTE     F11: DISPLAY", texts)
            if mode == Mode.PODER:
                self.assertIn("ATTACK: S", texts)
                self.assertIn("ATTACK: LEFT", texts)
            if mode == Mode.FOUR:
                self.assertIn("T / Y", texts)
                self.assertIn("V / B", texts)
