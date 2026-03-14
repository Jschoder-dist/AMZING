#!/usr/bin/env python3
"""
Configuration file parser for A-Maze-ing.

Reads a plain text file with one KEY=VALUE pair per line.
Lines starting with '#' are ignored (comments).

Mandatory keys:
    WIDTH        — number of columns  (integer > 0)
    HEIGHT       — number of rows     (integer > 0)
    ENTRY        — entry cell as x,y  (e.g. "0,0")
    EXIT         — exit cell as x,y   (e.g. "19,14")
    OUTPUT_FILE  — filename for the output maze  (e.g. "maze.txt")
    PERFECT      — True or False

Optional keys:
    SEED         — integer seed for reproducible random mazes
    ALGORITHM    — "backtracker" (default, only supported option for now)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from maze_generator import Point


@dataclass(frozen=True)
class MazeConfig:
    """All settings read from the configuration file."""

    width: int
    height: int
    entry: Point
    exit: Point
    output_file: str
    perfect: bool           # True = one unique path from entry to exit
    seed: Optional[int] = None  # Seed for reproducible random mazes


class ConfigError(Exception):
    """Raised when the config file is missing, unreadable, or invalid."""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_config_file(path: str) -> MazeConfig:
    """
    Read, parse and validate the config file at the given path.

    Returns:
        A fully validated MazeConfig.

    Raises:
        ConfigError: for any problem (file not found, bad value, etc.)
    """
    raw = _read_key_value_pairs(path)
    _check_mandatory_keys(raw)
    return _build_config(raw)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _read_key_value_pairs(path: str) -> Dict[str, str]:
    """
    Open the file and return a dict of KEY → value strings.
    Skips blank lines and lines starting with '#'.
    """
    pat = Path(path)

    if not pat.exists():
        raise ConfigError(f"Config file not found: {path}")
    if not pat.is_file():
        raise ConfigError(f"Not a regular file: {path}")

    result: Dict[str, str] = {}

    try:
        with pat.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                stripped = line.strip()

                # Skip blank lines and comments
                if not stripped or stripped.startswith("#"):
                    continue

                # Every other line must contain '='
                if "=" not in stripped:
                    raise ConfigError(
                        f"Line {line_number}: bad syntax: "
                        f"{stripped!r}"
                    )

                key, value = stripped.split("=", 1)
                key = key.strip().upper()
                value = value.strip()

                if not key:
                    raise ConfigError(f"Line {line_number}: empty key.")

                result[key] = value

    except OSError as e:
        raise ConfigError(f"Cannot read config file: {e}") from e

    return result


def _check_mandatory_keys(raw: Dict[str, str]) -> None:
    """Raise ConfigError if any mandatory key is missing."""
    mandatory = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
    for key in mandatory:
        if key not in raw:
            raise ConfigError(f"Missing mandatory key: {key}")


def _build_config(raw: Dict[str, str]) -> MazeConfig:
    """Parse all values and return a validated MazeConfig."""
    width = _parse_positive_int(raw["WIDTH"], "WIDTH")
    height = _parse_positive_int(raw["HEIGHT"], "HEIGHT")
    entry = _parse_point(raw["ENTRY"], "ENTRY")
    exit_ = _parse_point(raw["EXIT"], "EXIT")

    output_file = raw["OUTPUT_FILE"].strip()
    if not output_file:
        raise ConfigError("OUTPUT_FILE must not be empty.")

    perfect = _parse_bool(raw["PERFECT"], "PERFECT")

    seed: Optional[int] = None
    if "SEED" in raw:
        seed = _parse_int(raw["SEED"], "SEED")

    # Validate that entry and exit are inside the maze and are different
    _check_point_in_bounds(entry, width, height, "ENTRY")
    _check_point_in_bounds(exit_, width, height, "EXIT")

    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells.")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def _parse_int(text: str, key: str) -> int:
    """Parse text as an integer, or raise ConfigError."""
    try:
        return int(text.strip())
    except ValueError:
        raise ConfigError(f"{key}: expected an integer, got: {text!r}")


def _parse_positive_int(text: str, key: str) -> int:
    """Parse text as a positive integer (> 0), or raise ConfigError."""
    value = _parse_int(text, key)
    if value <= 0:
        raise ConfigError(f"{key}: must be greater than 0, got: {value}")
    if value > 100:
        raise ConfigError(f"{key}: must be lower than 101, got: {value}")
    return value


def _parse_bool(text: str, key: str) -> bool:
    """Parse 'True'/'False' (case-insensitive), or raise ConfigError."""
    lowered = text.strip().lower()
    if lowered in ("true", "yes", "1"):
        return True
    if lowered in ("false", "no", "0"):
        return False
    raise ConfigError(f"{key}: expected True or False, got: {text!r}")


def _parse_point(text: str, key: str) -> Point:
    """Parse 'x,y' into a Point, or raise ConfigError."""
    parts = text.strip().split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key}: expected 'x,y' format, got: {text!r}")
    x = _parse_int(parts[0], f"{key}.x")
    y = _parse_int(parts[1], f"{key}.y")
    return Point(x=x, y=y)


def _check_point_in_bounds(
        p: Point, width: int, height: int, key: str) -> None:
    """Raise ConfigError if point p is outside the maze bounds."""
    if not (0 <= p.x < width and 0 <= p.y < height):
        raise ConfigError(
            f"{key} ({p.x},{p.y}) is outside the maze "
            f"(valid range: 0..{width - 1}, 0..{height - 1})."
        )
