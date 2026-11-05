"""v2.1 integration: lifecycle, scaled input, settings, audio and previews."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from collections import defaultdict
from dataclasses import asdict
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
import pygame

from src.app import Application
from src.config import PLAYER_COLORS, PROJECT_ROOT, STEP
from src.modes import Mode
from src.navigation import MENUS, Screen, mode_parent
from src.powerups import PowerUp
from src.settings import Settings


def key(code, repeat=False):
    return pygame.event.Event(pygame.KEYDOWN, key=code, repeat=repeat)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.app = Application(settings=Settings(), persist=False)
        self.keys = defaultdict(bool)

    def tearDown(self):
        self.app.close()

    def ready(self, mode):
        self.app.transition(mode)
        self.app.start_match()
        self.app.transition(Screen.PLAYING)

    def advance(self, seconds):
        for _ in range(round(seconds / STEP)):
            self.app.update(STEP, self.keys)

    def click(self, logical):
        rect = self.app.viewport
        pos = (round(rect.x + logical[0] * rect.width / 800), round(rect.y + logical[1] * rect.height / 450))
        for kind in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.app.handle_event(pygame.event.Event(kind, button=1, pos=pos))

    def test_all_six_home_actions_route_correctly(self):
        self.assertEqual([item.label for item in MENUS[Screen.MAIN]],
                         ["SOLO", "VERSUS", "FREE-FOR-ALL", "OPTIONS", "CREDITS", "EXIT"])
        for index, target in enumerate((Screen.ONE_PLAYER, Screen.TWO_PLAYER, Screen.FOUR_PLAYER,
                                        Screen.OPTIONS, Screen.CREDITS, "quit")):
            self.app.transition(Screen.MAIN)
            self.app.navigation.selected = index
            self.app.handle_event(key(pygame.K_RETURN))
            if target == "quit":
                self.assertFalse(self.app.running)
            else:
                self.assertEqual(self.app.navigation.screen, target)

    def test_briefing_and_back_exist_for_every_mode(self):
        for mode in Mode:
            self.app.transition(mode)
            self.assertIsNone(self.app.match)
            self.assertEqual(self.app.navigation.screen, Screen.PRE_MATCH)
            self.app.draw()
            self.app.handle_event(key(pygame.K_ESCAPE))
            self.assertEqual(self.app.navigation.screen, mode_parent(mode))

    def test_countdown_freezes_every_mode_until_three_seconds(self):
        for mode in Mode:
            self.app.transition(mode)
            self.app.handle_event(key(pygame.K_RETURN))
            match = self.app.match
            ball = match.ball.position.copy()
            spawn = match.powerups.spawn_in if match.powerups else None
            self.keys[pygame.K_a] = True
            self.advance(2.9)
            self.assertEqual(self.app.navigation.screen, Screen.COUNTDOWN)
            self.assertEqual(match.ball.position, ball)
            self.assertEqual(match.paddles[0].position, 200)
            if match.powerups:
                self.assertEqual(match.powerups.spawn_in, spawn)
            self.advance(.12)
            self.assertEqual(self.app.navigation.screen, Screen.PLAYING)

    def test_every_mode_pause_freezes_gameplay_and_resumes_without_catchup(self):
        for mode in Mode:
            self.ready(mode)
            match = self.app.match
            self.app.handle_event(key(pygame.K_ESCAPE))
            self.assertEqual(self.app.navigation.screen, Screen.PAUSED)
            snapshot = (match.ball.position.copy(), [p.position for p in match.paddles], match.play_time, match.scores.copy())
            self.keys[pygame.K_a] = True
            self.advance(2)
            self.app.draw()
            self.assertEqual(snapshot, (match.ball.position, [p.position for p in match.paddles], match.play_time, match.scores))
            self.app.handle_event(key(pygame.K_ESCAPE))
            self.assertEqual(self.app.navigation.screen, Screen.PLAYING)
            self.app.update(STEP, self.keys)
            self.assertAlmostEqual(match.play_time, STEP)
            self.assertLess((match.ball.position - snapshot[0]).length(), 5)

    def test_paused_fun_freezes_spawn_and_effect_duration(self):
        for effect in (None, PowerUp.PHANTOM):
            self.ready(Mode.FUN)
            powers = self.app.match.powerups
            if effect:
                powers.activate(self.app.match, effect, 0)
            self.app.pause()
            spawn = powers.spawn_in
            self.advance(2)
            self.assertEqual(powers.spawn_in, spawn)
            if effect:
                self.assertEqual(powers.active.age, 0)
            self.assertIsNone(powers.pickup)

    def test_restart_from_pause_resets_every_mode_then_counts_down(self):
        for mode in Mode:
            self.ready(mode)
            old = self.app.match
            old.scores[0] = 3
            old.paddles[0].charge = 2
            old.last_touch = 0
            if old.powerups:
                old.powerups.activate(old, PowerUp.GIANT, 0)
            self.app.pause()
            self.app.navigation.selected = 1
            self.app.handle_event(key(pygame.K_RETURN))
            match = self.app.match
            self.assertIsNot(match, old)
            self.assertEqual(self.app.navigation.screen, Screen.COUNTDOWN)
            self.assertEqual(match.scores, [0] * len(match.paddles))
            self.assertEqual(match.ball.position, (400, 240))
            self.assertEqual(match.paddles[0].charge, 0)
            self.assertEqual(match.paddles[0].rect.height, 100)
            self.assertIsNone(match.last_touch)
            if match.powerups:
                self.assertIsNone(match.powerups.active)
                self.assertIsNone(match.powerups.pickup)

    def test_main_menu_from_pause_drops_match_and_game_audio(self):
        self.ready(Mode.FUN)
        self.app.pause()
        self.app.navigation.selected = 2
        self.app.handle_event(key(pygame.K_RETURN))
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)
        self.assertIsNone(self.app.match)
        self.assertFalse(self.app.audio.paused)
        self.assertEqual(self.app.audio.current, "menu")

    def test_results_play_again_resets_every_mode(self):
        for mode in Mode:
            self.ready(mode)
            self.app.match.finished = True
            self.app.match.winner = None if mode == Mode.WALL else 0
            self.app.transition(Screen.GAME_OVER)
            self.app.draw()
            self.app.handle_event(key(pygame.K_RETURN))
            self.assertEqual(self.app.navigation.screen, Screen.COUNTDOWN)
            self.assertFalse(self.app.match.finished)
            self.assertEqual(sum(self.app.match.scores), 0)

    def test_focus_loss_pauses_match(self):
        self.ready(Mode.CLASSIC)
        self.app.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertEqual(self.app.navigation.screen, Screen.PAUSED)

    def test_pause_during_countdown_preserves_remaining_time(self):
        self.app.transition(Mode.FUN)
        self.app.start_match()
        self.advance(1)
        self.app.handle_event(key(pygame.K_ESCAPE))
        self.advance(5)
        self.app.handle_event(key(pygame.K_ESCAPE))
        self.assertEqual(self.app.navigation.screen, Screen.COUNTDOWN)
        self.assertAlmostEqual(self.app.state_time, 1)

    def test_scaled_mouse_alignment_and_letterbox_at_multiple_sizes(self):
        for size in ((800, 450), (1200, 700), (600, 800)):
            self.app._set_display(size)
            self.app.transition(Screen.MAIN)
            self.click(self.app.navigation.rects()[1].center)
            self.assertEqual(self.app.navigation.screen, Screen.TWO_PLAYER)
            rect = self.app.viewport
            self.assertAlmostEqual(rect.width / rect.height, 16 / 9, delta=.01)
            if rect.y:
                self.assertIsNone(self.app.to_logical((10, 0)))

    def test_resize_event_recomputes_viewport(self):
        self.app.handle_event(pygame.event.Event(pygame.VIDEORESIZE, size=(1000, 700), w=1000, h=700))
        self.assertEqual(self.app.window.get_size(), (1000, 700))
        self.assertGreater(self.app.viewport.y, 0)

    def test_hover_and_keyboard_selection_are_consistent(self):
        self.app.transition(Screen.MAIN)
        rect = self.app.viewport
        target = self.app.navigation.rects()[2].center
        position = (round(target[0] * rect.width / 800), round(target[1] * rect.height / 450))
        self.app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=position, rel=(1, 1), buttons=(0, 0, 0)))
        self.assertEqual(self.app.navigation.selected, 2)
        self.app.handle_event(key(pygame.K_DOWN))
        self.assertEqual(self.app.navigation.selected, 3)
        self.assertIsNone(self.app.navigation.hover)

    def test_mouse_activation_requires_matching_press_release(self):
        self.app.transition(Screen.MAIN)
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(700, 180)))
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)

    def test_key_repeats_do_not_reactivate_menu_or_pause(self):
        self.app.transition(Screen.MAIN)
        self.app.handle_event(key(pygame.K_RETURN, repeat=True))
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)
        self.ready(Mode.CLASSIC)
        self.app.handle_event(key(pygame.K_ESCAPE))
        self.app.handle_event(key(pygame.K_ESCAPE, repeat=True))
        self.assertEqual(self.app.navigation.screen, Screen.PAUSED)

    def test_options_keyboard_changes_actual_music_and_sfx_volume(self):
        self.app.transition(Screen.OPTIONS)
        self.app.handle_event(key(pygame.K_LEFT))
        self.assertAlmostEqual(self.app.settings.music_volume, .6)
        self.assertAlmostEqual(pygame.mixer.music.get_volume(), .6, delta=.01)
        self.app.navigation.selected = 1
        self.app.handle_event(key(pygame.K_RIGHT))
        self.assertAlmostEqual(self.app.settings.sfx_volume, .9)
        self.assertAlmostEqual(self.app.audio.effects['paddle'].get_volume(), .9, delta=.01)

    def test_volume_slider_click_changes_real_volume(self):
        self.app.transition(Screen.OPTIONS)
        rect = self.app.navigation.rects()[0]
        self.click((rect.x + 238, rect.centery))
        self.assertAlmostEqual(self.app.settings.music_volume, .5)
        self.assertAlmostEqual(pygame.mixer.music.get_volume(), .5, delta=.01)

    def test_options_mute_reduced_flash_and_fullscreen_are_functional(self):
        self.app.option("mute")
        self.assertTrue(self.app.settings.muted)
        self.assertEqual(self.app.audio.effects['paddle'].get_volume(), 0)
        self.app.option("reduced_flash")
        self.assertTrue(self.app.settings.reduced_flash)
        self.app.option("fullscreen")
        self.assertTrue(self.app.settings.fullscreen)
        self.app.option("fullscreen")
        self.assertFalse(self.app.settings.fullscreen)

    def test_audio_lifecycle_pauses_resumes_and_clears_on_restart(self):
        self.ready(Mode.FUN)
        self.assertEqual(self.app.audio.current, Mode.FUN)
        self.app.pause()
        self.assertTrue(self.app.audio.paused)
        self.app.resume()
        self.assertFalse(self.app.audio.paused)
        self.app.start_match()
        self.assertIsNone(self.app.audio.current)
        self.advance(3.02)
        self.assertEqual(self.app.audio.current, Mode.FUN)

    def test_rendering_reuses_loaded_resources(self):
        self.app.transition(Screen.MAIN)
        with patch.object(pygame.image, 'load', side_effect=AssertionError('image reloaded')):
            self.app.draw()
            self.app.draw()

    def test_free_for_all_scoreboard_does_not_hide_top_paddle(self):
        self.ready(Mode.FOUR)
        self.app.draw()
        self.assertEqual(self.app.screen.get_at((420, 15))[:3], PLAYER_COLORS[2])

    def test_credited_screens_and_every_gameplay_overlay_render(self):
        for mode in Mode:
            self.ready(mode)
            self.app.draw()
            self.app.pause()
            self.app.draw()
            self.app.resume()
            self.app.match.winner = None if mode == Mode.WALL else 0
            self.app.transition(Screen.GAME_OVER)
            self.app.draw()
        self.app.transition(Screen.CREDITS)
        self.app.draw()

    def test_audio_decoder_failure_degrades_gracefully(self):
        from src.audio import Audio
        with patch.object(pygame.mixer, 'Sound', side_effect=pygame.error('decoder failure')):
            audio = Audio(True, Settings())
        self.assertFalse(audio.enabled)


class SettingsTests(unittest.TestCase):
    def test_settings_save_and_reload_roundtrip(self):
        directory = PROJECT_ROOT / '.diagnostics'
        directory.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=directory, suffix='.json', delete=False) as handle:
            path = Path(handle.name)
        try:
            original = Settings(.2, .4, True, False, True)
            self.assertTrue(original.save(path))
            self.assertEqual(asdict(Settings.load(path)), asdict(original))
        finally:
            path.unlink(missing_ok=True)

    def test_corrupt_or_invalid_preferences_fall_back_safely(self):
        for content in ('broken', '[]', '{"music_volume": 99, "muted": "yes"}'):
            with patch.object(Path, 'read_text', return_value=content):
                self.assertEqual(Settings.load(), Settings())

    def test_save_permission_error_does_not_crash(self):
        with patch.object(Path, 'mkdir', side_effect=PermissionError('read only')):
            self.assertFalse(Settings().save())
