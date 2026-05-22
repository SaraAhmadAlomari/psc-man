from typing import Any
from mazegenerator.mazegenerator import MazeGenerator


class MazeAdapter:
    def __init__(
            self, width: int,
            height: int,
            seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.seed = seed

        self.gen = MazeGenerator(
            size=(self.width, self.height),
            seed=self.seed or 0
        )

    def create_level(self, is_perfect: bool = False) -> list[list[Any]] | None:
        try:
            if self.width < 10 or self.height < 10:
                print("Warning: maze too small, using minimum size 10x10")
                self.width = max(self.width, 10)
                self.height = max(self.height, 10)

            self.gen = MazeGenerator(
                size=(self.width, self.height),
                perfect=is_perfect,
                seed=self.seed or 0
            )

            return self.gen.maze

        except Exception as error:
            print(f"Error during maze generation: {error}")
            return None
