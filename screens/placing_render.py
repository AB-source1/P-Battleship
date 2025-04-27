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

        # Display ship counter
        draw_text_center(screen,
                         f"Ships Left: {len(self.logic.ship_queue) + (1 if self.logic.active_ship else 0)}",
                         Config.WIDTH - 300, 100, 28)

        # Draw active ship (draggable one)
        if self.logic.active_ship:
            self.logic.active_ship.draw(screen)

        # Draw preview ship (next one, static)
        if self.logic.preview_ship:
            pygame.draw.rect(screen, Config.GRAY,
                             pygame.Rect(self.logic.preview_area_position(), (Config.CELL_SIZE * self.logic.preview_ship.size, Config.CELL_SIZE)))
            pygame.draw.rect(screen, Config.WHITE,
                             pygame.Rect(self.logic.preview_area_position(), (Config.CELL_SIZE * self.logic.preview_ship.size, Config.CELL_SIZE)), 2)

        # Buttons
        draw_button(screen, "Rotate Ship (R)",
                    Config.WIDTH - 350, Config.HEIGHT // 2 + 100,
                    140, 40,
                    Config.GRAY, Config.DARK_GRAY,
                    lambda: self.logic.active_ship.rotate() if self.logic.active_ship else None)

        draw_button(screen, "Undo Last Ship",
                    Config.WIDTH - 350, Config.HEIGHT // 2 + 160,
                    140, 40,
                    Config.GRAY, Config.DARK_GRAY,
                    self.logic.undo_last_ship)
