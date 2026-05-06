# <file>
# <summary>
# Interactive forward and inverse kinematics demo.
# </summary>
# </file>
"""Interactive forward and inverse kinematics demo."""

from __future__ import annotations

from math import degrees

from engine.debug import PerformanceOverlay
from engine.kinematics import IKResult, KinematicChain
from engine.math2d import Vec2
from media_capture import CaptureController


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 680
FIXED_DT = 1.0 / 120.0
ANGLE_STEP = 0.08
IK_ITERATIONS = 12
IK_TOLERANCE = 2.0
JOINT_RADIUS = 8


# <summary>
# Create the articulated arm used by the kinematics demo.
# </summary>
# <returns>Computed result described by the return type annotation.</returns>
def build_chain() -> KinematicChain:
    return KinematicChain.from_lengths(
        origin=Vec2(210.0, WINDOW_HEIGHT * 0.52),
        lengths=[105.0, 92.0, 74.0, 48.0],
        angles=[-0.55, 0.62, 0.48, -0.32],
    )


# <summary>
# Draw a compact help panel for the kinematics demo.
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
# Draw the articulated chain, joints, and target marker.
# </summary>
# <param name="surface">pygame surface used for drawing or capture.</param>
# <param name="chain">Kinematic chain to render.</param>
# <param name="selected_joint">Currently selected joint index.</param>
# <param name="target">World-space IK target.</param>
# <param name="ik_enabled">Whether IK mode is active.</param>
# <param name="ik_result">Most recent IK solve result.</param>
def draw_chain(
    surface,
    chain: KinematicChain,
    selected_joint: int,
    target: Vec2,
    ik_enabled: bool,
    ik_result: IKResult | None,
) -> None:
    import pygame

    positions = chain.joint_positions()

    target_color = (61, 150, 96)
    if ik_result is not None and not ik_result.target_reachable:
        target_color = (204, 91, 73)
    elif ik_result is not None and not ik_result.reached:
        target_color = (224, 154, 55)

    pygame.draw.circle(surface, target_color, target.to_tuple(), 13, 2)
    pygame.draw.line(
        surface,
        target_color,
        (target.x - 18, target.y),
        (target.x + 18, target.y),
        1,
    )
    pygame.draw.line(
        surface,
        target_color,
        (target.x, target.y - 18),
        (target.x, target.y + 18),
        1,
    )

    for index in range(len(positions) - 1):
        start = positions[index]
        end = positions[index + 1]
        color = (43, 57, 67) if index != selected_joint else (234, 161, 58)
        pygame.draw.line(surface, color, start.to_tuple(), end.to_tuple(), 9)
        pygame.draw.line(surface, (250, 252, 253), start.to_tuple(), end.to_tuple(), 3)

    for index, position in enumerate(positions):
        if index == 0:
            color = (60, 90, 126)
        elif index == selected_joint:
            color = (234, 161, 58)
        elif index == len(positions) - 1:
            color = (61, 150, 96) if ik_enabled else (70, 139, 195)
        else:
            color = (76, 89, 101)

        pygame.draw.circle(surface, color, position.to_tuple(), JOINT_RADIUS)
        pygame.draw.circle(surface, (250, 252, 253), position.to_tuple(), JOINT_RADIUS, 2)


# <summary>
# Run the interactive pygame demo loop.
# </summary>
def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("FK / IK Kinematics Demo")
    clock = pygame.time.Clock()
    overlay = PerformanceOverlay()
    help_font = pygame.font.Font(None, 22)
    capture = CaptureController(demo_name="kinematics")

    chain = build_chain()
    selected_joint = 0
    ik_enabled = True
    paused = False
    show_help = True
    ik_result: IKResult | None = None
    running = True

    while running:
        frame_time = min(clock.tick() / 1000.0, 0.25)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target = Vec2(float(mouse_x), float(mouse_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if capture.handle_keydown(event, screen):
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    chain = build_chain()
                    ik_result = None
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key == pygame.K_i:
                    ik_enabled = not ik_enabled
                    ik_result = None
                elif event.key == pygame.K_j:
                    selected_joint = (selected_joint + 1) % len(chain.lengths)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    requested = event.key - pygame.K_1
                    if requested < len(chain.lengths):
                        selected_joint = requested
                elif event.key == pygame.K_LEFT:
                    chain.add_angle(selected_joint, -ANGLE_STEP)
                    ik_result = None
                elif event.key == pygame.K_RIGHT:
                    chain.add_angle(selected_joint, ANGLE_STEP)
                    ik_result = None

        if ik_enabled and not paused:
            ik_result = chain.solve_ik(target, iterations=IK_ITERATIONS, tolerance=IK_TOLERANCE)

        screen.fill((242, 245, 246))
        draw_chain(screen, chain, selected_joint, target, ik_enabled, ik_result)

        angle_summary = " ".join(
            f"{index + 1}:{degrees(angle):.0f}deg"
            for index, angle in enumerate(chain.angles)
        )
        mode_name = "IK target" if ik_enabled else "FK manual"
        error_text = "--" if ik_result is None else f"{ik_result.error:.2f}"
        reachable_text = "--" if ik_result is None else str(ik_result.target_reachable)
        overlay_lines = [
            f"Mode: {mode_name}",
            f"Selected joint: {selected_joint + 1}/{len(chain.lengths)}",
            f"Target reachable: {reachable_text}",
            f"IK error: {error_text}",
            f"Angles: {angle_summary}",
        ]
        overlay_lines.extend(capture.overlay_lines())
        overlay.draw(screen, frame_time, FIXED_DT, extra_lines=overlay_lines)

        if show_help:
            draw_help(
                screen,
                help_font,
                [
                    "Mouse: IK target  I: toggle FK/IK  J or 1-4: select joint  LEFT/RIGHT: rotate selected",
                    "SPACE: pause IK  R: reset  H: hide help  TAB: screenshot  `: GIF  ESC: quit",
                ],
            )

        capture.update(screen, frame_time)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
