#!/usr/bin/env python3
"""
BFS Animation Laboratory for A-Maze-ing.

Shows BFS exploration in yellow, then the final shortest path in blue.
Run standalone:  python3 debug_animator.py [config.txt]
"""

from __future__ import annotations

import sys
import time
from collections import deque
from typing import Set, Tuple

from config_parser import parse_config_file
from maze_generator import (
    ALL_WALLS, Maze, MazeGenerator, WALL_E, WALL_N, WALL_S, WALL_W, Point,
)
from maze_renderer import _COLOR_LOGO, _COLOR_PATH, _RESET

# Animation colors
_COLOR_WALL = "\033[48;5;235m"    # dark grey
_COLOR_SCAN = "\033[48;5;220m"    # yellow  (BFS frontier)
_COLOR_ENTRY = "\033[48;5;40m"    # green
_COLOR_EXIT = "\033[48;5;202m"    # orange

# Speed (seconds per frame)
EXPLORE_DELAY = 0.02
PATH_DELAY = 0.04


def clear() -> None:
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="", flush=True)


def render_frame(
    maze: Maze,
    entry: Point,
    exit_: Point,
    highlighted: Set[Tuple[int, int]],
    color: str,
) -> str:
    """Build a rendered frame with the highlighted cells colored."""
    rows = []
    for y in range(maze.height):
        row_pixels = []
        for x in range(maze.width):
            bits = maze.get(Point(x, y))

            # Determine cell pixel
            if bits == ALL_WALLS:
                cell = _COLOR_LOGO + "  " + _RESET
            elif x == entry.x and y == entry.y:
                cell = _COLOR_ENTRY + "E " + _RESET
            elif x == exit_.x and y == exit_.y:
                cell = _COLOR_EXIT + "X " + _RESET
            elif (x, y) in highlighted:
                cell = color + "  " + _RESET
            else:
                cell = "  "

            # Insert wall pixel to the left (East passage of previous cell)
            if x == 0:
                # Left border — always a wall
                row_pixels.append(_COLOR_WALL + "  " + _RESET)
            else:
                prev_bits = maze.get(Point(x - 1, y))
                if prev_bits & WALL_E:
                    row_pixels.append(_COLOR_WALL + "  " + _RESET)
                else:
                    # Passage: color it if both sides are highlighted
                    if (x - 1, y) in highlighted and (x, y) in highlighted:
                        row_pixels.append(color + "  " + _RESET)
                    else:
                        row_pixels.append("  ")

            row_pixels.append(cell)

        # Right border
        row_pixels.append(_COLOR_WALL + "  " + _RESET)
        rows.append("".join(row_pixels))

    # Add horizontal wall rows (North border, then alternating wall/cell rows)
    full_rows = []
    # Top border
    full_rows.append(_COLOR_WALL + "  " * (maze.width * 2 + 1) + _RESET)

    for y, row in enumerate(rows):
        full_rows.append(row)
        # Horizontal wall row between cell rows
        wall_row = []
        for x in range(maze.width):
            wall_row.append(_COLOR_WALL + "  " + _RESET)
            bits = maze.get(Point(x, y))
            if bits & WALL_S or y + 1 >= maze.height:
                wall_row.append(_COLOR_WALL + "  " + _RESET)
            else:
                if (x, y) in highlighted and (x, y + 1) in highlighted:
                    wall_row.append(color + "  " + _RESET)
                else:
                    wall_row.append("  ")
        wall_row.append(_COLOR_WALL + "  " + _RESET)
        full_rows.append("".join(wall_row))

    return "\n".join(full_rows)


def animate(maze: Maze, entry: Point, exit_: Point) -> None:
    """Run the full BFS animation: explore phase, then path phase."""
    start = (entry.x, entry.y)
    goal = (exit_.x, exit_.y)

    queue: deque[Tuple[int, int]] = deque([start])
    visited: Set[Tuple[int, int]] = {start}
    came_from: dict[Tuple[int, int], Tuple[int, int]] = {}

    # --- Phase 1: BFS exploration (yellow) ---
    while queue:
        cx, cy = queue.popleft()

        clear()
        print("BFS ANIMATION — Phase 1: Exploration (yellow)")
        print(render_frame(maze, entry, exit_, visited, _COLOR_SCAN))
        print(f"Explored: {len(visited)} cells")
        time.sleep(EXPLORE_DELAY)

        if (cx, cy) == goal:
            break

        bits = maze.get(Point(cx, cy))
        for dx, dy, wall in [(0, -1, WALL_N), (1, 0, WALL_E),
                             (0, 1, WALL_S), (-1, 0, WALL_W)]:
            nx, ny = cx + dx, cy + dy
            if (
                0 <= nx < maze.width
                and 0 <= ny < maze.height
                and (nx, ny) not in visited
                and not (bits & wall)
            ):
                visited.add((nx, ny))
                came_from[(nx, ny)] = (cx, cy)
                queue.append((nx, ny))

    # --- Phase 2: shortest path reconstruction (blue) ---
    if goal not in came_from:
        print("No path found!")
        return

    path_cells: Set[Tuple[int, int]] = set()
    current = goal
    while current != start:
        path_cells.add(current)
        current = came_from[current]
        clear()
        print("BFS ANIMATION — Phase 2: Shortest path (blue)")
        print(render_frame(maze, entry, exit_, path_cells, _COLOR_PATH))
        print(f"Path length: {len(path_cells)} cells")
        time.sleep(PATH_DELAY)

    path_cells.add(start)
    clear()
    print("BFS ANIMATION — Done!")
    print(render_frame(maze, entry, exit_, path_cells, _COLOR_PATH))
    print(f"Shortest path: {len(path_cells)} cells")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.txt"
    try:
        cfg = parse_config_file(config_path)
        gen = MazeGenerator(cfg.width, cfg.height, cfg.seed)
        maze = gen.generate(perfect=cfg.perfect)
        animate(maze, cfg.entry, cfg.exit)
    except Exception as e:
        print(f"Error: {e}")
