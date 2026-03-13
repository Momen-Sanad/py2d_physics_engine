"""Small 2D math helpers used throughout the engine."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, sin


@dataclass(slots=True)
class Vec2:
    """Mutable 2D vector with helpers for hot-path in-place math."""

    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vec2":
        return self * scalar

    def __neg__(self) -> "Vec2":
        return Vec2(-self.x, -self.y)

    def __iadd__(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: "Vec2") -> "Vec2":
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: float) -> "Vec2":
        self.x *= scalar
        self.y *= scalar
        return self

    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    def __itruediv__(self, scalar: float) -> "Vec2":
        self.x /= scalar
        self.y /= scalar
        return self

    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vec2") -> float:
        return self.x * other.y - self.y * other.x

    def length(self) -> float:
        return hypot(self.x, self.y)

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def distance_to(self, other: "Vec2") -> float:
        return hypot(self.x - other.x, self.y - other.y)

    def normalized(self) -> "Vec2":
        magnitude = self.length()
        if magnitude == 0.0:
            return Vec2()
        return self / magnitude

    def rotate(self, radians: float) -> "Vec2":
        c = cos(radians)
        s = sin(radians)
        return Vec2(self.x * c - self.y * s, self.x * s + self.y * c)

    def perpendicular(self) -> "Vec2":
        return Vec2(-self.y, self.x)

    def set(self, x: float, y: float) -> "Vec2":
        self.x = x
        self.y = y
        return self

    def reset(self) -> "Vec2":
        self.x = 0.0
        self.y = 0.0
        return self

    def add_scaled(self, other: "Vec2", scalar: float) -> "Vec2":
        self.x += other.x * scalar
        self.y += other.y * scalar
        return self

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)
