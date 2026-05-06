# <file>
# <summary>
# Forward-kinematics helpers for articulated 2D chains.
# </summary>
# </file>
"""Forward-kinematics helpers for articulated 2D chains."""

from dataclasses import dataclass
from math import cos, sin
from typing import Sequence

from .math2d import Vec2


# <summary>
# Return joint positions for a planar articulated chain.
# </summary>
# <param name="origin">Input value for origin.</param>
# <param name="lengths">Input value for lengths.</param>
# <param name="angles">Input value for angles.</param>
# <returns>Computed result described by the return type annotation.</returns>
def forward_chain(origin: Vec2, lengths: list[float], angles: list[float]) -> list[Vec2]:
    """Return joint positions for a planar articulated chain."""

    positions = [origin]
    heading = 0.0
    cursor = origin

    for length, angle in zip(lengths, angles, strict=False):
        heading += angle
        offset = Vec2(cos(heading) * length, sin(heading) * length)
        cursor = cursor + offset
        positions.append(cursor)

    return positions


# <summary>
# Mutable planar articulated chain backed by local joint angles.
# </summary>
@dataclass(slots=True)
class KinematicChain:
    """Mutable planar articulated chain backed by local joint angles."""

    origin: Vec2
    lengths: list[float]
    angles: list[float]

    # <summary>
    # Initialize missing local angles to zero.
    # </summary>
    def __post_init__(self) -> None:
        if len(self.angles) < len(self.lengths):
            self.angles.extend(0.0 for _ in range(len(self.lengths) - len(self.angles)))
        elif len(self.angles) > len(self.lengths):
            del self.angles[len(self.lengths) :]

    # <summary>
    # Create a chain with optional local angles.
    # </summary>
    # <param name="origin">World-space chain root.</param>
    # <param name="lengths">Segment lengths in order from root to end effector.</param>
    # <param name="angles">Optional local joint angles in radians.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    @classmethod
    def from_lengths(
        cls,
        origin: Vec2,
        lengths: Sequence[float],
        angles: Sequence[float] | None = None,
    ) -> "KinematicChain":
        local_angles = [0.0 for _ in lengths] if angles is None else list(angles)
        return cls(origin=origin.copy(), lengths=list(lengths), angles=local_angles)

    # <summary>
    # Return all world-space joint positions.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def joint_positions(self) -> list[Vec2]:
        return forward_chain(self.origin, self.lengths, self.angles)

    # <summary>
    # Return the current world-space end-effector position.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def end_effector(self) -> Vec2:
        return self.joint_positions()[-1]

    # <summary>
    # Replace one local joint angle.
    # </summary>
    # <param name="index">Joint index to update.</param>
    # <param name="angle">New local angle in radians.</param>
    def set_angle(self, index: int, angle: float) -> None:
        self.angles[index] = angle

    # <summary>
    # Add a delta to one local joint angle.
    # </summary>
    # <param name="index">Joint index to update.</param>
    # <param name="delta">Angle delta in radians.</param>
    def add_angle(self, index: int, delta: float) -> None:
        self.angles[index] += delta


# <summary>
# Return the final point from a forward-kinematics chain.
# </summary>
# <param name="origin">World-space chain root.</param>
# <param name="lengths">Segment lengths in order from root to end effector.</param>
# <param name="angles">Local joint angles in radians.</param>
# <returns>Computed result described by the return type annotation.</returns>
def end_effector_position(origin: Vec2, lengths: list[float], angles: list[float]) -> Vec2:
    """Return the final point from a forward-kinematics chain."""

    return forward_chain(origin, lengths, angles)[-1]


# <summary>
# Return segment lengths measured from world-space joint positions.
# </summary>
# <param name="positions">World-space joint positions.</param>
# <returns>Computed result described by the return type annotation.</returns>
def measured_segment_lengths(positions: Sequence[Vec2]) -> list[float]:
    """Return segment lengths measured from world-space joint positions."""

    return [
        positions[index].distance_to(positions[index + 1])
        for index in range(len(positions) - 1)
    ]
