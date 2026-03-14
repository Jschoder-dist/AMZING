#!/usr/bin/env python3
"""
A-Maze-ing — main program.

Usage:
    python3 a_maze_ing.py config.txt

Interactive commands:
    r — Re-generate a new maze
    p — Toggle the solution path on/off
    c — Cycle wall color themes
    a — Open the BFS animation
    s — Show statistics
    q — Quit
"""

import subprocess
import sys

from config_parser import ConfigError, MazeConfig, parse_config_file
from maze_generator import Maze, MazeGenerator
from maze_renderer import RenderState, render_maze
from maze_solver import solve_shortest_path
from maze_writer import write_maze_output


def clear_screen() -> None:
    """Clear the terminal using ANSI escape codes."""
    print("\033[2J\033[H", end="")


def generate_maze(
    cfg: MazeConfig, seed: int | None
) -> tuple[Maze, str, list]:
    """Generate maze, solve it, write output. Return (maze, path, steps)."""
    gen = MazeGenerator(cfg.width, cfg.height, seed)
    maze = gen.generate(perfect=cfg.perfect)
    path, steps = solve_shortest_path(maze, cfg.entry, cfg.exit)
    write_maze_output(cfg.output_file, maze, cfg.entry, cfg.exit, path)
    return maze, path, steps


def show_stats(
    maze: Maze, cfg: MazeConfig, path: str, steps: list
) -> None:
    """Print statistics about the current maze and BFS solution."""
    total_cells = maze.width * maze.height
    path_length = len(path)
    explored = len(steps)
    efficiency = (path_length / explored * 100) if explored > 0 else 0

    clear_screen()
    print("\033[1;36m--- MAZE STATISTICS ---\033[0m")
    print(f"Size      : {maze.width}x{maze.height} ({total_cells} cells)")
    mode = "Perfect (one path)" if cfg.perfect else "Imperfect (loops)"
    print(f"Mode      : {mode}")
    en, ex = cfg.entry, cfg.exit
    print(f"Entry→Exit: ({en.x},{en.y}) → ({ex.x},{ex.y})")
    print("-" * 23)
    print(f"Shortest  : {path_length} steps (blue)")
    print(f"Explored  : {explored} cells (yellow in animation)")
    print(f"Efficiency: {efficiency:.1f}%")
    print("-" * 23)
    print("\033[3mLow % = many dead ends explored.\033[0m")
    input("\nPress ENTER to go back...")


def main(argv: list[str]) -> int:
    """Entry point: parse args, generate maze, run interactive loop."""
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 2

    try:
        cfg = parse_config_file(argv[1])
    except ConfigError as e:
        print(f"Config error: {e}")
        return 1

    state = RenderState()
    regen_count = 0

    def current_seed() -> int | None:
        """Seed for the current generation (increments on each regen)."""
        if cfg.seed is None:
            return None
        return cfg.seed + regen_count

    try:
        maze, path, steps = generate_maze(cfg, current_seed())
    except Exception as e:
        print(f"Error: {e}")
        return 1

    while True:
        clear_screen()
        print(render_maze(maze, cfg.entry, cfg.exit, path, state))

        seed_val = current_seed()
        seed_info = "random" if seed_val is None else str(seed_val)
        path_info = "ON" if state.show_path else "OFF"
        print(f"Seed: {seed_info} | Path: {path_info} | {cfg.output_file}")
        print("Commands: [r]egen [p]ath [c]olor [a]nim [s]tats [q]uit")

        cmd = input("→ ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "p":
            state.show_path = not state.show_path
        elif cmd == "c":
            state.next_color()
        elif cmd == "r":
            regen_count += 1
            try:
                maze, path, steps = generate_maze(cfg, current_seed())
            except Exception as e:
                print(f"Error: {e}")
                return 1
        elif cmd == "a":
            clear_screen()
            print("Starting BFS animation... (press Ctrl+C to stop)")
            subprocess.run([sys.executable, "debug_animator.py", argv[1]])
            input("\nAnimation done. Press ENTER to return...")
        elif cmd == "s":
            show_stats(maze, cfg, path, steps)
        else:
            print("Unknown command. Use r, p, c, a, s, or q.")
            input("Press ENTER to continue...")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
