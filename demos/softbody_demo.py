"""Pressure-ball demo extracted from the old soft-ball reference scene."""

from __future__ import annotations

from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.math2d import Vec2
from engine.softbody import SoftBody


WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
FIXED_DT = 1.0 / 120.0
GRAVITY = Vec2(0.0, 700.0)
LINEAR_DAMPING = 0.02
BOUNCE = 0.75
FLOOR_FRICTION = 0.20


def build_softbody() -> SoftBody:
    return SoftBody.circle(
        center=Vec2(WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.35),
        radius=60.0,
        particle_count=10,
        particle_mass=1.0,
        particle_radius=4.0,
        stiffness=120.0,
        damping=10.0,
        pressure_coefficient=35.0,
    )


def constrain_particles(softbody: SoftBody, dt: float) -> None:
    particles = softbody.particles

    bounce = BOUNCE
    width = WINDOW_WIDTH
    height = WINDOW_HEIGHT
    friction_step = max(0.0, 1.0 - FLOOR_FRICTION * dt)

    for particle in particles:
        r = particle.radius
        position = particle.position
        velocity = particle.velocity
        x = position.x
        y = position.y
        vx = velocity.x
        vy = velocity.y

        right = width - r
        bottom = height - r

        if x < r:
            x = r
            vx = abs(vx) * bounce
        elif x > right:
            x = right
            vx = -abs(vx) * bounce

        if y < r:
            y = r
            vy = abs(vy) * bounce
        elif y > bottom:
            y = bottom
            vy = -abs(vy) * bounce
            vx *= friction_step

        position.x = x
        position.y = y
        velocity.x = vx
        velocity.y = vy


def fill_polygon_buffer(softbody: SoftBody, point_buffer: list[list[float]]) -> None:
    particles = softbody.particles
    for index, particle in enumerate(particles):
        point_buffer[index][0] = particle.position.x
        point_buffer[index][1] = particle.position.y


def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Soft Body Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=5)
    overlay = PerformanceOverlay()

    softbody = build_softbody()
    point_buffer = [[0.0, 0.0] for _ in range(len(softbody.particles))]
    paused = False
    running = True

    while running:
        frame_time = min(clock.tick() / 1000.0, 0.25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    softbody = build_softbody()
                    point_buffer = [[0.0, 0.0] for _ in range(len(softbody.particles))]
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            for _ in range(simulation_clock.consume(frame_time)):
                softbody.step(FIXED_DT, gravity=GRAVITY, linear_damping=LINEAR_DAMPING)
                constrain_particles(softbody, FIXED_DT)

        screen.fill((250, 250, 245))
        fill_polygon_buffer(softbody, point_buffer)
        if len(point_buffer) >= 3:
            pygame.draw.polygon(screen, (186, 219, 204), point_buffer)

        for spring in softbody.springs:
            pygame.draw.line(
                screen,
                (40, 40, 40),
                spring.particle_a.position.to_tuple(),
                spring.particle_b.position.to_tuple(),
                2,
            )

        for particle in softbody.particles:
            pygame.draw.circle(
                screen,
                (178, 60, 60),
                particle.position.to_tuple(),
                int(particle.radius),
            )

        overlay.draw(screen, frame_time, FIXED_DT)
        pygame.display.flip()

    pygame.quit()
