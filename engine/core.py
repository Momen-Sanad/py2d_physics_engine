"""Core timing and system orchestration primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class System(Protocol):
    """Minimal interface shared by each simulation subsystem."""

    def step(self, dt: float) -> None:
        """Advance the system by one fixed simulation step."""


@dataclass(slots=True)
class SimulationClock:
    """Tracks a fixed-timestep accumulator for stable simulation."""

    fixed_dt: float
    max_substeps: int = 5
    accumulator: float = 0.0

    def consume(self, frame_time: float) -> int:
        """Return how many fixed substeps should run this frame."""

        self.accumulator += frame_time
        substeps = 0
        while self.accumulator >= self.fixed_dt and substeps < self.max_substeps:
            self.accumulator -= self.fixed_dt
            substeps += 1
        return substeps


@dataclass(slots=True)
class PhysicsWorld:
    """Simple registry that steps all active systems in order."""

    systems: list[System] = field(default_factory=list)

    def register(self, system: System) -> None:
        self.systems.append(system)

    def step(self, dt: float) -> None:
        for system in self.systems:
            system.step(dt)