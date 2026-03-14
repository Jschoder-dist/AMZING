#!/usr/bin/env python3
"""
Shortest-path solver for A-Maze-ing.

Uses BFS (Breadth-First Search) to find the shortest path from ENTRY to EXIT.

HOW BFS WORKS
=============
BFS explores the maze level by level (like ripples on water):
- Start from ENTRY, put it in a queue.
- Each step: take the first cell in the queue, check its open neighbours,
  add unvisited ones to the queue and record how we got there.
- Stop as soon as we reach EXIT.
- Walk backwards through the "how we got there" map to rebuild the path.

BFS always finds the SHORTEST path because it explores cells in order
of their distance from the start.

The path is returned as a string of letters: N, E, S, W.
Example: "EESENNE" means go East, East, South, East, North, North, East.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Tuple

from maze_generator import Maze
from maze_types import WALL_E, WALL_N, WALL_S, WALL_W, Point

# Directions: (delta_x, delta_y, wall_bit_to_check, letter_for_path)
DIRECTIONS: List[Tuple[int, int, int, str]] = [
    (0, -1, WALL_N, "N"),
    (1, 0, WALL_E, "E"),
    (0, 1, WALL_S, "S"),
    (-1, 0, WALL_W, "W"),
]


class MazeSolveError(Exception):
    """Raised when no path exists between entry and exit."""


def solve_shortest_path(
    maze: Maze, entry: Point, exit_: Point
) -> Tuple[str, List[Tuple[int, int]]]:
    """
    Find the shortest path from entry to exit_ using BFS.

    Returns:
        (path_string, exploration_steps)
        - path_string: e.g. "EESENN" — directions to walk from entry to exit
        - exploration_steps: (x,y) cells visited by BFS (for animation)

    Raises:
        MazeSolveError: if no path exists.
    """
    start = (entry.x, entry.y)
    goal = (exit_.x, exit_.y)

    # FIFO queue — BFS explores cells in order of distance
    queue: deque[Tuple[int, int]] = deque([start])

    # Cells we already visited (no revisiting)
    visited: set[Tuple[int, int]] = {start}

    # For each cell: remember predecessor + direction used
    # This lets us rebuild the path once we reach the goal.
    came_from: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]] = {}

    # Record the order in which BFS visited cells (used for the animation
    # feature)
    exploration_steps: List[Tuple[int, int]] = []

    while queue:
        current = queue.popleft()
        exploration_steps.append(current)

        # Reached the exit — stop here
        if current == goal:
            break

        cx, cy = current
        current_walls = maze.get(Point(cx, cy))

        for (dx, dy, wall_bit, letter) in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            neighbour = (nx, ny)

            # Skip out-of-bounds or already-visited cells
            if not (0 <= nx < maze.width and 0 <= ny < maze.height):
                continue
            if neighbour in visited:
                continue

            # Only move to a neighbour if the wall between us is OPEN
            # (bit is 0 = no wall = passage exists)
            if (current_walls & wall_bit) == 0:
                visited.add(neighbour)
                came_from[neighbour] = (current, letter)
                queue.append(neighbour)

    # If the goal was never reached, the maze has no solution
    if goal not in came_from:
        raise MazeSolveError(
            f"No path found from ({
                entry.x},{
                entry.y}) to ({
                exit_.x},{
                exit_.y})."
        )

    # Rebuild the path by walking backwards from goal to start
    path = _rebuild_path(came_from, start, goal)
    return path, exploration_steps


def _rebuild_path(
    came_from: Dict[Tuple[int, int], Tuple[Tuple[int, int], str]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> str:
    """
    Walk backwards from goal to start using the came_from map,
    collecting direction letters, then reverse to get start→goal order.
    """
    letters: List[str] = []
    current = goal

    while current != start:
        previous_cell, letter = came_from[current]
        letters.append(letter)
        current = previous_cell

    letters.reverse()
    return "".join(letters)
