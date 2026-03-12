"""Mass-spring primitives and force helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2


@dataclass(frozen=True, slots=True)
class Spring:
    """Connects two particles in a spring network."""

    a_index: int
    b_index: int
    rest_length: float
    stiffness: float
    damping: float


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
    spring_term = -stiffness * (distance - rest_length)
    damping_term = -damping * relative_velocity.dot(direction)
    force = direction * (spring_term + damping_term)
    return force, force * -1.0
