"""Headless integration tests using real SDL assets and scripted input."""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from collections import defaultdict
import hashlib
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import pygame

from src.app import Application
from src.assets import EFFECTS, FONT, IMAGES, MUSIC, asset_path
from src.config import GAME_OVER_SECONDS, INTRO_SECONDS, PROJECT_ROOT, STEP
from src.modes import Mode
from src.navigation import Navigation, Screen, MENUS
from src.settings import Settings


def key_event(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.app = Application(settings=Settings(), persist=False)
        self.keys = defaultdict(bool)

    def tearDown(self):
        self.app.close()
        self.assertFalse(pygame.display.get_init())
        self.assertIsNone(pygame.mixer.get_init())

    def play_mode(self, mode):
        self.app.transition(mode)
        self.app.start_match()
        self.app.transition(Screen.PLAYING)

    def click(self, position):
        rect = self.app.viewport
        pos = (round(rect.x + position[0] * rect.width / 800), round(rect.y + position[1] * rect.height / 450))
        for event_type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            self.app.handle_event(pygame.event.Event(event_type, button=1, pos=pos))

    def advance(self, seconds):
        for _ in range(round(seconds / STEP) + 1):
            self.app.update(STEP, self.keys)

    def test_intro_then_menu_and_skip(self):
        self.app.draw()
        self.advance(INTRO_SECONDS)
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)
        self.app.navigation.go(Screen.INTRO)
        self.app.handle_event(key_event(pygame.K_RETURN))
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)

    def test_keyboard_reaches_every_playable_mode(self):
        routes = (
            (Screen.ONE_PLAYER, 0, Mode.AI), (Screen.ONE_PLAYER, 1, Mode.WALL),
            (Screen.TWO_PLAYER, 0, Mode.CLASSIC), (Screen.TWO_PLAYER, 1, Mode.PODER),
            (Screen.FOUR_PLAYER, 0, Mode.FOUR),
        )
        for screen, index, mode in routes:
            with self.subTest(mode=mode):
                self.app.transition(screen)
                self.app.navigation.selected = index
                self.app.handle_event(key_event(pygame.K_RETURN))
                self.assertEqual(self.app.pending_mode, mode)
                self.assertEqual(self.app.navigation.screen, Screen.PRE_MATCH)
                self.app.handle_event(key_event(pygame.K_RETURN))
                self.assertEqual(self.app.navigation.screen, Screen.COUNTDOWN)
                self.advance(3)
                self.assertEqual(self.app.match.mode, mode)
                self.assertEqual(self.app.navigation.screen, Screen.PLAYING)
                for _ in range(20):
                    self.app.update(STEP, self.keys)
                    self.app.draw()

    def test_first_mouse_click_works_before_first_draw(self):
        self.app.transition(Screen.MAIN)
        self.click(self.app.navigation.rects()[0].center)
        self.assertEqual(self.app.navigation.screen, Screen.ONE_PLAYER)

    def test_fun_is_selectable_and_neural_controls_are_not_exposed(self):
        self.app.transition(Screen.TWO_PLAYER)
        self.app.navigation.selected = 2
        self.app.handle_event(key_event(pygame.K_RETURN))
        self.assertEqual(self.app.pending_mode, Mode.FUN)
        self.assertEqual(self.app.navigation.screen, Screen.PRE_MATCH)
        self.assertFalse(any("DeepIA" in item.label for items in MENUS.values() for item in items))

    def test_empty_event_frames_do_not_repeat_menu_input(self):
        self.app.transition(Screen.MAIN)
        self.app.handle_event(key_event(pygame.K_DOWN))
        for _ in range(10):
            self.app.update(STEP, self.keys)
        self.assertEqual(self.app.navigation.selected, 1)

    def test_navigation_includes_fun_and_wraps(self):
        nav = Navigation()
        nav.go(Screen.TWO_PLAYER)
        nav.move(1)
        nav.move(1)
        self.assertEqual(nav.selected, 2)
        self.assertEqual(nav.items[2].target, Mode.FUN)
        nav.move(1)
        self.assertEqual(nav.selected, 3)
        nav.move(1)
        self.assertEqual(nav.selected, 0)
        nav.move(-1)
        self.assertEqual(nav.selected, 3)

    def test_all_menus_render_and_back_returns_to_main(self):
        for screen in (Screen.MAIN, Screen.ONE_PLAYER, Screen.TWO_PLAYER,
                       Screen.FOUR_PLAYER, Screen.OPTIONS, Screen.CREDITS):
            self.app.transition(screen)
            self.app.draw()
        self.app.handle_event(key_event(pygame.K_ESCAPE))
        self.assertEqual(self.app.navigation.screen, Screen.MAIN)

    def test_controls_move_all_four_paddles_and_escape_pauses_match(self):
        self.play_mode(Mode.FOUR)
        self.keys.update({pygame.K_a: True, pygame.K_DOWN: True, pygame.K_t: True, pygame.K_b: True})
        self.app.update(STEP, self.keys)
        for paddle, expected in zip(self.app.match.paddles, [197, 203, 370, 380]):
            self.assertAlmostEqual(paddle.position, expected)
        self.app.handle_event(key_event(pygame.K_ESCAPE))
        self.assertEqual(self.app.navigation.screen, Screen.PAUSED)
        self.assertIsNotNone(self.app.match)

    def test_poder_attack_is_connected_to_both_keys(self):
        for player, key, x in ((0, pygame.K_s, 25), (1, pygame.K_LEFT, 775)):
            self.play_mode(Mode.PODER)
            self.keys.clear()
            self.keys[key] = True
            self.app.match.paddles[player].charge = 2
            self.app.match.ball.position.update(x, 250)
            self.app.update(STEP, self.keys)
            self.assertEqual(self.app.match.paddles[player].charge, 0)
            self.assertEqual(abs(self.app.match.ball.velocity.x), 1000)

    def test_every_mode_results_wait_for_choice_without_further_scoring(self):
        for mode in Mode:
            self.play_mode(mode)
            if mode == Mode.WALL:
                self.app.match.ball.position.update(-10, 100)
            else:
                self.app.match.scores[0] = 4
                self.app.match.last_touch = 0
                self.app.match.ball.position.update(810, 100)
            self.app.update(STEP, self.keys)
            self.assertEqual(self.app.navigation.screen, Screen.GAME_OVER)
            scores = self.app.match.scores.copy()
            self.app.draw()
            self.app.update(STEP, self.keys)
            self.assertEqual(self.app.match.scores, scores)
            self.advance(GAME_OVER_SECONDS)
            self.assertEqual(self.app.navigation.screen, Screen.GAME_OVER)
            self.app.navigation.selected = 1
            self.app.handle_event(key_event(pygame.K_RETURN))
            self.assertEqual(self.app.navigation.screen, Screen.MAIN)
            self.assertIsNone(self.app.match)

    def test_score_feedback_is_nonblocking_and_quit_stays_responsive(self):
        self.play_mode(Mode.CLASSIC)
        self.app.match.ball.position.update(810, 100)
        self.app.update(STEP, self.keys)
        position = self.app.match.ball.position.copy()
        self.app.update(STEP, self.keys)
        self.assertNotEqual(self.app.match.ball.position, position)
        self.app.handle_event(pygame.event.Event(pygame.QUIT))
        self.assertFalse(self.app.running)

    def test_quit_event_works_in_every_screen(self):
        for screen in Screen:
            self.app.navigation.go(screen)
            self.app.running = True
            self.app.handle_event(pygame.event.Event(pygame.QUIT))
            self.assertFalse(self.app.running)

    def test_music_and_mute_do_not_restart_on_same_menu(self):
        self.app.transition(Screen.MAIN)
        with patch.object(pygame.mixer.music, 'load') as load:
            self.app.transition(Screen.ONE_PLAYER)
            load.assert_not_called()
        self.app.handle_event(key_event(pygame.K_m))
        self.assertTrue(self.app.audio.muted)
        self.assertEqual(pygame.mixer.music.get_volume(), 0)
        self.app.handle_event(key_event(pygame.K_m))
        self.assertFalse(self.app.audio.muted)

    def test_fixed_step_is_independent_of_frame_batch_size(self):
        positions = []
        for dt, count in ((STEP, 10), (.05, 2)):
            self.play_mode(Mode.CLASSIC)
            for _ in range(count):
                self.app.update(dt, self.keys)
            positions.append(self.app.match.ball.position.copy())
        self.assertEqual(*positions)

    def test_run_loop_processes_quit_and_close_cleans_sdl(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        self.app.run(max_frames=3)
        self.assertFalse(self.app.running)


class AssetAndEntryTests(unittest.TestCase):
    def test_every_active_asset_loads_with_real_decoders(self):
        pygame.init()
        pygame.display.set_mode((800, 450))
        try:
            for relative in set(MUSIC.values()) | set(EFFECTS.values()):
                sound = pygame.mixer.Sound(asset_path(relative))
                self.assertGreater(sound.get_length(), 0, relative)
            for relative in IMAGES.values():
                pygame.image.load(asset_path(relative))
            pygame.font.Font(asset_path(FONT), 45)
        finally:
            pygame.quit()

    def test_preserved_files_match_migration_checksums(self):
        records = json.loads((PROJECT_ROOT / 'docs/ASSET_MIGRATION.json').read_text())
        self.assertEqual(len(records), 60)
        for record in records:
            self.assertEqual(hashlib.sha256((PROJECT_ROOT / record['path']).read_bytes()).hexdigest(),
                             record['sha256'], record['path'])

    def test_all_retained_media_decode_including_unused_variants(self):
        pygame.init()
        pygame.display.set_mode((800, 450))
        try:
            records = json.loads((PROJECT_ROOT / 'docs/ASSET_MIGRATION.json').read_text())
            for record in records:
                path = PROJECT_ROOT / record['path']
                with self.subTest(path=record['path']):
                    if path.suffix in ('.wav', '.mp3', '.flac'):
                        self.assertGreater(pygame.mixer.Sound(str(path)).get_length(), 0)
                    elif path.suffix in ('.png', '.jpg'):
                        pygame.image.load(str(path))
                    elif path.suffix == '.ttf':
                        pygame.font.Font(str(path), 22)
        finally:
            pygame.quit()

    def test_entry_point_runs_offline_from_another_working_directory_and_cleans_up(self):
        code = '''
import runpy, socket, sys
from pathlib import Path
from unittest.mock import patch
import pygame
root = Path(sys.argv[1])
sys.path.insert(0, str(root))
get_events = pygame.event.get
frames = 0
def events():
    global frames
    frames += 1
    return [pygame.event.Event(pygame.QUIT)] if frames >= 3 else get_events()
with patch.object(socket.socket, 'connect', side_effect=AssertionError('Network attempted')), patch.object(socket, 'create_connection', side_effect=AssertionError('Network attempted')), patch.object(pygame.event, 'get', events):
    runpy.run_path(str(root / 'main.py'), run_name='__main__')
assert not pygame.display.get_init()
assert pygame.mixer.get_init() is None
'''
        result = subprocess.run([sys.executable, '-c', code, str(PROJECT_ROOT)], cwd=PROJECT_ROOT / 'docs',
                                env=os.environ.copy(), capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_audio_hardware_failure_still_allows_local_game(self):
        with patch.object(pygame.mixer, 'init', side_effect=pygame.error('No audio hardware')):
            app = Application(settings=Settings(), persist=False)
        try:
            self.assertFalse(app.audio.enabled)
            app.transition(Mode.CLASSIC)
            app.run(max_frames=2)
        finally:
            app.close()

    def test_main_cleans_up_after_initialization_failure(self):
        from src.app import main
        with patch('src.app.Assets', side_effect=RuntimeError('bad asset')):
            with self.assertRaisesRegex(RuntimeError, 'bad asset'):
                main()
        self.assertFalse(pygame.display.get_init())
        self.assertIsNone(pygame.mixer.get_init())

    def test_main_cleans_up_after_runtime_failure(self):
        from src.app import main
        with patch.object(Application, 'run', side_effect=RuntimeError('runtime failure')):
            with self.assertRaisesRegex(RuntimeError, 'runtime failure'):
                main()
        self.assertFalse(pygame.display.get_init())
        self.assertIsNone(pygame.mixer.get_init())
