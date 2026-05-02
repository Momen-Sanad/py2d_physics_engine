# <file>
# <summary>
# Forward-kinematics helpers for articulated 2D chains.
# </summary>
# </file>
"""Forward-kinematics helpers for articulated 2D chains."""

from math import cos, sin

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
