#!/usr/bin/env python3
"""
Maze generator for A-Maze-ing.

HOW IT WORKS
============
We start with a grid where every cell has all 4 walls (value = 15).
Then we "carve" passages by removing walls between neighbours.

Two algorithms are available:

1. PERFECT maze (PERFECT=True in config)
   Uses the "Recursive Backtracker" algorithm (also called DFS):
   - Pick a starting cell.
   - Randomly visit unvisited neighbours, removing the wall between them.
   - Backtrack when stuck (no unvisited neighbours left).
   - Result: every cell is reachable, and there is exactly ONE path
     between any two cells (no loops, no dead-end islands).

2. NON-PERFECT maze (PERFECT=False in config)
   Same as above, then we add extra passages randomly.
   This creates loops, so there are multiple paths between some cells.

The "42" logo is placed FIRST as fully-closed cells (value = 15).
The carving algorithm skips those cells so the logo stays intact.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from maze_types import ALL_WALLS, WALL_E, WALL_N, WALL_S, WALL_W, Point

# The four directions we can travel from any cell.
# Each entry is: (delta_x, delta_y, wall_to_remove_in_current_cell,
# wall_to_remove_in_neighbour)
DIRECTIONS: List[Tuple[int, int, int, int]] = [
    # North: move up,    remove N wall here and S wall there
    (0, -1, WALL_N, WALL_S),
    # East:  move right,  remove E wall here and W wall there
    (1, 0, WALL_E, WALL_W),
    # South: move down,   remove S wall here and N wall there
    (0, 1, WALL_S, WALL_N),
    # West:  move left,   remove W wall here and E wall there
    (-1, 0, WALL_W, WALL_E),
]

# The "42" logo pattern.
# Each tuple is (col_offset, row_offset) relative to the logo top-left.
# The "4" occupies columns 0-3, the "2" occupies columns 5-8.
# The logo is 9 wide and 5 tall.
LOGO_CELLS: List[Tuple[int, int]] = [
    # Chiffre "4"
    (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2),  # left + horizontal bar
    (3, 0), (3, 1),                                      # right bar (top half)
    # right bar (bottom half)
    (3, 3), (3, 4),
    # Chiffre "2"
    (5, 0), (6, 0), (7, 0), (8, 0),   # top bar
    (8, 1),                             # right bar (top)
    (5, 2), (6, 2), (7, 2), (8, 2),   # middle bar
    (5, 3),                             # left bar (bottom)
    (5, 4), (6, 4), (7, 4), (8, 4),   # bottom bar
]

# Minimum maze size to display the logo (9 wide + 2 margin, 5 tall + 2 margin)
LOGO_MIN_WIDTH: int = 11
LOGO_MIN_HEIGHT: int = 7


@dataclass
class Maze:
    """
    The maze grid.

    cells[y][x] holds the wall bitmask of cell (x, y).
    Use get() and set() to read/write cells safely.
    """

    width: int
    height: int
    cells: List[List[int]]

    def in_bounds(self, p: Point) -> bool:
        """Return True if point p is inside the grid."""
        return 0 <= p.x < self.width and 0 <= p.y < self.height

    def get(self, p: Point) -> int:
        """Return the wall bitmask of cell p."""
        return self.cells[p.y][p.x]

    def set(self, p: Point, val: int) -> None:
        """Set the wall bitmask of cell p."""
        self.cells[p.y][p.x] = val


class MazeGenerator:
    """
    Generates a maze of the given size.

    Usage:
        gen = MazeGenerator(width=20, height=15, seed=42)
        maze = gen.generate(perfect=True)

    Args:
        width:  Number of columns.
        height: Number of rows.
        seed:   Optional integer for reproducible results.
                If None, the maze is different every time.
    """

    def __init__(self, width: int, height: int,
                 seed: Optional[int] = None) -> None:
        """Set up the generator. Fix the random seed for reproducibility."""
        self._width = width
        self._height = height
        # Fix the random seed so the same seed always gives the same maze
        if seed is not None:
            random.seed(seed)

    def generate(self, perfect: bool = True) -> Maze:
        """
        Generate and return a Maze object.

        Args:
            perfect: If True, carve a perfect maze (one path per pair).
                     If False, add extra passages to create loops.
        """
        # Step 1: create a blank grid — every cell starts with all 4 walls
        maze = Maze(
            width=self._width,
            height=self._height,
            cells=[[ALL_WALLS for _ in range(self._width)]
                   for _ in range(self._height)],
        )

        # Step 2: stamp the "42" logo (cells that must stay fully closed)
        logo_positions = self._place_logo(maze)

        # Step 3: carve passages using DFS backtracker
        #         (logo cells are pre-visited, so the carver skips them)
        self._carve_passages(maze, logo_positions)

        # Step 4 (optional): add extra passages to break the "perfect" property
        if not perfect:
            self._add_extra_passages(maze, logo_positions)

        return maze

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _place_logo(self, maze: Maze) -> Set[Tuple[int, int]]:
        """
        Stamp the "42" logo into the maze as fully-closed cells.

        Returns the set of (x, y) positions occupied by the logo.
        If the maze is too small, prints a warning and returns an empty set.
        """
        if maze.width < LOGO_MIN_WIDTH or maze.height < LOGO_MIN_HEIGHT:
            print(
                f"Warning: maze is too small ({maze.width}x{maze.height}) "
                f"to display the 42 logo "
            )
            return set()

        # Center the logo in the maze (9 wide, 5 tall, 1-cell margin)
        origin_x = (maze.width - 9) // 2
        origin_y = (maze.height - 5) // 2

        logo_set: Set[Tuple[int, int]] = set()
        for (dx, dy) in LOGO_CELLS:
            p = Point(origin_x + dx, origin_y + dy)
            if maze.in_bounds(p):
                # all 4 walls closed = red block in renderer
                maze.set(p, ALL_WALLS)
                logo_set.add((p.x, p.y))

        return logo_set

    def _carve_passages(
            self, maze: Maze, logo_positions: Set[Tuple[int, int]]) -> None:
        """
        Carve a perfect maze using the iterative DFS backtracker.

        The algorithm:
        1. Start at the top-left non-logo cell.
        2. Push it onto a stack and mark it visited.
        3. While the stack is not empty:
           a. Look at the top cell.
           b. If it has unvisited neighbours, pick one at random,
              remove the wall between them, push the neighbour.
           c. If no unvisited neighbours, pop (backtrack).

        This creates a spanning tree: all non-logo cells are connected,
        and there is exactly one path between any two cells.
        """
        # All logo cells are "visited" from the start so we never carve into
        # them
        visited: Set[Tuple[int, int]] = set(logo_positions)

        # Find the first cell that is not a logo cell
        start = self._find_start(maze, visited)
        if start is None:
            return  # edge case: entire grid is logo (should never happen)

        visited.add((start.x, start.y))
        stack = [start]

        while stack:
            current = stack[-1]

            # Collect unvisited neighbours (skip out-of-bounds and logo cells)
            neighbours = []
            for (dx, dy, wall_here, wall_there) in DIRECTIONS:
                nx, ny = current.x + dx, current.y + dy
                neighbour = Point(nx, ny)
                if maze.in_bounds(neighbour) and (nx, ny) not in visited:
                    neighbours.append((neighbour, wall_here, wall_there))

            if neighbours:
                # Choose a random unvisited neighbour and carve through to it
                next_cell, wall_here, wall_there = random.choice(neighbours)

                # Remove the shared wall: clear the bit in both cells
                maze.set(current, maze.get(current) & ~wall_here)
                maze.set(next_cell, maze.get(next_cell) & ~wall_there)

                visited.add((next_cell.x, next_cell.y))
                stack.append(next_cell)
            else:
                # Dead end — backtrack
                stack.pop()

    def _add_extra_passages(
        self, maze: Maze, logo_positions: Set[Tuple[int, int]]
    ) -> None:
        """
        Add extra passages to create loops (for non-perfect mazes).

        We randomly pick internal walls between non-logo cells and remove them.
        The number of extra passages = about 15% of total cells.
        """
        extra_count = max(1, (maze.width * maze.height) // 7)

        for _ in range(extra_count * 10):  # try many times to hit the quota
            if extra_count <= 0:
                break

            # Pick a random cell
            x = random.randint(0, maze.width - 2)
            y = random.randint(0, maze.height - 2)

            # Skip logo cells
            if (x, y) in logo_positions:
                continue

            # Randomly pick East or South direction
            direction = random.choice([
                (1, 0, WALL_E, WALL_W),   # East
                (0, 1, WALL_S, WALL_N),   # South
            ])
            dx, dy, wall_here, wall_there = direction
            nx, ny = x + dx, y + dy

            # Skip if neighbour is a logo cell
            if (nx, ny) in logo_positions:
                continue

            # Remove the wall between (x,y) and (nx,ny) if it exists
            here = Point(x, y)
            there = Point(nx, ny)
            if maze.get(here) & wall_here:  # wall still present → remove it
                maze.set(here, maze.get(here) & ~wall_here)
                maze.set(there, maze.get(there) & ~wall_there)
                extra_count -= 1

    def _find_start(
        self, maze: Maze, occupied: Set[Tuple[int, int]]
    ) -> Optional[Point]:
        """Return first cell (top-left scan) not in occupied set."""
        for y in range(maze.height):
            for x in range(maze.width):
                if (x, y) not in occupied:
                    return Point(x, y)
        return None
