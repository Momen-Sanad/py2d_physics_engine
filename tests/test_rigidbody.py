"""Regression tests for rigid-body lecture mechanics."""

from __future__ import annotations

from math import pi
import unittest

from engine.math2d import Vec2
from engine.math3d import (
    Quaternion,
    Vec3,
    solid_cube_inertia_tensor,
)
from engine.rigidbody import RigidBody2D, RigidBody3D


class InertiaTensorTests(unittest.TestCase):
    def test_solid_cube_inertia_matches_lecture_formula(self) -> None:
        inertia = solid_cube_inertia_tensor(mass=8.0, side_length=2.0)
        expected = (1.0 / 6.0) * 8.0 * 2.0 * 2.0

        self.assertAlmostEqual(inertia.rows[0][0], expected)
        self.assertAlmostEqual(inertia.rows[1][1], expected)
        self.assertAlmostEqual(inertia.rows[2][2], expected)
        self.assertAlmostEqual(inertia.rows[0][1], 0.0)
        self.assertAlmostEqual(inertia.rows[0][2], 0.0)


class QuaternionTests(unittest.TestCase):
    def test_axis_angle_rotates_vector(self) -> None:
        rotation = Quaternion.from_axis_angle(Vec3(0.0, 0.0, 1.0), pi * 0.5)
        rotated = rotation.rotate_vector(Vec3(1.0, 0.0, 0.0))

        self.assertAlmostEqual(rotated.x, 0.0, places=6)
        self.assertAlmostEqual(rotated.y, 1.0, places=6)
        self.assertAlmostEqual(rotated.z, 0.0, places=6)
        self.assertAlmostEqual(rotation.length(), 1.0, places=6)

    def test_quaternion_rotation_matrix_matches_vector_rotation(self) -> None:
        rotation = Quaternion.from_axis_angle(Vec3(0.0, 1.0, 0.0), pi)
        matrix_rotated = rotation.to_rotation_matrix() @ Vec3(1.0, 0.0, 0.0)
        quaternion_rotated = rotation.rotate_vector(Vec3(1.0, 0.0, 0.0))

        self.assertAlmostEqual(matrix_rotated.x, quaternion_rotated.x, places=6)
        self.assertAlmostEqual(matrix_rotated.y, quaternion_rotated.y, places=6)
        self.assertAlmostEqual(matrix_rotated.z, quaternion_rotated.z, places=6)


class RigidBody3DTests(unittest.TestCase):
    def test_torque_updates_angular_velocity_and_orientation(self) -> None:
        body = RigidBody3D(
            position=Vec3(),
            mass=8.0,
            inertia_body=solid_cube_inertia_tensor(8.0, 2.0),
        )

        body.apply_torque(Vec3(0.0, 0.0, 10.0))
        body.step(0.1)

        self.assertAlmostEqual(body.angular_velocity.x, 0.0)
        self.assertAlmostEqual(body.angular_velocity.y, 0.0)
        self.assertAlmostEqual(body.angular_velocity.z, 0.1875)
        self.assertAlmostEqual(body.orientation.length(), 1.0, places=6)
        self.assertAlmostEqual(body.torque.length_squared(), 0.0)

    def test_isotropic_body_has_no_gyroscopic_drift_without_torque(self) -> None:
        body = RigidBody3D(
            position=Vec3(),
            angular_velocity=Vec3(1.0, 1.0, 1.0),
            inertia_body=solid_cube_inertia_tensor(8.0, 2.0),
        )

        body.step(0.1)

        self.assertAlmostEqual(body.angular_velocity.x, 1.0)
        self.assertAlmostEqual(body.angular_velocity.y, 1.0)
        self.assertAlmostEqual(body.angular_velocity.z, 1.0)
        self.assertAlmostEqual(body.orientation.length(), 1.0, places=6)


class RigidBody2DTests(unittest.TestCase):
    def test_force_at_point_produces_linear_and_angular_motion(self) -> None:
        body = RigidBody2D(position=Vec2(), mass=1.0, inertia=2.0)

        body.apply_force_at_point(Vec2(0.0, 10.0), Vec2(1.0, 0.0))
        body.step(0.1)

        self.assertAlmostEqual(body.velocity.y, 1.0)
        self.assertAlmostEqual(body.position.y, 0.1)
        self.assertAlmostEqual(body.angular_velocity, 0.5)
        self.assertAlmostEqual(body.angle, 0.05)
        self.assertAlmostEqual(body.torque, 0.0)

    def test_impulse_at_point_affects_angular_velocity(self) -> None:
        body = RigidBody2D(position=Vec2(), mass=2.0, inertia=4.0)

        body.apply_impulse(Vec2(0.0, 2.0), Vec2(1.0, 0.0))

        self.assertAlmostEqual(body.velocity.y, 1.0)
        self.assertAlmostEqual(body.angular_velocity, 0.5)


if __name__ == "__main__":
    unittest.main()
