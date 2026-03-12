"""Constraint-solving helpers for the PBD and rope stages."""

from .math2d import Vec2


def solve_distance_constraint(
    a_position: Vec2,
    b_position: Vec2,
    rest_length: float,
    a_inverse_mass: float,
    b_inverse_mass: float,
    stiffness: float = 1.0,
) -> tuple[Vec2, Vec2]:
    """Return positional corrections for a simple PBD distance constraint."""

    delta = b_position - a_position
    distance = delta.length()
    if distance == 0.0:
        return Vec2(), Vec2()

    total_inverse_mass = a_inverse_mass + b_inverse_mass
    if total_inverse_mass == 0.0:
        return Vec2(), Vec2()

    direction = delta / distance
    error = distance - rest_length
    correction = direction * (stiffness * error / total_inverse_mass)
    return correction * a_inverse_mass, correction * -b_inverse_mass
