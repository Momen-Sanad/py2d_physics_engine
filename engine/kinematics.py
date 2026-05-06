# <file>
# <summary>
# Forward-kinematics helpers for articulated 2D chains.
# </summary>
# </file>
"""Forward-kinematics helpers for articulated 2D chains."""

from dataclasses import dataclass
from math import atan2, cos, sin
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
    # Solve this chain toward a target using CCD inverse kinematics.
    # </summary>
    # <param name="target">World-space target for the end effector.</param>
    # <param name="iterations">Maximum CCD passes to run.</param>
    # <param name="tolerance">Acceptable end-effector distance from target.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def solve_ik(
        self,
        target: Vec2,
        iterations: int = 16,
        tolerance: float = 1.0,
    ) -> "IKResult":
        return solve_ccd_ik(self, target, iterations=iterations, tolerance=tolerance)


# <summary>
# Result returned by an inverse-kinematics solve pass.
# </summary>
@dataclass(slots=True)
class IKResult:
    """Result returned by an inverse-kinematics solve pass."""

    reached: bool
    target_reachable: bool
    iterations: int
    error: float


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


# <summary>
# Solve a planar chain toward a target using cyclic coordinate descent.
# </summary>
# <param name="chain">Kinematic chain whose local angles are updated.</param>
# <param name="target">World-space target for the end effector.</param>
# <param name="iterations">Maximum CCD passes to run.</param>
# <param name="tolerance">Acceptable end-effector distance from target.</param>
# <returns>Computed result described by the return type annotation.</returns>
def solve_ccd_ik(
    chain: KinematicChain,
    target: Vec2,
    iterations: int = 16,
    tolerance: float = 1.0,
) -> IKResult:
    """Solve a planar chain toward a target using cyclic coordinate descent."""

    max_iterations = max(0, min(iterations, 128))
    acceptable_error = max(0.0, tolerance)
    total_length = sum(chain.lengths)
    target_distance = chain.origin.distance_to(target)

    if len(chain.lengths) == 0:
        error = chain.origin.distance_to(target)
        return IKResult(
            reached=error <= acceptable_error,
            target_reachable=error <= acceptable_error,
            iterations=0,
            error=error,
        )

    if target_distance > total_length:
        _extend_chain_toward_target(chain, target)
        error = chain.end_effector().distance_to(target)
        return IKResult(
            reached=error <= acceptable_error,
            target_reachable=False,
            iterations=0,
            error=error,
        )

    positions = chain.joint_positions()
    error = positions[-1].distance_to(target)
    if error <= acceptable_error:
        return IKResult(True, True, 0, error)

    completed_iterations = 0
    for completed_iterations in range(1, max_iterations + 1):
        for joint_index in range(len(chain.lengths) - 1, -1, -1):
            positions = chain.joint_positions()
            joint_position = positions[joint_index]
            end_position = positions[-1]

            to_end = end_position - joint_position
            to_target = target - joint_position
            if to_end.length_squared() == 0.0 or to_target.length_squared() == 0.0:
                continue

            chain.angles[joint_index] += _signed_angle_between(to_end, to_target)

        positions = chain.joint_positions()
        error = positions[-1].distance_to(target)
        if error <= acceptable_error:
            break

    return IKResult(
        reached=error <= acceptable_error,
        target_reachable=True,
        iterations=completed_iterations,
        error=error,
    )


# <summary>
# Return the signed angle from one vector to another.
# </summary>
# <param name="source">Starting direction vector.</param>
# <param name="target">Target direction vector.</param>
# <returns>Computed result described by the return type annotation.</returns>
def _signed_angle_between(source: Vec2, target: Vec2) -> float:
    return atan2(source.cross(target), source.dot(target))


# <summary>
# Aim every segment in the chain toward an unreachable target.
# </summary>
# <param name="chain">Kinematic chain whose local angles are updated.</param>
# <param name="target">World-space target for the end effector.</param>
def _extend_chain_toward_target(chain: KinematicChain, target: Vec2) -> None:
    direction = target - chain.origin
    if direction.length_squared() == 0.0:
        return

    chain.angles[0] = atan2(direction.y, direction.x)
    for index in range(1, len(chain.angles)):
        chain.angles[index] = 0.0
