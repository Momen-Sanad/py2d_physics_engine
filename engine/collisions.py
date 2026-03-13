"""Basic 2D collision helpers for early rigid-body demos."""

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

    contact = circle_vs_circle(
        a_position=body_a.position,
        a_radius=body_a.radius,
        b_position=body_b.position,
        b_radius=body_b.radius,
    )
    if contact is None:
        return False

    total_inverse_mass = body_a.inverse_mass + body_b.inverse_mass
    if total_inverse_mass == 0.0:
        return False

    correction = contact.normal * (contact.penetration / total_inverse_mass)
    body_a.position = body_a.position - correction * body_a.inverse_mass
    body_b.position = body_b.position + correction * body_b.inverse_mass

    relative_velocity = body_b.velocity - body_a.velocity
    separating_velocity = relative_velocity.dot(contact.normal)
    if separating_velocity > 0.0:
        return True

    bounce = (
        min(body_a.restitution, body_b.restitution)
        if restitution is None
        else restitution
    )
    impulse_magnitude = -(1.0 + bounce) * separating_velocity / total_inverse_mass
    impulse = contact.normal * impulse_magnitude

    body_a.velocity = body_a.velocity - impulse * body_a.inverse_mass
    body_b.velocity = body_b.velocity + impulse * body_b.inverse_mass
    return True
