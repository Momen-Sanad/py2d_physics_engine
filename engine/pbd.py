# <file>
# <summary>
# Helpers and placeholders for Position-Based Dynamics systems.
# </summary>
# </file>
"""Helpers and placeholders for Position-Based Dynamics systems."""

from __future__ import annotations

from dataclasses import dataclass

from .math2d import Vec2


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
    if dt == 0.0:
        return Vec2()
    return (corrected_position - previous_position) / dt
