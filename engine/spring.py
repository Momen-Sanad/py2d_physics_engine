"""Mass-spring primitives and force helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2
from .particle import Particle


@dataclass(slots=True)
class Spring:
    """Connects two particles in a spring network."""

    particle_a: Particle
    particle_b: Particle
    rest_length: float
    stiffness: float
    damping: float

    @classmethod
    def between(
        cls,
        particle_a: Particle,
        particle_b: Particle,
        stiffness: float,
        damping: float = 0.0,
        rest_length: float | None = None,
    ) -> "Spring":
        natural_length = (
            particle_a.position.distance_to(particle_b.position)
            if rest_length is None
            else rest_length
        )
        return cls(particle_a, particle_b, natural_length, stiffness, damping)

    def length(self) -> float:
        return self.particle_a.position.distance_to(self.particle_b.position)

    def force(self) -> tuple[Vec2, Vec2]:
        return spring_force(
            a_position=self.particle_a.position,
            a_velocity=self.particle_a.velocity,
            b_position=self.particle_b.position,
            b_velocity=self.particle_b.velocity,
            rest_length=self.rest_length,
            stiffness=self.stiffness,
            damping=self.damping,
        )

    def normal(self) -> Vec2:
        edge = self.particle_b.position - self.particle_a.position
        if edge.length() == 0.0:
            return Vec2()
        return Vec2(edge.y, -edge.x).normalized()

    def apply(self) -> None:
        force_a, force_b = self.force()
        self.particle_a.apply_force(force_a)
        self.particle_b.apply_force(force_b)


def spring_force(
    a_position: Vec2,
    a_velocity: Vec2,
    b_position: Vec2,
    b_velocity: Vec2,
    rest_length: float,
    stiffness: float,
    damping: float,
) -> tuple[Vec2, Vec2]:
    """Return equal and opposite spring forces for two endpoints."""

    delta = b_position - a_position
    distance = delta.length()
    if distance == 0.0:
        return Vec2(), Vec2()

    direction = delta / distance
    relative_velocity = b_velocity - a_velocity
    spring_term = stiffness * (distance - rest_length)
    damping_term = damping * relative_velocity.dot(direction)
    force_on_a = direction * (spring_term + damping_term)
    return force_on_a, -force_on_a
