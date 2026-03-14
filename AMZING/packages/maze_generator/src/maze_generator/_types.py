"""
Types and constants for the maze_generator package.

Each cell stores a number from 0 to 15.
Each bit of that number tells whether a wall is present:
    bit 0 (value 1) = North wall
    bit 1 (value 2) = East wall
    bit 2 (value 4) = South wall
    bit 3 (value 8) = West wall

Example:
    0b0101 = 5  => North wall + South wall, no East or West wall
    0b1111 = 15 => All 4 walls closed (used for the 42 logo pattern)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Wall bit values — one bit per direction
WALL_N: Final[int] = 1   # North  (bit 0)
WALL_E: Final[int] = 2   # East   (bit 1)
WALL_S: Final[int] = 4   # South  (bit 2)
WALL_W: Final[int] = 8   # West   (bit 3)

# A fully closed cell (all 4 walls set) — used to draw the "42" logo
ALL_WALLS: Final[int] = WALL_N | WALL_E | WALL_S | WALL_W  # = 15 = 0xF


@dataclass(frozen=True)
class Point:
    """A simple (x, y) position in the maze grid."""

    x: int
    y: int
