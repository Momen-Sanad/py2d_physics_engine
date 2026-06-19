"""Simple CPU opponent input for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from engine.math2d import Vec2

from . import config
from .entities import Arena, Ball
from .input import InputState, can_fire_projectile
from .state import PlayerState, TurnState


@dataclass(slots=True)
class CpuController:
    """Deterministic right-side controller for single-player matches."""

    seed: int = 33
    reaction_timer: float = 0.45
    rng: Random = field(init=False)

    def __post_init__(self) -> None:
        self.rng = Random(self.seed)

    def reset(self) -> None:
        """Reset reaction timing for a fresh match."""

        self.reaction_timer = 0.45
        self.rng.seed(self.seed)

    def build_input(
        self,
        player: PlayerState,
        ball: Ball,
        turn: TurnState,
        arena: Arena,
        projectile_count: int,
        dt: float,
    ) -> InputState:
        """Return the CPU's desired movement, aim, and fire state."""

        target_x = _clamp(
            ball.body.position.x + ball.body.velocity.x * 0.22,
            player.movement_min_x,
            player.movement_max_x,
        )
        dead_zone = 14.0
        move_axis = 0.0
        if target_x < player.position.x - dead_zone:
            move_axis = -1.0
        elif target_x > player.position.x + dead_zone:
            move_axis = 1.0

        aim_world = Vec2(
            ball.body.position.x + self.rng.uniform(-8.0, 8.0),
            ball.body.position.y + self.rng.uniform(-6.0, 6.0),
        )
        self.reaction_timer = max(0.0, self.reaction_timer - dt)

        projectile_budget = config.MAX_PROJECTILES - projectile_count
        candidate = InputState(move_axis=move_axis, aim_world=aim_world, fire_pressed=True)
        ready_to_fire = (
            self.reaction_timer <= 0.0
            and can_fire_projectile(candidate, turn, projectile_budget)
            and ball.body.position.x > arena.net_x - 120.0
        )
        if ready_to_fire:
            self.reaction_timer = self.rng.uniform(0.42, 0.74)
            return candidate

        return InputState(move_axis=move_axis, aim_world=aim_world, fire_pressed=False)


def _clamp(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)
