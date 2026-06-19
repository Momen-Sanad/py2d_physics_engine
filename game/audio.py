"""Generated sound effects for Splashline Showdown."""

from __future__ import annotations

from array import array
from dataclasses import dataclass, field
from math import pi, sin
from typing import Any


SAMPLE_RATE = 44100
SOUND_SPECS = {
    "menu": (660.0, 0.055, 0.22),
    "shot": (520.0, 0.09, 0.34),
    "hit": (170.0, 0.08, 0.42),
    "splash": (240.0, 0.16, 0.32),
    "powerup": (880.0, 0.18, 0.28),
    "match_over": (330.0, 0.36, 0.26),
    "victory": (740.0, 0.48, 0.30),
}
SOUND_COOLDOWNS = {
    "menu": 0.04,
    "shot": 0.03,
    "hit": 0.10,
    "splash": 0.22,
    "powerup": 0.10,
    "match_over": 0.50,
    "victory": 0.75,
}


@dataclass(slots=True)
class AudioManager:
    """Tiny audio manager that generates simple in-memory SFX."""

    sfx_volume: float = 0.8
    muted: bool = False
    enabled: bool = False
    sounds: dict[str, Any] = field(default_factory=dict)
    cooldowns: dict[str, float] = field(default_factory=dict)

    def load(self) -> None:
        """Create pygame sounds if the mixer is available."""

        try:
            import pygame

            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
            self.sounds = {
                name: pygame.mixer.Sound(buffer=_generate_tone_bytes(*spec))
                for name, spec in SOUND_SPECS.items()
            }
            self.enabled = True
        except Exception:
            self.sounds.clear()
            self.enabled = False

    def step(self, dt: float) -> None:
        """Advance internal cooldown timers."""

        expired: list[str] = []
        for name, remaining in self.cooldowns.items():
            remaining -= dt
            if remaining <= 0.0:
                expired.append(name)
            else:
                self.cooldowns[name] = remaining
        for name in expired:
            del self.cooldowns[name]

    def set_sfx_volume(self, value: float) -> None:
        """Set SFX volume in the 0..1 range."""

        self.sfx_volume = min(1.0, max(0.0, value))

    def set_muted(self, muted: bool) -> None:
        """Enable or disable all SFX playback."""

        self.muted = muted

    def play(self, name: str) -> None:
        """Play a named sound if it exists and is not cooling down."""

        if self.muted or not self.enabled or name in self.cooldowns:
            return
        sound = self.sounds.get(name)
        if sound is None:
            return
        sound.set_volume(self.sfx_volume)
        sound.play()
        cooldown = SOUND_COOLDOWNS.get(name, 0.05)
        if cooldown > 0.0:
            self.cooldowns[name] = cooldown


def _generate_tone_bytes(frequency: float, duration: float, volume: float) -> bytes:
    """Generate a short decaying 16-bit mono tone."""

    sample_count = max(1, int(SAMPLE_RATE * duration))
    samples = array("h")
    for index in range(sample_count):
        progress = index / sample_count
        envelope = (1.0 - progress) ** 1.8
        wave = sin(2.0 * pi * frequency * index / SAMPLE_RATE)
        samples.append(int(32767 * volume * envelope * wave))
    return samples.tobytes()
