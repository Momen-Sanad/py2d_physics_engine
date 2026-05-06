"""Regression tests for forward and inverse kinematics helpers."""

from __future__ import annotations

from math import pi
import unittest

from engine.kinematics import (
    KinematicChain,
    forward_chain,
    measured_segment_lengths,
    solve_ccd_ik,
)
from engine.math2d import Vec2


# <summary>
# Represents the ForwardKinematicsTests data structure.
# </summary>
class ForwardKinematicsTests(unittest.TestCase):
    # <summary>
    # Verify forward-chain output for a known two-link pose.
    # </summary>
    def test_forward_chain_returns_known_joint_positions(self) -> None:
        positions = forward_chain(
            Vec2(0.0, 0.0),
            [10.0, 5.0],
            [0.0, pi * 0.5],
        )

        self.assertAlmostEqual(positions[0].x, 0.0)
        self.assertAlmostEqual(positions[0].y, 0.0)
        self.assertAlmostEqual(positions[1].x, 10.0)
        self.assertAlmostEqual(positions[1].y, 0.0)
        self.assertAlmostEqual(positions[2].x, 10.0)
        self.assertAlmostEqual(positions[2].y, 5.0)

    # <summary>
    # Verify chain helper reports stable segment lengths after local edits.
    # </summary>
    def test_chain_helper_preserves_segment_lengths(self) -> None:
        chain = KinematicChain.from_lengths(Vec2(2.0, 3.0), [8.0, 6.0, 4.0])

        chain.add_angle(0, pi * 0.5)
        chain.add_angle(1, -pi * 0.25)
        lengths = measured_segment_lengths(chain.joint_positions())

        self.assertEqual(len(lengths), 3)
        self.assertAlmostEqual(lengths[0], 8.0)
        self.assertAlmostEqual(lengths[1], 6.0)
        self.assertAlmostEqual(lengths[2], 4.0)


# <summary>
# Represents the InverseKinematicsTests data structure.
# </summary>
class InverseKinematicsTests(unittest.TestCase):
    # <summary>
    # Verify CCD reaches a simple two-link target.
    # </summary>
    def test_ccd_solver_reaches_target(self) -> None:
        chain = KinematicChain.from_lengths(Vec2(0.0, 0.0), [10.0, 10.0])

        result = solve_ccd_ik(chain, Vec2(10.0, 10.0), iterations=8, tolerance=0.001)

        self.assertTrue(result.reached)
        self.assertTrue(result.target_reachable)
        self.assertLessEqual(result.error, 0.001)
        self.assertAlmostEqual(chain.end_effector().x, 10.0, places=3)
        self.assertAlmostEqual(chain.end_effector().y, 10.0, places=3)

    # <summary>
    # Verify IK solving keeps all segment lengths fixed.
    # </summary>
    def test_ccd_solver_preserves_segment_lengths(self) -> None:
        chain = KinematicChain.from_lengths(Vec2(4.0, 5.0), [12.0, 9.0, 6.0])

        solve_ccd_ik(chain, Vec2(15.0, 18.0), iterations=20, tolerance=0.01)
        lengths = measured_segment_lengths(chain.joint_positions())

        self.assertAlmostEqual(lengths[0], 12.0)
        self.assertAlmostEqual(lengths[1], 9.0)
        self.assertAlmostEqual(lengths[2], 6.0)

    # <summary>
    # Verify unreachable targets extend the chain toward the target.
    # </summary>
    def test_unreachable_target_extends_toward_target(self) -> None:
        chain = KinematicChain.from_lengths(Vec2(0.0, 0.0), [10.0, 5.0])

        result = solve_ccd_ik(chain, Vec2(100.0, 0.0), iterations=20, tolerance=0.01)
        end_effector = chain.end_effector()
        lengths = measured_segment_lengths(chain.joint_positions())

        self.assertFalse(result.reached)
        self.assertFalse(result.target_reachable)
        self.assertAlmostEqual(end_effector.x, 15.0)
        self.assertAlmostEqual(end_effector.y, 0.0)
        self.assertAlmostEqual(lengths[0], 10.0)
        self.assertAlmostEqual(lengths[1], 5.0)


if __name__ == "__main__":
    unittest.main()
