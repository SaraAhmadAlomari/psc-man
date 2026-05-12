import pygame
import random
from typing import List, Tuple, Optional

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8


class Entity:
    def __init__(self, x: int, y: int, tile_size: int, speed: int,
                 color: Tuple[int, int, int]) -> None:
        self.tile_size = tile_size
        self.speed = speed
        self.color = color
        self.pixel_x: float = float(x * tile_size + tile_size // 2)
        self.pixel_y: float = float(y * tile_size + tile_size // 2)
        self.direction: Tuple[int, int] = (0, 0)
        self.queued_direction: Tuple[int, int] = (0, 0)

    def get_grid_position(self) -> Tuple[int, int]:
        return (
                    int(self.pixel_y // self.tile_size),
                    int(self.pixel_x // self.tile_size)
        )

    def is_at_center(self) -> bool:
        offset = self.tile_size // 2
        # Use tolerance so higher speeds (which may skip over exact center)
        # still register
        return (
                abs(int(self.pixel_x) % self.tile_size - offset) < self.speed
                and
                abs(int(self.pixel_y) % self.tile_size - offset) < self.speed
                )

    def can_move(self,
                 grid: List[List[int]], direction: Tuple[int, int]) -> bool:
        row, col = self.get_grid_position()
        next_row, next_col = row + direction[1], col + direction[0]
        if not (0 <= next_row < len(grid) and 0 <= next_col < len(grid[0])):
            return False
        cell_value = grid[row][col]
        if direction == (0, -1):
            return not (cell_value & NORTH)
        if direction == (1, 0):
            return not (cell_value & EAST)
        if direction == (0, 1):
            return not (cell_value & SOUTH)
        if direction == (-1, 0):
            return not (cell_value & WEST)
        return False


class PacMan(Entity):
    def update(self, grid: List[List[int]]) -> None:
        if self.is_at_center():
            # Snap to exact tile center to prevent drift at high speeds
            offset = self.tile_size // 2
            self.pixel_x = ((int(self.pixel_x) // self.tile_size) *
                            self.tile_size + offset)
            self.pixel_y = ((int(self.pixel_y) // self.tile_size) *
                            self.tile_size + offset)

            if (self.queued_direction != (0, 0) and
                    self.can_move(grid, self.queued_direction)):
                self.direction = self.queued_direction
                self.queued_direction = (0, 0)
            if not self.can_move(grid, self.direction):
                self.direction = (0, 0)

        # Clamp movement: don't overshoot into a wall
        if self.direction != (0, 0):
            new_x = self.pixel_x + self.direction[0] * self.speed
            new_y = self.pixel_y + self.direction[1] * self.speed
            # Check if next tile center would be a wall; if so,
            # clamp to current center
            next_col = int(new_x) // self.tile_size
            next_row = int(new_y) // self.tile_size
            max_col = len(grid[0]) - 1
            max_row = len(grid) - 1
            if 0 <= next_row <= max_row and 0 <= next_col <= max_col:
                self.pixel_x = new_x
                self.pixel_y = new_y
            # If out of bounds, stop
            else:
                self.direction = (0, 0)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(
            screen, self.color,
            (int(self.pixel_x), int(self.pixel_y)),
            self.tile_size // 3
        )


class Ghost(Entity):
    def __init__(self, x: int, y: int, tile_size: int, speed: int,
                 color: Tuple[int, int, int]) -> None:
        super().__init__(x, y, tile_size, speed, color)
        self.frightened = False
        self.is_dead = False
        self.respawn_timer = 0

    def update(self, grid: List[List[int]],
               target_pos: Optional[Tuple[float, float]] = None) -> None:
        if self.is_dead:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.is_dead = False
            return

        if self.is_at_center():
            possible_dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            valid_dirs = [d for d in possible_dirs if self.can_move(grid, d)]
            if valid_dirs:
                if (target_pos and not self.frightened and
                        len(valid_dirs) > 1):
                    best_dir = valid_dirs[0]
                    min_dist = float('inf')
                    for d in valid_dirs:
                        nx = self.pixel_x + d[0] * self.tile_size
                        ny = self.pixel_y + d[1] * self.tile_size
                        dist = ((nx - target_pos[0]) ** 2 +
                                (ny - target_pos[1]) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist, best_dir = dist, d
                    self.direction = best_dir
                else:
                    rev = (-self.direction[0], -self.direction[1])
                    for_dirs = [d for d in valid_dirs if d != rev]
                    self.direction = random.choice(
                        for_dirs if for_dirs else valid_dirs
                    )

        self.pixel_x += self.direction[0] * self.speed
        self.pixel_y += self.direction[1] * self.speed

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_dead:
            return

        color = (0, 0, 255) if self.frightened else self.color
        x, y = int(self.pixel_x), int(self.pixel_y)
        size = self.tile_size // 3
        pygame.draw.circle(screen, color, (x, y), size)
        pygame.draw.rect(screen, color, (x - size, y, size * 2, size))
