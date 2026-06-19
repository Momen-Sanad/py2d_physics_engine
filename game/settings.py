"""Runtime settings for Splashline Showdown."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


SETTINGS_VERSION = 1


@dataclass(slots=True)
class InputBindings:
    """Serializable keyboard bindings for gameplay input."""

    move_left: str = "a"
    move_right: str = "d"
    fire: str = "f"

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-friendly representation."""

        return {
            "move_left": self.move_left,
            "move_right": self.move_right,
            "fire": self.fire,
        }

    @classmethod
    def from_dict(cls, data: object) -> "InputBindings":
        """Build bindings from untrusted JSON data."""

        if not isinstance(data, dict):
            return cls()

        defaults = cls()
        return cls(
            move_left=_clean_key_name(data.get("move_left"), defaults.move_left),
            move_right=_clean_key_name(data.get("move_right"), defaults.move_right),
            fire=_clean_key_name(data.get("fire"), defaults.fire),
        )


@dataclass(slots=True)
class GameSettings:
    """Small runtime-only settings container."""

    sfx_volume: float = 0.8
    muted: bool = False
    bindings: InputBindings = field(default_factory=InputBindings)
    tutorial_seen: bool = False

    def adjust_sfx_volume(self, delta: float) -> None:
        """Adjust SFX volume and clamp to the supported range."""

        self.sfx_volume = min(1.0, max(0.0, self.sfx_volume + delta))

    def toggle_muted(self) -> None:
        """Toggle all SFX playback."""

        self.muted = not self.muted

    def effective_sfx_volume(self) -> float:
        """Return the volume that should be applied to sounds."""

        return 0.0 if self.muted else self.sfx_volume

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""

        return {
            "version": SETTINGS_VERSION,
            "sfx_volume": self.sfx_volume,
            "muted": self.muted,
            "bindings": self.bindings.to_dict(),
            "tutorial_seen": self.tutorial_seen,
        }

    @classmethod
    def from_dict(cls, data: object) -> "GameSettings":
        """Build settings from untrusted JSON data."""

        if not isinstance(data, dict):
            return cls()

        settings = cls()
        settings.sfx_volume = _clean_volume(data.get("sfx_volume"), settings.sfx_volume)
        settings.muted = bool(data.get("muted", settings.muted))
        settings.bindings = InputBindings.from_dict(data.get("bindings"))
        settings.tutorial_seen = bool(data.get("tutorial_seen", settings.tutorial_seen))
        return settings


def default_settings_path() -> Path:
    """Return the platform-appropriate settings path."""

    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "SplashlineShowdown" / "settings.json"

    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "splashline-showdown" / "settings.json"


def load_settings(path: Path | None = None) -> GameSettings:
    """Load settings, falling back to defaults for missing or invalid files."""

    settings_path = default_settings_path() if path is None else path
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return GameSettings()
    return GameSettings.from_dict(data)


def save_settings(settings: GameSettings, path: Path | None = None) -> bool:
    """Persist settings and return whether the write succeeded."""

    settings_path = default_settings_path() if path is None else path
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(settings.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


def _clean_volume(value: object, fallback: float) -> float:
    try:
        return min(1.0, max(0.0, float(value)))
    except (TypeError, ValueError):
        return fallback


def _clean_key_name(value: object, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    cleaned = value.strip().lower()
    return cleaned or fallback
