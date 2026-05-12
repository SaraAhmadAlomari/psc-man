import pygame
import sys
from typing import Any, Dict, List, Optional
from .entities import PacMan, Ghost
from .highscore_manager import HighscoreManager
from .maze_adapter import MazeAdapter

POWER_TIMEOUT = pygame.USEREVENT + 1


class GameEngine:
    def __init__(self, config: Dict[str, Any], grid: List[List[int]],
                 maze_adapter: Optional['MazeAdapter'] = None) -> None:
        pygame.init()
        self.config, self.grid = config, grid
        self.maze_adapter = maze_adapter
        self.initial_grid = [row[:] for row in grid]
        self.tile_size = 32
        self.grid_width, self.grid_height = len(grid[0]), len(grid)
        self.screen_width = self.grid_width * self.tile_size
        self.screen_height = (self.grid_height * self.tile_size) + 50
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("Pac-Man 42 - Ghost Respawn Edition")

        self.clock = pygame.time.Clock()
        self.running, self.score = True, 0
        self.lives = config.get("lives", 3)
        self.dots = [row[:] for row in grid]

        mid_x, mid_y = self.grid_width // 2, self.grid_height // 2
        self.pacman = PacMan(mid_x, mid_y, self.tile_size, 2, (255, 255, 0))
        self.ghosts = self._init_ghosts()

        # ---- ADDED: game state machine ----
        self.state = "menu"
        self.game_result = ""
        self.player_name = ""

        # ---- ADDED: level system ----
        self.levels_config: List[Dict[str, Any]] = config.get("levels", [])
        if not self.levels_config:
            self.levels_config = [{
                "width": config.get("width", 15),
                "height": config.get("height", 15),
                "level_max_time": config.get("level_max_time", 90)
            }]
        self.current_level_idx = 0
        self.level_time_frames = (
            self.levels_config[0].get("level_max_time", 90) * 60
        )
        self.frame_count = 0

        # ---- ADDED: cheat mode ----
        self.cheat_mode = False
        self.ghost_freeze = False
        self.invincible = False

        # ---- ADDED: highscore manager ----
        self.highscore_manager = HighscoreManager(
            config.get("highscore_filename", "highscores.json")
        )

        # ---- ADDED: use config scoring values ----
        self.pts_pacgum = config.get("points_per_pacgum", 10)
        self.pts_super = config.get("points_per_super_pacgum", 50)
        self.pts_ghost = config.get("points_per_ghost", 200)

    # ================================================================
    #  EXISTING METHODS — unchanged except noted
    # ================================================================

    def _init_ghosts(self) -> List[Ghost]:
        return [
            Ghost(1, 1, self.tile_size, 2, (255, 0, 0)),
            Ghost(self.grid_width - 2, 1, self.tile_size, 2, (0, 255, 255)),
            Ghost(1, self.grid_height - 2, self.tile_size, 2, (0, 255, 0)),
            Ghost(
                self.grid_width - 2, self.grid_height - 2,
                self.tile_size, 2, (255, 182, 193)
            )
        ]

    def reset_positions(self) -> None:
        mid_x, mid_y = self.grid_width // 2, self.grid_height // 2
        self.pacman.pixel_x = float(
            mid_x * self.tile_size + self.tile_size // 2
        )
        self.pacman.pixel_y = float(
            mid_y * self.tile_size + self.tile_size // 2
        )
        self.pacman.direction = (0, 0)
        self.ghosts = self._init_ghosts()

    def activate_power_mode(self) -> None:
        for ghost in self.ghosts:
            if not ghost.is_dead:
                ghost.frightened = True
        pygame.time.set_timer(POWER_TIMEOUT, 7000)

    def check_collisions(self) -> None:
        row, col = self.pacman.get_grid_position()
        if 0 <= row < self.grid_height and 0 <= col < self.grid_width:
            if self.grid[row][col] != 15 and self.dots[row][col] != -1:
                corners = [
                    (1, 1),
                    (1, self.grid_width - 2),
                    (self.grid_height - 2, 1),
                    (self.grid_height - 2, self.grid_width - 2)
                ]
                if (row, col) in corners:
                    self.score += self.pts_super
                    self.activate_power_mode()
                else:
                    self.score += self.pts_pacgum
                self.dots[row][col] = -1

        for ghost in self.ghosts:
            if ghost.is_dead:
                continue

            dist = ((self.pacman.pixel_x - ghost.pixel_x) ** 2 +
                    (self.pacman.pixel_y - ghost.pixel_y) ** 2) ** 0.5
            if dist < self.tile_size // 1.5:
                if ghost.frightened:
                    self.score += self.pts_ghost
                    ghost.frightened = False
                    ghost.is_dead = True
                    ghost.respawn_timer = 360

                    temp_ghosts = self._init_ghosts()
                    idx = self.ghosts.index(ghost)
                    ghost.pixel_x, ghost.pixel_y = (
                        temp_ghosts[idx].pixel_x,
                        temp_ghosts[idx].pixel_y
                    )
                else:
                    if not self.invincible:
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_result = "lose"
                            self.state = "name_entry"
                        else:
                            self.reset_positions()
                    break

    def draw_maze(self) -> None:
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                x1, y1 = x * self.tile_size, y * self.tile_size
                if cell == 15:
                    pygame.draw.rect(
                        self.screen, (33, 33, 255),
                        (x1, y1, self.tile_size, self.tile_size)
                    )
                else:
                    color = (200, 200, 200)
                    if cell & 1:  # NORTH
                        pygame.draw.line(
                            self.screen, color, (x1, y1),
                            (x1 + self.tile_size, y1), 2
                        )
                    if cell & 2:  # EAST
                        pygame.draw.line(
                            self.screen, color,
                            (x1 + self.tile_size, y1),
                            (x1 + self.tile_size, y1 + self.tile_size), 2
                        )
                    if cell & 4:  # SOUTH
                        pygame.draw.line(
                            self.screen, color,
                            (x1, y1 + self.tile_size),
                            (x1 + self.tile_size, y1 + self.tile_size), 2
                        )
                    if cell & 8:  # WEST
                        pygame.draw.line(
                            self.screen, color, (x1, y1),
                            (x1, y1 + self.tile_size), 2
                        )
                    if self.dots[y][x] != -1:
                        corners = [
                            (1, 1),
                            (1, self.grid_width - 2),
                            (self.grid_height - 2, 1),
                            (self.grid_height - 2, self.grid_width - 2)
                        ]
                        radius = 6 if (y, x) in corners else 2
                        pygame.draw.circle(
                            self.screen, (255, 184, 151),
                            (x1 + self.tile_size // 2,
                             y1 + self.tile_size // 2), radius
                        )
        pygame.draw.rect(
            self.screen, (33, 33, 255),
            (0, 0, self.grid_width * self.tile_size,
             self.grid_height * self.tile_size), 3
        )

    def handle_events(self) -> None:
        """Handle events during gameplay."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == POWER_TIMEOUT:
                for ghost in self.ghosts:
                    ghost.frightened = False
            if event.type == pygame.KEYDOWN:
                # Arrow keys (existing)
                if event.key == pygame.K_UP:
                    self.pacman.queued_direction = (0, -1)
                if event.key == pygame.K_DOWN:
                    self.pacman.queued_direction = (0, 1)
                if event.key == pygame.K_LEFT:
                    self.pacman.queued_direction = (-1, 0)
                if event.key == pygame.K_RIGHT:
                    self.pacman.queued_direction = (1, 0)
                # ADDED: WASD controls
                if event.key == pygame.K_w:
                    self.pacman.queued_direction = (0, -1)
                if event.key == pygame.K_s:
                    self.pacman.queued_direction = (0, 1)
                if event.key == pygame.K_a:
                    self.pacman.queued_direction = (-1, 0)
                if event.key == pygame.K_d:
                    self.pacman.queued_direction = (1, 0)
                # ADDED: Pause
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = "paused"
                # ADDED: Cheat mode toggle
                elif event.key == pygame.K_c:
                    self.cheat_mode = not self.cheat_mode
                # ADDED: Cheat mode actions
                elif self.cheat_mode:
                    if event.key == pygame.K_i:
                        self.invincible = not self.invincible
                    elif event.key == pygame.K_f:
                        self.ghost_freeze = not self.ghost_freeze
                    elif event.key == pygame.K_n:
                        self._skip_level()
                    elif event.key == pygame.K_l:
                        self.lives += 1
                    elif event.key in (
                        pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS
                    ):
                        # Only allow speeds that evenly divide tile_size (32)
                        # to prevent wall clipping
                        # Valid speeds that divide 32: 1, 2, 4, 8, 16
                        valid_speeds = [
                            s for s in [1, 2, 4, 8, 16]
                            if s > self.pacman.speed
                        ]
                        if valid_speeds:
                            self.pacman.speed = valid_speeds[0]

    def update(self) -> None:
        self.pacman.update(self.grid)
        p_pos = (self.pacman.pixel_x, self.pacman.pixel_y)
        for i, ghost in enumerate(self.ghosts):
            if not self.ghost_freeze:
                ghost.update(self.grid, p_pos if i < 2 else None)
        self.check_collisions()
        self._check_level_complete()
        # ADDED: countdown timer
        self.frame_count += 1
        if self.frame_count >= self.level_time_frames and self.state == "playing":  # noqa: E501
            self.game_result = "lose"
            self.state = "name_entry"

    def run(self) -> None:
        """Main game loop — state machine."""
        while self.running:
            if self.state == "menu":
                self._draw_main_menu()
                self._handle_menu_events()
            elif self.state == "playing":
                self.handle_events()
                if self.state != "playing":
                    continue
                self.update()
                if self.state != "playing":
                    continue
                self.draw_maze()
                self.pacman.draw(self.screen)
                for g in self.ghosts:
                    g.draw(self.screen)
                self._draw_hud()
                if self.cheat_mode:
                    self._draw_cheat_overlay()
                pygame.display.flip()
            elif self.state == "paused":
                self._draw_pause_menu()
                self._handle_pause_events()
            elif self.state == "name_entry":
                self._draw_name_entry()
                self._handle_name_entry_events()
            elif self.state == "instructions":
                self._draw_instructions()
                self._handle_instructions_events()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    # ================================================================
    #  ADDED METHODS
    # ================================================================

    def _start_new_game(self) -> None:
        """Reset all game state and start from level 0."""
        self.score = 0
        self.lives = self.config.get("lives", 3)
        self.current_level_idx = 0
        self.frame_count = 0
        self.grid = [row[:] for row in self.initial_grid]
        self.grid_width = len(self.grid[0])
        self.grid_height = len(self.grid)
        self.screen_width = self.grid_width * self.tile_size
        self.screen_height = self.grid_height * self.tile_size + 50
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        self.dots = [row[:] for row in self.initial_grid]
        self.level_time_frames = (
            self.levels_config[0].get("level_max_time", 90) * 60
        )
        mid_x, mid_y = self.grid_width // 2, self.grid_height // 2
        self.pacman = PacMan(mid_x, mid_y, self.tile_size, 2, (255, 255, 0))
        self.ghosts = self._init_ghosts()
        self.player_name = ""
        self.cheat_mode = False
        self.ghost_freeze = False
        self.invincible = False
        self.state = "playing"

    def _load_next_level(self) -> bool:
        """Generate and load the next level. Returns False when all levels done."""  # noqa: E501
        self.current_level_idx += 1
        if self.current_level_idx >= len(self.levels_config):
            return False

        level_cfg = self.levels_config[self.current_level_idx]
        width: int = level_cfg.get("width", self.config.get("width", 15))
        height: int = level_cfg.get("height", self.config.get("height", 15))

        try:
            new_adapter = MazeAdapter(width, height, seed=None)
            new_grid = new_adapter.create_level(is_perfect=False)
            if new_grid is None:
                error_msg = f"Error: maze generation failed for level {self.current_level_idx + 1}"  # noqa: E501
                print(error_msg)
                return False
            self.grid = new_grid
            self.grid_width = len(new_grid[0])
            self.grid_height = len(new_grid)
            self.screen_width = self.grid_width * self.tile_size
            self.screen_height = self.grid_height * self.tile_size + 50
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
            self.dots = [row[:] for row in new_grid]
        except Exception as e:
            print(f"Error loading level {self.current_level_idx + 1}: {e}")
            return False

        self.level_time_frames = level_cfg.get("level_max_time", 90) * 60
        self.frame_count = 0
        mid_x, mid_y = self.grid_width // 2, self.grid_height // 2
        self.pacman = PacMan(mid_x, mid_y, self.tile_size, 2, (255, 255, 0))
        self.ghosts = self._init_ghosts()
        return True

    def _check_level_complete(self) -> None:
        """Win the current level when all pacgums are eaten."""
        if self.state != "playing":
            return
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] != 15 and self.dots[y][x] != -1:
                    return
        # All dots eaten — advance
        if not self._load_next_level():
            self.game_result = "win"
            self.state = "name_entry"

    def _skip_level(self) -> None:
        """Cheat: skip the current level immediately."""
        if not self._load_next_level():
            self.game_result = "win"
            self.state = "name_entry"

    # ---- HUD ----

    def _draw_hud(self) -> None:
        """Draw in-game HUD: score, lives, level, remaining time."""
        font = pygame.font.SysFont("Arial", 18)
        hud_y = self.screen_height - 38
        remaining_secs = max(
            0, (self.level_time_frames - self.frame_count) // 60
        )
        time_color = (255, 50, 50) if remaining_secs <= 10 else (255, 255, 255)

        self.screen.blit(
            font.render(f"Score: {self.score}", True, (255, 255, 255)),
            (5, hud_y)
        )
        self.screen.blit(
            font.render(f"Lives: {self.lives}", True, (255, 255, 255)),
            (self.screen_width // 4, hud_y)
        )
        self.screen.blit(
            font.render(f"Level: {self.current_level_idx + 1}",
                        True, (255, 255, 255)),
            (self.screen_width // 2, hud_y)
        )
        self.screen.blit(
            font.render(f"Time: {remaining_secs}s", True, time_color),
            (3 * self.screen_width // 4, hud_y)
        )

    # ---- Cheat overlay ----

    def _draw_cheat_overlay(self) -> None:
        """Show active cheat indicators in top-left corner."""
        font = pygame.font.SysFont("Arial", 13)
        lines = [
            "[C] CHEAT ON  |  [N] Skip  [L] +Life  [+] Speed",
            "[I] Invincible  [F] Freeze Ghosts",
        ]
        if self.invincible:
            lines.append(">>> INVINCIBLE <<<")
        if self.ghost_freeze:
            lines.append(">>> GHOSTS FROZEN <<<")
        bg = pygame.Surface((self.screen_width, 4 + len(lines) * 15 + 2))
        bg.set_alpha(140)
        bg.fill((0, 0, 0))
        self.screen.blit(bg, (0, 0))
        for i, line in enumerate(lines):
            color = (
                (255, 50, 50) if ("INVINCIBLE" in line or "FROZEN" in line)
                else (255, 200, 0)
            )
            txt = font.render(line, True, color)
            self.screen.blit(txt, (4, 4 + i * 15))

    # ---- Main Menu ----

    def _draw_main_menu(self) -> None:
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont("Arial", 52, bold=True)
        font_med = pygame.font.SysFont("Arial", 24)
        font_sm = pygame.font.SysFont("Arial", 18)

        title = font_big.render("PAC-MAN 42", True, (255, 255, 0))
        self.screen.blit(
            title,
            (self.screen_width // 2 - title.get_width() // 2, 25)
        )

        sub = font_sm.render("Ghosts! More Ghosts!", True, (180, 180, 180))
        self.screen.blit(
            sub,
            (self.screen_width // 2 - sub.get_width() // 2, 85)
        )

        opts = [
            ("[SPACE] Start Game", (255, 255, 255)),
            ("[I]     Instructions", (255, 255, 255)),
            ("[ESC]   Exit", (200, 80, 80))
        ]
        for idx, (text, color) in enumerate(opts):
            surf = font_med.render(text, True, color)
            self.screen.blit(
                surf,
                (self.screen_width // 2 - surf.get_width() // 2,
                 135 + idx * 38)
            )

        scores = self.highscore_manager.load_scores()
        hs_title = font_med.render("── Highscores ──", True, (255, 255, 0))
        self.screen.blit(
            hs_title,
            (self.screen_width // 2 - hs_title.get_width() // 2, 260)
        )
        if scores:
            for i, entry in enumerate(scores[:10]):
                name = entry.get("name", "???")
                sc = entry.get("score", 0)
                line = font_sm.render(
                    f"{i + 1:2}. {name:<10} {sc} pts", True, (210, 210, 210)
                )
                self.screen.blit(
                    line,
                    (self.screen_width // 2 - line.get_width() // 2,
                     290 + i * 22)
                )
        else:
            ns = font_sm.render(
                "No scores yet — be the first!", True, (130, 130, 130)
            )
            self.screen.blit(
                ns,
                (self.screen_width // 2 - ns.get_width() // 2, 295)
            )

        pygame.display.flip()

    def _handle_menu_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._start_new_game()
                elif event.key == pygame.K_i:
                    self.state = "instructions"
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    # ---- Pause Menu ----

    def _draw_pause_menu(self) -> None:
        # Redraw game behind the overlay
        self.draw_maze()
        self.pacman.draw(self.screen)
        for g in self.ghosts:
            g.draw(self.screen)
        self._draw_hud()

        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("Arial", 42, bold=True)
        font_med = pygame.font.SysFont("Arial", 24)

        pt = font_big.render("PAUSED", True, (255, 255, 0))
        self.screen.blit(
            pt,
            (self.screen_width // 2 - pt.get_width() // 2,
             self.screen_height // 2 - 70)
        )

        for i, (label, color) in enumerate([
            ("[P] Resume", (255, 255, 255)),
            ("[ESC] Main Menu", (200, 80, 80))
        ]):
            t = font_med.render(label, True, color)
            self.screen.blit(
                t,
                (self.screen_width // 2 - t.get_width() // 2,
                 self.screen_height // 2 + i * 40)
            )
        pygame.display.flip()

    def _handle_pause_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    # ---- Name Entry (Game Over / Victory) ----

    def _draw_name_entry(self) -> None:
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont("Arial", 52, bold=True)
        font_med = pygame.font.SysFont("Arial", 24)
        font_sm = pygame.font.SysFont("Arial", 18)

        if self.game_result == "win":
            title_surf = font_big.render("YOU WIN!", True, (255, 255, 0))
            msg = "Congratulations — all levels cleared!"
        else:
            title_surf = font_big.render("GAME OVER", True, (255, 50, 50))
            msg = "Better luck next time!"

        self.screen.blit(
            title_surf,
            (self.screen_width // 2 - title_surf.get_width() // 2, 50)
        )

        msg_surf = font_sm.render(msg, True, (180, 180, 180))
        self.screen.blit(
            msg_surf,
            (self.screen_width // 2 - msg_surf.get_width() // 2, 115)
        )

        sc_surf = font_med.render(
            f"Final Score: {self.score}", True, (255, 255, 255)
        )
        self.screen.blit(
            sc_surf,
            (self.screen_width // 2 - sc_surf.get_width() // 2, 155)
        )

        prompt = font_med.render("Enter your name:", True, (255, 255, 0))
        self.screen.blit(
            prompt,
            (self.screen_width // 2 - prompt.get_width() // 2, 215)
        )

        name_surf = font_med.render(self.player_name + "|", True,
                                    (255, 255, 255))
        self.screen.blit(
            name_surf,
            (self.screen_width // 2 - name_surf.get_width() // 2, 250)
        )

        hint = font_sm.render(
            "[ENTER] Save & return to menu   [ESC] Skip",
            True, (120, 120, 120)
        )
        self.screen.blit(
            hint,
            (self.screen_width // 2 - hint.get_width() // 2, 305)
        )

        pygame.display.flip()

    def _handle_name_entry_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    name = self.player_name.strip() or "Anonymous"
                    self.highscore_manager.save_score(self.score, name)
                    self.state = "menu"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                else:
                    ch = event.unicode
                    if (ch.isalnum() or ch == " ") and len(self.player_name) < 10:  # noqa: E501
                        self.player_name += ch

    # ---- Instructions ----

    def _draw_instructions(self) -> None:
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont("Arial", 34, bold=True)
        font_med = pygame.font.SysFont("Arial", 20)

        title = font_big.render("INSTRUCTIONS", True, (255, 255, 0))
        self.screen.blit(
            title,
            (self.screen_width // 2 - title.get_width() // 2, 18)
        )

        lines = [
            ("Controls", True),
            ("  Move: Arrow Keys or WASD", False),
            ("  Pause: P or ESC", False),
            ("", False),
            ("Objective", True),
            ("  Eat all dots to complete each level.", False),
            ("  Avoid ghosts — each hit costs a life.", False),
            ("  Corner dots are Super-Pacgums: make ghosts edible!", False),
            ("  Eat a frightened ghost for bonus points.", False),
            ("", False),
            ("Cheat Mode  (C to toggle)", True),
            ("  I: Invincibility    F: Freeze ghosts", False),
            ("  N: Skip level       L: Add a life", False),
            ("  +: Speed boost", False),
            ("", False),
            ("[ESC]  Back to Main Menu", False),
        ]
        for i, (text, bold) in enumerate(lines):
            color = (255, 220, 0) if bold else (220, 220, 220)
            surf = font_med.render(text, True, color)
            self.screen.blit(surf, (30, 70 + i * 26))

        pygame.display.flip()

    def _handle_instructions_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "menu"
