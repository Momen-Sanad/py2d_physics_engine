"""Powerup pickups and temporary match effects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random

from engine.math2d import Vec2

from . import config
from .entities import Arena, Ball, Projectile
from .state import PlayerId, PlayerState


class PowerupKind(str, Enum):
    """Readable powerup identifiers."""

    HEAVY_SHOT = "heavy_shot"
    DOUBLE_SHOT = "double_shot"
    NULL_WIND = "null_wind"

    def label(self) -> str:
        labels = {
            PowerupKind.HEAVY_SHOT: "Heavy Shot",
            PowerupKind.DOUBLE_SHOT: "Double Shot",
            PowerupKind.NULL_WIND: "Null Wind",
        }
        return labels[self]


@dataclass(slots=True)
class PowerupPickup:
    """World-space pickup orb."""

    kind: PowerupKind
    position: Vec2
    radius: float = config.POWERUP_PICKUP_RADIUS
    lifetime: float = config.POWERUP_LIFETIME


@dataclass(slots=True)
class ActiveEffect:
    """Temporary effect attached to a player or the global arena."""

    kind: PowerupKind
    owner: PlayerId | None
    remaining: float


@dataclass(slots=True)
class FireModifiers:
    """One-shot projectile spawn modifiers."""

    projectile_count: int = 1
    speed_scale: float = 1.0
    mass_scale: float = 1.0


def spawn_powerup(
    rng: Random,
    arena: Arena,
    pickups: list[PowerupPickup],
    max_pickups: int = config.MAX_POWERUPS,
) -> PowerupPickup | None:
    """Spawn one airborne powerup if pickup capacity allows it."""

    if len(pickups) >= max_pickups:
        return None

    for _ in range(12):
        x = rng.uniform(arena.left + 90.0, arena.right - 90.0)
        if abs(x - arena.net_x) < 88.0:
            continue
        y = rng.uniform(arena.top + 120.0, arena.water_y - 130.0)
        kind = rng.choice(
            [
                PowerupKind.HEAVY_SHOT,
                PowerupKind.DOUBLE_SHOT,
                PowerupKind.NULL_WIND,
            ]
        )
        pickup = PowerupPickup(kind=kind, position=Vec2(x, y))
        pickups.append(pickup)
        return pickup
    return None


def tick_pickups(pickups: list[PowerupPickup], dt: float) -> None:
    """Age out expired floating pickups."""

    write_index = 0
    for pickup in pickups:
        pickup.lifetime -= dt
        if pickup.lifetime <= 0.0:
            continue
        pickups[write_index] = pickup
        write_index += 1

    if write_index < len(pickups):
        del pickups[write_index:]


def collect_powerups(
    ball: Ball,
    projectiles: list[Projectile],
    pickups: list[PowerupPickup],
    active_effects: list[ActiveEffect],
    active_player: PlayerId,
    players: tuple[PlayerState, PlayerState],
) -> list[PowerupKind]:
    """Collect overlapping pickups with the ball or projectiles and activate them."""

    collected: list[PowerupKind] = []
    write_index = 0
    for pickup in pickups:
        owner = _pickup_owner(pickup, ball, projectiles, active_player)
        if owner is not None:
            effect_owner = None if pickup.kind is PowerupKind.NULL_WIND else owner
            activate_effect(active_effects, pickup.kind, effect_owner)
            collected.append(pickup.kind)
            continue
        pickups[write_index] = pickup
        write_index += 1

    if write_index < len(pickups):
        del pickups[write_index:]

    if collected:
        sync_effect_timers(players, active_effects)
    return collected


def _pickup_owner(
    pickup: PowerupPickup,
    ball: Ball,
    projectiles: list[Projectile],
    active_player: PlayerId,
) -> PlayerId | None:
    """Resolve which player should receive a pickup hit this step."""

    if _overlaps_pickup(pickup, ball.body.position, ball.body.radius):
        return active_player

    for projectile in projectiles:
        if _overlaps_pickup(pickup, projectile.body.position, projectile.body.radius):
            return projectile.owner

    return None


def _overlaps_pickup(
    pickup: PowerupPickup,
    position: Vec2,
    radius: float,
) -> bool:
    """Return whether a circular gameplay object overlaps a pickup."""

    delta = pickup.position - position
    radius_sum = pickup.radius + radius
    return delta.length_squared() <= radius_sum * radius_sum


def activate_effect(
    active_effects: list[ActiveEffect],
    kind: PowerupKind,
    owner: PlayerId | None,
) -> None:
    """Add or refresh a timed effect."""

    duration = {
        PowerupKind.HEAVY_SHOT: config.HEAVY_SHOT_DURATION,
        PowerupKind.DOUBLE_SHOT: config.DOUBLE_SHOT_DURATION,
        PowerupKind.NULL_WIND: config.NULL_WIND_DURATION,
    }[kind]

    for effect in active_effects:
        if effect.kind is kind and effect.owner is owner:
            effect.remaining = duration
            return

    active_effects.append(ActiveEffect(kind=kind, owner=owner, remaining=duration))


def expire_effects(
    active_effects: list[ActiveEffect],
    dt: float,
    players: tuple[PlayerState, PlayerState],
) -> None:
    """Decrease durations and remove expired effects."""

    write_index = 0
    for effect in active_effects:
        effect.remaining -= dt
        if effect.remaining <= 0.0:
            continue
        active_effects[write_index] = effect
        write_index += 1

    if write_index < len(active_effects):
        del active_effects[write_index:]

    sync_effect_timers(players, active_effects)


def apply_active_effects(active_effects: list[ActiveEffect], wind_force_x: float) -> float:
    """Return wind force after global powerup effects are applied."""

    return 0.0 if has_effect(active_effects, PowerupKind.NULL_WIND) else wind_force_x


def pop_fire_modifiers(
    active_effects: list[ActiveEffect],
    owner: PlayerId,
    players: tuple[PlayerState, PlayerState],
) -> FireModifiers:
    """Consume next-shot effects and return projectile spawn modifiers."""

    modifiers = FireModifiers()
    kept_effects: list[ActiveEffect] = []
    for effect in active_effects:
        if effect.owner is owner and effect.kind is PowerupKind.HEAVY_SHOT:
            modifiers.mass_scale = max(modifiers.mass_scale, 1.75)
            modifiers.speed_scale = max(modifiers.speed_scale, 1.12)
            continue
        if effect.owner is owner and effect.kind is PowerupKind.DOUBLE_SHOT:
            modifiers.projectile_count = max(modifiers.projectile_count, 2)
            continue
        kept_effects.append(effect)

    active_effects[:] = kept_effects
    sync_effect_timers(players, active_effects)
    return modifiers


def has_effect(
    active_effects: list[ActiveEffect],
    kind: PowerupKind,
    owner: PlayerId | None = None,
) -> bool:
    """Check whether a matching effect is currently active."""

    return any(effect.kind is kind and effect.owner is owner for effect in active_effects)


def sync_effect_timers(
    players: tuple[PlayerState, PlayerState],
    active_effects: list[ActiveEffect],
) -> None:
    """Project active effects into each player's UI-friendly timer map."""

    for player in players:
        player.effect_timers.clear()

    for effect in active_effects:
        if effect.owner is None:
            continue
        for player in players:
            if player.player_id is effect.owner:
                player.effect_timers[effect.kind.label()] = effect.remaining
                break
