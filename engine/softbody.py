"""Pressure-based soft-body helpers built from particles and springs."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, pi, sin

from .math2d import Vec2
from .particle import Particle, step_particles
from .spring import Spring


def polygon_area_from_particles(particles: list[Particle]) -> float:
    """Return polygon area directly from particle positions without list copies."""

    particle_count = len(particles)
    if particle_count < 3:
        return 0.0

    area_sum = 0.0
    previous = particles[-1].position
    for index in range(particle_count):
        current = particles[index].position
        area_sum += previous.x * current.y - previous.y * current.x
        previous = current
    return abs(area_sum) * 0.5


@dataclass(slots=True)
class SoftBody:
    """Closed spring loop with a simple internal pressure term."""

    particles: list[Particle]
    springs: list[Spring]
    pressure_coefficient: float
    initial_area: float

    @classmethod
    def circle(
        cls,
        center: Vec2,
        radius: float,
        particle_count: int,
        particle_mass: float,
        particle_radius: float,
        stiffness: float,
        damping: float,
        pressure_coefficient: float,
    ) -> "SoftBody":
        particles: list[Particle] = []

        for index in range(particle_count):
            angle = index * (2.0 * pi / particle_count)
            direction = Vec2(sin(angle), -cos(angle))
            particles.append(
                Particle(
                    position=center + direction * radius,
                    mass=particle_mass,
                    radius=particle_radius,
                )
            )

        springs = [
            Spring.between(
                particles[index],
                particles[(index + 1) % particle_count],
                stiffness=stiffness,
                damping=damping,
            )
            for index in range(particle_count)
        ]

        return cls(
            particles=particles,
            springs=springs,
            pressure_coefficient=pressure_coefficient,
            initial_area=polygon_area_from_particles(particles),
        )

    def area(self) -> float:
        return polygon_area_from_particles(self.particles)

    def step(
        self,
        dt: float,
        gravity: Vec2,
        linear_damping: float = 0.0,
    ) -> None:
        current_area = max(self.area(), 1e-6)
        pressure = self.pressure_coefficient * (self.initial_area / current_area)
        pressure_scale = pressure * 0.5

        for spring in self.springs:
            particle_a = spring.particle_a
            particle_b = spring.particle_b
            dx = particle_b.position.x - particle_a.position.x
            dy = particle_b.position.y - particle_a.position.y
            distance_sq = dx * dx + dy * dy
            if distance_sq == 0.0:
                continue

            distance = hypot(dx, dy)
            inverse_distance = 1.0 / distance
            normal_x = dx * inverse_distance
            normal_y = dy * inverse_distance

            relative_velocity_x = particle_b.velocity.x - particle_a.velocity.x
            relative_velocity_y = particle_b.velocity.y - particle_a.velocity.y
            spring_term = spring.stiffness * (distance - spring.rest_length)
            damping_term = spring.damping * (
                relative_velocity_x * normal_x + relative_velocity_y * normal_y
            )
            spring_force_x = normal_x * (spring_term + damping_term)
            spring_force_y = normal_y * (spring_term + damping_term)

            pressure_force_x = dy * pressure_scale
            pressure_force_y = -dx * pressure_scale

            particle_a.force.x += spring_force_x + pressure_force_x
            particle_a.force.y += spring_force_y + pressure_force_y
            particle_b.force.x += -spring_force_x + pressure_force_x
            particle_b.force.y += -spring_force_y + pressure_force_y

        step_particles(self.particles, dt, gravity=gravity, linear_damping=linear_damping)
