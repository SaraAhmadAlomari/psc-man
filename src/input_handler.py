import pygame
from typing import Tuple

from .game_model import GameModel

POWER_TIMEOUT = pygame.USEREVENT + 1


class InputHandler:
    def __init__(self, model: GameModel) -> None:
        self.model = model

    def handle_gameplay_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == POWER_TIMEOUT:
                for ghost in self.model.ghosts:
                    ghost.frightened = False
            if event.type == pygame.KEYDOWN:
                self._process_movement(event)
                self._process_game_keys(event)
        return True

    def _process_movement(self, event: pygame.event.Event) -> None:
        key_map: dict[int, Tuple[int, int]] = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0),
        }
        if event.key in key_map:
            self.model.pacman.queued_direction = key_map[event.key]

    def _process_game_keys(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_p, pygame.K_ESCAPE):
            self.model.state = "paused"
            return

        if event.key == pygame.K_c:
            self.model.cheat_mode = not self.model.cheat_mode
            return

        if not self.model.cheat_mode:
            return

        if event.key == pygame.K_i:
            self.model.invincible = not self.model.invincible
        elif event.key == pygame.K_f:
            self.model.ghost_freeze = not self.model.ghost_freeze
        elif event.key == pygame.K_n:
            self.model.state = "skip_level"
        elif event.key == pygame.K_l:
            self.model.lives += 1
        elif event.key in (
            pygame.K_PLUS,
            pygame.K_KP_PLUS,
            pygame.K_EQUALS,
        ):
            valid_speeds = [
                s
                for s in [1, 2, 4, 8, 16]
                if s > self.model.pacman.speed
            ]
            if valid_speeds:
                self.model.pacman.speed = valid_speeds[0]

    def handle_menu_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.model.reset_for_new_game()
                elif event.key == pygame.K_i:
                    self.model.state = "instructions"
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    def handle_pause_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.model.state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    self.model.state = "menu"
        return True

    def handle_name_entry_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = self.model.player_name.strip() or "Anonymous"
                    self.model.highscore_manager.save_score(
                        self.model.score, name
                        )
                    self.model.state = "menu"
                elif event.key == pygame.K_ESCAPE:
                    self.model.state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    self.model.player_name = self.model.player_name[:-1]
                else:
                    character = event.unicode
                    if (
                        (character.isalnum() or character == " ")
                        and len(self.model.player_name) < 10
                    ):
                        self.model.player_name += character
        return True

    def handle_instructions_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.model.state = "menu"
        return True
