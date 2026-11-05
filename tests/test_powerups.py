"""Deterministic Fun coverage without opening a window or initializing SDL."""
import random
import unittest
import pygame
from src.config import STEP
from src.modes import Match, Mode
from src.powerups import Effect, Pickup, PowerUp, PowerUps, POWERUP_FILES, RESERVED_FILE


class FunTests(unittest.TestCase):
    def setUp(self):
        self.match = Match(Mode.FUN, random.Random(19))
        self.powers = self.match.powerups

    def activate(self, kind, owner=0):
        self.assertTrue(self.powers.activate(self.match, kind, owner))

    def test_fun_is_two_players_with_classic_score_limit(self):
        self.assertEqual(len(self.match.paddles), 2)
        self.match.scores[0] = 4
        self.match.ball.position.update(801, 100)
        self.match.step(0)
        self.assertTrue(self.match.finished)
        self.assertEqual(self.match.winner, 0)

    def test_seeded_spawns_are_reproducible_and_within_safe_bounds(self):
        other = Match(Mode.FUN, random.Random(19))
        for match in (self.match, other):
            match.powerups.spawn_in = 0
            match.powerups.update(match, STEP)
        self.assertEqual(self.powers.pickup, other.powerups.pickup)
        self.assertLessEqual(350, self.powers.pickup.position.x)
        self.assertLessEqual(self.powers.pickup.position.x, 450)
        self.assertLessEqual(85, self.powers.pickup.position.y)
        self.assertLessEqual(self.powers.pickup.position.y, 365)

    def test_initial_interval_is_six_to_twelve_seconds(self):
        self.assertLessEqual(6, self.powers.spawn_in)
        self.assertLessEqual(self.powers.spawn_in, 12)

    def test_no_spawn_before_interval(self):
        self.powers.update(self.match, self.powers.spawn_in - .01)
        self.assertIsNone(self.powers.pickup)
        self.powers.update(self.match, .02)
        self.assertIsNotNone(self.powers.pickup)

    def test_only_one_collectible_can_exist(self):
        self.powers.spawn_in = 0
        self.powers.update(self.match, STEP)
        pickup = self.powers.pickup
        self.match.ball.position.update(100, 100)
        for _ in range(100):
            self.powers.update(self.match, 1)
        self.assertIs(self.powers.pickup, pickup)

    def test_lightning_is_preserved_but_excluded_from_random_pool(self):
        self.assertEqual(len(PowerUp), 6)
        self.assertEqual(RESERVED_FILE, "power_up_lightning.png")
        self.assertNotIn(RESERVED_FILE, POWERUP_FILES.values())
        for _ in range(100):
            self.powers.pickup = None
            self.powers.spawn_in = 0
            self.powers.update(self.match, STEP)
            self.assertIn(self.powers.pickup.kind, tuple(PowerUp))

    def test_overlap_collection_uses_last_hitter(self):
        self.match.last_touch = 1
        self.powers.pickup = Pickup(PowerUp.GIANT, self.match.ball.position.copy())
        events = self.powers.update(self.match, 0)
        self.assertEqual(events, [("pickup", 1)])
        self.assertIsNone(self.powers.pickup)
        self.assertEqual(self.powers.active.owner, 1)
        self.assertEqual(self.match.paddles[1].rect.height, 150)

    def test_before_first_hit_collection_uses_serving_owner(self):
        self.match.serving_player = 1
        self.powers.pickup = Pickup(PowerUp.SHIELD, self.match.ball.position.copy())
        self.powers.update(self.match, 0)
        self.assertEqual(self.powers.active.owner, 1)

    def test_pickup_needs_actual_ball_overlap(self):
        self.powers.pickup = Pickup(PowerUp.GIANT, pygame.Vector2(400, 100))
        self.powers.update(self.match, 0)
        self.assertIsNone(self.powers.active)

    def test_effects_do_not_stack_or_spawn_during_active_effect(self):
        self.activate(PowerUp.GIANT)
        self.assertFalse(self.powers.activate(self.match, PowerUp.HYPERBALL, 1))
        self.powers.spawn_in = 0
        self.powers.update(self.match, 100)
        self.assertEqual(self.powers.active.kind, PowerUp.GIANT)
        self.assertIsNone(self.powers.pickup)

    def test_giant_resizes_and_restores_both_owners_in_bounds(self):
        for owner in (0, 1):
            paddle = self.match.paddles[owner]
            paddle.move(1, 300, 10)
            self.activate(PowerUp.GIANT, owner)
            self.assertEqual(paddle.rect.height, 150)
            self.assertLessEqual(paddle.rect.bottom, 450)
            self.powers.expire(self.match)
            self.assertEqual(paddle.rect.height, 100)

    def test_sabotage_affects_only_opponent_preserving_center(self):
        center = self.match.paddles[1].rect.centery
        self.activate(PowerUp.SABOTAGE)
        self.assertEqual(self.match.paddles[1].rect.height, 65)
        self.assertLessEqual(abs(self.match.paddles[1].rect.centery - center), 1)
        self.assertEqual(self.match.paddles[0].rect.height, 100)
        self.powers.expire(self.match)
        self.assertEqual(self.match.paddles[1].rect.height, 100)

    def test_hyperball_preserves_direction_and_reverses_multiplier(self):
        velocity = self.match.ball.velocity.copy()
        self.activate(PowerUp.HYPERBALL)
        self.assertEqual(self.match.ball.velocity, velocity * 1.5)
        self.powers.expire(self.match)
        self.assertEqual(self.match.ball.velocity, velocity)

    def test_hyperball_does_not_tunnel_through_paddle(self):
        self.match.ball.position.update(730, 250)
        self.match.ball.velocity.update(1000, 0)
        self.activate(PowerUp.HYPERBALL)
        events = self.match.step(.05)
        self.assertIn(("paddle", 1), events)
        self.assertEqual(self.match.scores, [0, 0])
        self.assertLess(self.match.ball.velocity.x, 0)
        self.assertIsNone(self.powers.active)

    def test_phantom_warning_then_invisibility_only_toward_opponent(self):
        self.activate(PowerUp.PHANTOM)
        self.assertTrue(self.powers.ball_visible(self.match))
        self.powers.update(self.match, .61)
        self.assertFalse(self.powers.ball_visible(self.match))
        self.match.ball.velocity.x = -100
        self.assertTrue(self.powers.ball_visible(self.match))

    def test_phantom_remains_physical_and_reappears_on_return(self):
        self.activate(PowerUp.PHANTOM)
        self.powers.active.age = 1
        self.match.ball.position.update(778, 250)
        self.match.ball.velocity.update(100, 0)
        self.match.step(0)
        self.assertLess(self.match.ball.velocity.x, 0)
        self.assertTrue(self.powers.ball_visible(self.match))
        self.assertIsNone(self.powers.active)

    def test_straight_shot_heads_toward_opponent_for_both_owners(self):
        for owner in (0, 1):
            self.activate(PowerUp.STRAIGHT, owner)
            self.assertEqual(self.match.ball.velocity.y, 0)
            self.assertGreater(self.match.ball.velocity.x * (1 if owner == 0 else -1), 0)
            self.powers.expire(self.match)
            self.assertNotEqual(self.match.ball.velocity.y, 0)

    def test_straight_return_restores_non_horizontal_motion(self):
        self.activate(PowerUp.STRAIGHT)
        self.match.ball.position.update(778, 250)
        self.match.step(0)
        self.assertLess(self.match.ball.velocity.x, 0)
        self.assertNotEqual(self.match.ball.velocity.y, 0)
        self.assertIsNone(self.powers.active)

    def test_non_shield_effects_expire_only_after_opponent_return(self):
        for kind in PowerUp:
            if kind == PowerUp.SHIELD:
                continue
            with self.subTest(kind=kind):
                self.activate(kind)
                self.powers.on_return(self.match, 0)
                self.assertIsNotNone(self.powers.active)
                self.powers.on_return(self.match, 1)
                self.assertIsNone(self.powers.active)
                self.assertGreaterEqual(self.powers.spawn_in, 6)

    def test_shield_survives_opponent_return_then_saves_without_point(self):
        for owner, x in ((0, -1), (1, 801)):
            self.activate(PowerUp.SHIELD, owner)
            self.powers.on_return(self.match, 1 - owner)
            self.assertIsNotNone(self.powers.active)
            self.match.ball.position.update(x, 100)
            self.match.ball.velocity.update(-100 if owner == 0 else 100, 0)
            events = self.match.step(0)
            self.assertIn(("shield", owner), events)
            self.assertEqual(self.match.scores, [0, 0])
            self.assertIsNone(self.powers.active)
            self.assertGreater(self.match.ball.velocity.x * (1 if owner == 0 else -1), 0)
            self.assertNotEqual(self.match.ball.velocity.y, 0)

    def test_shield_does_not_protect_opponent_and_clears_on_point(self):
        self.activate(PowerUp.SHIELD)
        self.match.ball.position.update(801, 100)
        self.match.step(0)
        self.assertEqual(self.match.scores, [1, 0])
        self.assertIsNone(self.powers.active)

    def test_every_effect_is_removed_on_rally_end(self):
        for kind in PowerUp:
            self.match = Match(Mode.FUN, random.Random(19))
            self.powers = self.match.powerups
            self.activate(kind)
            self.match.ball.position.update(801, 100)
            self.match.step(0)
            self.assertIsNone(self.powers.active)
            self.assertIsNone(self.powers.pickup)
            self.assertEqual([p.rect.height for p in self.match.paddles], [100, 100])
            self.assertEqual(self.match.ball.velocity, (100, 300))

    def test_uncollected_pickup_clears_at_rally_end(self):
        self.powers.pickup = Pickup(PowerUp.GIANT, pygame.Vector2(400, 200))
        self.match.ball.position.update(801, 100)
        self.match.step(0)
        self.assertIsNone(self.powers.pickup)
        self.assertGreaterEqual(self.powers.spawn_in, 6)

    def test_after_consumption_next_pickup_waits_for_fresh_interval(self):
        self.activate(PowerUp.SHIELD)
        self.powers.expire(self.match)
        self.powers.update(self.match, 1)
        self.assertIsNone(self.powers.pickup)

    def test_finished_matches_do_not_advance_effects(self):
        self.activate(PowerUp.PHANTOM)
        self.match.finished = True
        self.match.step(1)
        self.assertEqual(self.powers.active.age, 0)
