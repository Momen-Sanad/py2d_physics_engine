"""Circle collision demo"""

from __future__ import annotations

from engine.collisions import resolve_circle_collision
from engine.core import SimulationClock
from engine.math2d import Vec2
from engine.rigidbody import CircleBody


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
TARGET_FPS = 60
FIXED_DT = 1.0 / 120.0
GRAVITY = Vec2(0.0, 900.0)
LINEAR_DAMPING = 0.05
FLOOR_FRICTION = 6.0


def build_bodies() -> list[CircleBody]:
    return [
        CircleBody(
            position=Vec2(380.0, 180.0),
            velocity=Vec2(-220.0, -120.0),
            radius=20.0,
            mass=20.0,
            restitution=0.95,
        ),
        CircleBody(
            position=Vec2(450.0, 180.0),
            velocity=Vec2(170.0, -80.0),
            radius=36.0,
            mass=36.0,
            restitution=0.95,
        ),
        CircleBody(
            position=Vec2(540.0, 190.0),
            velocity=Vec2(-120.0, 0.0),
            radius=52.0,
            mass=52.0,
            restitution=0.95,
        ),
    ]


def contain_body(body: CircleBody, dt: float) -> None:
    x, y = body.position.x, body.position.y
    vx, vy = body.velocity.x, body.velocity.y

    if x < body.radius:
        x = body.radius
        vx = abs(vx) * body.restitution
    elif x > WINDOW_WIDTH - body.radius:
        x = WINDOW_WIDTH - body.radius
        vx = -abs(vx) * body.restitution

    if y < body.radius:
        y = body.radius
        vy = abs(vy) * body.restitution
    elif y > WINDOW_HEIGHT - body.radius:
        y = WINDOW_HEIGHT - body.radius
        vy = -abs(vy) * body.restitution
        vx *= max(0.0, 1.0 - FLOOR_FRICTION * dt)

    body.position = Vec2(x, y)
    body.velocity = Vec2(vx, vy)


def step_scene(bodies: list[CircleBody], dt: float) -> None:
    for body in bodies:
        body.step(dt, gravity=GRAVITY, linear_damping=LINEAR_DAMPING)
        contain_body(body, dt)

    for index, body in enumerate(bodies):
        for other in bodies[index + 1 :]:
            resolve_circle_collision(body, other)


def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rigid Body Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=5)

    bodies = build_bodies()
    paused = False
    running = True

    while running:
        frame_time = min(clock.tick(TARGET_FPS) / 1000.0, 0.25)

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
                step_scene(bodies, FIXED_DT)

        screen.fill((24, 28, 35))
        for body in bodies:
            pygame.draw.circle(
                screen,
                (209, 88, 88),
                body.position.to_tuple(),
                int(body.radius),
            )

        pygame.display.flip()

    pygame.quit()
