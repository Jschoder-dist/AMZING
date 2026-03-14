#!/usr/bin/env python3
"""
Output file writer for A-Maze-ing.

Writes the maze to a text file in the required format:
    - One row per line, each cell as a single uppercase hex digit (0-F)
    - An empty line
    - Entry coordinates: "x,y"
    - Exit coordinates:  "x,y"
    - Shortest path:     e.g. "EESENNW"

Example output (5x3 maze):
    9513F
    A6C2E
    C5457

    0,0
    4,2
    EESEE
"""

from __future__ import annotations

from pathlib import Path

from maze_generator import Maze
from maze_types import Point


class MazeOutputError(Exception):
    """Raised when the maze file cannot be written."""


def write_maze_output(
    output_file: str,
    maze: Maze,
    entry: Point,
    exit_: Point,
    path: str,
) -> None:
    """
    Write the maze grid, entry, exit, and shortest path to output_file.

    Args:
        output_file: path to the file to write.
        maze:        the generated maze.
        entry:       entry cell coordinates.
        exit_:       exit cell coordinates.
        path:        shortest path string (only N, E, S, W characters).

    Raises:
        MazeOutputError: if the file cannot be written.
    """
    lines: list[str] = []

    # 1. One row per line, each cell as a hex digit
    for y in range(maze.height):
        row = ""
        for x in range(maze.width):
            cell_value = maze.cells[y][x]
            # Each cell value is 0-15, displayed as a single uppercase hex char
            row += format(cell_value, "X")
        lines.append(row)

    # 2. Empty separator line
    lines.append("")

    # 3. Entry, exit, path
    lines.append(f"{entry.x},{entry.y}")
    lines.append(f"{exit_.x},{exit_.y}")
    lines.append(path)

    # Write everything at once
    content = "\n".join(lines) + "\n"
    _write_file(output_file, content)


def _write_file(filename: str, content: str) -> None:
    """Write text to a file, raising MazeOutputError on failure."""
    try:
        with Path(filename).open("w", encoding="utf-8") as f:
            f.write(content)
    except OSError as e:
        raise MazeOutputError(f"Cannot write to '{filename}': {e}") from e
