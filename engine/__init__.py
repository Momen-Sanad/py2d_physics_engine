"""Shared 2D physics engine package."""

from .config import EngineConfig
from .math2d import Vec2
from .softbody import SoftBody

__all__ = ["EngineConfig", "SoftBody", "Vec2"]
