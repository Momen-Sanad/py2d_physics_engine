"""Shared contract for future demo scenes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DemoSpec:
    """Small metadata container for a runnable demo module."""

    name: str
    goal: str
