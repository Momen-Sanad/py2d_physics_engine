# <file>
# <summary>
# Small 3D math helpers for rigid-body rotation demos.
# </summary>
# </file>
"""Small 3D math helpers for rigid-body rotation demos."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, sqrt


# <summary>
# Mutable 3D vector used by the rigid-body rotation module.
# </summary>
@dataclass(slots=True)
class Vec3:
    """Mutable 3D vector used by the rigid-body rotation module."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # <summary>
    # Return the sum of this value and another value.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    # <summary>
    # Return the difference between this value and another value.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    # <summary>
    # Return this value multiplied by another value.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    # <summary>
    # Return this value multiplied from the right-hand side.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __rmul__(self, scalar: float) -> "Vec3":
        return self * scalar

    # <summary>
    # Return this value divided by a scalar.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __truediv__(self, scalar: float) -> "Vec3":
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    # <summary>
    # Return the negated value.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    # <summary>
    # Add another value into this value in place.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __iadd__(self, other: "Vec3") -> "Vec3":
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    # <summary>
    # Subtract another value from this value in place.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __isub__(self, other: "Vec3") -> "Vec3":
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    # <summary>
    # Scale this value in place.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __imul__(self, scalar: float) -> "Vec3":
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    # <summary>
    # Calculate the scalar dot product with another vector.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    # <summary>
    # Calculate the 3D vector cross product with another vector.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    # <summary>
    # Calculate the Euclidean vector magnitude.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def length(self) -> float:
        return sqrt(self.length_squared())

    # <summary>
    # Calculate squared magnitude without a square root.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    # <summary>
    # Return a unit-length copy, or zero when the vector has no length.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def normalized(self) -> "Vec3":
        magnitude = self.length()
        if magnitude == 0.0:
            return Vec3()
        return self / magnitude

    # <summary>
    # Add another vector multiplied by a scalar in place.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def add_scaled(self, other: "Vec3", scalar: float) -> "Vec3":
        self.x += other.x * scalar
        self.y += other.y * scalar
        self.z += other.z * scalar
        return self

    # <summary>
    # Reset all vector components to zero in place.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def reset(self) -> "Vec3":
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        return self

    # <summary>
    # Return a detached copy of this value.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def copy(self) -> "Vec3":
        return Vec3(self.x, self.y, self.z)

    # <summary>
    # Convert this value into a tuple of numeric components.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


# <summary>
# Tiny immutable 3x3 matrix with the operations rigid bodies need.
# </summary>
@dataclass(frozen=True, slots=True)
class Mat3:
    """Tiny immutable 3x3 matrix with the operations rigid bodies need."""

    rows: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]

    # <summary>
    # Return the multiplicative identity for this rotation type.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def identity(cls) -> "Mat3":
        return cls.diagonal(1.0, 1.0, 1.0)

    # <summary>
    # Return a matrix with all coefficients set to zero.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def zero(cls) -> "Mat3":
        return cls(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))

    # <summary>
    # Build a diagonal matrix from the supplied principal values.
    # </summary>
    # <param name="xx">Input value for xx.</param>
    # <param name="yy">Input value for yy.</param>
    # <param name="zz">Input value for zz.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def diagonal(cls, xx: float, yy: float, zz: float) -> "Mat3":
        return cls(((xx, 0.0, 0.0), (0.0, yy, 0.0), (0.0, 0.0, zz)))

    # <summary>
    # Multiply this matrix by a 3D vector.
    # </summary>
    # <param name="vector">Vector input used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def transform_vec3(self, vector: Vec3) -> Vec3:
        row0, row1, row2 = self.rows
        return Vec3(
            row0[0] * vector.x + row0[1] * vector.y + row0[2] * vector.z,
            row1[0] * vector.x + row1[1] * vector.y + row1[2] * vector.z,
            row2[0] * vector.x + row2[1] * vector.y + row2[2] * vector.z,
        )

    # <summary>
    # Apply matrix multiplication to another matrix or vector.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __matmul__(self, other: "Mat3 | Vec3") -> "Mat3 | Vec3":
        if isinstance(other, Vec3):
            return self.transform_vec3(other)
        if isinstance(other, Mat3):
            columns = other.transpose().rows
            return Mat3(
                tuple(
                    tuple(
                        row[0] * column[0] + row[1] * column[1] + row[2] * column[2]
                        for column in columns
                    )
                    for row in self.rows
                )
            )
        return NotImplemented

    # <summary>
    # Return this value multiplied by another value.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __mul__(self, scalar: float) -> "Mat3":
        return Mat3(tuple(tuple(value * scalar for value in row) for row in self.rows))

    # <summary>
    # Return this value multiplied from the right-hand side.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __rmul__(self, scalar: float) -> "Mat3":
        return self * scalar

    # <summary>
    # Return this matrix with rows and columns swapped.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def transpose(self) -> "Mat3":
        row0, row1, row2 = self.rows
        return Mat3(
            (
                (row0[0], row1[0], row2[0]),
                (row0[1], row1[1], row2[1]),
                (row0[2], row1[2], row2[2]),
            )
        )

    # <summary>
    # Calculate the 3x3 determinant used by inversion.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def determinant(self) -> float:
        a, b, c = self.rows[0]
        d, e, f = self.rows[1]
        g, h, i = self.rows[2]
        return (
            a * (e * i - f * h)
            - b * (d * i - f * g)
            + c * (d * h - e * g)
        )

    # <summary>
    # Return the inverse matrix, or raise when the matrix is singular.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def inverse(self) -> "Mat3":
        a, b, c = self.rows[0]
        d, e, f = self.rows[1]
        g, h, i = self.rows[2]
        determinant = self.determinant()
        if abs(determinant) <= 1e-12:
            raise ValueError("matrix is singular")

        inverse_det = 1.0 / determinant
        return Mat3(
            (
                (
                    (e * i - f * h) * inverse_det,
                    (c * h - b * i) * inverse_det,
                    (b * f - c * e) * inverse_det,
                ),
                (
                    (f * g - d * i) * inverse_det,
                    (a * i - c * g) * inverse_det,
                    (c * d - a * f) * inverse_det,
                ),
                (
                    (d * h - e * g) * inverse_det,
                    (b * g - a * h) * inverse_det,
                    (a * e - b * d) * inverse_det,
                ),
            )
        )


# <summary>
# Rotation quaternion in w, x, y, z order.
# </summary>
@dataclass(slots=True)
class Quaternion:
    """Rotation quaternion in w, x, y, z order."""

    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # <summary>
    # Return the multiplicative identity for this rotation type.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def identity(cls) -> "Quaternion":
        return cls()

    # <summary>
    # Build a normalized quaternion from an axis-angle rotation.
    # </summary>
    # <param name="axis">Rotation axis vector.</param>
    # <param name="radians">Angle in radians.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def from_axis_angle(cls, axis: Vec3, radians: float) -> "Quaternion":
        unit_axis = axis.normalized()
        half_angle = 0.5 * radians
        scale = sin(half_angle)
        quaternion = cls(
            cos(half_angle),
            unit_axis.x * scale,
            unit_axis.y * scale,
            unit_axis.z * scale,
        )
        quaternion.normalize()
        return quaternion

    # <summary>
    # Return the sum of this value and another value.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __add__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(
            self.w + other.w,
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    # <summary>
    # Return this value multiplied by another value.
    # </summary>
    # <param name="other">Second object or value used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __mul__(self, other: "Quaternion | float") -> "Quaternion":
        if isinstance(other, (int, float)):
            return Quaternion(
                self.w * other,
                self.x * other,
                self.y * other,
                self.z * other,
            )
        if isinstance(other, Quaternion):
            w1, x1, y1, z1 = self.w, self.x, self.y, self.z
            w2, x2, y2, z2 = other.w, other.x, other.y, other.z
            return Quaternion(
                w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
            )
        return NotImplemented

    # <summary>
    # Return this value multiplied from the right-hand side.
    # </summary>
    # <param name="scalar">Scalar multiplier used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def __rmul__(self, scalar: float) -> "Quaternion":
        return self * scalar

    # <summary>
    # Calculate squared magnitude without a square root.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def length_squared(self) -> float:
        return self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z

    # <summary>
    # Calculate the Euclidean vector magnitude.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def length(self) -> float:
        return sqrt(self.length_squared())

    # <summary>
    # Normalize this quaternion in place to keep it on the unit sphere.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def normalize(self) -> "Quaternion":
        magnitude = self.length()
        if magnitude == 0.0:
            self.w = 1.0
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            return self

        self.w /= magnitude
        self.x /= magnitude
        self.y /= magnitude
        self.z /= magnitude
        return self

    # <summary>
    # Return a unit-length copy, or zero when the vector has no length.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def normalized(self) -> "Quaternion":
        return self.copy().normalize()

    # <summary>
    # Return the quaternion conjugate used for inverse rotation.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    # <summary>
    # Rotate a 3D vector by this quaternion.
    # </summary>
    # <param name="vector">Vector input used by the operation.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def rotate_vector(self, vector: Vec3) -> Vec3:
        vector_q = Quaternion(0.0, vector.x, vector.y, vector.z)
        rotated = self.normalized() * vector_q * self.normalized().conjugate()
        return Vec3(rotated.x, rotated.y, rotated.z)

    # <summary>
    # Convert this quaternion orientation into a 3x3 rotation matrix.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def to_rotation_matrix(self) -> Mat3:
        q = self.normalized()
        w, x, y, z = q.w, q.x, q.y, q.z
        xx, yy, zz = x * x, y * y, z * z
        xy, xz, yz = x * y, x * z, y * z
        wx, wy, wz = w * x, w * y, w * z
        return Mat3(
            (
                (1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)),
                (2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)),
                (2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)),
            )
        )

    # <summary>
    # Return a detached copy of this value.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def copy(self) -> "Quaternion":
        return Quaternion(self.w, self.x, self.y, self.z)

    # <summary>
    # Convert this value into a tuple of numeric components.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.w, self.x, self.y, self.z)


# <summary>
# Return a diagonal inertia tensor from principal moments.
# </summary>
# <param name="ix">Principal moment of inertia around the x axis.</param>
# <param name="iy">Principal moment of inertia around the y axis.</param>
# <param name="iz">Principal moment of inertia around the z axis.</param>
# <returns>Computed result described by the return type annotation.</returns>
def inertia_tensor_from_principal(ix: float, iy: float, iz: float) -> Mat3:
    """Return a diagonal inertia tensor from principal moments."""

    return Mat3.diagonal(ix, iy, iz)


# <summary>
# Calculate the principal inertia tensor for a solid cube.
# </summary>
# <param name="mass">Mass value used by the physics calculation.</param>
# <param name="side_length">Cube side length used by the inertia calculation.</param>
# <returns>Computed result described by the return type annotation.</returns>
def solid_cube_inertia_tensor(mass: float, side_length: float) -> Mat3:
    moment = (1.0 / 6.0) * mass * side_length * side_length
    return inertia_tensor_from_principal(moment, moment, moment)


# <summary>
# Calculate the principal inertia tensor for a solid sphere.
# </summary>
# <param name="mass">Mass value used by the physics calculation.</param>
# <param name="radius">Radius value used by the geometry or physics calculation.</param>
# <returns>Computed result described by the return type annotation.</returns>
def solid_sphere_inertia_tensor(mass: float, radius: float) -> Mat3:
    moment = (2.0 / 5.0) * mass * radius * radius
    return inertia_tensor_from_principal(moment, moment, moment)


# <summary>
# Calculate the principal inertia tensor for a solid cylinder.
# </summary>
# <param name="mass">Mass value used by the physics calculation.</param>
# <param name="radius">Radius value used by the geometry or physics calculation.</param>
# <param name="height">Height value used by the geometry or physics calculation.</param>
# <returns>Computed result described by the return type annotation.</returns>
def solid_cylinder_inertia_tensor(mass: float, radius: float, height: float) -> Mat3:
    radial_moment = (1.0 / 12.0) * mass * (3.0 * radius * radius + height * height)
    axial_moment = 0.5 * mass * radius * radius
    return inertia_tensor_from_principal(radial_moment, radial_moment, axial_moment)


# <summary>
# Calculate the principal inertia tensor for a thin rod.
# </summary>
# <param name="mass">Mass value used by the physics calculation.</param>
# <param name="length">Length value used by the geometry or physics calculation.</param>
# <returns>Computed result described by the return type annotation.</returns>
def thin_rod_inertia_tensor(mass: float, length: float) -> Mat3:
    cross_axis_moment = (1.0 / 12.0) * mass * length * length
    return inertia_tensor_from_principal(cross_axis_moment, cross_axis_moment, 0.0)


# <summary>
# Calculate the principal inertia tensor for a rectangular plate.
# </summary>
# <param name="mass">Mass value used by the physics calculation.</param>
# <param name="width">Width value used by the geometry or physics calculation.</param>
# <param name="height">Height value used by the geometry or physics calculation.</param>
# <returns>Computed result described by the return type annotation.</returns>
def rectangular_plate_inertia_tensor(mass: float, width: float, height: float) -> Mat3:
    ix = (1.0 / 12.0) * mass * height * height
    iy = (1.0 / 12.0) * mass * width * width
    iz = (1.0 / 12.0) * mass * (width * width + height * height)
    return inertia_tensor_from_principal(ix, iy, iz)
