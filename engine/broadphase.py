# <file>
# <summary>
# Broadphase utilities for reducing collision candidate counts.
# </summary>
# </file>
"""Broadphase utilities for reducing collision candidate counts."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from typing import Iterable

from .rigidbody import CircleBody


# <summary>
# Uniform-grid broadphase that preserves circle collision candidates.
# </summary>
@dataclass(slots=True)
class SpatialHashGrid:
    """Uniform-grid broadphase that preserves circle collision candidates."""

    cell_size: float
    buckets: dict[tuple[int, int], list[int]] = field(default_factory=dict)
    pair_buffer: set[tuple[int, int]] = field(default_factory=set)

    # <summary>
    # Insert each circle into every cell touched by its AABB.
    # </summary>
    # <param name="bodies">Rigid body collection being read or updated.</param>
    def rebuild_circles(self, bodies: Iterable[CircleBody]) -> None:
        """Insert each circle into every cell touched by its AABB."""

        buckets = self.buckets
        buckets.clear()
        cell_size = self.cell_size
        inverse_cell_size = 1.0 / cell_size

        for index, body in enumerate(bodies):
            min_x = floor((body.position.x - body.radius) * inverse_cell_size)
            max_x = floor((body.position.x + body.radius) * inverse_cell_size)
            min_y = floor((body.position.y - body.radius) * inverse_cell_size)
            max_y = floor((body.position.y + body.radius) * inverse_cell_size)

            for cell_y in range(min_y, max_y + 1):
                for cell_x in range(min_x, max_x + 1):
                    key = (cell_x, cell_y)
                    cell = buckets.get(key)
                    if cell is None:
                        buckets[key] = [index]
                    else:
                        cell.append(index)

    # <summary>
    # Yield unique candidate pairs from occupied cells.
    # </summary>
    # <returns>Computed result described by the return type annotation.</returns>
    def iter_pairs(self) -> Iterable[tuple[int, int]]:
        """Yield unique candidate pairs from occupied cells."""

        seen_pairs = self.pair_buffer
        seen_pairs.clear()

        for indices in self.buckets.values():
            count = len(indices)
            for offset in range(count - 1):
                index_a = indices[offset]
                for inner in range(offset + 1, count):
                    index_b = indices[inner]
                    pair = (index_a, index_b) if index_a < index_b else (index_b, index_a)
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    yield pair
