# <file>
# <summary>
# Interactive particle playground demo.
# </summary>
# </file>
"""Interactive particle playground demo."""

from __future__ import annotations

from math import cos, sin, tau
from random import Random

from engine.core import SimulationClock
from engine.debug import PerformanceOverlay
from engine.forces import drag_force
from engine.math2d import Vec2
from engine.particle import Particle, step_particles
from media_capture import CaptureController


WINDOW_WIDTH = 980
WINDOW_HEIGHT = 700
FIXED_DT = 1.0 / 120.0
MAX_PARTICLES = 4200

BASE_GRAVITY = Vec2(0.0, 900.0)
LINEAR_DAMPING = 0.7
AIR_DRAG = 0.85
WIND_FORCE_X = 320.0
FLOOR_FRICTION = 1.2
# Macro-style COR switch:
# - Keep this line for fixed COR.
# - Comment it out to use randomized COR fallback in emit_particle().
BOUNCE_RESTITUTION = 0.7

BASE_EMIT_RATE = 260.0
BURST_COUNT = 220

EMITTER_MODES = ("Fountain", "Spray", "Radial")
COLOR_MODES = ("Classic", "Lifetime", "Speed", "Mass")
DRAW_MODES = ("Circle", "Square", "Ring")
BACKGROUND_THEMES = (
    ("Night", (17, 20, 28), (17, 20, 28, 42)),
    ("Paper", (239, 235, 226), (239, 235, 226, 34)),
    ("Neon", (7, 10, 12), (7, 10, 12, 46)),
)


# <summary>
# Clamp a numeric value into an inclusive range.
# </summary>
# <param name="value">Input value to process.</param>
# <param name="minimum">Lower bound used when clamping the value.</param>
# <param name="maximum">Upper bound used when clamping the value.</param>
# <returns>Computed result described by the return type annotation.</returns>
def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


# <summary>
# Blend two RGB colors by a normalized interpolation amount.
# </summary>
# <param name="color_a">First RGB color endpoint.</param>
# <param name="color_b">Second RGB color endpoint.</param>
# <param name="t">Interpolation amount between 0.0 and 1.0.</param>
# <returns>Computed result described by the return type annotation.</returns>
def mix_color(color_a: tuple[int, int, int], color_b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    blend = clamp(t, 0.0, 1.0)
    return (
        int(color_a[0] + (color_b[0] - color_a[0]) * blend),
        int(color_a[1] + (color_b[1] - color_a[1]) * blend),
        int(color_a[2] + (color_b[2] - color_a[2]) * blend),
    )


# <summary>
# Create an initial particle velocity for the selected emitter mode.
# </summary>
# <param name="mode_index">Selected mode index controlling behavior.</param>
# <param name="rng">Random number generator used for deterministic sampling.</param>
# <returns>Computed result described by the return type annotation.</returns>
def spawn_velocity(mode_index: int, rng: Random) -> Vec2:
    if mode_index == 0:
        angle = rng.uniform(-2.1, -1.0)
        speed = rng.uniform(220.0, 560.0)
    elif mode_index == 1:
        angle = rng.uniform(-2.8, -0.3)
        speed = rng.uniform(180.0, 480.0)
    else:
        angle = rng.uniform(0.0, tau)
        speed = rng.uniform(160.0, 420.0)
    return Vec2(cos(angle) * speed, sin(angle) * speed)


# <summary>
# Create and append one particle using the current emitter settings.
# </summary>
# <param name="particles">Particle collection being read or updated.</param>
# <param name="birth_lifetimes">Input value for birth lifetimes.</param>
# <param name="emitter_position">Input value for emitter position.</param>
# <param name="emitter_mode">Input value for emitter mode.</param>
# <param name="lifetime_scale">Input value for lifetime scale.</param>
# <param name="pin_mode">Input value for pin mode.</param>
# <param name="rng">Random number generator used for deterministic sampling.</param>
def emit_particle(
    particles: list[Particle],
    birth_lifetimes: dict[int, float],
    emitter_position: Vec2,
    emitter_mode: int,
    lifetime_scale: float,
    pin_mode: bool,
    rng: Random,
) -> None:
    if len(particles) >= MAX_PARTICLES:
        return

    radius = rng.uniform(2.0, 5.0)
    mass = rng.uniform(0.8, 2.2) * radius
    lifetime = rng.uniform(1.0, 2.6) * lifetime_scale
    pinned = pin_mode and rng.random() < 0.09
    velocity = Vec2() if pinned else spawn_velocity(emitter_mode, rng)

    if "BOUNCE_RESTITUTION" in globals():
        cor = BOUNCE_RESTITUTION
    else:
        cor = rng.uniform(0.50, 0.94)

    particle = Particle(
        position=emitter_position.copy(),
        velocity=velocity,
        mass=mass,
        radius=radius,
        lifetime=lifetime,
        pinned=pinned,
        restitution=cor,
    )
    particles.append(particle)
    birth_lifetimes[id(particle)] = lifetime


# <summary>
# Remove expired particles and stale lifetime bookkeeping entries.
# </summary>
# <param name="particles">Particle collection being read or updated.</param>
# <param name="birth_lifetimes">Input value for birth lifetimes.</param>
def cleanup_particles(particles: list[Particle], birth_lifetimes: dict[int, float]) -> None:
    write_index = 0
    for particle in particles:
        if particle.lifetime is not None and particle.lifetime <= 0.0:
            birth_lifetimes.pop(id(particle), None)
            continue
        particles[write_index] = particle
        write_index += 1
    if write_index < len(particles):
        del particles[write_index:]


# <summary>
# Resolve particle collision against the demo window bounds.
# </summary>
# <param name="particle">Particle instance being read or updated.</param>
# <param name="dt">Simulation timestep in seconds.</param>
def contain_particle(particle: Particle, dt: float) -> None:
    if particle.pinned:
        return

    position = particle.position
    velocity = particle.velocity
    radius = particle.radius
    restitution = particle.restitution
    x = position.x
    y = position.y
    vx = velocity.x
    vy = velocity.y

    if x < radius:
        x = radius
        vx = abs(vx) * restitution
    elif x > WINDOW_WIDTH - radius:
        x = WINDOW_WIDTH - radius
        vx = -abs(vx) * restitution

    if y < radius:
        y = radius
        vy = abs(vy) * restitution
    elif y > WINDOW_HEIGHT - radius:
        y = WINDOW_HEIGHT - radius
        vy = -abs(vy) * restitution
        vx *= max(0.0, 1.0 - FLOOR_FRICTION * dt)

    position.x = x
    position.y = y
    velocity.x = vx
    velocity.y = vy


# <summary>
# Apply the currently enabled particle-demo forces.
# </summary>
# <param name="particles">Particle collection being read or updated.</param>
# <param name="use_wind">Input value for use wind.</param>
# <param name="use_air_drag">Input value for use air drag.</param>
# <param name="wind_strength">Input value for wind strength.</param>
def apply_forces(
    particles: list[Particle],
    use_wind: bool,
    use_air_drag: bool,
    wind_strength: float,
) -> None:
    for particle in particles:
        if particle.pinned:
            continue
        if use_wind:
            particle.apply_force(Vec2(wind_strength, 0.0))
        if use_air_drag:
            particle.apply_force(drag_force(particle.velocity, AIR_DRAG))


# <summary>
# Choose the display color for a particle based on age and mode.
# </summary>
# <param name="particle">Particle instance being read or updated.</param>
# <param name="mode_index">Selected mode index controlling behavior.</param>
# <param name="birth_lifetimes">Input value for birth lifetimes.</param>
# <returns>Computed result described by the return type annotation.</returns>
def particle_color(
    particle: Particle,
    mode_index: int,
    birth_lifetimes: dict[int, float],
) -> tuple[int, int, int]:
    speed = particle.velocity.length()
    if mode_index == 0:
        speed_ratio = clamp(speed / 560.0, 0.0, 1.0)
        return mix_color((129, 196, 255), (255, 120, 96), speed_ratio)
    if mode_index == 1:
        born_lifetime = birth_lifetimes.get(id(particle), 1.0)
        current_lifetime = 0.0 if particle.lifetime is None else particle.lifetime
        life_ratio = clamp(current_lifetime / max(born_lifetime, 0.001), 0.0, 1.0)
        return mix_color((255, 112, 76), (118, 197, 255), life_ratio)
    if mode_index == 2:
        speed_ratio = clamp(speed / 700.0, 0.0, 1.0)
        return mix_color((76, 132, 255), (255, 211, 92), speed_ratio)
    mass_ratio = clamp((particle.mass - 2.0) / 9.0, 0.0, 1.0)
    return mix_color((92, 223, 168), (247, 105, 193), mass_ratio)


# <summary>
# Render one particle using the selected drawing style.
# </summary>
# <param name="surface">pygame surface used for drawing or capture.</param>
# <param name="particle">Particle instance being read or updated.</param>
# <param name="color">Input value for color.</param>
# <param name="draw_mode">Input value for draw mode.</param>
# <param name="render_scale">Input value for render scale.</param>
def draw_particle(surface, particle: Particle, color: tuple[int, int, int], draw_mode: int, render_scale: float) -> None:
    x = int(particle.position.x)
    y = int(particle.position.y)
    radius = max(1, int(particle.radius * render_scale))

    if draw_mode == 0:
        import pygame

        pygame.draw.circle(surface, color, (x, y), radius)
        return
    if draw_mode == 1:
        import pygame

        side = radius * 2
        pygame.draw.rect(surface, color, (x - radius, y - radius, side, side))
        return

    import pygame

    pygame.draw.circle(surface, color, (x, y), radius, 1)


# <summary>
# Render the particle-demo help panel.
# </summary>
# <param name="surface">pygame surface used for drawing or capture.</param>
# <param name="font">Font object used to render text.</param>
# <param name="lines">Text lines to draw or return.</param>
def draw_help(surface, font, lines: list[str]) -> None:
    import pygame

    margin = 14
    x = margin
    y = WINDOW_HEIGHT - (len(lines) * 20 + margin)
    panel_width = max(font.size(line)[0] for line in lines) + 12
    panel_height = len(lines) * 20 + 10

    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 130))
    surface.blit(panel, (x - 4, y - 6))

    for line in lines:
        text = font.render(line, True, (245, 245, 245))
        surface.blit(text, (x, y))
        y += 20


# <summary>
# Run the interactive pygame demo loop.
# </summary>
def run() -> None:
    import pygame

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Particle Playground Demo")
    clock = pygame.time.Clock()
    simulation_clock = SimulationClock(fixed_dt=FIXED_DT, max_substeps=8)
    overlay = PerformanceOverlay(font_size=20, update_interval=0.35)
    help_font = pygame.font.Font(None, 22)
    capture = CaptureController(demo_name="particle")

    rng = Random(7)
    particles: list[Particle] = []
    birth_lifetimes: dict[int, float] = {}
    emitter_position = Vec2(WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.6)

    emit_rate = BASE_EMIT_RATE
    render_scale = 1.0
    lifetime_scale = 1.0
    wind_strength = WIND_FORCE_X

    emitter_mode = 0
    color_mode = 0
    draw_mode = 0
    theme_index = 0

    paused = False
    show_help = True
    trails_enabled = True
    gravity_enabled = True
    damping_enabled = True
    wind_enabled = False
    drag_enabled = True
    pin_mode = False
    emit_budget = 0.0
    running = True

    fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    while running:
        frame_time = min(clock.tick() / 1000.0, 0.25)
        theme_name, background_color, trail_color = BACKGROUND_THEMES[theme_index]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if capture.handle_keydown(event, screen):
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    particles.clear()
                    birth_lifetimes.clear()
                    emit_budget = 0.0
                elif event.key == pygame.K_x:
                    for _ in range(BURST_COUNT):
                        emit_particle(
                            particles,
                            birth_lifetimes,
                            emitter_position,
                            emitter_mode,
                            lifetime_scale,
                            pin_mode,
                            rng,
                        )
                elif event.key == pygame.K_e:
                    emitter_mode = (emitter_mode + 1) % len(EMITTER_MODES)
                elif event.key == pygame.K_c:
                    color_mode = (color_mode + 1) % len(COLOR_MODES)
                elif event.key == pygame.K_v:
                    draw_mode = (draw_mode + 1) % len(DRAW_MODES)
                elif event.key == pygame.K_b:
                    theme_index = (theme_index + 1) % len(BACKGROUND_THEMES)
                elif event.key == pygame.K_t:
                    trails_enabled = not trails_enabled
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key == pygame.K_g:
                    gravity_enabled = not gravity_enabled
                elif event.key == pygame.K_d:
                    damping_enabled = not damping_enabled
                elif event.key == pygame.K_w:
                    wind_enabled = not wind_enabled
                elif event.key == pygame.K_f:
                    drag_enabled = not drag_enabled
                elif event.key == pygame.K_p:
                    pin_mode = not pin_mode
                elif event.key == pygame.K_UP:
                    emit_rate = min(1200.0, emit_rate + 30.0)
                elif event.key == pygame.K_DOWN:
                    emit_rate = max(0.0, emit_rate - 30.0)
                elif event.key == pygame.K_LEFT:
                    wind_strength = max(-900.0, wind_strength - 40.0)
                elif event.key == pygame.K_RIGHT:
                    wind_strength = min(900.0, wind_strength + 40.0)
                elif event.key == pygame.K_LEFTBRACKET:
                    render_scale = clamp(render_scale - 0.1, 0.5, 2.2)
                elif event.key in (pygame.K_RIGHTBRACKET, pygame.K_SLASH):
                    render_scale = clamp(render_scale + 0.1, 0.5, 2.2)
                elif event.key == pygame.K_MINUS:
                    lifetime_scale = clamp(lifetime_scale - 0.1, 0.4, 2.5)
                elif event.key == pygame.K_EQUALS:
                    lifetime_scale = clamp(lifetime_scale + 0.1, 0.4, 2.5)



        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            emitter_position.set(float(mouse_x), float(mouse_y))

        if not paused:
            for _ in range(simulation_clock.consume(frame_time)):
                emit_budget += emit_rate * FIXED_DT
                spawn_count = int(emit_budget)
                emit_budget -= spawn_count
                for _ in range(spawn_count):
                    emit_particle(
                        particles,
                        birth_lifetimes,
                        emitter_position,
                        emitter_mode,
                        lifetime_scale,
                        pin_mode,
                        rng,
                    )

                apply_forces(
                    particles,
                    use_wind=wind_enabled,
                    use_air_drag=drag_enabled,
                    wind_strength=wind_strength,
                )
                step_particles(
                    particles,
                    FIXED_DT,
                    gravity=BASE_GRAVITY if gravity_enabled else None,
                    linear_damping=LINEAR_DAMPING if damping_enabled else 0.0,
                )
                for particle in particles:
                    contain_particle(particle, FIXED_DT)
                cleanup_particles(particles, birth_lifetimes)

        if trails_enabled:
            fade_surface.fill(trail_color)
            screen.blit(fade_surface, (0, 0))
        else:
            screen.fill(background_color)

        for particle in particles:
            color = particle_color(particle, color_mode, birth_lifetimes)
            if particle.pinned:
                color = (255, 255, 255)
            draw_particle(screen, particle, color, draw_mode, render_scale)

        emitter_xy = (int(emitter_position.x), int(emitter_position.y))
        pygame.draw.circle(screen, (250, 250, 250), emitter_xy, 7, 1)
        pygame.draw.line(
            screen,
            (250, 250, 250),
            (emitter_xy[0] - 10, emitter_xy[1]),
            (emitter_xy[0] + 10, emitter_xy[1]),
            1,
        )
        pygame.draw.line(
            screen,
            (250, 250, 250),
            (emitter_xy[0], emitter_xy[1] - 10),
            (emitter_xy[0], emitter_xy[1] + 10),
            1,
        )

        pinned_count = sum(1 for particle in particles if particle.pinned)
        moving_count = max(1, len(particles) - pinned_count)
        avg_speed = (
            sum(particle.velocity.length() for particle in particles if not particle.pinned)
            / moving_count
        )
        damping_step_factor = max(0.0, 1.0 - LINEAR_DAMPING * FIXED_DT)
        overlay_lines = [
            f"Particles: {len(particles)}/{MAX_PARTICLES}",
            f"Emitter: {EMITTER_MODES[emitter_mode]} @ {emit_rate:.0f}/s",
            f"Modes: color={COLOR_MODES[color_mode]} draw={DRAW_MODES[draw_mode]} bg={theme_name}",
            f"Forces: gravity={gravity_enabled} wind={wind_enabled}",
            f"Damping(D): enabled={damping_enabled} c={LINEAR_DAMPING:.2f} step={damping_step_factor:.4f}",
            f"Drag(F): enabled={drag_enabled} c={AIR_DRAG:.2f} (opposes velocity)",
            f"Wind X: {wind_strength:+.0f}  Lifetime Scale: {lifetime_scale:.2f}",
            f"Avg speed: {avg_speed:.1f}",
            f"Pinned: {pinned_count} (spawn pin mode={pin_mode})",
        ]
        overlay_lines.extend(capture.overlay_lines())
        overlay.draw(
            screen,
            frame_time,
            FIXED_DT,
            extra_lines=overlay_lines,
        )

        if show_help:
            draw_help(
                screen,
                help_font,
                [
                    "LMB: move emitter  X: burst  TAB: screenshot  `: GIF  SPACE: pause  R: reset  ESC: quit",
                    "E: emitter mode  C: color mode  V: draw mode  B: background  T: trails  H: hide help",
                    "G: gravity  D: linear damping  F: drag force  W: wind on/off  LEFT/RIGHT: wind strength",
                    "UP/DOWN: emission rate  [: size-  ] or /: size+  -/=: lifetime scale  P: spawn pinned particles",
                ],
            )

        capture.update(screen, frame_time)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
