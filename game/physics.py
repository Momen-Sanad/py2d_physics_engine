"""Physics glue that adapts engine rigid bodies to gameplay rules."""

from __future__ import annotations

from math import sqrt
from random import Random

from engine.broadphase import SpatialHashGrid
from engine.collisions import resolve_circle_collision
from engine.math2d import Vec2
from engine.rigidbody import CircleBody, step_circle_bodies

from . import config
from .entities import Arena, Ball, Projectile
from .state import PlayerId


def build_ball(arena: Arena) -> Ball:
    """Create the main beach ball used by each rally."""

    return Ball(
        body=CircleBody(
            position=Vec2(arena.net_x, arena.serve_y),
            velocity=Vec2(),
            radius=config.BALL_RADIUS,
            mass=config.BALL_MASS,
            restitution=config.BALL_RESTITUTION,
        ),
        last_side=PlayerId.LEFT,
    )


def reset_ball(ball: Ball, arena: Arena, rng: Random) -> None:
    """Restore the ball to its rally-start pose."""

    ball.body.position.set(arena.net_x, arena.serve_y)
    ball.body.velocity.set(rng.uniform(-40.0, 40.0), rng.uniform(-50.0, 10.0))
    ball.body.force.reset()
    ball.touched_water = False
    ball.drip_intensity = 0.08
    ball.last_side = PlayerId.LEFT


def build_projectile(
    owner: PlayerId,
    origin: Vec2,
    aim_world: Vec2,
    arena: Arena,
    speed_scale: float = 1.0,
    mass_scale: float = 1.0,
    spread: float = 0.0,
) -> Projectile:
    """Create a projectile aimed toward the current mouse target."""

    direction = aim_world - origin
    if direction.length_squared() == 0.0:
        direction = Vec2(1.0, 0.0) if owner is PlayerId.LEFT else Vec2(-1.0, 0.0)
    else:
        direction = direction.normalized()
    if spread != 0.0:
        direction = direction.rotate(spread)

    spawn = origin + direction * (config.PLAYER_WIDTH * 0.5 + config.PROJECTILE_RADIUS + 10.0)
    spawn.x = min(max(spawn.x, arena.left + config.PROJECTILE_RADIUS), arena.right - config.PROJECTILE_RADIUS)
    spawn.y = min(max(spawn.y, arena.top + config.PROJECTILE_RADIUS), arena.water_y - config.PROJECTILE_RADIUS - 12.0)

    velocity = direction * (config.PROJECTILE_SPEED * speed_scale)
    projectile = Projectile(
        body=CircleBody(
            position=spawn,
            velocity=velocity,
            radius=config.PROJECTILE_RADIUS,
            mass=config.PROJECTILE_MASS * mass_scale,
            restitution=config.PROJECTILE_RESTITUTION,
        ),
        owner=owner,
        lifetime=config.PROJECTILE_LIFETIME,
        heavy=mass_scale > 1.0,
    )
    return projectile


def step_rigid_bodies(ball: Ball, projectiles: list[Projectile], dt: float) -> None:
    """Advance the ball and active projectiles using the shared engine helper."""

    bodies = [ball.body, *(projectile.body for projectile in projectiles)]
    step_circle_bodies(
        bodies,
        dt,
        gravity=config.GRAVITY,
        linear_damping=config.PROJECTILE_LINEAR_DAMPING,
    )


def update_ball_side(ball: Ball, arena: Arena) -> tuple[PlayerId, PlayerId]:
    """Track which side of the net currently contains the ball."""

    previous_side = ball.last_side
    current_side = arena.side_for_x(ball.body.position.x, fallback=previous_side)
    ball.last_side = current_side
    return previous_side, current_side


def ball_water_side(ball: Ball, arena: Arena) -> PlayerId:
    """Resolve the effective scoring side for water contact."""

    return arena.side_for_x(ball.body.position.x, fallback=ball.last_side)


def resolve_arena_bounds(ball: Ball, projectiles: list[Projectile], arena: Arena, dt: float) -> None:
    """Apply wall and water interactions, and cull dead projectiles."""

    _bounce_circle(ball.body, arena.left, arena.top, arena.right, arena.water_y, dt, stop_at_floor=True)
    if ball.body.position.y + ball.body.radius >= arena.water_y:
        ball.touched_water = True
        ball.body.position.y = arena.water_y - ball.body.radius

    write_index = 0
    for projectile in projectiles:
        projectile.lifetime -= dt
        body = projectile.body
        _bounce_circle(body, arena.left, arena.top, arena.right, arena.water_y, dt, stop_at_floor=False)

        remove_projectile = (
            projectile.lifetime <= 0.0
            or body.position.y - body.radius > arena.bottom + 8.0
            or body.position.y + body.radius >= arena.water_y
        )
        if remove_projectile:
            continue

        projectiles[write_index] = projectile
        write_index += 1

    if write_index < len(projectiles):
        del projectiles[write_index:]


def resolve_net_collisions(ball: Ball, projectiles: list[Projectile], arena: Arena) -> None:
    """Resolve circle collisions against the vertical net rectangle."""

    _resolve_circle_vs_net(ball.body, arena)
    for projectile in projectiles:
        _resolve_circle_vs_net(projectile.body, arena)


def resolve_projectile_collisions(
    ball: Ball,
    projectiles: list[Projectile],
    broadphase: SpatialHashGrid,
) -> float:
    """Resolve ball-projectile collisions and return the strongest impact speed."""

    if not projectiles:
        return 0.0

    bodies = [ball.body, *(projectile.body for projectile in projectiles)]
    broadphase.rebuild_circles(bodies)
    max_impact_speed = 0.0

    for index_a, index_b in broadphase.iter_pairs():
        if 0 not in (index_a, index_b):
            continue

        other_index = index_b if index_a == 0 else index_a
        other_body = bodies[other_index]
        relative_velocity = other_body.velocity - ball.body.velocity
        impact_speed = sqrt(relative_velocity.length_squared())
        if resolve_circle_collision(ball.body, other_body):
            max_impact_speed = max(max_impact_speed, impact_speed)

    return max_impact_speed


def _bounce_circle(
    body: CircleBody,
    left: float,
    top: float,
    right: float,
    bottom: float,
    dt: float,
    stop_at_floor: bool,
) -> None:
    radius = body.radius
    position = body.position
    velocity = body.velocity
    restitution = body.restitution

    if position.x < left + radius:
        position.x = left + radius
        velocity.x = abs(velocity.x) * restitution
    elif position.x > right - radius:
        position.x = right - radius
        velocity.x = -abs(velocity.x) * restitution

    if position.y < top + radius:
        position.y = top + radius
        velocity.y = abs(velocity.y) * restitution
    elif position.y > bottom - radius:
        position.y = bottom - radius
        if stop_at_floor:
            velocity.y = 0.0
            velocity.x *= max(0.0, 1.0 - 4.0 * dt)
        else:
            velocity.y = -abs(velocity.y) * restitution


def _resolve_circle_vs_net(body: CircleBody, arena: Arena) -> None:
    left, top, right, bottom = arena.net_rect()
    position = body.position

    closest_x = min(max(position.x, left), right)
    closest_y = min(max(position.y, top), bottom)
    dx = position.x - closest_x
    dy = position.y - closest_y
    radius = body.radius
    distance_sq = dx * dx + dy * dy
    if distance_sq >= radius * radius:
        return

    if distance_sq == 0.0:
        if position.x < arena.net_x:
            dx = -1.0
        else:
            dx = 1.0
        dy = 0.0
        distance = 1.0
    else:
        distance = distance_sq ** 0.5

    normal_x = dx / distance
    normal_y = dy / distance
    penetration = radius - distance

    position.x += normal_x * penetration
    position.y += normal_y * penetration

    separating_velocity = body.velocity.x * normal_x + body.velocity.y * normal_y
    if separating_velocity < 0.0:
        impulse = -(1.0 + body.restitution) * separating_velocity
        body.velocity.x += normal_x * impulse
        body.velocity.y += normal_y * impulse
