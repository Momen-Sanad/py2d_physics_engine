"""Arena and runtime entity containers for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass

from engine.math2d import Vec2
from engine.rigidbody import CircleBody

from . import config
from .state import PlayerId, PlayerState


@dataclass(slots=True)
class Arena:
    """Static arena geometry and layout values."""

    left: float
    top: float
    right: float
    bottom: float
    water_y: float
    net_x: float
    net_width: float
    net_height: float
    player_y: float
    serve_y: float

    def side_for_x(self, x: float, fallback: PlayerId | None = None) -> PlayerId:
        if x < self.net_x:
            return PlayerId.LEFT
        if x > self.net_x:
            return PlayerId.RIGHT
        return fallback or PlayerId.LEFT

    def player_bounds(self, player_id: PlayerId) -> tuple[float, float]:
        lane_padding = 56.0
        if player_id is PlayerId.LEFT:
            return self.left + lane_padding, self.net_x - 90.0
        return self.net_x + 90.0, self.right - lane_padding

    def net_rect(self) -> tuple[float, float, float, float]:
        half_width = self.net_width * 0.5
        return (
            self.net_x - half_width,
            self.water_y - self.net_height,
            self.net_x + half_width,
            self.water_y,
        )


@dataclass(slots=True)
class Ball:
    """Playable beach ball state."""

    body: CircleBody
    drip_intensity: float = 0.0
    last_side: PlayerId = PlayerId.LEFT
    touched_water: bool = False


@dataclass(slots=True)
class Projectile:
    """Shot projectile fired by a player."""

    body: CircleBody
    owner: PlayerId
    lifetime: float
    heavy: bool = False


def build_arena() -> Arena:
    return Arena(
        left=config.ARENA_MARGIN,
        top=config.ARENA_MARGIN,
        right=config.WINDOW_WIDTH - config.ARENA_MARGIN,
        bottom=float(config.WINDOW_HEIGHT),
        water_y=config.WATER_Y,
        net_x=config.NET_X,
        net_width=config.NET_WIDTH,
        net_height=config.NET_HEIGHT,
        player_y=config.PLAYER_Y,
        serve_y=config.WATER_Y - config.NET_HEIGHT - 72.0,
    )


def build_players(arena: Arena) -> tuple[PlayerState, PlayerState]:
    left_min_x, left_max_x = arena.player_bounds(PlayerId.LEFT)
    right_min_x, right_max_x = arena.player_bounds(PlayerId.RIGHT)
    left_x = left_min_x + (left_max_x - left_min_x) * 0.32
    right_x = right_min_x + (right_max_x - right_min_x) * 0.68

    return (
        PlayerState(
            player_id=PlayerId.LEFT,
            position=Vec2(left_x, arena.player_y),
            movement_min_x=left_min_x,
            movement_max_x=left_max_x,
            speed=config.PLAYER_SPEED,
        ),
        PlayerState(
            player_id=PlayerId.RIGHT,
            position=Vec2(right_x, arena.player_y),
            movement_min_x=right_min_x,
            movement_max_x=right_max_x,
            speed=config.PLAYER_SPEED,
        ),
    )


def player_gun_origin(player: PlayerState) -> Vec2:
    direction = 1.0 if player.player_id is PlayerId.LEFT else -1.0
    return Vec2(
        player.position.x + config.PLAYER_GUN_OFFSET_X * direction,
        player.position.y + config.PLAYER_GUN_OFFSET_Y,
    )
