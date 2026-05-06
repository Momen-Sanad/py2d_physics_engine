"""Regression tests for Position-Based Dynamics helpers."""

from __future__ import annotations

import unittest

from engine.math2d import Vec2
from engine.pbd import (
    PBDBounds,
    PBDDistanceConstraint,
    PredictedParticle,
    constrain_to_bounds,
    solve_predicted_particles,
    velocity_from_positions,
)


# <summary>
# Represents the PBDConstraintTests data structure.
# </summary>
class PBDConstraintTests(unittest.TestCase):
    # <summary>
    # Verify distance projection restores the requested rest length.
    # </summary>
    def test_distance_constraint_converges_to_rest_length(self) -> None:
        particles = [
            PredictedParticle(Vec2(), Vec2(0.0, 0.0), Vec2(), 1.0),
            PredictedParticle(Vec2(), Vec2(2.0, 0.0), Vec2(), 1.0),
        ]
        constraint = PBDDistanceConstraint(0, 1, rest_length=1.0)

        solve_predicted_particles(particles, [constraint], iterations=1)

        self.assertAlmostEqual(particles[0].position.distance_to(particles[1].position), 1.0)

    # <summary>
    # Verify an infinite-mass endpoint is not moved by distance projection.
    # </summary>
    def test_infinite_mass_particle_does_not_move(self) -> None:
        particles = [
            PredictedParticle(Vec2(), Vec2(0.0, 0.0), Vec2(), 0.0),
            PredictedParticle(Vec2(), Vec2(2.0, 0.0), Vec2(), 1.0),
        ]
        constraint = PBDDistanceConstraint(0, 1, rest_length=1.0)

        solve_predicted_particles(particles, [constraint], iterations=1)

        self.assertAlmostEqual(particles[0].position.x, 0.0)
        self.assertAlmostEqual(particles[0].position.y, 0.0)
        self.assertAlmostEqual(particles[1].position.x, 1.0)

    # <summary>
    # Verify velocity reconstruction uses corrected displacement over timestep.
    # </summary>
    def test_velocity_reconstruction_uses_corrected_positions(self) -> None:
        velocity = velocity_from_positions(Vec2(1.0, 2.0), Vec2(4.0, 8.0), 0.5)

        self.assertAlmostEqual(velocity.x, 6.0)
        self.assertAlmostEqual(velocity.y, 12.0)

    # <summary>
    # Verify bounds projection clamps movable predicted particles only.
    # </summary>
    def test_bounds_projection_clamps_movable_particles(self) -> None:
        particles = [
            PredictedParticle(Vec2(), Vec2(-10.0, 20.0), Vec2(), 1.0),
            PredictedParticle(Vec2(), Vec2(-10.0, 20.0), Vec2(), 0.0),
        ]

        constrain_to_bounds(particles, PBDBounds(0.0, 0.0, 100.0, 100.0, radius=5.0))

        self.assertAlmostEqual(particles[0].position.x, 5.0)
        self.assertAlmostEqual(particles[0].position.y, 20.0)
        self.assertAlmostEqual(particles[1].position.x, -10.0)


if __name__ == "__main__":
    unittest.main()
