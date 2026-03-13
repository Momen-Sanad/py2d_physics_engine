"""Small 2D math helpers used throughout the engine."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, sin


@dataclass(frozen=True, slots=True)
class Vec2:
    """Immutable 2D vector with the operations needed by the engine."""

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

    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vec2") -> float:
        return self.x * other.y - self.y * other.x

    def length(self) -> float:
        return hypot(self.x, self.y)

    def distance_to(self, other: "Vec2") -> float:
        return (self - other).length()

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

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)
