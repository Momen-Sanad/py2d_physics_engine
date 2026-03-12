"""Rigid-body primitives for 2D motion and collision experiments."""

from __future__ import annotations

from dataclasses import dataclass, field

from .math2d import Vec2


@dataclass(slots=True)
class RigidBody2D:
    """Minimal rigid body state for the first collision scenes."""

    position: Vec2
    velocity: Vec2 = field(default_factory=Vec2)
    force: Vec2 = field(default_factory=Vec2)
    angle: float = 0.0
    angular_velocity: float = 0.0
    torque: float = 0.0
    mass: float = 1.0
    inertia: float = 1.0
    is_static: bool = False

    @property
    def inverse_mass(self) -> float:
        if self.is_static or self.mass == 0.0:
            return 0.0
        return 1.0 / self.mass

    @property
    def inverse_inertia(self) -> float:
        if self.is_static or self.inertia == 0.0:
            return 0.0
        return 1.0 / self.inertia

    def apply_force(self, applied_force: Vec2) -> None:
        if not self.is_static:
            self.force += applied_force

    def clear_forces(self) -> None:
        self.force = Vec2()
        self.torque = 0.0
