"""Reusable external force helpers."""

from .math2d import Vec2


def gravity_force(mass: float, gravity: Vec2) -> Vec2:
    return gravity * mass


def drag_force(velocity: Vec2, coefficient: float) -> Vec2:
    return velocity * -coefficient


def accumulate_forces(*forces: Vec2) -> Vec2:
    total = Vec2()
    for force in forces:
        total += force
    return total
