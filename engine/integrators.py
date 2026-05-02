# <file>
# <summary>
# Numerical integration helpers for particle and rigid-body motion.
# </summary>
# </file>
"""Numerical integration helpers for particle and rigid-body motion."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2


# <summary>
# State tuple used by the basic integrator helpers.
# </summary>
@dataclass(frozen=True, slots=True)
class IntegrationState:
    """State tuple used by the basic integrator helpers."""

    position: Vec2
    velocity: Vec2
    acceleration: Vec2


# <summary>
# Simple but less stable reference integrator.
# </summary>
# <param name="state">Input value for state.</param>
# <param name="dt">Simulation timestep in seconds.</param>
# <returns>Computed result described by the return type annotation.</returns>
def explicit_euler(state: IntegrationState, dt: float) -> IntegrationState:
    """Simple but less stable reference integrator."""

    next_position = state.position + state.velocity * dt
    next_velocity = state.velocity + state.acceleration * dt
    return IntegrationState(next_position, next_velocity, state.acceleration)


# <summary>
# Default integrator for the early engine stages.
# </summary>
# <param name="state">Input value for state.</param>
# <param name="dt">Simulation timestep in seconds.</param>
# <returns>Computed result described by the return type annotation.</returns>
def semi_implicit_euler(state: IntegrationState, dt: float) -> IntegrationState:
    """Default integrator for the early engine stages."""

    next_velocity = state.velocity + state.acceleration * dt
    next_position = state.position + next_velocity * dt
    return IntegrationState(next_position, next_velocity, state.acceleration)
