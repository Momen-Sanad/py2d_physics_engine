"""Small screen and menu helpers for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ScreenMode(str, Enum):
    """High-level player-facing overlay modes."""

    START = "start"
    PLAYING = "playing"
    PAUSED = "paused"
    HOW_TO_PLAY = "how_to_play"
    POWERUPS = "powerups"
    OPTIONS = "options"
    CONTROLS = "controls"
    GAME_OVER = "game_over"


class MenuAction(str, Enum):
    """Actions triggered by overlay menu items."""

    START_GAME = "start_game"
    RESUME = "resume"
    RESTART = "restart"
    HOW_TO_PLAY = "how_to_play"
    POWERUPS = "powerups"
    OPTIONS = "options"
    CONTROLS = "controls"
    REMAP_LEFT = "remap_left"
    REMAP_RIGHT = "remap_right"
    REMAP_FIRE = "remap_fire"
    RESET_BINDINGS = "reset_bindings"
    MAIN_MENU = "main_menu"
    SFX_VOLUME = "sfx_volume"
    MUTE = "mute"
    BACK = "back"
    EXIT = "exit"


@dataclass(frozen=True, slots=True)
class MenuItem:
    """Text label plus action for a simple keyboard menu row."""

    label: str
    action: MenuAction


def clamp_menu_index(index: int, item_count: int) -> int:
    """Wrap menu selection around available items."""

    if item_count <= 0:
        return 0
    return index % item_count
