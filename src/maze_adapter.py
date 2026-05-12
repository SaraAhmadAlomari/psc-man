from typing import Any
from mazegen.maze_generator import MazeGenerator


class MazeAdapter:
    """Adapter for the maze generator package."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.seed = seed

        self.gen = MazeGenerator(
            width=self.width,
            height=self.height,
            seed=self.seed,
        )

    def create_level(
        self,
        is_perfect: bool = False,
    ) -> list[list[Any]] | None:
        """Generate and return maze grid."""

        try:
            self.gen.generate(perfect=is_perfect)
            return self.gen.grid

        except Exception as error:
            print(f"Error during maze generation: {error}")
            return None
