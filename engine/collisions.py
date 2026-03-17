"""Basic 2D collision helpers"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .math2d import Vec2


@dataclass(frozen=True, slots=True)
class Contact:
    """Collision contact data shared by simple response code."""

    normal: Vec2
    penetration: float


class CircleBodyLike(Protocol):
    """Minimal shape needed for circle-vs-circle collision resolution."""

    position: Vec2
    velocity: Vec2
    radius: float
    restitution: float

    @property
    def inverse_mass(self) -> float:
        ...

    sleeping: bool


def circle_vs_circle(
    a_position: Vec2,
    a_radius: float,
    b_position: Vec2,
    b_radius: float,
) -> Contact | None:
    delta = b_position - a_position
    distance = delta.length()
    penetration = (a_radius + b_radius) - distance
    if penetration <= 0.0:
        return None
    normal = delta.normalized() if distance > 0.0 else Vec2(1.0, 0.0)
    return Contact(normal=normal, penetration=penetration)


def circle_vs_ground(position: Vec2, radius: float, ground_y: float) -> Contact | None:
    penetration = (position.y + radius) - ground_y
    if penetration <= 0.0:
        return None
    return Contact(normal=Vec2(0.0, -1.0), penetration=penetration)


def resolve_circle_collision(
    body_a: CircleBodyLike,
    body_b: CircleBodyLike,
    restitution: float | None = None,
) -> bool:
    """Resolve overlap and velocity response for two circle bodies."""

    position_a = body_a.position
    position_b = body_b.position
    dx = position_b.x - position_a.x
    dy = position_b.y - position_a.y
    radius_sum = body_a.radius + body_b.radius
    distance_sq = dx * dx + dy * dy
    if distance_sq == 0.0:
        distance = radius_sum
        normal_x = 1.0
        normal_y = 0.0
    else:
        distance = distance_sq ** 0.5
        if distance >= radius_sum:
            return False
        inverse_distance = 1.0 / distance
        normal_x = dx * inverse_distance
        normal_y = dy * inverse_distance

    penetration = radius_sum - distance
    if penetration <= 0.0:
        return False

    inverse_mass_a = 0.0 if body_a.sleeping else body_a.inverse_mass
    inverse_mass_b = 0.0 if body_b.sleeping else body_b.inverse_mass
    total_inverse_mass = inverse_mass_a + inverse_mass_b
    if total_inverse_mass == 0.0:
        return False

    correction_scale = penetration / total_inverse_mass
    correction_x = normal_x * correction_scale
    correction_y = normal_y * correction_scale
    body_a.position.x -= correction_x * inverse_mass_a
    body_a.position.y -= correction_y * inverse_mass_a
    body_b.position.x += correction_x * inverse_mass_b
    body_b.position.y += correction_y * inverse_mass_b

    relative_velocity_x = body_b.velocity.x - body_a.velocity.x
    relative_velocity_y = body_b.velocity.y - body_a.velocity.y
    separating_velocity = relative_velocity_x * normal_x + relative_velocity_y * normal_y
    if separating_velocity > 0.0:
        return True

    bounce = (
        min(body_a.restitution, body_b.restitution)
        if restitution is None
        else restitution
    )
    impulse_magnitude = -(1.0 + bounce) * separating_velocity / total_inverse_mass
    impulse_x = normal_x * impulse_magnitude
    impulse_y = normal_y * impulse_magnitude

    body_a.velocity.x -= impulse_x * inverse_mass_a
    body_a.velocity.y -= impulse_y * inverse_mass_a
    body_b.velocity.x += impulse_x * inverse_mass_b
    body_b.velocity.y += impulse_y * inverse_mass_b
    return True
