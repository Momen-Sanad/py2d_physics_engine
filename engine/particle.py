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
    radius: float = 4.0
    lifetime: float | None = None
    pinned: bool = False
    restitution: float = 0.9

    @property
    def inverse_mass(self) -> float:
        if self.pinned or self.mass == 0.0:
            return 0.0
        return 1.0 / self.mass

    def apply_force(self, applied_force: Vec2) -> None:
        if not self.pinned:
            self.force += applied_force

    def step(
        self,
        dt: float,
        gravity: Vec2 | None = None,
        linear_damping: float = 0.0,
    ) -> None:
        """Advance the particle by one timestep."""

        self.lifetime = None if self.lifetime is None else self.lifetime - dt
        if self.pinned:
            self.clear_forces()
            return

        gravity_force = gravity if gravity is not None else Vec2()
        acceleration = gravity_force + self.force * self.inverse_mass
        self.velocity = self.velocity + acceleration * dt

        if linear_damping > 0.0:
            damping_factor = max(0.0, 1.0 - linear_damping * dt)
            self.velocity = self.velocity * damping_factor

        self.position = self.position + self.velocity * dt
        self.clear_forces()

    def clear_forces(self) -> None:
        self.force = Vec2()
