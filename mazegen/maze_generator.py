"""
Maze Generator Module - mazegen
A reusable maze generator using recursive backtracking (DFS).

Usage example:
    from mazegen.maze_generator import MazeGenerator

    gen = MazeGenerator(width=20, height=15, seed=42)
    gen.generate(entry=(0, 0), exit=(19, 14), perfect=True)

    # Access maze grid (2D list of wall bitmasks)
    grid = gen.grid

    # Get shortest path as list of directions ('N','E','S','W')
    path = gen.solution

    # Get hex string per row
    for row in gen.to_hex_rows():
        print(row)
"""

import random
from collections import deque
from typing import List, Optional, Tuple


# Wall bitmask constants
NORTH: int = 1
EAST:  int = 2
SOUTH: int = 4
WEST:  int = 8

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

DIR_DELTA: dict[int, Tuple[int, int]] = {
    NORTH: (0, -1),
    EAST:  (1,  0),
    SOUTH: (0,  1),
    WEST:  (-1, 0),
}

DIR_LETTER: dict[int, str] = {
    NORTH: 'N',
    EAST:  'E',
    SOUTH: 'S',
    WEST:  'W',
}

DIGIT_4: List[List[int]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

DIGIT_2: List[List[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

PATTERN_42: List[List[int]] = [
    row4 + [0] + row2
    for row4, row2 in zip(DIGIT_4, DIGIT_2)
]


class MazeGenerator:
    """Generate a maze using recursive backtracking (DFS).

    Args:
        width:  Number of cells horizontally.
        height: Number of cells vertically.
        seed:   Optional random seed for reproducibility.

    Attributes:
        grid:     2D list[list[int]] of wall bitmasks per cell.
        solution: List of direction letters from entry to exit after generate.
        entry:    Entry cell (x, y).
        exit:     Exit cell (x, y).
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize the maze generator with dimensions and optional seed."""
        if width < 2 or height < 2:
            raise ValueError("Maze dimensions must be at least 2x2.")
        self.width: int = width
        self.height: int = height
        self.seed: Optional[int] = seed
        self.rng: random.Random = random.Random(seed)
        # Grid: each cell starts fully walled (all 4 walls closed = 0xF)
        self.grid: List[List[int]] = [
            [0xF] * width for _ in range(height)
        ]
        self.entry: Tuple[int, int] = (0, 0)
        self.exit: Tuple[int, int] = (width - 1, height - 1)
        self.solution: List[str] = []
        self._pattern_cells: set[Tuple[int, int]] = set()

    def generate(
        self,
        entry: Tuple[int, int] = (0, 0),
        exit_: Tuple[int, int] = None,  # type: ignore[assignment]
        perfect: bool = True,
    ) -> None:
        """Generate the maze.

        Args:
            entry:   (x, y) coordinates of the entrance cell.
            exit_:   (x, y) coordinates of the exit cell.
                     Defaults to (width-1, height-1).
            perfect: If True, generate a perfect maze (unique path).
        """
        if exit_ is None:
            exit_ = (self.width - 1, self.height - 1)

        self._validate_coords(entry, "entry")
        self._validate_coords(exit_, "exit")
        if entry == exit_:
            raise ValueError("Entry and exit must be different cells.")

        self.entry = entry
        self.exit = exit_

        self.grid = [[0xF] * self.width for _ in range(self.height)]
        self._pattern_cells = set()

        pattern_ok = self._carve_42_pattern()
        if not pattern_ok:
            print(
                "Warning: maze is too small to embed the '42' pattern. "
                "Skipping pattern."
            )

        visited: List[List[bool]] = [
            [False] * self.width for _ in range(self.height)
        ]
        self._dfs_carve(entry[0], entry[1], visited)

        self._open_border_wall(entry)
        self._open_border_wall(exit_)

        if not perfect:
            self._add_extra_passages()

        self._enforce_corridor_width()

        self.solution = self._bfs_solve()

    def to_hex_rows(self) -> List[str]:
        """Return the maze as a list of hex strings, one per row.

        Returns:
            List of strings where each char is a hex digit for a cell.
        """
        return [
            ''.join(format(cell, 'X') for cell in row)
            for row in self.grid
        ]

    def _validate_coords(self, coords: Tuple[int, int], name: str) -> None:
        """Validate that coordinates are inside maze bounds."""
        x, y = coords
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(
                f"{name} coordinates {coords} are out of maze bounds "
                f"({self.width}x{self.height})."
            )

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _remove_wall(self, x: int, y: int, direction: int) -> None:
        """Remove wall between (x,y) and its neighbor in direction."""
        dx, dy = DIR_DELTA[direction]
        nx, ny = x + dx, y + dy
        # Clear wall bit on this cell
        self.grid[y][x] &= ~direction
        # Clear opposite wall on neighbor
        self.grid[ny][nx] &= ~OPPOSITE[direction]

    def _dfs_carve(
        self, x: int, y: int, visited: List[List[bool]]
    ) -> None:
        """Recursive DFS carving; skips pattern cells."""
        visited[y][x] = True
        directions = [NORTH, EAST, SOUTH, WEST]
        self.rng.shuffle(directions)

        for direction in directions:
            dx, dy = DIR_DELTA[direction]
            nx, ny = x + dx, y + dy
            if not self._in_bounds(nx, ny):
                continue
            if visited[ny][nx]:
                continue
            if (nx, ny) in self._pattern_cells:
                continue
            self._remove_wall(x, y, direction)
            self._dfs_carve(nx, ny, visited)

    def _open_border_wall(self, coords: Tuple[int, int]) -> None:
        """Open one border wall of a cell to serve as entry/exit."""
        x, y = coords
        if y == 0:
            self.grid[y][x] &= ~NORTH
        elif y == self.height - 1:
            self.grid[y][x] &= ~SOUTH
        elif x == 0:
            self.grid[y][x] &= ~WEST
        elif x == self.width - 1:
            self.grid[y][x] &= ~EAST

    def _add_extra_passages(self) -> None:
        """Remove ~15% extra walls to create loops (imperfect maze)."""
        extra = max(1, int(self.width * self.height * 0.15))
        for _ in range(extra):
            x = self.rng.randint(0, self.width - 2)
            y = self.rng.randint(0, self.height - 2)
            direction = self.rng.choice([EAST, SOUTH])
            dx, dy = DIR_DELTA[direction]
            nx, ny = x + dx, y + dy
            if (x, y) not in self._pattern_cells and \
               (nx, ny) not in self._pattern_cells:
                self._remove_wall(x, y, direction)

    def _bfs_solve(self) -> List[str]:
        """BFS from entry to exit; return list of direction letters."""
        ex, ey = self.entry
        start = (ex, ey)
        gx, gy = self.exit
        goal = (gx, gy)

        queue: deque[Tuple[int, int]] = deque([start])
        came_from: dict[Tuple[int, int], Optional[Tuple[int, int, int]]] = {
            start: None
        }

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                break
            for direction in [NORTH, EAST, SOUTH, WEST]:
                # Check if wall is open (bit is 0)
                if self.grid[cy][cx] & direction:
                    continue  # wall is closed
                dx, dy = DIR_DELTA[direction]
                nx, ny = cx + dx, cy + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) not in came_from:
                    came_from[(nx, ny)] = (cx, cy, direction)
                    queue.append((nx, ny))

        path: List[str] = []
        cur: Tuple[int, int] = goal
        while came_from.get(cur) is not None:
            node = came_from[cur]
            assert node is not None
            px, py, direction = node
            path.append(DIR_LETTER[direction])
            cur = (px, py)
        path.reverse()
        return path

    def _carve_42_pattern(self) -> bool:
        """Reserve cells that form the '42' pattern (fully walled).

        Returns:
            True if pattern fits, False if maze is too small.
        """
        pat_w = 7
        pat_h = 5

        min_w = pat_w + 4
        min_h = pat_h + 4

        if self.width < min_w or self.height < min_h:
            return False

        # Place pattern roughly in the center
        ox = (self.width - pat_w) // 2
        oy = (self.height - pat_h) // 2

        for row_idx, row in enumerate(PATTERN_42):
            for col_idx, bit in enumerate(row):
                if bit:
                    cx = ox + col_idx
                    cy = oy + row_idx
                    self._pattern_cells.add((cx, cy))

        # Keep pattern cells fully walled (already 0xF by default)
        return True

    def _enforce_corridor_width(self) -> None:
        """Scan for 3x3 open areas and add walls to break them up."""
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                # Check if 3x3 block starting at (x,y) is fully open
                if self._is_open_block(x, y, 3, 3):
                    # Add a wall somewhere inside the block
                    self.grid[y + 1][x + 1] |= EAST
                    self.grid[y + 1][x + 2] |= WEST

    def _is_open_block(
        self, x: int, y: int, w: int, h: int
    ) -> bool:
        """Return True if all internal passages in a w×h block are open."""
        for cy in range(y, y + h):
            for cx in range(x, x + w):
                cell = self.grid[cy][cx]
                if cx < x + w - 1 and (cell & EAST):
                    return False
                if cy < y + h - 1 and (cell & SOUTH):
                    return False
        return True
