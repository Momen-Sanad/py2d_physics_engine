# <file>
# <summary>
# Position-Based Dynamics particles, constraints, and solve helpers.
# </summary>
# </file>
"""Position-Based Dynamics particles, constraints, and solve helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .constraints import solve_distance_constraint
from .math2d import Vec2
from .particle import Particle


# <summary>
# Temporary particle state used during a PBD solve pass.
# </summary>
@dataclass(slots=True)
class PredictedParticle:
    """Temporary particle state used during a PBD solve pass."""

    previous_position: Vec2
    position: Vec2
    velocity: Vec2
    inverse_mass: float


# <summary>
# Distance relationship between two predicted particles.
# </summary>
@dataclass(slots=True)
class PBDDistanceConstraint:
    """Distance relationship between two predicted particles."""

    index_a: int
    index_b: int
    rest_length: float
    stiffness: float = 1.0

    # <summary>
    # Build a distance constraint from the current predicted particle positions.
    # </summary>
    # <param name="index_a">Index of the first constrained particle.</param>
    # <param name="index_b">Index of the second constrained particle.</param>
    # <param name="particles">Particle collection used to derive rest length.</param>
    # <param name="stiffness">Projection stiffness in the inclusive range 0..1.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def between(
        cls,
        index_a: int,
        index_b: int,
        particles: Sequence[PredictedParticle] | Sequence[Particle],
        stiffness: float = 1.0,
    ) -> "PBDDistanceConstraint":
        a_position = particles[index_a].position
        b_position = particles[index_b].position
        return cls(
            index_a=index_a,
            index_b=index_b,
            rest_length=a_position.distance_to(b_position),
            stiffness=stiffness,
        )


# <summary>
# Anchor that pins one predicted particle to a world-space position.
# </summary>
@dataclass(slots=True)
class PBDPinConstraint:
    """Anchor that pins one predicted particle to a world-space position."""

    index: int
    position: Vec2
    stiffness: float = 1.0


# <summary>
# Axis-aligned boundary used to keep predicted particles inside a demo area.
# </summary>
@dataclass(slots=True)
class PBDBounds:
    """Axis-aligned boundary used to keep predicted particles inside a demo area."""

    left: float
    top: float
    right: float
    bottom: float
    radius: float = 0.0


# <summary>
# Complete PBD particle system that can be stepped by PhysicsWorld.
# </summary>
@dataclass(slots=True)
class PBDSystem:
    """Complete PBD particle system that can be stepped by PhysicsWorld."""

    particles: list[Particle]
    distance_constraints: list[PBDDistanceConstraint] = field(default_factory=list)
    pin_constraints: list[PBDPinConstraint] = field(default_factory=list)
    iterations: int = 8
    gravity: Vec2 | None = None
    linear_damping: float = 0.0
    bounds: PBDBounds | None = None

    # <summary>
    # Advance the PBD system by one fixed timestep.
    # </summary>
    # <param name="dt">Simulation timestep in seconds.</param>
    def step(self, dt: float) -> None:
        predicted = predict_particles(
            self.particles,
            dt,
            gravity=self.gravity,
            linear_damping=self.linear_damping,
        )
        solve_predicted_particles(
            predicted,
            self.distance_constraints,
            self.pin_constraints,
            iterations=self.iterations,
            bounds=self.bounds,
        )
        update_particles_from_predictions(self.particles, predicted, dt)


# <summary>
# Reconstruct velocity from old and corrected positions.
# </summary>
# <param name="previous_position">Input value for previous position.</param>
# <param name="corrected_position">Input value for corrected position.</param>
# <param name="dt">Simulation timestep in seconds.</param>
# <returns>Computed result described by the return type annotation.</returns>
def velocity_from_positions(
    previous_position: Vec2,
    corrected_position: Vec2,
    dt: float,
) -> Vec2:
    """Reconstruct velocity from old and corrected positions."""

    if dt == 0.0:
        return Vec2()
    return (corrected_position - previous_position) / dt


# <summary>
# Create predicted particles from live particles and external acceleration.
# </summary>
# <param name="particles">Particle collection being read or updated.</param>
# <param name="dt">Simulation timestep in seconds.</param>
# <param name="gravity">Optional gravity acceleration vector.</param>
# <param name="linear_damping">Linear damping coefficient applied during prediction.</param>
# <returns>Computed result described by the return type annotation.</returns>
def predict_particles(
    particles: Sequence[Particle],
    dt: float,
    gravity: Vec2 | None = None,
    linear_damping: float = 0.0,
) -> list[PredictedParticle]:
    """Create predicted particles from live particles and external acceleration."""

    gravity_x = 0.0 if gravity is None else gravity.x
    gravity_y = 0.0 if gravity is None else gravity.y
    damping_factor = max(0.0, 1.0 - linear_damping * dt) if linear_damping > 0.0 else 1.0
    out: list[PredictedParticle] = []

    for particle in particles:
        previous_position = particle.position.copy()
        inverse_mass = particle.inverse_mass

        if inverse_mass == 0.0:
            out.append(
                PredictedParticle(
                    previous_position=previous_position,
                    position=previous_position.copy(),
                    velocity=Vec2(),
                    inverse_mass=0.0,
                )
            )
            continue

        velocity = particle.velocity.copy()
        velocity.x += (gravity_x + particle.force.x * inverse_mass) * dt
        velocity.y += (gravity_y + particle.force.y * inverse_mass) * dt
        velocity *= damping_factor

        out.append(
            PredictedParticle(
                previous_position=previous_position,
                position=previous_position + velocity * dt,
                velocity=velocity,
                inverse_mass=inverse_mass,
            )
        )

    return out


# <summary>
# Project distance, pin, and boundary constraints for predicted particles.
# </summary>
# <param name="particles">Predicted particle collection being corrected.</param>
# <param name="distance_constraints">Distance constraints to solve iteratively.</param>
# <param name="pin_constraints">Anchor constraints to enforce after each iteration.</param>
# <param name="iterations">Number of projection iterations to run.</param>
# <param name="bounds">Optional rectangle used for boundary projection.</param>
def solve_predicted_particles(
    particles: Sequence[PredictedParticle],
    distance_constraints: Sequence[PBDDistanceConstraint],
    pin_constraints: Sequence[PBDPinConstraint] | None = None,
    iterations: int = 8,
    bounds: PBDBounds | None = None,
) -> None:
    """Project distance, pin, and boundary constraints for predicted particles."""

    clamped_iterations = max(0, iterations)
    pins = () if pin_constraints is None else pin_constraints

    apply_pin_constraints(particles, pins)
    for _ in range(clamped_iterations):
        solve_distance_constraints(particles, distance_constraints)
        apply_pin_constraints(particles, pins)
        if bounds is not None:
            constrain_to_bounds(particles, bounds)

    if bounds is not None:
        constrain_to_bounds(particles, bounds)


# <summary>
# Project all distance constraints once.
# </summary>
# <param name="particles">Predicted particle collection being corrected.</param>
# <param name="constraints">Distance constraints to solve.</param>
def solve_distance_constraints(
    particles: Sequence[PredictedParticle],
    constraints: Sequence[PBDDistanceConstraint],
) -> None:
    """Project all distance constraints once."""

    for constraint in constraints:
        particle_a = particles[constraint.index_a]
        particle_b = particles[constraint.index_b]
        correction_a, correction_b = solve_distance_constraint(
            particle_a.position,
            particle_b.position,
            constraint.rest_length,
            particle_a.inverse_mass,
            particle_b.inverse_mass,
            stiffness=constraint.stiffness,
        )
        particle_a.position += correction_a
        particle_b.position += correction_b


# <summary>
# Enforce anchor constraints for predicted particles.
# </summary>
# <param name="particles">Predicted particle collection being corrected.</param>
# <param name="constraints">Pin constraints to solve.</param>
def apply_pin_constraints(
    particles: Sequence[PredictedParticle],
    constraints: Sequence[PBDPinConstraint],
) -> None:
    """Enforce anchor constraints for predicted particles."""

    for constraint in constraints:
        particle = particles[constraint.index]
        stiffness = max(0.0, min(1.0, constraint.stiffness))
        if stiffness >= 1.0:
            particle.position = constraint.position.copy()
        elif stiffness > 0.0:
            delta = constraint.position - particle.position
            particle.position += delta * stiffness


# <summary>
# Keep movable predicted particles inside an axis-aligned rectangle.
# </summary>
# <param name="particles">Predicted particle collection being corrected.</param>
# <param name="bounds">Boundary used to clamp particle positions.</param>
def constrain_to_bounds(
    particles: Sequence[PredictedParticle],
    bounds: PBDBounds,
) -> None:
    """Keep movable predicted particles inside an axis-aligned rectangle."""

    left = bounds.left + bounds.radius
    top = bounds.top + bounds.radius
    right = bounds.right - bounds.radius
    bottom = bounds.bottom - bounds.radius

    for particle in particles:
        if particle.inverse_mass == 0.0:
            continue

        position = particle.position
        position.x = min(max(position.x, left), right)
        position.y = min(max(position.y, top), bottom)


# <summary>
# Copy corrected PBD state back into live particles.
# </summary>
# <param name="particles">Particle collection being updated.</param>
# <param name="predicted">Corrected predicted state for each live particle.</param>
# <param name="dt">Simulation timestep in seconds.</param>
def update_particles_from_predictions(
    particles: Sequence[Particle],
    predicted: Sequence[PredictedParticle],
    dt: float,
) -> None:
    """Copy corrected PBD state back into live particles."""

    for particle, prediction in zip(particles, predicted, strict=False):
        particle.position = prediction.position.copy()
        if particle.inverse_mass == 0.0:
            particle.velocity.reset()
        else:
            particle.velocity = velocity_from_positions(
                prediction.previous_position,
                prediction.position,
                dt,
            )
        particle.clear_forces()
