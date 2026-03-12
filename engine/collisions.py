"""Basic 2D collision helpers for early rigid-body demos."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2


@dataclass(frozen=True, slots=True)
class Contact:
    """Collision contact data shared by simple response code."""

    normal: Vec2
    penetration: float


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
