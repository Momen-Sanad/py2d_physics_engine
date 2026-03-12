"""Particle data structures shared by particles, springs, and PBD."""

from __future__ import annotations

from dataclasses import dataclass, field

from .math2d import Vec2


@dataclass(slots=True)
class Particle:
    """Point-mass particle with accumulated forces."""

    position: Vec2
    velocity: Vec2 = field(default_factory=Vec2)
    force: Vec2 = field(default_factory=Vec2)
    mass: float = 1.0
    lifetime: float | None = None
    pinned: bool = False

    @property
    def inverse_mass(self) -> float:
        if self.pinned or self.mass == 0.0:
            return 0.0
        return 1.0 / self.mass

    def apply_force(self, applied_force: Vec2) -> None:
        if not self.pinned:
            self.force += applied_force

    def clear_forces(self) -> None:
        self.force = Vec2()
