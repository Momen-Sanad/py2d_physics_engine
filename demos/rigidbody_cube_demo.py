# <file>
# <summary>
# Torque-driven rigid-body rotation demo.
# </summary>
# </file>
"""Torque-driven rigid-body rotation demo."""

from __future__ import annotations

from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.math3d import Vec3, solid_cube_inertia_tensor
from engine.rigidbody import RigidBody3D
from media_capture import CaptureController


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
FIXED_DT = 1.0 / 120.0

MASS = 8.0
SIDE_LENGTH = 2.0
CAMERA_DISTANCE = 6.0
FOCAL_LENGTH = 520.0
TORQUE_MAGNITUDE = 22.0
ANGULAR_DAMPING = 0.08

INERTIA_BODY = solid_cube_inertia_tensor(MASS, SIDE_LENGTH)
INERTIA_DIAGONAL = (
    INERTIA_BODY.rows[0][0],
    INERTIA_BODY.rows[1][1],
    INERTIA_BODY.rows[2][2],
)


# <summary>
# Create the configured rigid cube body for the rotation demo.
# </summary>
# <returns>Computed result described by the return type annotation.</returns>
def build_cube_body() -> RigidBody3D:
    return RigidBody3D(
        position=Vec3(0.0, 0.0, CAMERA_DISTANCE),
        mass=MASS,
        inertia_body=INERTIA_BODY,
        angular_damping=ANGULAR_DAMPING,
    )


# <summary>
# Return the cube's local-space vertex positions.
# </summary>
# <returns>Computed result described by the return type annotation.</returns>
def cube_vertices() -> list[Vec3]:
    half_side = SIDE_LENGTH * 0.5
    return [
        Vec3(-half_side, -half_side, -half_side),
        Vec3(half_side, -half_side, -half_side),
        Vec3(half_side, half_side, -half_side),
        Vec3(-half_side, half_side, -half_side),
        Vec3(-half_side, -half_side, half_side),
        Vec3(half_side, -half_side, half_side),
        Vec3(half_side, half_side, half_side),
        Vec3(-half_side, half_side, half_side),
    ]


CUBE_VERTICES = cube_vertices()
CUBE_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]


# <summary>
# Project a 3D point into 2D screen coordinates.
# </summary>
# <param name="point">Point or vector being transformed.</param>
# <returns>Computed result described by the return type annotation.</returns>
def project(point: Vec3) -> tuple[int, int] | None:
    if point.z <= 0.1:
        return None

    factor = FOCAL_LENGTH / point.z
    return (
        int(point.x * factor + WINDOW_WIDTH * 0.5),
        int(-point.y * factor + WINDOW_HEIGHT * 0.5),
    )


# <summary>
# Transform cube vertices from local space into world space.
# </summary>
# <param name="body">Rigid body instance being read or updated.</param>
# <returns>Computed result described by the return type annotation.</returns>
def transformed_vertices(body: RigidBody3D) -> list[Vec3]:
    rotation = body.rotation_matrix()
    return [rotation @ vertex + body.position for vertex in CUBE_VERTICES]


# <summary>
# Draw the cube's rotated local basis axes.
# </summary>
# <param name="screen">pygame display surface used for rendering.</param>
# <param name="body">Rigid body instance being read or updated.</param>
def draw_axis(screen, body: RigidBody3D) -> None:
    import pygame

    rotation = body.rotation_matrix()
    center = project(body.position)
    if center is None:
        return

    axes = [
        (Vec3(1.45, 0.0, 0.0), (234, 82, 82)),
        (Vec3(0.0, 1.45, 0.0), (94, 194, 116)),
        (Vec3(0.0, 0.0, 1.45), (88, 158, 235)),
    ]
    for local_axis, color in axes:
        endpoint = project(rotation @ local_axis + body.position)
        if endpoint is not None:
            pygame.draw.line(screen, color, center, endpoint, 4)
            pygame.draw.circle(screen, color, endpoint, 5)


# <summary>
# Render the wireframe cube and its local axes.
# </summary>
# <param name="screen">pygame display surface used for rendering.</param>
# <param name="body">Rigid body instance being read or updated.</param>
def draw_cube(screen, body: RigidBody3D) -> None:
    import pygame

    vertices_2d = [project(vertex) for vertex in transformed_vertices(body)]
    for edge_index, (start_index, end_index) in enumerate(CUBE_EDGES):
        start = vertices_2d[start_index]
        end = vertices_2d[end_index]
        if start is None or end is None:
            continue

        color = (83, 214, 211) if edge_index < 8 else (245, 205, 92)
        pygame.draw.line(screen, color, start, end, 3)

    for point in vertices_2d:
        if point is not None:
            pygame.draw.circle(screen, (236, 242, 255), point, 4)

    draw_axis(screen, body)


# <summary>
# Apply torque to the cube from the current keyboard state.
# </summary>
# <param name="body">Rigid body instance being read or updated.</param>
# <param name="keys">Current keyboard state returned by pygame.</param>
def apply_keyboard_torque(body: RigidBody3D, keys) -> None:
    import pygame

    torque = Vec3()
    if keys[pygame.K_UP]:
        torque.x -= TORQUE_MAGNITUDE
    if keys[pygame.K_DOWN]:
        torque.x += TORQUE_MAGNITUDE
    if keys[pygame.K_LEFT]:
        torque.y -= TORQUE_MAGNITUDE
    if keys[pygame.K_RIGHT]:
        torque.y += TORQUE_MAGNITUDE
    if keys[pygame.K_q]:
        torque.z -= TORQUE_MAGNITUDE
    if keys[pygame.K_e]:
        torque.z += TORQUE_MAGNITUDE

    if torque.length_squared() > 0.0:
        body.apply_torque(torque)


# <summary>
# Build debug-overlay text for the rigid-body cube demo.
# </summary>
# <param name="body">Rigid body instance being read or updated.</param>
# <param name="paused">Whether the simulation is currently paused.</param>
# <returns>Computed result described by the return type annotation.</returns>
def overlay_lines(body: RigidBody3D, paused: bool) -> list[str]:
    q = body.orientation
    w = body.angular_velocity
    return [
        "Rigid Body Rotation Cube",
        f"State: {'Paused' if paused else 'Running'}",
        f"Mass: {MASS:.1f} kg  Side: {SIDE_LENGTH:.1f} m",
        (
            "Inertia diag: "
            f"[{INERTIA_DIAGONAL[0]:.2f}, {INERTIA_DIAGONAL[1]:.2f}, "
            f"{INERTIA_DIAGONAL[2]:.2f}]"
        ),
        f"Omega: [{w.x: .2f}, {w.y: .2f}, {w.z: .2f}] rad/s",
        f"Quat: [{q.w: .2f}, {q.x: .2f}, {q.y: .2f}, {q.z: .2f}]",
        f"Quat norm: {q.length():.4f}",
        "Arrows: torque X/Y   Q/E: torque Z",
        "Space: pause   R: reset   Esc: quit",
    ]


# <summary>
# Run the interactive pygame demo loop.
# </summary>
def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rigid Body Cube Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=5)
    overlay = PerformanceOverlay(font_size=20)
    capture = CaptureController(demo_name="rigidbody_cube")

    body = build_cube_body()
    paused = False
    running = True

    while running:
        frame_time = min(clock.tick(60) / 1000.0, 0.25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if capture.handle_keydown(event, screen):
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    body = build_cube_body()
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        keys = pygame.key.get_pressed()
        if not paused:
            for _ in range(simulation_clock.consume(frame_time)):
                apply_keyboard_torque(body, keys)
                body.step(FIXED_DT)

        screen.fill((18, 21, 29))
        draw_cube(screen, body)

        lines = overlay_lines(body, paused)
        lines.extend(capture.overlay_lines())
        overlay.draw(screen, frame_time, FIXED_DT, extra_lines=lines)
        capture.update(screen, frame_time)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
