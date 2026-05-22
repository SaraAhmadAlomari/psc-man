import sys
import os
from src.config_parser import load_config
from src.maze_adapter import MazeAdapter
from src.game_engine import GameEngine


def get_config_path() -> str:
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        return os.path.join(base_path, "config.json")
    return "config.json"


def main() -> None:
    """Run the Pac-Man maze generator."""

    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    else:
        config_path = get_config_path()

    config = load_config(config_path)

    # Use first-level config (or top-level fallback) for the initial maze
    levels = config.get("levels", [])
    first_level = levels[0] if levels else {}
    width: int = first_level.get("width", config.get("width", 15))
    height: int = first_level.get("height", config.get("height", 15))
    seed: int = config.get("seed", 42)

    try:
        adapter = MazeAdapter(width, height, seed)
        grid = adapter.create_level(is_perfect=False)

        if grid is None:
            print("Error: The maze generator failed to return a valid grid.")
            return

        # ADDED: pass adapter so GameEngine can generate subsequent levels
        game = GameEngine(config, grid, maze_adapter=adapter)
        game.run()

    except Exception as e:
        print(f"A critical error occurred during gameplay: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
