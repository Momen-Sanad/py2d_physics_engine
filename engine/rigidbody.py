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


@dataclass(slots=True)
class CircleBody:
    """Simple circle body extracted from the bouncing-ball reference."""

    position: Vec2
    radius: float
    velocity: Vec2 = field(default_factory=Vec2)
    force: Vec2 = field(default_factory=Vec2)
    mass: float = 1.0
    restitution: float = 1.0
    is_static: bool = False

    @property
    def inverse_mass(self) -> float:
        if self.is_static or self.mass == 0.0:
            return 0.0
        return 1.0 / self.mass

    def apply_force(self, applied_force: Vec2) -> None:
        if not self.is_static:
            self.force += applied_force

    def step(
        self,
        dt: float,
        gravity: Vec2 | None = None,
        linear_damping: float = 0.0,
    ) -> None:
        """Advance the circle body by one timestep."""

        if self.is_static:
            self.clear_forces()
            return

        gravity_force = gravity if gravity is not None else Vec2()
        acceleration = gravity_force + self.force * self.inverse_mass
        self.velocity = self.velocity + acceleration * dt

        if linear_damping > 0.0:
            damping_factor = max(0.0, 1.0 - linear_damping * dt)
            self.velocity = self.velocity * damping_factor

        self.position = self.position + self.velocity * dt
        self.clear_forces()

    def clear_forces(self) -> None:
        self.force = Vec2()
