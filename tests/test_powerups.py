"""Regression tests for Splashline Showdown powerups."""

from __future__ import annotations

import unittest

from engine.math2d import Vec2

from game.entities import build_arena
from game.input import InputState, try_fire_projectiles
from game.physics import build_ball, build_projectile
from game.powerups import ActiveEffect, PowerupPickup, PowerupKind, apply_active_effects, collect_powerups, pop_fire_modifiers
from game.scene import SplashlineScene
from game.state import PlayerId, PlayerState, TurnState


def _players():
    return (
        PlayerState(PlayerId.LEFT, Vec2(180.0, 260.0), 80.0, 420.0, 300.0),
        PlayerState(PlayerId.RIGHT, Vec2(900.0, 260.0), 680.0, 1020.0, 300.0),
    )


class PowerupTests(unittest.TestCase):
    def test_random_spawned_powerup_activates_from_ball_hit(self) -> None:
        arena = build_arena()
        left, right = _players()
        ball = build_ball(arena)
        ball.body.position.set(320.0, 240.0)
        pickups = [PowerupPickup(kind=PowerupKind.HEAVY_SHOT, position=Vec2(320.0, 240.0))]
        effects: list[ActiveEffect] = []

        collected = collect_powerups(
            ball,
            [],
            pickups,
            effects,
            PlayerId.LEFT,
            (left, right),
        )

        self.assertEqual(collected, [PowerupKind.HEAVY_SHOT])
        self.assertEqual(pickups, [])
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].owner, PlayerId.LEFT)

    def test_random_spawned_powerup_activates_from_projectile_hit(self) -> None:
        arena = build_arena()
        left, right = _players()
        ball = build_ball(arena)
        projectile = build_projectile(
            owner=PlayerId.RIGHT,
            origin=Vec2(860.0, 260.0),
            aim_world=Vec2(720.0, 260.0),
            arena=arena,
        )
        projectile.body.position.set(700.0, 250.0)
        pickups = [PowerupPickup(kind=PowerupKind.DOUBLE_SHOT, position=Vec2(700.0, 250.0))]
        effects: list[ActiveEffect] = []

        collected = collect_powerups(
            ball,
            [projectile],
            pickups,
            effects,
            PlayerId.LEFT,
            (left, right),
        )

        self.assertEqual(collected, [PowerupKind.DOUBLE_SHOT])
        self.assertEqual(pickups, [])
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0].owner, PlayerId.RIGHT)

    def test_heavy_shot_modifier_changes_projectile_mass_and_speed(self) -> None:
        arena = build_arena()
        left, right = _players()
        effects = [ActiveEffect(PowerupKind.HEAVY_SHOT, PlayerId.LEFT, 4.0)]

        modifiers = pop_fire_modifiers(effects, PlayerId.LEFT, (left, right))
        projectiles = try_fire_projectiles(
            left,
            InputState(move_axis=0.0, aim_world=Vec2(420.0, 260.0), fire_pressed=True),
            TurnState(active_player=PlayerId.LEFT, shots_left=2),
            arena,
            fire_count=modifiers.projectile_count,
            speed_scale=modifiers.speed_scale,
            mass_scale=modifiers.mass_scale,
        )

        self.assertEqual(len(projectiles), 1)
        self.assertGreater(projectiles[0].body.mass, 0.65)
        self.assertGreater(projectiles[0].body.velocity.length(), 830.0)
        self.assertEqual(effects, [])

    def test_double_shot_spawns_two_projectiles(self) -> None:
        arena = build_arena()
        left, right = _players()
        effects = [ActiveEffect(PowerupKind.DOUBLE_SHOT, PlayerId.LEFT, 4.0)]

        modifiers = pop_fire_modifiers(effects, PlayerId.LEFT, (left, right))
        projectiles = try_fire_projectiles(
            left,
            InputState(move_axis=0.0, aim_world=Vec2(420.0, 220.0), fire_pressed=True),
            TurnState(active_player=PlayerId.LEFT, shots_left=2),
            arena,
            fire_count=modifiers.projectile_count,
            speed_scale=modifiers.speed_scale,
            mass_scale=modifiers.mass_scale,
        )

        self.assertEqual(len(projectiles), 2)
        self.assertNotEqual(projectiles[0].body.velocity.y, projectiles[1].body.velocity.y)

    def test_null_wind_suppresses_force(self) -> None:
        effects = [ActiveEffect(PowerupKind.NULL_WIND, None, 5.0)]

        wind_force = apply_active_effects(effects, 140.0)

        self.assertEqual(wind_force, 0.0)

    def test_next_shot_powerup_survives_rejected_fire_on_cooldown(self) -> None:
        scene = SplashlineScene()
        scene.match.turn.cooldown_remaining = 1.0
        scene.active_effects = [ActiveEffect(PowerupKind.HEAVY_SHOT, PlayerId.LEFT, 4.0)]

        scene.step(
            InputState(move_axis=0.0, aim_world=Vec2(420.0, 260.0), fire_pressed=True),
            0.0,
        )

        self.assertEqual(len(scene.projectiles), 0)
        self.assertEqual(scene.match.turn.shots_left, 3)
        self.assertEqual([effect.kind for effect in scene.active_effects], [PowerupKind.HEAVY_SHOT])

    def test_next_shot_powerup_survives_rejected_fire_without_ammo(self) -> None:
        scene = SplashlineScene()
        scene.match.turn.shots_left = 0
        scene.active_effects = [ActiveEffect(PowerupKind.DOUBLE_SHOT, PlayerId.LEFT, 4.0)]

        scene.step(
            InputState(move_axis=0.0, aim_world=Vec2(420.0, 260.0), fire_pressed=True),
            0.0,
        )

        self.assertEqual(len(scene.projectiles), 0)
        self.assertEqual(scene.match.turn.shots_left, 0)
        self.assertEqual([effect.kind for effect in scene.active_effects], [PowerupKind.DOUBLE_SHOT])


if __name__ == "__main__":
    unittest.main()
