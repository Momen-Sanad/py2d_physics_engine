"""Particle data structures shared by particles, springs, and PBD."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

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
            self.force.x += applied_force.x
            self.force.y += applied_force.y

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

        inverse_mass = self.inverse_mass
        gravity_x = 0.0 if gravity is None else gravity.x
        gravity_y = 0.0 if gravity is None else gravity.y

        velocity = self.velocity
        force = self.force
        position = self.position

        velocity.x += (gravity_x + force.x * inverse_mass) * dt
        velocity.y += (gravity_y + force.y * inverse_mass) * dt

        if linear_damping > 0.0:
            damping_factor = max(0.0, 1.0 - linear_damping * dt)
            velocity.x *= damping_factor
            velocity.y *= damping_factor

        position.x += velocity.x * dt
        position.y += velocity.y * dt
        self.clear_forces()

    def clear_forces(self) -> None:
        self.force.reset()


def step_particles(
    particles: Iterable[Particle],
    dt: float,
    gravity: Vec2 | None = None,
    linear_damping: float = 0.0,
) -> None:
    """Advance many particles with minimal temporary allocations."""

    gravity_x = 0.0 if gravity is None else gravity.x
    gravity_y = 0.0 if gravity is None else gravity.y
    damping_factor = max(0.0, 1.0 - linear_damping * dt) if linear_damping > 0.0 else 1.0
    use_damping = linear_damping > 0.0

    for particle in particles:
        particle.lifetime = None if particle.lifetime is None else particle.lifetime - dt
        if particle.pinned:
            particle.force.reset()
            continue

        inverse_mass = particle.inverse_mass
        velocity = particle.velocity
        force = particle.force
        position = particle.position

        velocity.x += (gravity_x + force.x * inverse_mass) * dt
        velocity.y += (gravity_y + force.y * inverse_mass) * dt

        if use_damping:
            velocity.x *= damping_factor
            velocity.y *= damping_factor

        position.x += velocity.x * dt
        position.y += velocity.y * dt
        force.reset()
