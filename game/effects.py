"""Wind and particle effects for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from engine.forces import drag_force
from engine.math2d import Vec2
from engine.particle import Particle, step_particles
from engine.rigidbody import CircleBody

from . import config
from .entities import Ball


@dataclass(slots=True)
class WindState:
    """Time-varying horizontal wind state."""

    current_force_x: float = 0.0
    timer: float = 0.0
    next_change: float = 1.8


@dataclass(slots=True)
class DripEmitter:
    """Small reusable particle container for drips and splashes."""

    particles: list[Particle] = field(default_factory=list)
    birth_lifetimes: dict[int, float] = field(default_factory=dict)
    colors: dict[int, tuple[int, int, int]] = field(default_factory=dict)
    emit_accumulator: float = 0.0


def update_wind(wind: WindState, dt: float, rng: Random) -> None:
    """Advance wind timing and switch to a fresh random wind sample."""

    wind.timer += dt
    if wind.timer >= wind.next_change:
        wind.timer = 0.0
        wind.next_change = rng.uniform(config.WIND_INTERVAL_MIN, config.WIND_INTERVAL_MAX)
        wind.current_force_x = rng.uniform(config.WIND_MIN_FORCE, config.WIND_MAX_FORCE)


def reset_wind(wind: WindState, rng: Random) -> None:
    """Start a rally with a fresh non-accumulating random wind value."""

    wind.current_force_x = rng.uniform(config.WIND_MIN_FORCE, config.WIND_MAX_FORCE)
    wind.timer = 0.0
    wind.next_change = rng.uniform(config.WIND_INTERVAL_MIN, config.WIND_INTERVAL_MAX)


def apply_wind_to_bodies(bodies: list[CircleBody], wind_force_x: float) -> None:
    """Apply the same wind acceleration to all moving rigid bodies."""

    if wind_force_x == 0.0:
        return

    for body in bodies:
        body.apply_force(Vec2(wind_force_x * body.mass, 0.0))


def update_drip_intensity(ball: Ball, impact_speed: float, dt: float) -> None:
    """Decay drip intensity and add a burst after strong impacts."""

    ball.drip_intensity = max(0.0, ball.drip_intensity - 0.18 * dt)
    if impact_speed > 150.0:
        ball.drip_intensity = min(1.0, ball.drip_intensity + min(0.45, impact_speed / 900.0))


def emit_ball_drips(
    ball: Ball,
    emitter: DripEmitter,
    wind_force_x: float,
    rng: Random,
    dt: float,
) -> None:
    """Continuously emit drip particles from the ball."""

    intensity = max(0.06, ball.drip_intensity)
    emitter.emit_accumulator += (7.0 + intensity * 22.0) * dt
    spawn_count = int(emitter.emit_accumulator)
    if spawn_count <= 0:
        return
    emitter.emit_accumulator -= spawn_count

    for _ in range(spawn_count):
        spawn_drip_particle(emitter, ball.body.position, wind_force_x, rng, intensity)


def spawn_drip_particle(
    emitter: DripEmitter,
    position: Vec2,
    wind_force_x: float,
    rng: Random,
    intensity: float,
) -> None:
    """Spawn a single downward-trending drip particle."""

    if len(emitter.particles) >= config.MAX_EFFECT_PARTICLES:
        return

    velocity = Vec2(
        rng.uniform(-26.0, 26.0) + wind_force_x * 0.05,
        rng.uniform(50.0, 135.0 + 80.0 * intensity),
    )
    particle = Particle(
        position=Vec2(position.x + rng.uniform(-8.0, 8.0), position.y + rng.uniform(-4.0, 12.0)),
        velocity=velocity,
        mass=1.0,
        radius=rng.uniform(1.5, 3.6),
        lifetime=rng.uniform(0.55, 1.15),
        restitution=0.35,
    )
    emitter.particles.append(particle)
    emitter.birth_lifetimes[id(particle)] = particle.lifetime or 0.0


def spawn_splash_burst(
    emitter: DripEmitter,
    position: Vec2,
    wind_force_x: float,
    rng: Random,
    count: int = 16,
) -> None:
    """Emit a short burst of upward splash particles."""

    for _ in range(count):
        if len(emitter.particles) >= config.MAX_EFFECT_PARTICLES:
            return

        particle = Particle(
            position=Vec2(position.x + rng.uniform(-12.0, 12.0), position.y),
            velocity=Vec2(
                rng.uniform(-120.0, 120.0) + wind_force_x * 0.06,
                rng.uniform(-240.0, -70.0),
            ),
            mass=1.0,
            radius=rng.uniform(1.8, 4.2),
            lifetime=rng.uniform(0.55, 1.0),
            restitution=0.2,
        )
        emitter.particles.append(particle)
        emitter.birth_lifetimes[id(particle)] = particle.lifetime or 0.0


def spawn_confetti_burst(
    emitter: DripEmitter,
    rng: Random,
    count: int = config.VICTORY_CONFETTI_COUNT,
) -> None:
    """Emit a celebratory confetti burst using the shared particle system."""

    colors = (
        (255, 87, 99),
        (255, 207, 64),
        (73, 196, 255),
        (91, 217, 132),
        (178, 121, 255),
        (255, 142, 72),
    )
    for _ in range(count):
        if len(emitter.particles) >= config.MAX_EFFECT_PARTICLES:
            return

        side = -1.0 if rng.random() < 0.5 else 1.0
        origin_x = config.WINDOW_WIDTH * (0.32 if side < 0.0 else 0.68)
        particle = Particle(
            position=Vec2(origin_x + rng.uniform(-40.0, 40.0), rng.uniform(42.0, 110.0)),
            velocity=Vec2(
                rng.uniform(80.0, 260.0) * -side,
                rng.uniform(-270.0, -95.0),
            ),
            mass=0.8,
            radius=rng.uniform(2.0, 4.4),
            lifetime=rng.uniform(1.5, 2.7),
            restitution=0.15,
        )
        emitter.particles.append(particle)
        emitter.birth_lifetimes[id(particle)] = particle.lifetime or 0.0
        emitter.colors[id(particle)] = colors[rng.randrange(len(colors))]


def step_effect_particles(emitter: DripEmitter, dt: float, wind_force_x: float) -> None:
    """Advance and cull effect particles."""

    for particle in emitter.particles:
        particle.apply_force(Vec2(wind_force_x * 0.12, 0.0))
        particle.apply_force(drag_force(particle.velocity, config.EFFECT_PARTICLE_DRAG))

    step_particles(
        emitter.particles,
        dt,
        gravity=config.EFFECT_PARTICLE_GRAVITY,
        linear_damping=config.EFFECT_PARTICLE_DAMPING,
    )

    write_index = 0
    for particle in emitter.particles:
        expired = particle.lifetime is not None and particle.lifetime <= 0.0
        if expired or particle.position.y > config.WINDOW_HEIGHT + 24.0:
            emitter.birth_lifetimes.pop(id(particle), None)
            emitter.colors.pop(id(particle), None)
            continue
        emitter.particles[write_index] = particle
        write_index += 1

    if write_index < len(emitter.particles):
        del emitter.particles[write_index:]
