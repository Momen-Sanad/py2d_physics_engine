"""Regression tests for Splashline Showdown gameplay physics glue."""

from __future__ import annotations

import unittest

from engine.broadphase import SpatialHashGrid
from engine.math2d import Vec2

from game import config
from game.effects import update_drip_intensity
from game.entities import build_arena
from game.input import InputState, check_turn_cross_net, should_sync_turn_to_ball_side
from game.physics import build_ball, build_projectile, resolve_arena_bounds, resolve_projectile_collisions, update_ball_side
from game.scene import SplashlineScene
from game.state import PlayerId


class GamePhysicsTests(unittest.TestCase):
    def test_projectile_cleanup_removes_expired_projectiles(self) -> None:
        arena = build_arena()
        projectile = build_projectile(
            owner=PlayerId.LEFT,
            origin=Vec2(120.0, 200.0),
            aim_world=Vec2(240.0, 200.0),
            arena=arena,
        )
        projectile.lifetime = 0.01
        ball = build_ball(arena)
        projectiles = [projectile]

        resolve_arena_bounds(ball, projectiles, arena, dt=0.02)

        self.assertEqual(projectiles, [])

    def test_turn_cross_net_detects_single_direction_crossing(self) -> None:
        self.assertTrue(check_turn_cross_net(PlayerId.LEFT, PlayerId.LEFT, PlayerId.RIGHT))
        self.assertTrue(check_turn_cross_net(PlayerId.RIGHT, PlayerId.RIGHT, PlayerId.LEFT))
        self.assertFalse(check_turn_cross_net(PlayerId.RIGHT, PlayerId.LEFT, PlayerId.LEFT))

    def test_turn_sync_corrects_side_mismatch_once_ball_is_clearly_in_half(self) -> None:
        self.assertTrue(
            should_sync_turn_to_ball_side(
                PlayerId.LEFT,
                PlayerId.RIGHT,
                ball_x=620.0,
                net_x=550.0,
                settle_distance=30.0,
            )
        )
        self.assertFalse(
            should_sync_turn_to_ball_side(
                PlayerId.LEFT,
                PlayerId.RIGHT,
                ball_x=566.0,
                net_x=550.0,
                settle_distance=30.0,
            )
        )
        self.assertFalse(
            should_sync_turn_to_ball_side(
                PlayerId.RIGHT,
                PlayerId.RIGHT,
                ball_x=700.0,
                net_x=550.0,
                settle_distance=30.0,
            )
        )

    def test_ball_projectile_collision_reports_impact(self) -> None:
        arena = build_arena()
        ball = build_ball(arena)
        ball.body.position.set(300.0, 220.0)
        projectile = build_projectile(
            owner=PlayerId.LEFT,
            origin=Vec2(220.0, 220.0),
            aim_world=Vec2(420.0, 220.0),
            arena=arena,
        )
        projectile.body.position.set(ball.body.position.x - ball.body.radius - projectile.body.radius + 2.0, 220.0)
        projectile.body.velocity.set(320.0, 0.0)

        impact_speed = resolve_projectile_collisions(
            ball,
            [projectile],
            SpatialHashGrid(cell_size=64.0),
        )

        self.assertGreater(impact_speed, 0.0)
        self.assertGreater(ball.body.velocity.length_squared(), 0.0)

    def test_update_ball_side_uses_previous_side_as_center_fallback(self) -> None:
        arena = build_arena()
        ball = build_ball(arena)
        ball.last_side = PlayerId.RIGHT
        ball.body.position.x = arena.net_x

        previous_side, current_side = update_ball_side(ball, arena)

        self.assertEqual(previous_side, PlayerId.RIGHT)
        self.assertEqual(current_side, PlayerId.RIGHT)

    def test_drip_intensity_increases_then_clamps(self) -> None:
        arena = build_arena()
        ball = build_ball(arena)
        ball.drip_intensity = 0.2

        update_drip_intensity(ball, impact_speed=500.0, dt=0.0)
        self.assertGreater(ball.drip_intensity, 0.2)

        ball.drip_intensity = 0.99
        update_drip_intensity(ball, impact_speed=900.0, dt=0.0)
        self.assertLessEqual(ball.drip_intensity, 1.0)

    def test_final_shot_waits_for_cross_before_refill(self) -> None:
        scene = SplashlineScene()
        scene.ball.body.position.set(scene.arena.net_x - 150.0, scene.arena.serve_y)
        scene.ball.last_side = PlayerId.LEFT
        scene.match.turn.active_player = PlayerId.LEFT
        scene.match.turn.shots_left = 1
        scene.match.turn.cooldown_remaining = 0.0
        scene.allow_turn_side_sync = True

        scene.step(
            InputState(
                move_axis=0.0,
                aim_world=Vec2(scene.arena.net_x - 60.0, scene.arena.serve_y),
                fire_pressed=True,
            ),
            config.FIXED_DT,
        )

        self.assertEqual(scene.match.turn.active_player, PlayerId.LEFT)
        self.assertEqual(scene.match.turn.shots_left, 0)
        self.assertTrue(scene.match.turn.awaiting_cross)

    def test_ball_crossing_refills_waiting_opponent(self) -> None:
        scene = SplashlineScene()
        scene.wind.current_force_x = 0.0
        scene.ball.body.position.set(scene.arena.net_x + 80.0, scene.arena.serve_y)
        scene.ball.body.velocity.reset()
        scene.ball.last_side = PlayerId.LEFT
        scene.match.turn.active_player = PlayerId.LEFT
        scene.match.turn.shots_left = 0
        scene.match.turn.awaiting_cross = True
        scene.allow_turn_side_sync = False

        scene.step(
            InputState(
                move_axis=0.0,
                aim_world=Vec2(scene.arena.net_x, scene.arena.serve_y),
                fire_pressed=False,
            ),
            config.FIXED_DT,
        )

        self.assertEqual(scene.match.turn.active_player, PlayerId.RIGHT)
        self.assertEqual(scene.match.turn.shots_left, config.SHOTS_PER_TURN)
        self.assertFalse(scene.match.turn.awaiting_cross)

    def test_out_of_ammo_failsafe_switches_control(self) -> None:
        scene = SplashlineScene()
        scene.wind.current_force_x = 0.0
        scene.ball.body.position.set(scene.arena.net_x - 150.0, scene.arena.serve_y)
        scene.ball.body.velocity.reset()
        scene.ball.last_side = PlayerId.LEFT
        scene.match.turn.active_player = PlayerId.LEFT
        scene.match.turn.shots_left = 0
        scene.match.turn.awaiting_cross = True
        scene.match.turn.out_of_ammo_timer = config.OUT_OF_AMMO_TURN_FAILSAFE
        scene.allow_turn_side_sync = False

        scene.step(
            InputState(
                move_axis=0.0,
                aim_world=Vec2(scene.arena.net_x, scene.arena.serve_y),
                fire_pressed=False,
            ),
            config.FIXED_DT,
        )

        self.assertEqual(scene.match.turn.active_player, PlayerId.RIGHT)
        self.assertEqual(scene.match.turn.shots_left, config.SHOTS_PER_TURN)
        self.assertFalse(scene.match.turn.awaiting_cross)

    def test_match_over_feedback_queues_victory_and_confetti_once(self) -> None:
        scene = SplashlineScene()

        scene.queue_match_over_audio()
        first_events = scene.drain_audio_events()
        scene.queue_match_over_audio()

        self.assertEqual(first_events, ["match_over", "victory"])
        self.assertEqual(scene.emitter.particles, [])
        self.assertEqual(scene.drain_audio_events(), [])

    def test_cpu_control_syncs_back_when_ball_settles_on_human_side(self) -> None:
        scene = SplashlineScene(cpu_enabled=True)
        scene.wind.current_force_x = 0.0
        scene.ball.body.position.set(scene.arena.net_x - 120.0, scene.arena.serve_y)
        scene.ball.body.velocity.reset()
        scene.ball.last_side = PlayerId.LEFT
        scene.match.turn.active_player = PlayerId.RIGHT
        scene.match.turn.shots_left = config.SHOTS_PER_TURN
        scene.allow_turn_side_sync = False
        scene.turn_side_sync_guard = 0.0

        scene.step(
            InputState(
                move_axis=0.0,
                aim_world=Vec2(scene.arena.net_x, scene.arena.serve_y),
                fire_pressed=False,
            ),
            config.FIXED_DT,
        )

        self.assertEqual(scene.match.turn.active_player, PlayerId.LEFT)

    def test_side_sync_guard_prevents_immediate_turn_bounce(self) -> None:
        scene = SplashlineScene(cpu_enabled=True)
        scene.wind.current_force_x = 0.0
        scene.ball.body.position.set(scene.arena.net_x - 120.0, scene.arena.serve_y)
        scene.ball.body.velocity.reset()
        scene.ball.last_side = PlayerId.LEFT
        scene.match.turn.active_player = PlayerId.RIGHT
        scene.allow_turn_side_sync = False
        scene.turn_side_sync_guard = config.TURN_SIDE_SYNC_GUARD

        scene.step(
            InputState(
                move_axis=0.0,
                aim_world=Vec2(scene.arena.net_x, scene.arena.serve_y),
                fire_pressed=False,
            ),
            config.FIXED_DT,
        )

        self.assertEqual(scene.match.turn.active_player, PlayerId.RIGHT)


if __name__ == "__main__":
    unittest.main()
