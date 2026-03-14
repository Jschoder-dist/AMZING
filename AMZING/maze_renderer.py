#!/usr/bin/env python3
"""
Terminal renderer for A-Maze-ing.

HOW IT WORKS
=======================
Terminal renderer for A-Maze-ing.
Walls between cells are drawn as filled blocks (dark grey background).
Open passages are drawn as empty (transparent) blocks.

The render grid is (2*width + 1) columns wide and (2*height + 1) rows tall.
Extra row/col on each side = outer border.

For a 3x2 maze, the render grid is 7x5:
    ┌─┬─┬─┐   row 0 (top border)
    │ │ │ │   row 1 (cell row 0)
    ├─┼─┼─┤   row 2 (wall row between cell rows 0 and 1)
    │ │ │ │   row 3 (cell row 1)
    └─┴─┴─┘   row 4 (bottom border)

COLORS
======
We use ANSI 256-color background codes (\033[48;5;Nm).
Available wall color themes are in WALL_COLORS below.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, List, Set, Tuple

from maze_generator import Maze
from maze_types import WALL_E, WALL_S, Point

# ANSI escape codes
_RESET: Final[str] = "\033[0m"

# Special cell colors
_COLOR_WALL: Final[str] = "\033[48;5;235m"   # very dark grey  (wall block)
_COLOR_PATH: Final[str] = "\033[48;5;39m"    # bright blue     (solution path)
_COLOR_LOGO: Final[str] = "\033[48;5;196m"   # bright red      (42 logo cells)
_COLOR_ENTRY: Final[str] = "\033[48;5;40m"    # green           (entry cell)
_COLOR_EXIT: Final[str] = "\033[48;5;202m"   # orange          (exit cell)

# Rotating wall color themes (activated by 'c' command)
# Each theme replaces the default dark-grey wall color
WALL_COLORS: Final[List[str]] = [
    "\033[48;5;235m",   # 0: dark grey  (default)
    "\033[48;5;94m",    # 1: brown
    "\033[48;5;22m",    # 2: dark green
    "\033[48;5;17m",    # 3: dark blue
    "\033[48;5;52m",    # 4: dark red
    "\033[48;5;55m",    # 5: dark purple
]


@dataclass
class RenderState:
    """Holds display options that the user can toggle at runtime."""

    show_path: bool = False    # whether to highlight the solution path
    color_index: int = 0       # which wall color theme is active

    def next_color(self) -> None:
        """Cycle to the next wall color theme."""
        self.color_index = (self.color_index + 1) % len(WALL_COLORS)

    def wall_color(self) -> str:
        """Return the current ANSI wall background color."""
        return WALL_COLORS[self.color_index]


def render_maze(
    maze: Maze,
    entry: Point,
    exit_: Point,
    path: str,
    state: RenderState,
) -> str:
    """
    Render the maze as a coloured string for terminal display.

    Args:
        maze:   the maze to render.
        entry:  entry cell (shown in green with 'E').
        exit_:  exit cell (shown in orange with 'X').
        path:   solution path string (e.g. "EESNNE").
        state:  current display options (show path, wall color).

    Returns:
        A multi-line string ready to print to the terminal.
    """
    # Compute which cells are on the solution path (only if path display is ON)
    path_cells: Set[Tuple[int, int]] = set()
    if state.show_path:
        path_cells = _path_string_to_cell_set(entry, path)

    wall_bg = state.wall_color()

    # Build a 2D grid of coloured string "pixels"
    # Each pixel is a 2-character wide block with an ANSI background color
    render_width = maze.width * 2 + 1
    render_height = maze.height * 2 + 1

    # Start everything as a wall pixel
    grid: List[List[str]] = [
        [wall_bg + "  " + _RESET for _ in range(render_width)]
        for _ in range(render_height)
    ]

    # Fill in each maze cell and its open passages
    for y in range(maze.height):
        for x in range(maze.width):
            bits = maze.get(Point(x, y))
            # Each cell (x, y) maps to render position (rx, ry)
            rx = x * 2 + 1
            ry = y * 2 + 1

            # Choose the cell's background color
            cell_bg = _cell_color(
                x, y, entry, exit_, path_cells, bits, wall_bg)
            grid[ry][rx] = cell_bg

            # If the East wall is OPEN, fill the wall pixel between this cell
            # and the next one to the right with the appropriate color
            if x + 1 < maze.width and not (bits & WALL_E):
                passage_bg = _passage_color(
                    x, y, x + 1, y, path_cells, bits, wall_bg
                )
                grid[ry][rx + 1] = passage_bg

            # If the South wall is OPEN, fill the wall pixel between this cell
            # and the one below with the appropriate color
            if y + 1 < maze.height and not (bits & WALL_S):
                passage_bg = _passage_color(
                    x, y, x, y + 1, path_cells, bits, wall_bg
                )
                grid[ry + 1][rx] = passage_bg

    # Join all pixels into lines, then join lines with newlines
    return "\n".join("".join(row) for row in grid)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _cell_color(
    x: int,
    y: int,
    entry: Point,
    exit_: Point,
    path_cells: Set[Tuple[int, int]],
    bits: int,
    wall_bg: str,
) -> str:
    """Return the colored pixel string for a maze cell."""
    from maze_types import ALL_WALLS

    if bits == ALL_WALLS:
        # Fully closed cell = part of the 42 logo
        return _COLOR_LOGO + "  " + _RESET

    if x == entry.x and y == entry.y:
        return _COLOR_ENTRY + "E " + _RESET

    if x == exit_.x and y == exit_.y:
        return _COLOR_EXIT + "X " + _RESET

    if (x, y) in path_cells:
        return _COLOR_PATH + "  " + _RESET

    # Regular open cell — transparent (no background, just spaces)
    return "  "


def _passage_color(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    path_cells: Set[Tuple[int, int]],
    bits: int,
    wall_bg: str,
) -> str:
    """
    Return the color for the wall pixel between two adjacent cells.

    The passage is blue if BOTH connected cells are on the solution path.
    The passage is red if it belongs to the logo.
    Otherwise it is transparent (open corridor).
    """
    from maze_types import ALL_WALLS

    if bits == ALL_WALLS:
        return _COLOR_LOGO + "  " + _RESET

    if (x1, y1) in path_cells and (x2, y2) in path_cells:
        return _COLOR_PATH + "  " + _RESET

    return "  "   # open passage, no background


def _path_string_to_cell_set(entry: Point, path: str) -> Set[Tuple[int, int]]:
    """
    Convert a path string like "EESNN" into a set of (x, y) cells.

    Starts at entry and follows each direction letter.
    """
    moves = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    x, y = entry.x, entry.y
    cells: Set[Tuple[int, int]] = {(x, y)}

    for letter in path:
        if letter in moves:
            dx, dy = moves[letter]
            x += dx
            y += dy
            cells.add((x, y))

    return cells
