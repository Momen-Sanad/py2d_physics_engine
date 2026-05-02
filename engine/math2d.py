# <file>
# <summary>
# Small 2D math helpers used throughout the engine.
# </summary>
# </file>
"""Small 2D math helpers used throughout the engine."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, sin


# <summary>
# Mutable 2D vector with helpers for hot-path in-place math.
# </summary>
@dataclass(slots=True)
class Vec2:
    """Mutable 2D vector with helpers for hot-path in-place math."""

    x: float = 0.0
    y: float = 0.0

    # <summary>
    # Return the sum of this value and another value.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    # <summary>
    # Return the difference between this value and another value.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    # <summary>
    # Return this value multiplied by another value.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    # <summary>
    # Return this value multiplied from the right-hand side.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __rmul__(self, scalar: float) -> "Vec2":
        return self * scalar

    # <summary>
    # Return the negated value.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def __neg__(self) -> "Vec2":
        return Vec2(-self.x, -self.y)

    # <summary>
    # Add another value into this value in place.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __iadd__(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self

    # <summary>
    # Subtract another value from this value in place.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __isub__(self, other: "Vec2") -> "Vec2":
        self.x -= other.x
        self.y -= other.y
        return self

    # <summary>
    # Scale this value in place.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __imul__(self, scalar: float) -> "Vec2":
        self.x *= scalar
        self.y *= scalar
        return self

    # <summary>
    # Return this value divided by a scalar.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    # <summary>
    # Divide this value by a scalar in place.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __itruediv__(self, scalar: float) -> "Vec2":
        self.x /= scalar
        self.y /= scalar
        return self

    # <summary>
    # Calculate the scalar dot product with another vector.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def dot(self, other: "Vec2") -> float:
        return self.x * other.x + self.y * other.y

    # <summary>
    # Calculate the 2D scalar cross product with another vector.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def cross(self, other: "Vec2") -> float:
        return self.x * other.y - self.y * other.x

    # <summary>
    # Calculate the Euclidean vector magnitude.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def length(self) -> float:
        return hypot(self.x, self.y)

    # <summary>
    # Calculate squared magnitude without a square root.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    # <summary>
    # Calculate Euclidean distance to another point.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def distance_to(self, other: "Vec2") -> float:
        return hypot(self.x - other.x, self.y - other.y)

    # <summary>
    # Return a unit-length copy, or zero when the vector has no length.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def normalized(self) -> "Vec2":
        magnitude = self.length()
        if magnitude == 0.0:
            return Vec2()
        return self / magnitude

    # <summary>
    # Return this vector rotated by the supplied angle.
    # </summary>
    # <param name="radians">Angle in radians.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def rotate(self, radians: float) -> "Vec2":
        c = cos(radians)
        s = sin(radians)
        return Vec2(self.x * c - self.y * s, self.x * s + self.y * c)

    # <summary>
    # Return a vector perpendicular to this one.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def perpendicular(self) -> "Vec2":
        return Vec2(-self.y, self.x)

    # <summary>
    # Replace both vector components in place.
    # </summary>
    # <param name="x">Horizontal drawing coordinate.</param>
    # <param name="y">Vertical drawing coordinate.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def set(self, x: float, y: float) -> "Vec2":
        self.x = x
        self.y = y
        return self

    # <summary>
    # Reset both vector components to zero in place.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def reset(self) -> "Vec2":
        self.x = 0.0
        self.y = 0.0
        return self

    # <summary>
    # Add another vector multiplied by a scalar in place.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def add_scaled(self, other: "Vec2", scalar: float) -> "Vec2":
        self.x += other.x * scalar
        self.y += other.y * scalar
        return self

    # <summary>
    # Return a detached copy of this vector.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    # <summary>
    # Convert the vector into an x-y tuple.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)
