# screens/placing_render.py

import pygame
from helpers.draw_helpers import (
    draw_top_bar, draw_grid, draw_text_center, draw_button
)
from core.config import Config
from game.board_helpers import Cell

class PlacingRender:
    def __init__(self, logic):
        self.logic = logic

    def draw_preview(self, cells, screen, valid):
        for row, col in cells:
            x = Config.BOARD_OFFSET_X + col * Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + row * Config.CELL_SIZE
            s = pygame.Surface((Config.CELL_SIZE, Config.CELL_SIZE), pygame.SRCALPHA)
            s.fill(Config.PREVIEW_GREEN if valid else Config.PREVIEW_RED)
            screen.blit(s, (x, y))

    # ─── Section backgrounds ───────────────────────────────
        
    def draw(self, screen, state):
        # Top bar with Restart/Quit buttons
        draw_top_bar(screen, state)

        draw_button(
            screen, "Back (esc)",
            10, 5, 130, 30,
            Config.GRAY, Config.DARK_GRAY,
            lambda: setattr(state, "game_state", "menu")
        )

        # 1) Grid area background
        grid_bg = pygame.Surface((Config.GRID_WIDTH, Config.GRID_WIDTH), pygame.SRCALPHA)
        grid_bg.fill((0, 0, 0, 120))  # 120/255 alpha for a dark overlay
        screen.blit(grid_bg, (Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y))  # uses Config.GRID_WIDTH & BOARD_OFFSET_Y :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}


        # Player’s board with ships
        draw_grid(
            screen,
            state.player_board,
            Config.BOARD_OFFSET_X,
            Config.BOARD_OFFSET_Y,
            show_ships=True
        )

        # “Ships Left” counter
        ships_left = len(self.logic.ship_queue) + (1 if self.logic.active_ship else 0)
        draw_text_center(
            screen,
            f"Ships Left: {ships_left}",
            Config.WIDTH - 300, 100, 28
        )

        # Live placement preview when dragging
        if self.logic.active_ship and self.logic.active_ship.dragging:
            # Snap a temporary center to compute preview cells
            mx, my = self.logic.active_ship.image.center
            col = (mx - Config.BOARD_OFFSET_X) // Config.CELL_SIZE
            row = (my - Config.BOARD_OFFSET_Y) // Config.CELL_SIZE
            snapped_center = (
                Config.BOARD_OFFSET_X + col * Config.CELL_SIZE + Config.CELL_SIZE // 2,
                Config.BOARD_OFFSET_Y + row * Config.CELL_SIZE + Config.CELL_SIZE // 2
            )
            # Save/restore the ship’s real position
            orig_topleft = self.logic.active_ship.image.topleft
            self.logic.active_ship.image.center = snapped_center

            preview_cells = self.logic.active_ship.get_preview_cells(
                Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y
            )
            self.logic.active_ship.image.topleft = orig_topleft

            if preview_cells:
                valid = all(
                    state.player_board[r][c] == Cell.EMPTY
                    for r, c in preview_cells
                )
                self.draw_preview(preview_cells, screen, valid)

        # Draw the draggable “active” ship
        if self.logic.active_ship:
            self.logic.active_ship.draw(screen)

        # Draw the static “next ship” preview
        if self.logic.preview_ship:
            w = Config.CELL_SIZE * self.logic.preview_ship.size
            h = Config.CELL_SIZE
            pos = self.logic.preview_area_position()
            pygame.draw.rect(
                screen,
                Config.GRAY,
                pygame.Rect(pos, (w, h))
            )
            pygame.draw.rect(
                screen,
                Config.WHITE,
                pygame.Rect(pos, (w, h)),
                2
            )

        # Rotate and Undo buttons
        draw_button(
            screen, "Rotate Ship (R)",
            Config.WIDTH - 350,
            Config.HEIGHT // 2 + 100,
            140, 40,
            Config.GRAY, Config.DARK_GRAY,
            lambda: self.logic.active_ship.rotate()
                    if self.logic.active_ship else None
        )
        draw_button(
            screen, "Undo Last Ship",
            Config.WIDTH - 350,
            Config.HEIGHT // 2 + 160,
            140, 40,
            Config.GRAY, Config.DARK_GRAY,
            self.logic.undo_last_ship
        )

        # ─── Multiplayer “Waiting” Overlay ───────────────────────────
        if state.network and state.waiting_for_sync:
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # 70% opaque black
            screen.blit(overlay, (0, 0))
            draw_text_center(
                screen,
                "Waiting for opponent to finish placing…",
                Config.WIDTH // 2,
                Config.HEIGHT // 2,
                28
            )
