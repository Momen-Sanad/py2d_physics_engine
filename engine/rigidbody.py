"""Rigid-body primitives for 2D motion and collision experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

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
            self.force.x += applied_force.x
            self.force.y += applied_force.y

    def clear_forces(self) -> None:
        self.force.reset()
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
    sleeping: bool = False
    sleep_timer: float = 0.0
    contact_count: int = 0

    @property
    def inverse_mass(self) -> float:
        if self.is_static or self.mass == 0.0:
            return 0.0
        return 1.0 / self.mass

    def apply_force(self, applied_force: Vec2) -> None:
        if not self.is_static:
            if applied_force.x != 0.0 or applied_force.y != 0.0:
                self.wake()
            self.force.x += applied_force.x
            self.force.y += applied_force.y

    def speed_squared(self) -> float:
        velocity = self.velocity
        return velocity.x * velocity.x + velocity.y * velocity.y

    def wake(self) -> None:
        self.sleeping = False
        self.sleep_timer = 0.0

    def sleep(self) -> None:
        self.sleeping = True
        self.sleep_timer = 0.0
        self.velocity.reset()
        self.force.reset()

    def step(
        self,
        dt: float,
        gravity: Vec2 | None = None,
        linear_damping: float = 0.0,
    ) -> None:
        """Advance the circle body by one timestep."""

        if self.is_static or self.sleeping:
            self.clear_forces()
            return

        gravity_x = 0.0 if gravity is None else gravity.x
        gravity_y = 0.0 if gravity is None else gravity.y
        inverse_mass = self.inverse_mass
        velocity = self.velocity
        force = self.force
        position = self.position

        velocity.x += (gravity_x + force.x * inverse_mass) * dt
        velocity.y += (gravity_y + force.y * inverse_mass) * dt

        if linear_damping > 0.0:
            damping_factor = max(0.0, 1.0 - linear_damping * dt)
            velocity.x *= damping_factor
            velocity.y *= damping_factor

        position.x += velocity.x * dt
        position.y += velocity.y * dt
        self.clear_forces()

    def clear_forces(self) -> None:
        self.force.reset()


def step_circle_bodies(
    bodies: Iterable[CircleBody],
    dt: float,
    gravity: Vec2 | None = None,
    linear_damping: float = 0.0,
) -> None:
    """Advance many circle bodies with a flat loop."""

    gravity_x = 0.0 if gravity is None else gravity.x
    gravity_y = 0.0 if gravity is None else gravity.y
    damping_factor = max(0.0, 1.0 - linear_damping * dt) if linear_damping > 0.0 else 1.0
    use_damping = linear_damping > 0.0

    for body in bodies:
        body.contact_count = 0
        if body.is_static or body.sleeping:
            body.force.reset()
            continue

        inverse_mass = body.inverse_mass
        velocity = body.velocity
        force = body.force
        position = body.position

        velocity.x += (gravity_x + force.x * inverse_mass) * dt
        velocity.y += (gravity_y + force.y * inverse_mass) * dt

        if use_damping:
            velocity.x *= damping_factor
            velocity.y *= damping_factor

        position.x += velocity.x * dt
        position.y += velocity.y * dt
        force.reset()


def update_sleeping(
    bodies: Iterable[CircleBody],
    dt: float,
    linear_speed_threshold: float,
    sleep_delay: float,
) -> None:
    """Put resting bodies to sleep after sustained low-speed contact."""

    threshold_sq = linear_speed_threshold * linear_speed_threshold

    for body in bodies:
        if body.is_static or body.sleeping:
            continue

        if body.contact_count > 0 and body.speed_squared() <= threshold_sq:
            body.sleep_timer += dt
            if body.sleep_timer >= sleep_delay:
                body.sleep()
        else:
            body.sleep_timer = 0.0
