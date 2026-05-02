"""Shared 2D physics engine package."""

from .config import EngineConfig
from .math3d import Mat3, Quaternion, Vec3
from .math2d import Vec2
from .softbody import SoftBody

__all__ = ["EngineConfig", "Mat3", "Quaternion", "SoftBody", "Vec2", "Vec3"]
