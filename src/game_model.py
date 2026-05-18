import pygame
from typing import Any

from .entities import Ghost, PacMan
from .highscore_manager import HighscoreManager


POWER_TIMEOUT = pygame.USEREVENT + 1


class GameModel:
    def __init__(self, config: dict[str, Any], grid: list[list[int]]) -> None:
        self.config = config
        self.initial_grid = [row[:] for row in grid]
        self._setup_grid(grid)

        self.tile_size: int = 32
        self.score: int = 0
        self.lives: int = config.get("lives", 3)

        self.pacman = self._create_pacman()
        self.ghosts = self._init_ghosts()

        self.state: str = "menu"
        self.game_result: str = ""
        self.player_name: str = ""

        self.levels_config: list[dict[str, Any]] = (
            config.get("levels", [])
            or [{
                "width": config.get("width", 15),
                "height": config.get("height", 15),
                "level_max_time": config.get("level_max_time", 90),
            }]
        )

        self.current_level_idx: int = 0

        self.level_time_frames: int = (
            self.current_level_config().get("level_max_time", 90) * 60
        )

        self.frame_count: int = 0

        self.cheat_mode: bool = False
        self.ghost_freeze: bool = False
        self.invincible: bool = False

        self.pts_pacgum: int = config.get("points_per_pacgum", 10)
        self.pts_super: int = config.get("points_per_super_pacgum", 50)
        self.pts_ghost: int = config.get("points_per_ghost", 200)

        self.highscore_manager = HighscoreManager(
            config.get("highscore_filename", "highscores.json")
        )

    def _setup_grid(self, grid: list[list[int]]) -> None:
        self.grid = [row[:] for row in grid]
        self.grid_height: int = len(self.grid)
        self.grid_width: int = len(self.grid[0]) if self.grid else 0
        self.dots = [row[:] for row in self.grid]

    def _create_pacman(self) -> PacMan:
        mid_x = self.grid_width // 2
        mid_y = self.grid_height // 2
        return PacMan(mid_x, mid_y, self.tile_size, 2, (255, 255, 0))

    def _init_ghosts(self) -> list[Ghost]:
        return [
            Ghost(1, 1, self.tile_size, 2, (255, 0, 0)),
            Ghost(self.grid_width - 2, 1, self.tile_size, 2, (0, 255, 255)),
            Ghost(1, self.grid_height - 2, self.tile_size, 2, (0, 255, 0)),
            Ghost(
                self.grid_width - 2,
                self.grid_height - 2,
                self.tile_size,
                2,
                (255, 182, 193),
            ),
        ]

    def current_level_config(self) -> dict[str, Any]:
        return self.levels_config[self.current_level_idx]

    def get_corner_positions(self) -> list[tuple[int, int]]:
        return [
            (1, 1),
            (1, self.grid_width - 2),
            (self.grid_height - 2, 1),
            (self.grid_height - 2, self.grid_width - 2),
        ]

    def reset_positions(self) -> None:
        mid_x = self.grid_width // 2
        mid_y = self.grid_height // 2

        self.pacman.pixel_x = float(
            mid_x * self.tile_size + self.tile_size // 2
        )
        self.pacman.pixel_y = float(
            mid_y * self.tile_size + self.tile_size // 2
        )

        self.pacman.direction = (0, 0)
        self.pacman.queued_direction = (0, 0)

        self.ghosts = self._init_ghosts()

    def activate_power_mode(self) -> None:
        for ghost in self.ghosts:
            if not ghost.is_dead:
                ghost.frightened = True

        pygame.time.set_timer(POWER_TIMEOUT, 7000)

    def reset_for_new_game(self) -> None:
        self.score = 0
        self.lives = self.config.get("lives", 3)
        self.current_level_idx = 0
        self.frame_count = 0

        self._setup_grid(self.initial_grid)

        self.level_time_frames = (
            self.current_level_config().get("level_max_time", 90) * 60
        )

        self.pacman = self._create_pacman()
        self.ghosts = self._init_ghosts()

        self.player_name = ""
        self.cheat_mode = False
        self.ghost_freeze = False
        self.invincible = False

        self.state = "playing"

    def update_grid(self, grid: list[list[int]]) -> None:
        self._setup_grid(grid)

        self.level_time_frames = (
            self.current_level_config().get("level_max_time", 90) * 60
        )

        self.frame_count = 0
        self.pacman = self._create_pacman()
        self.ghosts = self._init_ghosts()
