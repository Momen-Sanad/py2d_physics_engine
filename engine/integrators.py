"""Numerical integration helpers for particle and rigid-body motion."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2


@dataclass(frozen=True, slots=True)
class IntegrationState:
    """State tuple used by the basic integrator helpers."""

    position: Vec2
    velocity: Vec2
    acceleration: Vec2


def explicit_euler(state: IntegrationState, dt: float) -> IntegrationState:
    """Simple but less stable reference integrator."""

    next_position = state.position + state.velocity * dt
    next_velocity = state.velocity + state.acceleration * dt
    return IntegrationState(next_position, next_velocity, state.acceleration)


def semi_implicit_euler(state: IntegrationState, dt: float) -> IntegrationState:
    """Default integrator for the early engine stages."""

    next_velocity = state.velocity + state.acceleration * dt
    next_position = state.position + next_velocity * dt
    return IntegrationState(next_position, next_velocity, state.acceleration)
