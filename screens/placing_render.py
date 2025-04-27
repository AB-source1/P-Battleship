import pygame
from helpers.draw_helpers import draw_top_bar, draw_grid, draw_text_center, draw_button
from core.config import Config

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

        draw_grid(screen, state.player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y, show_ships=True)

        if self.logic.draggable_ships:
            draw_text_center(screen,
                f"Place ship of length {self.logic.draggable_ships[0].size} ({'H' if self.logic.orientation == 'h' else 'V'})",
                Config.WIDTH // 2, 50)

        draw_button(screen, "Toggle H/V", Config.WIDTH - 160, 50 + Config.TOP_BAR_HEIGHT, 140, 40,
                    Config.GRAY, Config.DARK_GRAY, self.logic.toggle_orientation)

        draw_button(screen, "Undo Last Ship", Config.WIDTH - 160, 100 + Config.TOP_BAR_HEIGHT, 140, 40,
                    Config.GRAY, Config.DARK_GRAY, self.logic.undo_last_ship)

        for ship in self.logic.draggable_ships:
            if ship.dragging:
                cells = ship.get_preview_cells(Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
                if cells:
                    valid = all(state.player_board[r][c] == 0 for r, c in cells)
                    self.draw_preview(cells, screen, valid)
            ship.draw(screen)
