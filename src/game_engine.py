import pygame
import sys
from typing import Any, Dict, List, Optional

from .game_logic import GameLogic
from .game_model import GameModel
from .game_renderer import GameRenderer
from .input_handler import InputHandler
from .level_manager import LevelManager
from .maze_adapter import MazeAdapter


class GameEngine:
    def __init__(
        self,
        config: Dict[str, Any],
        grid: List[List[int]],
        maze_adapter: Optional[MazeAdapter] = None,
    ) -> None:
        pygame.init()
        pygame.display.set_caption("Pac-Man 42 - Ghost Respawn Edition")

        self.config = config
        self.model = GameModel(config, grid)
        self.maze_adapter = maze_adapter
        self.level_manager = LevelManager(config, maze_adapter, self.model)

        self.clock = pygame.time.Clock()
        self.running = True

        self.screen = pygame.display.set_mode(
            (
                self.model.grid_width * self.model.tile_size,
                self.model.grid_height * self.model.tile_size + 50,
            )
        )
        self.renderer = GameRenderer(self.model, self.screen)
        self.input_handler = InputHandler(self.model)
        self.logic = GameLogic(self.model)

    def _resize_screen(self) -> None:
        self.screen = pygame.display.set_mode(
            (
                self.model.grid_width * self.model.tile_size,
                self.model.grid_height * self.model.tile_size + 50,
            )
        )
        self.renderer.screen = self.screen

    def _start_new_game(self) -> None:
        self.model.reset_for_new_game()
        self._resize_screen()

    def _load_next_level(self) -> bool:
        if not self.level_manager.load_next_level():
            return False
        self._resize_screen()
        return True

    def run(self) -> None:
        while self.running:
            if self.model.state == "menu":
                self.renderer.draw_main_menu()
                if not self.input_handler.handle_menu_events():
                    self.running = False
                elif self.model.state == "playing":
                    self._resize_screen()
            elif self.model.state == "playing":
                if not self.input_handler.handle_gameplay_events():
                    self.running = False
                    continue

                if self.model.state == "skip_level":
                    self.model.state = "playing"
                    if not self._load_next_level():
                        self.model.game_result = "win"
                        self.model.state = "name_entry"
                    continue

                self.logic.update()
                if self.model.state != "playing":
                    continue

                if self.logic.is_level_complete():
                    if not self._load_next_level():
                        self.model.game_result = "win"
                        self.model.state = "name_entry"
                    continue

                self.renderer.draw_gameplay()
            elif self.model.state == "paused":
                self.renderer.draw_pause_menu()
                if not self.input_handler.handle_pause_events():
                    self.running = False
            elif self.model.state == "name_entry":
                self.renderer.draw_name_entry()
                if not self.input_handler.handle_name_entry_events():
                    self.running = False
            elif self.model.state == "instructions":
                self.renderer.draw_instructions()
                if not self.input_handler.handle_instructions_events():
                    self.running = False

            self.clock.tick(60)

        pygame.quit()
        sys.exit()
