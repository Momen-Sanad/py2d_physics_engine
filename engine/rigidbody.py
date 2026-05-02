"""Rigid-body primitives for 2D motion and collision experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .math3d import Mat3, Quaternion, Vec3
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

    def apply_torque(self, applied_torque: float) -> None:
        if not self.is_static:
            self.torque += applied_torque

    def apply_force_at_point(self, applied_force: Vec2, world_point: Vec2) -> None:
        if self.is_static:
            return

        lever_arm = world_point - self.position
        self.apply_force(applied_force)
        self.torque += lever_arm.cross(applied_force)

    def apply_impulse(self, impulse: Vec2, world_point: Vec2 | None = None) -> None:
        if self.is_static:
            return

        inverse_mass = self.inverse_mass
        self.velocity.x += impulse.x * inverse_mass
        self.velocity.y += impulse.y * inverse_mass
        if world_point is not None:
            lever_arm = world_point - self.position
            self.angular_velocity += lever_arm.cross(impulse) * self.inverse_inertia

    def step(
        self,
        dt: float,
        gravity: Vec2 | None = None,
        linear_damping: float = 0.0,
        angular_damping: float = 0.0,
    ) -> None:
        """Advance linear and angular 2D state with semi-implicit Euler."""

        if self.is_static:
            self.clear_forces()
            return

        gravity_x = 0.0 if gravity is None else gravity.x
        gravity_y = 0.0 if gravity is None else gravity.y
        inverse_mass = self.inverse_mass

        self.velocity.x += (gravity_x + self.force.x * inverse_mass) * dt
        self.velocity.y += (gravity_y + self.force.y * inverse_mass) * dt
        if linear_damping > 0.0:
            damping_factor = max(0.0, 1.0 - linear_damping * dt)
            self.velocity.x *= damping_factor
            self.velocity.y *= damping_factor

        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt

        self.angular_velocity += self.torque * self.inverse_inertia * dt
        if angular_damping > 0.0:
            self.angular_velocity *= max(0.0, 1.0 - angular_damping * dt)
        self.angle += self.angular_velocity * dt
        self.clear_forces()

    def clear_forces(self) -> None:
        self.force.reset()
        self.torque = 0.0


@dataclass(slots=True)
class RigidBody3D:
    """Torque-driven rigid body in principal/body frame coordinates."""

    position: Vec3
    velocity: Vec3 = field(default_factory=Vec3)
    force: Vec3 = field(default_factory=Vec3)
    orientation: Quaternion = field(default_factory=Quaternion)
    angular_velocity: Vec3 = field(default_factory=Vec3)
    torque: Vec3 = field(default_factory=Vec3)
    mass: float = 1.0
    inertia_body: Mat3 = field(default_factory=Mat3.identity)
    linear_damping: float = 0.0
    angular_damping: float = 0.0
    is_static: bool = False

    @property
    def inverse_mass(self) -> float:
        if self.is_static or self.mass == 0.0:
            return 0.0
        return 1.0 / self.mass

    @property
    def inverse_inertia_body(self) -> Mat3:
        if self.is_static:
            return Mat3.zero()
        try:
            return self.inertia_body.inverse()
        except ValueError:
            return Mat3.zero()

    def rotation_matrix(self) -> Mat3:
        return self.orientation.to_rotation_matrix()

    def angular_momentum(self) -> Vec3:
        return self.inertia_body @ self.angular_velocity

    def angular_acceleration(self) -> Vec3:
        angular_momentum = self.angular_momentum()
        gyroscopic_term = self.angular_velocity.cross(angular_momentum)
        return self.inverse_inertia_body @ (self.torque - gyroscopic_term)

    def apply_force(self, applied_force: Vec3) -> None:
        if not self.is_static:
            self.force += applied_force

    def apply_torque(self, applied_torque: Vec3) -> None:
        if not self.is_static:
            self.torque += applied_torque

    def apply_force_at_point(self, applied_force: Vec3, world_point: Vec3) -> None:
        if self.is_static:
            return

        lever_arm = world_point - self.position
        self.force += applied_force
        self.torque += lever_arm.cross(applied_force)

    def step(self, dt: float, gravity: Vec3 | None = None) -> None:
        """Advance linear and rotational state with semi-implicit Euler."""

        if self.is_static:
            self.clear_forces()
            return

        inverse_mass = self.inverse_mass
        acceleration = self.force * inverse_mass
        if gravity is not None:
            acceleration += gravity

        self.velocity.add_scaled(acceleration, dt)
        if self.linear_damping > 0.0:
            self.velocity *= max(0.0, 1.0 - self.linear_damping * dt)
        self.position.add_scaled(self.velocity, dt)

        alpha = self.angular_acceleration()
        self.angular_velocity.add_scaled(alpha, dt)
        if self.angular_damping > 0.0:
            self.angular_velocity *= max(0.0, 1.0 - self.angular_damping * dt)

        omega_q = Quaternion(
            0.0,
            self.angular_velocity.x,
            self.angular_velocity.y,
            self.angular_velocity.z,
        )
        dq_dt = self.orientation * omega_q * 0.5
        self.orientation = (self.orientation + dq_dt * dt).normalize()
        self.clear_forces()

    def clear_forces(self) -> None:
        self.force.reset()
        self.torque.reset()


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
