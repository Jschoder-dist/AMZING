"""
maze_generator — standalone maze generation library.

Public API:
    Maze            — the maze grid dataclass
    MazeGenerator   — generates mazes via DFS backtracker
    Point           — (x, y) coordinate dataclass
    WALL_N/E/S/W    — wall bitmask constants
    ALL_WALLS       — bitmask for a fully-closed cell (logo cells)
"""

from ._generator import Maze, MazeGenerator
from ._types import ALL_WALLS, WALL_E, WALL_N, WALL_S, WALL_W, Point

__all__ = [
    "Maze",
    "MazeGenerator",
    "Point",
    "ALL_WALLS",
    "WALL_N",
    "WALL_E",
    "WALL_S",
    "WALL_W",
]
