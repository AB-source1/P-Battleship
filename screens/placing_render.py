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
        draw_top_bar(screen, state)

        draw_grid(
            screen,
            state.player_board,
            Config.BOARD_OFFSET_X,
            Config.BOARD_OFFSET_Y,
            show_ships=True
        )

        for ship in self.logic.placed_ships:
            ship.draw(screen)

        ships_left = len(self.logic.ship_queue) + (1 if self.logic.active_ship else 0)
        draw_text_center(
            screen,
            f"Ships Left: {ships_left}",
            Config.WIDTH - 300, 100, 28
        )

        if self.logic.active_ship and self.logic.active_ship.dragging:
            mx, my = self.logic.active_ship.image.center
            col = (mx - Config.BOARD_OFFSET_X) // Config.CELL_SIZE
            row = (my - Config.BOARD_OFFSET_Y) // Config.CELL_SIZE
            snapped_center = (
                Config.BOARD_OFFSET_X + col * Config.CELL_SIZE + Config.CELL_SIZE // 2,
                Config.BOARD_OFFSET_Y + row * Config.CELL_SIZE + Config.CELL_SIZE // 2 - 25  # lifted upward
            )

            orig_topleft = self.logic.active_ship.image.topleft
            self.logic.active_ship.image.center = snapped_center

            preview_cells = self.logic.active_ship.get_preview_cells(
                Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y
            )
            self.logic.active_ship.image.topleft = orig_topleft

            if preview_cells:
                valid = all(
                    0 <= r < Config.GRID_SIZE and 0 <= c < Config.GRID_SIZE and state.player_board[r][c] == Cell.EMPTY
                    for r, c in preview_cells
                )
                self.draw_preview(preview_cells, screen, valid)

        if self.logic.active_ship:
            self.logic.active_ship.draw(screen)

        if self.logic.preview_ship:
            w = Config.CELL_SIZE * self.logic.preview_ship.size
            h = Config.CELL_SIZE
            pos = self.logic.preview_area_position()
            pygame.draw.rect(
                screen,
                Config.WHITE,
                pygame.Rect(pos, (w, h)),
                2
    )

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

        if state.network and state.waiting_for_sync:
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text_center(
                screen,
                "Waiting for opponent to finish placing…",
                Config.WIDTH // 2,
                Config.HEIGHT // 2,
                28
            )
