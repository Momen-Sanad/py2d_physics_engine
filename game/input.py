"""Input helpers for the playable Splashline Showdown scene."""

from __future__ import annotations

from dataclasses import dataclass

from engine.math2d import Vec2

from . import config
from .entities import Arena, Projectile, player_gun_origin
from .physics import build_projectile
from .settings import InputBindings
from .state import PlayerId, PlayerState, TurnState


@dataclass(slots=True)
class InputState:
    """Per-frame input snapshot used by the fixed update."""

    move_axis: float
    aim_world: Vec2
    fire_pressed: bool = False
    hop_pressed: bool = False


def read_input(
    events,
    keys,
    mouse_pos: tuple[int, int],
    bindings: InputBindings | None = None,
) -> InputState:
    """Convert pygame input into a small engine-agnostic snapshot."""

    import pygame

    active_bindings = bindings or InputBindings()
    move_axis = 0.0
    if _is_key_down(keys, active_bindings.move_left):
        move_axis -= 1.0
    if _is_key_down(keys, active_bindings.move_right):
        move_axis += 1.0

    fire_pressed = any(
        event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        for event in events
    ) or any(
        event.type == pygame.KEYDOWN and event.key == _key_code(active_bindings.fire)
        for event in events
    )
    return InputState(
        move_axis=move_axis,
        aim_world=Vec2(float(mouse_pos[0]), float(mouse_pos[1])),
        fire_pressed=fire_pressed,
        hop_pressed=False,
    )


def _is_key_down(keys, key_name: str) -> bool:
    key_code = _key_code(key_name)
    if key_code is None:
        return False
    try:
        return bool(keys[key_code])
    except (IndexError, KeyError, TypeError):
        return False


def _key_code(key_name: str) -> int | None:
    import pygame

    try:
        return pygame.key.key_code(key_name)
    except (ValueError, TypeError):
        return None


def update_player_movement(player: PlayerState, input_state: InputState, dt: float) -> None:
    """Move one player horizontally within their lane."""

    player.position.x += input_state.move_axis * player.speed * dt
    player.position.x = min(max(player.position.x, player.movement_min_x), player.movement_max_x)


def consume_shot_or_reject(turn: TurnState) -> bool:
    """Spend one shot if the current cooldown and budget allow it."""

    if turn.cooldown_remaining > 0.0 or turn.shots_left <= 0:
        return False
    turn.shots_left -= 1
    if turn.shots_left <= 0:
        turn.awaiting_cross = True
        turn.out_of_ammo_timer = 0.0
    return True


def can_fire_projectile(input_state: InputState, turn: TurnState, projectile_budget: int) -> bool:
    """Return whether a fire attempt can spend ammo and create a projectile."""

    return (
        input_state.fire_pressed
        and projectile_budget > 0
        and turn.cooldown_remaining <= 0.0
        and turn.shots_left > 0
    )


def check_turn_cross_net(
    active_player: PlayerId,
    previous_side: PlayerId,
    current_side: PlayerId,
) -> bool:
    """Return whether the ball crossed into the opponent's side this step."""

    return previous_side is not current_side and current_side is active_player.opponent()


def should_sync_turn_to_ball_side(
    active_player: PlayerId,
    current_side: PlayerId,
    ball_x: float,
    net_x: float,
    settle_distance: float,
) -> bool:
    """Return whether turn ownership should snap to the ball's settled side."""

    return (
        current_side is not active_player
        and abs(ball_x - net_x) >= settle_distance
    )


def try_fire_projectiles(
    player: PlayerState,
    input_state: InputState,
    turn: TurnState,
    arena: Arena,
    fire_count: int = 1,
    speed_scale: float = 1.0,
    mass_scale: float = 1.0,
    projectile_budget: int = config.MAX_PROJECTILES,
) -> list[Projectile]:
    """Spawn one or more projectiles from the active player's gun."""

    if not can_fire_projectile(input_state, turn, projectile_budget):
        return []
    consume_shot_or_reject(turn)

    origin = player_gun_origin(player)
    spread_angles = [0.0]
    if fire_count > 1:
        spread_angles = [-config.DOUBLE_SHOT_SPREAD, config.DOUBLE_SHOT_SPREAD]

    projectiles: list[Projectile] = []
    for spread in spread_angles[:projectile_budget]:
        projectiles.append(
            build_projectile(
                owner=player.player_id,
                origin=origin,
                aim_world=input_state.aim_world,
                arena=arena,
                speed_scale=speed_scale,
                mass_scale=mass_scale,
                spread=spread,
            )
        )

    turn.cooldown_remaining = config.SHOT_COOLDOWN
    return projectiles
