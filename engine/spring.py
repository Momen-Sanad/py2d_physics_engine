"""Mass-spring primitives and force helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Iterable

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
        if rest_length is None:
            dx = particle_b.position.x - particle_a.position.x
            dy = particle_b.position.y - particle_a.position.y
            natural_length = hypot(dx, dy)
        else:
            natural_length = rest_length
        return cls(particle_a, particle_b, natural_length, stiffness, damping)

    def length(self) -> float:
        dx = self.particle_b.position.x - self.particle_a.position.x
        dy = self.particle_b.position.y - self.particle_a.position.y
        return hypot(dx, dy)

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
        dx = self.particle_b.position.x - self.particle_a.position.x
        dy = self.particle_b.position.y - self.particle_a.position.y
        distance = hypot(dx, dy)
        if distance == 0.0:
            return Vec2()
        inverse_distance = 1.0 / distance
        return Vec2(dy * inverse_distance, -dx * inverse_distance)

    def apply(self) -> None:
        particle_a = self.particle_a
        particle_b = self.particle_b
        dx = particle_b.position.x - particle_a.position.x
        dy = particle_b.position.y - particle_a.position.y
        distance_sq = dx * dx + dy * dy
        if distance_sq == 0.0:
            return

        distance = hypot(dx, dy)
        inverse_distance = 1.0 / distance
        normal_x = dx * inverse_distance
        normal_y = dy * inverse_distance

        relative_velocity_x = particle_b.velocity.x - particle_a.velocity.x
        relative_velocity_y = particle_b.velocity.y - particle_a.velocity.y
        spring_term = self.stiffness * (distance - self.rest_length)
        damping_term = self.damping * (
            relative_velocity_x * normal_x + relative_velocity_y * normal_y
        )
        force_x = normal_x * (spring_term + damping_term)
        force_y = normal_y * (spring_term + damping_term)

        particle_a.force.x += force_x
        particle_a.force.y += force_y
        particle_b.force.x -= force_x
        particle_b.force.y -= force_y


def apply_springs(springs: Iterable[Spring]) -> None:
    """Apply spring forces with a flat loop to reduce Python call overhead."""

    for spring in springs:
        spring.apply()


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
