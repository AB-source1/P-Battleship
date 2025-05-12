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

    def draw(self, screen, state):
        # Top bar with Restart/Quit buttons
        draw_top_bar(screen, state)

        def back():
            if state.history:
                state.skip_push = True
                state.game_state = state.history.pop()
            else:
                state.game_state = "menu"
        draw_button(screen, "Back (esc)", 10, 40, 130, 30,
                    Config.GRAY, Config.DARK_GRAY, back)

       # Player’s board (don’t auto‐draw ships as blue squares)
        draw_grid(
            screen,
            state.player_board,
            Config.BOARD_OFFSET_X,
            Config.BOARD_OFFSET_Y,
            show_ships=False
        )

        # Overlay each placed ship’s real sprite at its grid location
        for ship in self.logic.placed_ships:
            # find the top-left cell of this ship
            rows = [r for r, c in ship.coords]
            cols = [c for r, c in ship.coords]
            row0, col0 = min(rows), min(cols)

            # compute pixel position on the grid
            x = Config.BOARD_OFFSET_X + col0 * Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + row0 * Config.CELL_SIZE

            # blit the sprite (already rotated/oriented)  
            screen.blit(ship.image, (x, y))

        # “Ships Left” counter
        ships_left = len(self.logic.ship_queue) + (1 if self.logic.active_ship else 0)
        draw_text_center(
            screen,
            f"Ships Left: {ships_left}",
            Config.WIDTH - 300, 100, 28
        )

        # Live placement preview when dragging
        if self.logic.active_ship and self.logic.active_ship.dragging:
            # Compute which grid cells the ship would occupy
            mx, my = self.logic.active_ship.rect.center
            row = (my - Config.BOARD_OFFSET_Y) // Config.CELL_SIZE
            col = (mx - Config.BOARD_OFFSET_X) // Config.CELL_SIZE

            preview_cells = self.logic.active_ship.get_preview_cells(
                Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y
            )
            if preview_cells:
                # Highlight the cells instead of showing the sprite
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
            # Position and draw the next‐ship sprite instead of a grey box
            pos = self.logic.preview_area_position()
            self.logic.preview_ship.rect.topleft = pos
            self.logic.preview_ship.draw(screen)

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
