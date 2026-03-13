"""Central configuration values for the 2D physics engine."""

from dataclasses import dataclass, field

from .math2d import Vec2


@dataclass(frozen=True, slots=True)
class EngineConfig:
    """Shared simulation settings used across demos and systems."""

    fixed_dt: float = 1.0 / 120.0
    gravity: Vec2 = field(default_factory=lambda: Vec2(0.0, 980.0))
    solver_iterations: int = 8
    max_substeps: int = 5
