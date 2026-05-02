# <file>
# <summary>
# Reusable external force helpers.
# </summary>
# </file>
"""Reusable external force helpers."""

from .math2d import Vec2


# <summary>
# Calculate a gravity force from mass and acceleration.
# </summary>
# <param name="mass">Mass value used by the physics calculation.</param>
# <param name="gravity">Optional gravity acceleration vector.</param>
# <returns>Computed result described by the return type annotation.</returns>
def gravity_force(mass: float, gravity: Vec2) -> Vec2:
    return gravity * mass


# <summary>
# Calculate a linear drag force opposite velocity.
# </summary>
# <param name="velocity">Velocity vector used by the calculation.</param>
# <param name="coefficient">Input value for coefficient.</param>
# <returns>Computed result described by the return type annotation.</returns>
def drag_force(velocity: Vec2, coefficient: float) -> Vec2:
    return velocity * -coefficient


# <summary>
# Sum multiple 2D force vectors.
# </summary>
# <param name="forces">Input value for forces.</param>
# <returns>Computed result described by the return type annotation.</returns>
def accumulate_forces(*forces: Vec2) -> Vec2:
    total = Vec2()
    for force in forces:
        total += force
    return total
