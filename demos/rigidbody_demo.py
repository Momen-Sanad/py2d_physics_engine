"""Circle collision demo"""

from __future__ import annotations

from math import ceil

from engine.broadphase import SpatialHashGrid
from engine.collisions import resolve_circle_collision
from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.math2d import Vec2
from engine.rigidbody import CircleBody, step_circle_bodies, update_sleeping


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
FIXED_DT = 1.0 / 120.0
GRAVITY = Vec2(0.0, 900.0)
LINEAR_DAMPING = 0.05
FLOOR_FRICTION = 6.0
BODY_COUNT = 200
BODY_RADIUS = 8.0
BODY_RESTITUTION = 0.92
BODY_SPACING = 20.0
SPAWN_TOP = 50.0
BROADPHASE_CELL_SIZE = 32.0
SLEEP_ENABLED = True
SLEEP_SPEED_THRESHOLD = 35.0
SLEEP_DELAY = 0.75
WAKE_SPEED_THRESHOLD = 65.0


def build_bodies() -> list[CircleBody]:
    radius = BODY_RADIUS
    spacing = BODY_SPACING
    width_available = WINDOW_WIDTH - 2.0 * radius - 40.0
    columns = max(1, int(width_available // spacing))
    rows = ceil(BODY_COUNT / columns)
    total_width = (columns - 1) * spacing
    start_x = 0.5 * (WINDOW_WIDTH - total_width)
    start_y = SPAWN_TOP
    mass = radius * radius
    bodies: list[CircleBody] = []

    for index in range(BODY_COUNT):
        row = index // columns
        column = index % columns
        stagger = radius if row % 2 else 0.0
        x = start_x + column * spacing + stagger
        y = start_y + row * spacing

        if x > WINDOW_WIDTH - radius:
            continue

        lateral_band = (column % 5) - 2
        vertical_band = row % 3
        velocity = Vec2(lateral_band * 12.0, -vertical_band * 10.0)

        bodies.append(
            CircleBody(
                position=Vec2(x, y),
                velocity=velocity,
                radius=radius,
                mass=mass,
                restitution=BODY_RESTITUTION,
            )
        )

    return bodies


def contain_body(body: CircleBody, dt: float) -> None:
    position = body.position
    velocity = body.velocity
    radius = body.radius
    restitution = body.restitution
    touched_boundary = False
    x = position.x
    y = position.y
    vx = velocity.x
    vy = velocity.y

    if x < radius:
        x = radius
        vx = abs(vx) * restitution
        touched_boundary = True
    elif x > WINDOW_WIDTH - radius:
        x = WINDOW_WIDTH - radius
        vx = -abs(vx) * restitution
        touched_boundary = True

    if y < radius:
        y = radius
        vy = abs(vy) * restitution
        touched_boundary = True
    elif y > WINDOW_HEIGHT - radius:
        y = WINDOW_HEIGHT - radius
        vy = -abs(vy) * restitution
        vx *= max(0.0, 1.0 - FLOOR_FRICTION * dt)
        touched_boundary = True

    position.x = x
    position.y = y
    velocity.x = vx
    velocity.y = vy

    if touched_boundary:
        body.contact_count += 1


def step_scene(bodies: list[CircleBody], broadphase: SpatialHashGrid, dt: float) -> None:
    step_circle_bodies(bodies, dt, gravity=GRAVITY, linear_damping=LINEAR_DAMPING)
    for body in bodies:
        contain_body(body, dt)

    broadphase.rebuild_circles(bodies)
    resolve = resolve_circle_collision
    wake_threshold_sq = WAKE_SPEED_THRESHOLD * WAKE_SPEED_THRESHOLD
    for index_a, index_b in broadphase.iter_pairs():
        body_a = bodies[index_a]
        body_b = bodies[index_b]

        if body_a.sleeping and body_b.sleeping:
            continue

        if body_a.sleeping and body_b.speed_squared() >= wake_threshold_sq:
            body_a.wake()
        if body_b.sleeping and body_a.speed_squared() >= wake_threshold_sq:
            body_b.wake()

        if resolve(body_a, body_b):
            body_a.contact_count += 1
            body_b.contact_count += 1

    if SLEEP_ENABLED:
        update_sleeping(
            bodies,
            dt,
            linear_speed_threshold=SLEEP_SPEED_THRESHOLD,
            sleep_delay=SLEEP_DELAY,
        )


def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rigid Body Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=5)
    overlay = PerformanceOverlay()

    bodies = build_bodies()
    broadphase = SpatialHashGrid(cell_size=BROADPHASE_CELL_SIZE)
    paused = False
    running = True

    while running:
        frame_time = min(clock.tick() / 1000.0, 0.25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    bodies = build_bodies()
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            for _ in range(simulation_clock.consume(frame_time)):
                step_scene(bodies, broadphase, FIXED_DT)

        screen.fill((24, 28, 35))
        for body in bodies:
            pygame.draw.circle(
                screen,
                (209, 88, 88),
                body.position.to_tuple(),
                int(body.radius),
            )

        sleeping_count = sum(1 for body in bodies if body.sleeping)
        overlay.draw(
            screen,
            frame_time,
            FIXED_DT,
            extra_lines=[f"Sleeping: {sleeping_count}/{len(bodies)}"],
        )
        pygame.display.flip()

    pygame.quit()
