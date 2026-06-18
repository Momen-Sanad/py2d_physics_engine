"""Runtime settings for Splashline Showdown."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GameSettings:
    """Small runtime-only settings container."""

    sfx_volume: float = 0.8
    muted: bool = False

    def adjust_sfx_volume(self, delta: float) -> None:
        """Adjust SFX volume and clamp to the supported range."""

        self.sfx_volume = min(1.0, max(0.0, self.sfx_volume + delta))

    def toggle_muted(self) -> None:
        """Toggle all SFX playback."""

        self.muted = not self.muted

    def effective_sfx_volume(self) -> float:
        """Return the volume that should be applied to sounds."""

        return 0.0 if self.muted else self.sfx_volume
