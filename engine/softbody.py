"""Pressure-based soft-body helpers built from particles and springs."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin, cos

from .math2d import Vec2
from .particle import Particle
from .spring import Spring


def polygon_area(points: list[Vec2]) -> float:
    """Return the absolute polygon area using the shoelace formula."""

    if len(points) < 3:
        return 0.0

    area_sum = 0.0
    for index, point in enumerate(points):
        next_point = points[(index + 1) % len(points)]
        area_sum += point.cross(next_point)
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
            initial_area=polygon_area([particle.position for particle in particles]),
        )

    def area(self) -> float:
        return polygon_area([particle.position for particle in self.particles])

    def step(
        self,
        dt: float,
        gravity: Vec2,
        linear_damping: float = 0.0,
    ) -> None:
        current_area = max(self.area(), 1e-6)
        pressure = self.pressure_coefficient * (self.initial_area / current_area)

        for spring in self.springs:
            force_a, force_b = spring.force()
            pressure_force = spring.normal() * (pressure * spring.length() * 0.5)
            spring.particle_a.apply_force(force_a + pressure_force)
            spring.particle_b.apply_force(force_b + pressure_force)

        for particle in self.particles:
            particle.step(dt, gravity=gravity, linear_damping=linear_damping)
