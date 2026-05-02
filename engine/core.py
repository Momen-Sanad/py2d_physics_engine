# <file>
# <summary>
# Core timing and system orchestration primitives.
# </summary>
# </file>
"""Core timing and system orchestration primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


# <summary>
# Minimal interface shared by each simulation subsystem.
# </summary>
class System(Protocol):
    """Minimal interface shared by each simulation subsystem."""

    # <summary>
    # Advance the system by one fixed simulation step.
    # </summary>
    # <param name="dt">Simulation timestep in seconds.</param>
    def step(self, dt: float) -> None:
        """Advance the system by one fixed simulation step."""


# <summary>
# Tracks a fixed-timestep accumulator for stable simulation.
# </summary>
@dataclass(slots=True)
class SimulationClock:
    """Tracks a fixed-timestep accumulator for stable simulation."""

    fixed_dt: float
    max_substeps: int = 5
    accumulator: float = 0.0

    # <summary>
    # Return how many fixed substeps should run this frame.
    # </summary>
    # <param name="frame_time">Elapsed frame time in seconds.</param>
    # <returns>Computed result described by the return type annotation.</returns>
    def consume(self, frame_time: float) -> int:
        """Return how many fixed substeps should run this frame."""

        self.accumulator += frame_time
        substeps = 0
        while self.accumulator >= self.fixed_dt and substeps < self.max_substeps:
            self.accumulator -= self.fixed_dt
            substeps += 1
        return substeps


# <summary>
# Simple registry that steps all active systems in order.
# </summary>
@dataclass(slots=True)
class PhysicsWorld:
    """Simple registry that steps all active systems in order."""

    systems: list[System] = field(default_factory=list)

    # <summary>
    # Add a simulation system to the world update list.
    # </summary>
    # <param name="system">Input value for system.</param>
    def register(self, system: System) -> None:
        self.systems.append(system)

    # <summary>
    # Step every registered system once using the shared timestep.
    # </summary>
    # <param name="dt">Simulation timestep in seconds.</param>
    def step(self, dt: float) -> None:
        for system in self.systems:
            system.step(dt)
