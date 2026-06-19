"""UI-layer particle effects for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from engine.forces import drag_force
from engine.math2d import Vec2
from engine.particle import Particle, step_particles

from . import config


CONFETTI_COLORS = (
    (255, 87, 99),
    (255, 207, 64),
    (73, 196, 255),
    (91, 217, 132),
    (178, 121, 255),
    (255, 142, 72),
)


@dataclass(slots=True)
class UiConfetti:
    """Confetti particles stepped independently from paused gameplay."""

    particles: list[Particle] = field(default_factory=list)
    colors: dict[int, tuple[int, int, int]] = field(default_factory=dict)

    def clear(self) -> None:
        self.particles.clear()
        self.colors.clear()


def spawn_victory_confetti(
    confetti: UiConfetti,
    rng: Random,
    count: int = config.VICTORY_CONFETTI_COUNT,
) -> None:
    """Spawn a game-over confetti burst in logical screen coordinates."""

    confetti.clear()
    for _ in range(count):
        side = -1.0 if rng.random() < 0.5 else 1.0
        origin_x = config.WINDOW_WIDTH * (0.25 if side < 0.0 else 0.75)
        particle = Particle(
            position=Vec2(origin_x + rng.uniform(-70.0, 70.0), rng.uniform(28.0, 96.0)),
            velocity=Vec2(
                rng.uniform(60.0, 230.0) * -side,
                rng.uniform(-220.0, -60.0),
            ),
            mass=0.8,
            radius=rng.uniform(2.0, 4.4),
            lifetime=rng.uniform(2.2, 4.2),
            restitution=0.1,
        )
        confetti.particles.append(particle)
        confetti.colors[id(particle)] = CONFETTI_COLORS[rng.randrange(len(CONFETTI_COLORS))]


def step_ui_confetti(confetti: UiConfetti, dt: float) -> None:
    """Advance confetti even when the game simulation itself is paused."""

    for particle in confetti.particles:
        particle.apply_force(drag_force(particle.velocity, 0.18))

    step_particles(
        confetti.particles,
        dt,
        gravity=Vec2(0.0, 360.0),
        linear_damping=0.05,
    )

    write_index = 0
    for particle in confetti.particles:
        expired = particle.lifetime is not None and particle.lifetime <= 0.0
        outside = particle.position.y > config.WINDOW_HEIGHT + 32.0
        if expired or outside:
            confetti.colors.pop(id(particle), None)
            continue
        confetti.particles[write_index] = particle
        write_index += 1

    if write_index < len(confetti.particles):
        del confetti.particles[write_index:]


def draw_ui_confetti(surface, confetti: UiConfetti) -> None:
    """Draw UI-layer confetti particles over the paused game scene."""

    import pygame

    for particle in confetti.particles:
        color = confetti.colors.get(id(particle), (255, 255, 255))
        rect = pygame.Rect(0, 0, max(2, int(particle.radius * 2.0)), max(2, int(particle.radius)))
        rect.center = particle.position.to_tuple()
        pygame.draw.rect(surface, color, rect, border_radius=1)
