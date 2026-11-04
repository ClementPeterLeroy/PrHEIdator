"""Deterministic checks for preserved rules and repaired collision behavior."""

import random
import unittest

import pygame

from src.collisions import bounce_paddle, bounce_walls
from src.config import STEP
from src.entities import Ball, Paddle
from src.modes import Match, Mode


class EntityTests(unittest.TestCase):
    def test_ball_moves_with_elapsed_time(self):
        ball = Ball()
        ball.move(0.5)
        self.assertEqual(ball.position, (450, 390))

    def test_ball_reset(self):
        ball = Ball()
        ball.velocity.update(-1000, 0)
        ball.reset()
        self.assertEqual(ball.position, (400, 200))
        self.assertEqual(ball.velocity, (100, 300))

    def test_vertical_paddle_clamped_at_both_boundaries(self):
        paddle = Paddle(pygame.Rect(10, 200, 10, 100), 0)
        paddle.move(-1, 300, 10)
        self.assertEqual(paddle.rect.top, 0)
        paddle.move(1, 300, 10)
        self.assertEqual(paddle.rect.bottom, 450)

    def test_horizontal_paddle_clamped_with_corner_margin(self):
        paddle = Paddle(pygame.Rect(375, 10, 100, 10), 2, True)
        paddle.move(-1, 500, 10, margin=20)
        self.assertEqual(paddle.rect.left, 20)
        paddle.move(1, 500, 10, margin=20)
        self.assertEqual(paddle.rect.right, 780)


class CollisionTests(unittest.TestCase):
    def test_wall_bounce_does_not_repeat_when_moving_away(self):
        ball = Ball()
        ball.position.y = 0
        ball.velocity.y = -300
        self.assertTrue(bounce_walls(ball))
        self.assertEqual(ball.velocity.y, 300)
        self.assertFalse(bounce_walls(ball))

    def test_bottom_wall_bounce(self):
        ball = Ball()
        ball.position.y = 450
        self.assertTrue(bounce_walls(ball))
        self.assertEqual(ball.position.y, 445)
        self.assertLess(ball.velocity.y, 0)

    def test_vertical_hit_zones_are_symmetric(self):
        for y, zone in ((210, "upper"), (250, "center"), (290, "lower")):
            velocities = []
            for player, x, vx in ((0, 22, -300), (1, 778, 300)):
                ball = Ball(pygame.Vector2(x, y), pygame.Vector2(vx, 300))
                paddle = Paddle(pygame.Rect(10 if player == 0 else 780, 200, 10, 100), player)
                self.assertEqual(bounce_paddle(ball, paddle), zone)
                velocities.append((abs(ball.velocity.x), ball.velocity.y))
                self.assertIsNone(bounce_paddle(ball, paddle))
            self.assertEqual(*velocities)

    def test_each_four_player_paddle_bounces_outward(self):
        match = Match(Mode.FOUR)
        for player, position, velocity in (
            (0, (22, 250), (-100, 300)), (1, (778, 250), (100, 300)),
            (2, (420, 22), (100, -300)), (3, (420, 428), (100, 300)),
        ):
            with self.subTest(player=player):
                ball = Ball(pygame.Vector2(position), pygame.Vector2(velocity))
                self.assertEqual(bounce_paddle(ball, match.paddles[player], False), "plain")
                self.assertIsNone(bounce_paddle(ball, match.paddles[player], False))

    def test_edge_speed_is_bounded(self):
        ball = Ball(pygame.Vector2(22, 210), pygame.Vector2(-490, 990))
        bounce_paddle(ball, Paddle(pygame.Rect(10, 200, 10, 100), 0))
        self.assertEqual(ball.velocity, (500, 1000))


class RuleTests(unittest.TestCase):
    def test_every_mode_initializes_fresh(self):
        for mode, count in ((Mode.AI, 2), (Mode.WALL, 1), (Mode.CLASSIC, 2),
                            (Mode.PODER, 2), (Mode.FOUR, 4)):
            with self.subTest(mode=mode):
                match = Match(mode)
                self.assertEqual(len(match.paddles), count)
                self.assertEqual(match.scores, [0] * count)
                self.assertFalse(match.finished)
                self.assertIsNone(match.last_touch)
                match.scores[0] = 4
                self.assertEqual(Match(mode).scores[0], 0)

    def test_no_fun_or_neural_mode_is_exposed(self):
        for name in ("Fun", "DeepIA"):
            with self.assertRaises(ValueError):
                Match(name)

    def test_classic_point_ownership_and_reset(self):
        for x, scorer in ((-1, 1), (801, 0)):
            match = Match(Mode.CLASSIC)
            match.ball.position.update(x, 100)
            events = match.step(0)
            self.assertEqual(match.scores[scorer], 1)
            self.assertIn(("point", scorer), events)
            self.assertEqual(match.ball.position, (400, 200))

    def test_five_points_end_match_and_freeze_simulation(self):
        for mode in (Mode.CLASSIC, Mode.PODER, Mode.AI, Mode.FOUR):
            match = Match(mode)
            match.scores[0] = 4
            match.last_touch = 0
            match.ball.position.update(801, 100)
            match.step(0)
            self.assertTrue(match.finished)
            self.assertEqual(match.winner, 0)
            position = match.ball.position.copy()
            self.assertEqual(match.step(1, {0: -1}), [])
            self.assertEqual(match.ball.position, position)

    def test_wall_scores_only_on_right_wall_and_has_no_five_point_limit(self):
        match = Match(Mode.WALL)
        match.scores[0] = 5
        match.ball.position.update(801, 100)
        match.step(0)
        self.assertEqual(match.scores, [6])
        self.assertLess(match.ball.velocity.x, 0)
        self.assertFalse(match.finished)

    def test_wall_miss_ends_game_immediately(self):
        match = Match(Mode.WALL)
        match.ball.position.update(-1, 100)
        match.step(0)
        self.assertTrue(match.finished)
        self.assertIsNone(match.winner)

    def test_four_player_last_touch_scores_on_any_exit(self):
        for player in range(4):
            for position in ((-1, 100), (801, 100), (100, -1), (100, 451)):
                with self.subTest(player=player, position=position):
                    match = Match(Mode.FOUR)
                    match.last_touch = player
                    match.ball.position.update(position)
                    match.step(0)
                    self.assertEqual(match.scores[player], 1)
                    self.assertIsNone(match.last_touch)

    def test_four_player_exit_before_first_hit_awards_nobody(self):
        match = Match(Mode.FOUR)
        match.ball.position.update(801, 100)
        match.step(0)
        self.assertEqual(match.scores, [0, 0, 0, 0])

    def test_ai_moves_only_after_detection_threshold_and_stays_in_bounds(self):
        match = Match(Mode.AI, random.Random(7))
        match.ball.position.update(100, 0)
        match.move_players({}, STEP)
        self.assertEqual(match.paddles[1].rect.y, 200)
        match.ball.position.x = 750
        match.move_players({}, STEP)
        self.assertEqual(match.paddles[1].rect.y, 196)
        match.move_players({}, 100)
        self.assertEqual(match.paddles[1].rect.y, 0)

    def test_ai_integral_replacement_matches_numerical_legacy_formula(self):
        from math import exp, pi, sqrt
        seed = 17
        rng = random.Random(seed)
        value = abs(rng.random() - rng.random())
        dx = value / 2000
        density = lambda x: exp(-0.5 * ((x - .1) / .4) ** 2) / (.4 * sqrt(2 * pi))
        integral = sum((density(i * dx) + density((i + 1) * dx)) * .5 * dx for i in range(2000))
        self.assertEqual(Match(Mode.AI, random.Random(seed))._next_ai_detection(),
                         min(round(integral, 2) + .15, .95))


class PoderTests(unittest.TestCase):
    def test_center_hits_charge_to_two_and_edge_hits_do_not(self):
        match = Match(Mode.PODER)
        for y, expected in ((210, 0), (250, 1), (250, 2), (250, 2)):
            match.ball.position.update(22, y)
            match.ball.velocity.update(-100, 300)
            match.step(0)
            self.assertEqual(match.paddles[0].charge, expected)

    def test_both_attacks_require_charge_proximity_and_alignment(self):
        for player in (0, 1):
            match = Match(Mode.PODER)
            paddle = match.paddles[player]
            self.assertFalse(match.attack(player))
            paddle.charge = 2
            self.assertFalse(match.attack(player))
            match.ball.position.update(25 if player == 0 else 775, 150)
            self.assertFalse(match.attack(player))
            match.ball.position.y = 250
            self.assertTrue(match.attack(player))
            self.assertEqual(match.ball.velocity, (1000 if player == 0 else -1000, 0))
            self.assertEqual(paddle.charge, 0)
            self.assertFalse(match.attack(player))

    def test_point_clears_only_losing_players_charge(self):
        match = Match(Mode.PODER)
        for paddle in match.paddles:
            paddle.charge = 2
        match.ball.position.update(801, 100)
        match.step(0)
        self.assertEqual([p.charge for p in match.paddles], [2, 0])

    def test_attack_cannot_tunnel_through_opponent_at_fixed_step(self):
        match = Match(Mode.PODER)
        match.paddles[0].charge = 2
        match.ball.position.update(25, 250)
        self.assertTrue(match.attack(0))
        for _ in range(100):
            events = match.step(STEP)
            if ("paddle", 1) in events:
                break
        else:
            self.fail("Special attack missed the aligned opponent")
        self.assertLess(match.ball.velocity.x, 0)
        self.assertEqual(match.scores, [0, 0])
