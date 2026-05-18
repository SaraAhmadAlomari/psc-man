from typing import Any

from .game_model import GameModel
from .maze_adapter import MazeAdapter


class LevelManager:
    def __init__(
        self,
        config: dict[str, Any],
        maze_adapter: MazeAdapter | None,
        model: GameModel,
    ) -> None:
        self.config = config
        self.maze_adapter = maze_adapter
        self.model = model

    def load_next_level(self) -> bool:
        next_index = self.model.current_level_idx + 1
        if next_index >= len(self.model.levels_config):
            return False

        self.model.current_level_idx = next_index
        level_config = self.model.current_level_config()
        width = level_config.get("width", self.config.get("width", 15))
        height = level_config.get("height", self.config.get("height", 15))

        try:
            adapter = MazeAdapter(width, height, seed=None)
            new_grid = adapter.create_level(is_perfect=False)
            if new_grid is None:
                print(
                    f"Error: maze generation failed for level "
                    f"{self.model.current_level_idx + 1}"
                )
                return False

            self.model.update_grid(new_grid)
            return True

        except Exception as error:
            print(
                f"Error loading level "
                f"{self.model.current_level_idx + 1}: "
                f"{error}"
            )
            return False
