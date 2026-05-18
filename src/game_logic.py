from .game_model import GameModel


class GameLogic:
    def __init__(self, model: GameModel) -> None:
        self.model = model

    def update(self) -> None:
        self.model.pacman.update(self.model.grid)
        position = (self.model.pacman.pixel_x, self.model.pacman.pixel_y)

        for index, ghost in enumerate(self.model.ghosts):
            if self.model.ghost_freeze:
                continue
            target = position if index < 2 else None
            ghost.update(self.model.grid, target)

        self.check_collisions()
        self.model.frame_count += 1

        if (
            self.model.frame_count >= self.model.level_time_frames
            and self.model.state == "playing"
        ):
            self.model.game_result = "lose"
            self.model.state = "name_entry"

    def check_collisions(self) -> None:
        row, col = self.model.pacman.get_grid_position()
        if (
            0 <= row < self.model.grid_height
            and 0 <= col < self.model.grid_width
            and self.model.grid[row][col] != 15
            and self.model.dots[row][col] != -1
        ):
            if (row, col) in self.model.get_corner_positions():
                self.model.score += self.model.pts_super
                self.model.activate_power_mode()
            else:
                self.model.score += self.model.pts_pacgum
            self.model.dots[row][col] = -1

        for ghost in self.model.ghosts:
            if ghost.is_dead:
                continue

            dist = ((self.model.pacman.pixel_x - ghost.pixel_x) ** 2 +
                    (self.model.pacman.pixel_y - ghost.pixel_y) ** 2) ** 0.5
            if dist < self.model.tile_size / 1.5:
                if ghost.frightened:
                    self.model.score += self.model.pts_ghost
                    ghost.frightened = False
                    ghost.is_dead = True
                    ghost.respawn_timer = 360
                    replacement = self.model._init_ghosts()[
                        self.model.ghosts.index(ghost)
                    ]
                    ghost.pixel_x = replacement.pixel_x
                    ghost.pixel_y = replacement.pixel_y
                else:
                    if not self.model.invincible:
                        self.model.lives -= 1
                        if self.model.lives <= 0:
                            self.model.game_result = "lose"
                            self.model.state = "name_entry"
                        else:
                            self.model.reset_positions()
                    break

    def is_level_complete(self) -> bool:
        if self.model.state != "playing":
            return False

        for y in range(self.model.grid_height):
            for x in range(self.model.grid_width):
                if self.model.grid[y][x] != 15 and self.model.dots[y][x] != -1:
                    return False
        return True
