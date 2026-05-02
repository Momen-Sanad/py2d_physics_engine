"""Small 3D math helpers for rigid-body rotation demos."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, sqrt


@dataclass(slots=True)
class Vec3:
    """Mutable 3D vector used by the rigid-body rotation module."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vec3":
        return self * scalar

    def __truediv__(self, scalar: float) -> "Vec3":
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def __iadd__(self, other: "Vec3") -> "Vec3":
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other: "Vec3") -> "Vec3":
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, scalar: float) -> "Vec3":
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self) -> float:
        return sqrt(self.length_squared())

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalized(self) -> "Vec3":
        magnitude = self.length()
        if magnitude == 0.0:
            return Vec3()
        return self / magnitude

    def add_scaled(self, other: "Vec3", scalar: float) -> "Vec3":
        self.x += other.x * scalar
        self.y += other.y * scalar
        self.z += other.z * scalar
        return self

    def reset(self) -> "Vec3":
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        return self

    def copy(self) -> "Vec3":
        return Vec3(self.x, self.y, self.z)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True, slots=True)
class Mat3:
    """Tiny immutable 3x3 matrix with the operations rigid bodies need."""

    rows: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]

    @classmethod
    def identity(cls) -> "Mat3":
        return cls.diagonal(1.0, 1.0, 1.0)

    @classmethod
    def zero(cls) -> "Mat3":
        return cls(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))

    @classmethod
    def diagonal(cls, xx: float, yy: float, zz: float) -> "Mat3":
        return cls(((xx, 0.0, 0.0), (0.0, yy, 0.0), (0.0, 0.0, zz)))

    def transform_vec3(self, vector: Vec3) -> Vec3:
        row0, row1, row2 = self.rows
        return Vec3(
            row0[0] * vector.x + row0[1] * vector.y + row0[2] * vector.z,
            row1[0] * vector.x + row1[1] * vector.y + row1[2] * vector.z,
            row2[0] * vector.x + row2[1] * vector.y + row2[2] * vector.z,
        )

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

    def __mul__(self, scalar: float) -> "Mat3":
        return Mat3(tuple(tuple(value * scalar for value in row) for row in self.rows))

    def __rmul__(self, scalar: float) -> "Mat3":
        return self * scalar

    def transpose(self) -> "Mat3":
        row0, row1, row2 = self.rows
        return Mat3(
            (
                (row0[0], row1[0], row2[0]),
                (row0[1], row1[1], row2[1]),
                (row0[2], row1[2], row2[2]),
            )
        )

    def determinant(self) -> float:
        a, b, c = self.rows[0]
        d, e, f = self.rows[1]
        g, h, i = self.rows[2]
        return (
            a * (e * i - f * h)
            - b * (d * i - f * g)
            + c * (d * h - e * g)
        )

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


@dataclass(slots=True)
class Quaternion:
    """Rotation quaternion in w, x, y, z order."""

    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @classmethod
    def identity(cls) -> "Quaternion":
        return cls()

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

    def __add__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(
            self.w + other.w,
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

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

    def __rmul__(self, scalar: float) -> "Quaternion":
        return self * scalar

    def length_squared(self) -> float:
        return self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z

    def length(self) -> float:
        return sqrt(self.length_squared())

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

    def normalized(self) -> "Quaternion":
        return self.copy().normalize()

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def rotate_vector(self, vector: Vec3) -> Vec3:
        vector_q = Quaternion(0.0, vector.x, vector.y, vector.z)
        rotated = self.normalized() * vector_q * self.normalized().conjugate()
        return Vec3(rotated.x, rotated.y, rotated.z)

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

    def copy(self) -> "Quaternion":
        return Quaternion(self.w, self.x, self.y, self.z)

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.w, self.x, self.y, self.z)


def inertia_tensor_from_principal(ix: float, iy: float, iz: float) -> Mat3:
    """Return a diagonal inertia tensor from principal moments."""

    return Mat3.diagonal(ix, iy, iz)


def solid_cube_inertia_tensor(mass: float, side_length: float) -> Mat3:
    moment = (1.0 / 6.0) * mass * side_length * side_length
    return inertia_tensor_from_principal(moment, moment, moment)


def solid_sphere_inertia_tensor(mass: float, radius: float) -> Mat3:
    moment = (2.0 / 5.0) * mass * radius * radius
    return inertia_tensor_from_principal(moment, moment, moment)


def solid_cylinder_inertia_tensor(mass: float, radius: float, height: float) -> Mat3:
    radial_moment = (1.0 / 12.0) * mass * (3.0 * radius * radius + height * height)
    axial_moment = 0.5 * mass * radius * radius
    return inertia_tensor_from_principal(radial_moment, radial_moment, axial_moment)


def thin_rod_inertia_tensor(mass: float, length: float) -> Mat3:
    cross_axis_moment = (1.0 / 12.0) * mass * length * length
    return inertia_tensor_from_principal(cross_axis_moment, cross_axis_moment, 0.0)


def rectangular_plate_inertia_tensor(mass: float, width: float, height: float) -> Mat3:
    ix = (1.0 / 12.0) * mass * height * height
    iy = (1.0 / 12.0) * mass * width * width
    iz = (1.0 / 12.0) * mass * (width * width + height * height)
    return inertia_tensor_from_principal(ix, iy, iz)
