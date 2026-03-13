"""Spring-net demo extracted from the old falling-net reference scene."""

from __future__ import annotations

from engine.core import SimulationClock
from engine.math2d import Vec2
from engine.particle import Particle
from engine.spring import Spring


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
TARGET_FPS = 60
FIXED_DT = 1.0 / 120.0
GRAVITY = Vec2(0.0, 900.0)
LINEAR_DAMPING = 1.2
SPRING_STIFFNESS = 140.0
SPRING_DAMPING = 12.0
PARTICLE_RADIUS = 4.0
BOUNCE = 0.4
ROWS = 10
COLUMNS = 12
SPACING = 28.0


def build_cloth() -> tuple[list[Particle], list[Spring]]:
    particles: list[Particle] = []
    grid: list[list[Particle]] = []
    springs: list[Spring] = []

    origin = Vec2(
        WINDOW_WIDTH * 0.5 - ((COLUMNS - 1) * SPACING) * 0.5,
        90.0,
    )

    for row_index in range(ROWS):
        row: list[Particle] = []
        for column_index in range(COLUMNS):
            pinned = row_index == 0 and column_index in {0, COLUMNS - 1}
            particle = Particle(
                position=Vec2(
                    origin.x + column_index * SPACING,
                    origin.y + row_index * SPACING,
                ),
                mass=1.0,
                radius=PARTICLE_RADIUS,
                pinned=pinned,
            )
            particles.append(particle)
            row.append(particle)
        grid.append(row)

    for row_index in range(ROWS):
        for column_index in range(COLUMNS):
            if column_index < COLUMNS - 1:
                springs.append(
                    Spring.between(
                        grid[row_index][column_index],
                        grid[row_index][column_index + 1],
                        stiffness=SPRING_STIFFNESS,
                        damping=SPRING_DAMPING,
                    )
                )
            if row_index < ROWS - 1:
                springs.append(
                    Spring.between(
                        grid[row_index][column_index],
                        grid[row_index + 1][column_index],
                        stiffness=SPRING_STIFFNESS,
                        damping=SPRING_DAMPING,
                    )
                )

    return particles, springs


def constrain_particle(particle: Particle) -> None:
    if particle.pinned:
        return

    x, y = particle.position.x, particle.position.y
    vx, vy = particle.velocity.x, particle.velocity.y

    if x < particle.radius:
        x = particle.radius
        vx = abs(vx) * BOUNCE
    elif x > WINDOW_WIDTH - particle.radius:
        x = WINDOW_WIDTH - particle.radius
        vx = -abs(vx) * BOUNCE

    if y > WINDOW_HEIGHT - particle.radius:
        y = WINDOW_HEIGHT - particle.radius
        vy = -abs(vy) * BOUNCE

    particle.position = Vec2(x, y)
    particle.velocity = Vec2(vx, vy)


def step_scene(particles: list[Particle], springs: list[Spring], dt: float) -> None:
    for spring in springs:
        spring.apply()

    for particle in particles:
        particle.step(dt, gravity=GRAVITY, linear_damping=LINEAR_DAMPING)
        constrain_particle(particle)


def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Spring Net Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=5)

    particles, springs = build_cloth()
    paused = False
    running = True

    while running:
        frame_time = min(clock.tick(TARGET_FPS) / 1000.0, 0.25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    particles, springs = build_cloth()
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            for _ in range(simulation_clock.consume(frame_time)):
                step_scene(particles, springs, FIXED_DT)

        screen.fill((248, 249, 250))
        for spring in springs:
            pygame.draw.line(
                screen,
                (40, 40, 40),
                spring.particle_a.position.to_tuple(),
                spring.particle_b.position.to_tuple(),
                1,
            )

        for particle in particles:
            color = (201, 62, 62) if particle.pinned else (48, 143, 94)
            pygame.draw.circle(
                screen,
                color,
                particle.position.to_tuple(),
                int(particle.radius),
            )

        pygame.display.flip()

    pygame.quit()
