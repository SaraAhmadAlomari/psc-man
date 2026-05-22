import json
import sys
from typing import Any


def load_config(file_path: str) -> dict[str, Any]:
    """Load, validate, and sanitize game configuration."""

    defaults: dict[str, Any] = {
        "lives": 3,
        "level_max_time": 90,
        "points_per_pacgum": 10,
        "seed": 42,
        "highscore_filename": "highscores.json",
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "width": 15,
        "height": 15,
        "levels": []
    }

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Remove comments
        clean_content = "".join(
            line for line in lines if not line.strip().startswith("#")
        )

        user_config: dict[str, Any] = json.loads(clean_content)

    except FileNotFoundError:
        print(f"Error: Config file '{file_path}' not found.")
        sys.exit(1)

    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        sys.exit(1)

    # Merge config
    final_config: dict[str, Any] = {
        **defaults,
        **user_config,
    }

    # ----------------------------
    # Unknown keys handling
    # ----------------------------
    allowed_keys = set(defaults.keys())
    for key in user_config:
        if key not in allowed_keys:
            print(f"Warning: Unknown config key '{key}' ignored.")

    # ----------------------------
    # Type validation
    # ----------------------------
    int_fields = [
        "lives",
        "width",
        "height",
        "seed",
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
        "level_max_time",
    ]

    for key in int_fields:
        if not isinstance(final_config[key], int):
            print(f"Error: '{key}' must be an integer.")
            sys.exit(1)

    # ----------------------------
    # Clamping (safety limits)
    # ----------------------------

    # Lives: at least 1
    final_config["lives"] = max(3, final_config["lives"])

    # Maze size: playable range
    final_config["width"] = max(15, min(final_config["width"], 50))
    final_config["height"] = max(15, min(final_config["height"], 50))

    # Time: minimum 30 seconds
    final_config["level_max_time"] = max(30, final_config["level_max_time"])

    # Points: no negative scores
    final_config["points_per_pacgum"] = max(
        10, final_config["points_per_pacgum"]
    )
    final_config["points_per_super_pacgum"] = max(
        50, final_config["points_per_super_pacgum"]
    )
    final_config["points_per_ghost"] = max(0, final_config["points_per_ghost"])

    # Levels must be list
    if not isinstance(final_config["levels"], list):
        print("Error: 'levels' must be a list.")
        sys.exit(1)

    return final_config
