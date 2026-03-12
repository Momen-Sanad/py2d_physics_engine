"""Helpers and placeholders for Position-Based Dynamics systems."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2


@dataclass(slots=True)
class PredictedParticle:
    """Temporary particle state used during a PBD solve pass."""

    previous_position: Vec2
    position: Vec2
    velocity: Vec2
    inverse_mass: float


def velocity_from_positions(
    previous_position: Vec2,
    corrected_position: Vec2,
    dt: float,
) -> Vec2:
    if dt == 0.0:
        return Vec2()
    return (corrected_position - previous_position) / dt
