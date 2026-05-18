import pygame

from .game_model import GameModel


class GameRenderer:
    def __init__(self, model: GameModel, screen: pygame.Surface) -> None:
        self.model = model
        self.screen = screen

    def draw_gameplay(self) -> None:
        self.screen.fill((0, 0, 0))
        self.draw_maze()
        self.model.pacman.draw(self.screen)
        for ghost in self.model.ghosts:
            ghost.draw(self.screen)
        self.draw_hud()
        if self.model.cheat_mode:
            self.draw_cheat_overlay()
        pygame.display.flip()

    def draw_maze(self) -> None:
        for y, row in enumerate(self.model.grid):
            for x, cell in enumerate(row):
                x1 = x * self.model.tile_size
                y1 = y * self.model.tile_size
                if cell == 15:
                    pygame.draw.rect(
                        self.screen,
                        (33, 33, 255),
                        (x1, y1, self.model.tile_size, self.model.tile_size),
                    )
                else:
                    color = (200, 200, 200)
                    if cell & 1:
                        pygame.draw.line(
                            self.screen, color, (x1, y1),
                            (x1 + self.model.tile_size, y1), 2
                        )
                    if cell & 2:
                        pygame.draw.line(
                            self.screen, color,
                            (x1 + self.model.tile_size, y1),
                            (
                                x1 + self.model.tile_size,
                                y1 + self.model.tile_size), 2
                        )
                    if cell & 4:
                        pygame.draw.line(
                            self.screen, color,
                            (x1, y1 + self.model.tile_size),
                            (
                                x1 + self.model.tile_size,
                                y1 + self.model.tile_size,
                            ), 2
                        )
                    if cell & 8:
                        pygame.draw.line(
                            self.screen, color, (x1, y1),
                            (x1, y1 + self.model.tile_size), 2
                        )
                    if self.model.dots[y][x] != -1:
                        radius = (
                            6
                            if (y, x) in self.model.get_corner_positions()
                            else 2
                        )
                        pygame.draw.circle(
                            self.screen, (255, 184, 151),
                            (x1 + self.model.tile_size // 2,
                             y1 + self.model.tile_size // 2),
                            radius,
                        )
        pygame.draw.rect(
            self.screen, (33, 33, 255),
            (0, 0, self.model.grid_width * self.model.tile_size,
             self.model.grid_height * self.model.tile_size),
            3,
        )

    def draw_hud(self) -> None:
        font = pygame.font.SysFont("Arial", 18)
        hud_y = self.screen.get_height() - 38
        remaining_secs = max(
            0,
            (self.model.level_time_frames - self.model.frame_count) // 60,
        )
        time_color = (255, 50, 50) if remaining_secs <= 10 else (255, 255, 255)

        self.screen.blit(
            font.render(f"Score: {self.model.score}", True, (255, 255, 255)),
            (5, hud_y),
        )
        self.screen.blit(
            font.render(f"Lives: {self.model.lives}", True, (255, 255, 255)),
            (self.screen.get_width() // 4, hud_y),
        )
        self.screen.blit(
            font.render(
                f"Level: {self.model.current_level_idx + 1}", True,
                (255, 255, 255),
            ),
            (self.screen.get_width() // 2, hud_y),
        )
        self.screen.blit(
            font.render(f"Time: {remaining_secs}s", True, time_color),
            (3 * self.screen.get_width() // 4, hud_y),
        )

    def draw_cheat_overlay(self) -> None:
        font = pygame.font.SysFont("Arial", 13)
        lines = [
            "[C] CHEAT ON  |  [N] Skip  [L] +Life  [+] Speed",
            "[I] Invincible  [F] Freeze Ghosts",
        ]
        if self.model.invincible:
            lines.append(">>> INVINCIBLE <<<")
        if self.model.ghost_freeze:
            lines.append(">>> GHOSTS FROZEN <<<")

        bg = pygame.Surface((self.screen.get_width(), 4 + len(lines) * 15 + 2))
        bg.set_alpha(140)
        bg.fill((0, 0, 0))
        self.screen.blit(bg, (0, 0))
        for index, line in enumerate(lines):
            color = (
                (255, 50, 50)
                if "INVINCIBLE" in line or "FROZEN" in line
                else (255, 200, 0)
            )
            self.screen.blit(
                font.render(line, True, color),
                (4, 4 + index * 15),
            )

    def draw_main_menu(self) -> None:
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont("Arial", 52, bold=True)
        font_med = pygame.font.SysFont("Arial", 24)
        font_sm = pygame.font.SysFont("Arial", 18)

        title = font_big.render("PAC-MAN 42", True, (255, 255, 0))
        self.screen.blit(
            title,
            (self.screen.get_width() // 2 - title.get_width() // 2, 25),
        )

        sub = font_sm.render("Ghosts! More Ghosts!", True, (180, 180, 180))
        self.screen.blit(
            sub,
            (self.screen.get_width() // 2 - sub.get_width() // 2, 85),
        )

        options = [
            ("[SPACE] Start Game", (255, 255, 255)),
            ("[I]     Instructions", (255, 255, 255)),
            ("[ESC]   Exit", (200, 80, 80)),
        ]
        for index, (text, color) in enumerate(options):
            surf = font_med.render(text, True, color)
            self.screen.blit(
                surf,
                (
                    self.screen.get_width() // 2 - surf.get_width() // 2,
                    135 + index * 38,
                ),
            )

        scores = self.model.highscore_manager.load_scores()
        hs_title = font_med.render("── Highscores ──", True, (255, 255, 0))
        self.screen.blit(
            hs_title,
            (
                self.screen.get_width() // 2 - hs_title.get_width() // 2,
                260,
            ),
        )

        if scores:
            for index, entry in enumerate(scores[:10]):
                name = entry.get("name", "???")
                score = entry.get("score", 0)
                line = font_sm.render(
                    f"{index + 1:2}. {name:<10} {score} pts", True,
                    (210, 210, 210),
                )
                self.screen.blit(
                    line,
                    (
                        self.screen.get_width() // 2 - line.get_width() // 2,
                        290 + index * 22,
                    ),
                )
        else:
            no_scores = font_sm.render(
                "No scores yet — be the first!", True, (130, 130, 130)
            )
            self.screen.blit(
                no_scores,
                (
                    self.screen.get_width() // 2 - no_scores.get_width() // 2,
                    295,
                ),
            )

        pygame.display.flip()

    def draw_pause_menu(self) -> None:
        self.draw_maze()
        self.model.pacman.draw(self.screen)
        for ghost in self.model.ghosts:
            ghost.draw(self.screen)
        self.draw_hud()

        overlay = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
            )
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont("Arial", 42, bold=True)
        font_med = pygame.font.SysFont("Arial", 24)

        paused = font_big.render("PAUSED", True, (255, 255, 0))
        self.screen.blit(
            paused,
            (
                self.screen.get_width() // 2 - paused.get_width() // 2,
                self.screen.get_height() // 2 - 70,
            ),
        )

        labels = [
            ("[P] Resume", (255, 255, 255)),
            ("[ESC] Main Menu", (200, 80, 80)),
        ]
        for index, (label, color) in enumerate(labels):
            surf = font_med.render(label, True, color)
            self.screen.blit(
                surf,
                (
                    self.screen.get_width() // 2 - surf.get_width() // 2,
                    self.screen.get_height() // 2 + index * 40,
                ),
            )
        pygame.display.flip()

    def draw_name_entry(self) -> None:
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont("Arial", 52, bold=True)
        font_med = pygame.font.SysFont("Arial", 24)
        font_sm = pygame.font.SysFont("Arial", 18)

        if self.model.game_result == "win":
            title = font_big.render("YOU WIN!", True, (255, 255, 0))
            message = "Congratulations — all levels cleared!"
        else:
            title = font_big.render("GAME OVER", True, (255, 50, 50))
            message = "Better luck next time!"

        self.screen.blit(
            title,
            (
                self.screen.get_width() // 2 - title.get_width() // 2,
                50,
            ),
        )

        rendered_message = font_sm.render(message, True, (180, 180, 180))
        self.screen.blit(
            rendered_message,
            (
                self.screen.get_width() // 2
                - rendered_message.get_width() // 2,
                115,
            ),
        )

        rendered_score = font_med.render(
            f"Final Score: {self.model.score}", True, (255, 255, 255))
        self.screen.blit(
            rendered_score,
            (
                self.screen.get_width() // 2 - rendered_score.get_width() // 2,
                155,
            ),
        )

        prompt = font_med.render("Enter your name:", True, (255, 255, 0))
        self.screen.blit(
            prompt,
            (
                self.screen.get_width() // 2 - prompt.get_width() // 2,
                215,
            ),
        )

        name_text = font_med.render(
            self.model.player_name + "|", True, (255, 255, 255)
            )
        self.screen.blit(
            name_text,
            (
                self.screen.get_width() // 2 - name_text.get_width() // 2,
                250,
            ),
        )

        hint = font_sm.render(
            "[ENTER] Save & return to menu   [ESC] Skip",
            True,
            (120, 120, 120),
        )
        self.screen.blit(
            hint,
            (
                self.screen.get_width() // 2 - hint.get_width() // 2,
                305,
            ),
        )
        pygame.display.flip()

    def draw_instructions(self) -> None:
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont("Arial", 34, bold=True)
        font_med = pygame.font.SysFont("Arial", 20)

        title = font_big.render("INSTRUCTIONS", True, (255, 255, 0))
        self.screen.blit(
            title,
            (
                self.screen.get_width() // 2 - title.get_width() // 2,
                18,
            ),
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
            ("[ESC]   Back to Main Menu", False),
        ]
        for index, (text, bold) in enumerate(lines):
            color = (255, 220, 0) if bold else (220, 220, 220)
            self.screen.blit(
                font_med.render(text, True, color),
                (30, 70 + index * 26),
            )
        pygame.display.flip()
