# <file>
# <summary>
# Shared contract for future demo scenes.
# </summary>
# </file>
"""Shared contract for future demo scenes."""

from __future__ import annotations

from dataclasses import dataclass


# <summary>
# Small metadata container for a runnable demo module.
# </summary>
@dataclass(slots=True)
class DemoSpec:
    """Small metadata container for a runnable demo module."""

    name: str
    goal: str
