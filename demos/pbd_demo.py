# <file>
# <summary>
# Interactive Position-Based Dynamics rope demo.
# </summary>
# </file>
"""Interactive Position-Based Dynamics rope demo."""

from __future__ import annotations

from math import sin

from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.math2d import Vec2
from engine.particle import Particle
from engine.pbd import (
    PBDBounds,
    PBDDistanceConstraint,
    PBDPinConstraint,
    PBDSystem,
)
from media_capture import CaptureController


WINDOW_WIDTH = 940
WINDOW_HEIGHT = 680
FIXED_DT = 1.0 / 120.0
GRAVITY = Vec2(0.0, 900.0)
LINEAR_DAMPING = 0.25
PARTICLE_RADIUS = 5.0
PARTICLE_COUNT = 26
SPACING = 24.0
DEFAULT_ITERATIONS = 10
MIN_ITERATIONS = 1
MAX_ITERATIONS = 32
DRAG_RADIUS = 38.0


# <summary>
# Clamp a numeric value into an inclusive range.
# </summary>
# <param name="value">Input value to process.</param>
# <param name="minimum">Lower bound used when clamping the value.</param>
# <param name="maximum">Upper bound used when clamping the value.</param>
# <returns>Computed result described by the return type annotation.</returns>
def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


# <summary>
# Create the rope system and its static anchor constraints.
# </summary>
# <returns>Computed result described by the return type annotation.</returns>
def build_rope() -> tuple[PBDSystem, list[PBDPinConstraint]]:
    particles: list[Particle] = []
    constraints: list[PBDDistanceConstraint] = []
    pins: list[PBDPinConstraint] = []
    start = Vec2(150.0, 125.0)

    for index in range(PARTICLE_COUNT):
        position = Vec2(
            start.x + index * SPACING,
            start.y + sin(index * 0.45) * 14.0,
        )
        pinned = index in {0, PARTICLE_COUNT - 1}
        particle = Particle(
            position=position,
            mass=1.0,
            radius=PARTICLE_RADIUS,
            pinned=pinned,
        )
        particles.append(particle)
        if pinned:
            pins.append(PBDPinConstraint(index, position.copy()))

    for index in range(PARTICLE_COUNT - 1):
        constraints.append(
            PBDDistanceConstraint(
                index,
                index + 1,
                rest_length=SPACING,
                stiffness=1.0,
            )
        )

    for index in range(PARTICLE_COUNT - 2):
        constraints.append(
            PBDDistanceConstraint(
                index,
                index + 2,
                rest_length=SPACING * 2.0,
                stiffness=0.25,
            )
        )

    system = PBDSystem(
        particles=particles,
        distance_constraints=constraints,
        pin_constraints=list(pins),
        iterations=DEFAULT_ITERATIONS,
        gravity=GRAVITY,
        linear_damping=LINEAR_DAMPING,
        bounds=PBDBounds(
            0.0,
            0.0,
            float(WINDOW_WIDTH),
            float(WINDOW_HEIGHT),
            radius=PARTICLE_RADIUS,
        ),
    )
    return system, pins


# <summary>
# Return the nearest movable particle index within the drag radius.
# </summary>
# <param name="particles">Particle collection being read or updated.</param>
# <param name="target">World-space drag target.</param>
# <returns>Computed result described by the return type annotation.</returns>
def nearest_draggable_particle(particles: list[Particle], target: Vec2) -> int | None:
    nearest_index: int | None = None
    nearest_distance_sq = DRAG_RADIUS * DRAG_RADIUS

    for index, particle in enumerate(particles):
        if particle.pinned:
            continue

        offset = particle.position - target
        distance_sq = offset.length_squared()
        if distance_sq <= nearest_distance_sq:
            nearest_distance_sq = distance_sq
            nearest_index = index

    return nearest_index


# <summary>
# Draw a compact help panel for the PBD demo.
# </summary>
# <param name="surface">pygame surface used for drawing or capture.</param>
# <param name="font">Font object used to render text.</param>
# <param name="lines">Text lines to draw.</param>
def draw_help(surface, font, lines: list[str]) -> None:
    import pygame

    margin = 14
    line_height = 20
    x = margin
    y = WINDOW_HEIGHT - (len(lines) * line_height + margin)
    width = max(font.size(line)[0] for line in lines) + 12
    height = len(lines) * line_height + 10
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 130))
    surface.blit(panel, (x - 4, y - 6))

    for line in lines:
        text = font.render(line, True, (245, 245, 245))
        surface.blit(text, (x, y))
        y += line_height


# <summary>
# Run the interactive pygame demo loop.
# </summary>
def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PBD Rope Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=6)
    overlay = PerformanceOverlay()
    help_font = pygame.font.Font(None, 22)
    capture = CaptureController(demo_name="pbd")

    system, static_pins = build_rope()
    paused = False
    show_help = True
    drag_index: int | None = None
    running = True

    while running:
        frame_time = min(clock.tick() / 1000.0, 0.25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if capture.handle_keydown(event, screen):
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    system, static_pins = build_rope()
                    drag_index = None
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key in (pygame.K_UP, pygame.K_EQUALS):
                    system.iterations = clamp(system.iterations + 1, MIN_ITERATIONS, MAX_ITERATIONS)
                elif event.key in (pygame.K_DOWN, pygame.K_MINUS):
                    system.iterations = clamp(system.iterations - 1, MIN_ITERATIONS, MAX_ITERATIONS)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                drag_index = nearest_draggable_particle(system.particles, Vec2(float(mouse_x), float(mouse_y)))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                drag_index = None

        mouse_x, mouse_y = pygame.mouse.get_pos()
        drag_pin: PBDPinConstraint | None = None
        if drag_index is not None:
            drag_pin = PBDPinConstraint(drag_index, Vec2(float(mouse_x), float(mouse_y)))
            system.pin_constraints = [*static_pins, drag_pin]
        else:
            system.pin_constraints = list(static_pins)

        if not paused:
            for _ in range(simulation_clock.consume(frame_time)):
                system.step(FIXED_DT)

        screen.fill((242, 245, 247))

        for constraint in system.distance_constraints:
            particle_a = system.particles[constraint.index_a]
            particle_b = system.particles[constraint.index_b]
            color = (36, 45, 52) if abs(constraint.index_a - constraint.index_b) == 1 else (148, 161, 170)
            width = 2 if abs(constraint.index_a - constraint.index_b) == 1 else 1
            pygame.draw.line(
                screen,
                color,
                particle_a.position.to_tuple(),
                particle_b.position.to_tuple(),
                width,
            )

        for index, particle in enumerate(system.particles):
            if particle.pinned:
                color = (198, 58, 70)
            elif index == drag_index:
                color = (255, 181, 64)
            else:
                color = (55, 139, 117)
            pygame.draw.circle(
                screen,
                color,
                particle.position.to_tuple(),
                int(particle.radius),
            )

        if drag_pin is not None:
            pygame.draw.circle(screen, (255, 181, 64), drag_pin.position.to_tuple(), 9, 1)

        overlay_lines = [
            f"PBD particles: {len(system.particles)}",
            f"Distance constraints: {len(system.distance_constraints)}",
            f"Solver iterations: {system.iterations}",
            f"Dragging: {drag_index is not None}",
        ]
        overlay_lines.extend(capture.overlay_lines())
        overlay.draw(screen, frame_time, FIXED_DT, extra_lines=overlay_lines)

        if show_help:
            draw_help(
                screen,
                help_font,
                [
                    "LMB: drag nearest rope node  UP/DOWN or +/-: solver iterations",
                    "SPACE: pause  R: reset  H: hide help  TAB: screenshot  `: GIF  ESC: quit",
                ],
            )

        capture.update(screen, frame_time)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
