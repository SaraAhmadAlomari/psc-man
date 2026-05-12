import json
import sys
from typing import Any


def load_config(file_path: str) -> dict[str, Any]:
    """Load and validate configuration file."""

    defaults: dict[str, Any] = {
        "lives": 3,
        "level_max_time": 90,
        "points_per_pacgum": 10,
        "seed": 42,
        "highscore_filename": "highscores.json",
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "level_max_time": 90,
        "width": 15,
        "height": 15,
        "levels": []
    }

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        clean_content = "".join(
            line
            for line in lines
            if not line.strip().startswith("#")
        )

        user_config: dict[str, Any] = json.loads(clean_content)

        final_config: dict[str, Any] = {
            **defaults,
            **user_config,
        }

        return final_config

    except FileNotFoundError:
        print(
            f"Error: Config file '{file_path}' not found. "
            "Using defaults."
        )
        return defaults

    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        sys.exit(1)

    except Exception as error:
        print(f"Unexpected error: {error}")
        sys.exit(1)
