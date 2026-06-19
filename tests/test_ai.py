"""Regression tests for Splashline Showdown CPU opponent input."""

from __future__ import annotations

import unittest

from engine.math2d import Vec2

from game.ai import CpuController
from game.entities import build_arena, build_players
from game.physics import build_ball
from game.scene import SplashlineScene
from game.state import PlayerId, TurnState


class CpuControllerTests(unittest.TestCase):
    def test_cpu_moves_toward_ball_intercept(self) -> None:
        arena = build_arena()
        _, right = build_players(arena)
        ball = build_ball(arena)
        ball.body.position.set(right.position.x - 120.0, ball.body.position.y)
        turn = TurnState(active_player=PlayerId.RIGHT, shots_left=3)
        cpu = CpuController(seed=1)

        input_state = cpu.build_input(right, ball, turn, arena, projectile_count=0, dt=0.1)

        self.assertEqual(input_state.move_axis, -1.0)

    def test_cpu_fires_when_possession_and_cooldown_allow(self) -> None:
        arena = build_arena()
        _, right = build_players(arena)
        ball = build_ball(arena)
        ball.body.position.set(arena.net_x + 90.0, ball.body.position.y)
        turn = TurnState(active_player=PlayerId.RIGHT, shots_left=3)
        cpu = CpuController(seed=2, reaction_timer=0.0)

        input_state = cpu.build_input(right, ball, turn, arena, projectile_count=0, dt=0.1)

        self.assertTrue(input_state.fire_pressed)
        self.assertGreater(cpu.reaction_timer, 0.0)

    def test_cpu_respects_cooldown_and_ammo(self) -> None:
        arena = build_arena()
        _, right = build_players(arena)
        ball = build_ball(arena)
        ball.body.position.set(arena.net_x + 90.0, ball.body.position.y)
        cpu = CpuController(seed=3, reaction_timer=0.0)

        cooldown_input = cpu.build_input(
            right,
            ball,
            TurnState(active_player=PlayerId.RIGHT, shots_left=3, cooldown_remaining=0.5),
            arena,
            projectile_count=0,
            dt=0.1,
        )
        no_ammo_input = cpu.build_input(
            right,
            ball,
            TurnState(active_player=PlayerId.RIGHT, shots_left=0),
            arena,
            projectile_count=0,
            dt=0.1,
        )

        self.assertFalse(cooldown_input.fire_pressed)
        self.assertFalse(no_ammo_input.fire_pressed)

    def test_scene_cpu_mode_is_opt_in(self) -> None:
        local_scene = SplashlineScene()
        cpu_scene = SplashlineScene(cpu_enabled=True)

        self.assertFalse(local_scene.cpu_enabled)
        self.assertIsNone(local_scene.cpu)
        self.assertTrue(cpu_scene.cpu_enabled)
        self.assertIsNotNone(cpu_scene.cpu)
        self.assertIsInstance(cpu_scene.last_cpu_input.aim_world, Vec2)


if __name__ == "__main__":
    unittest.main()
