# screens/placing_render.py

import pygame
from helpers.draw_helpers import (
    draw_top_bar, draw_grid, draw_text_center, draw_button
)
from core.config import Config
from game.board_helpers import Cell

_panel_raw = None

class PlacingRender:
    def __init__(self, logic):
        self.logic = logic
        # load+convert the panel now that display is up
        global _panel_raw
        if _panel_raw is None:
            _panel_raw = (
                pygame.image
                      .load("resources/images/grid_panel.png")
                      .convert_alpha()
            )
        grid_px   = Config.GRID_SIZE * Config.CELL_SIZE
        margin = int(1.9 * Config.CELL_SIZE)
        padded_px = grid_px + 2 * margin
        self.panel = pygame.transform.smoothscale(_panel_raw, (padded_px, padded_px))

    def draw_preview(self, cells, screen, valid):
        for row, col in cells:
            x = Config.BOARD_OFFSET_X + 34 + col * Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + 31 + row * Config.CELL_SIZE
            s = pygame.Surface((Config.CELL_SIZE, Config.CELL_SIZE), pygame.SRCALPHA)
            s.fill(Config.PREVIEW_GREEN if valid else Config.PREVIEW_RED)
            screen.blit(s, (x, y))

    def draw(self, screen, state):
        # Top bar with Restart/Quit buttons
        draw_top_bar(screen, state)

        def back():
            # ─── NEW: wipe out any ships/board state so it won't persist on re-entry
            self.logic.reset()
            if state.history:
                state.skip_push   = True
                state.game_state  = state.history.pop()
            else:
                state.game_state  = "menu"
        draw_button(screen, "Back (esc)", 10, 40, 130, 30,
                    Config.GRAY, Config.DARK_GRAY, back, 3)

        # ─── Grid Panel Frame ─────────────────────
        padded = Config.CELL_SIZE * 2
        size   = Config.GRID_WIDTH + padded
        panel = pygame.transform.smoothscale(
            _panel_raw,
            (size, size)
        )
        panel_pos = (
            Config.BOARD_OFFSET_X - 1 * Config.CELL_SIZE,
            Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT - 2.1 * Config.CELL_SIZE
        )
        screen.blit(self.panel, panel_pos)

        # Player Board Grid
        draw_grid(
            screen,
            state.player_board,
            Config.BOARD_OFFSET_X + 34,
            Config.BOARD_OFFSET_Y + 31,
            show_ships=False
        )

        # Draw all placed ship sprites
        for ship in self.logic.placed_ships:
            rows = [r for r, c in ship.coords]
            cols = [c for r, c in ship.coords]
            row0, col0 = min(rows), min(cols)
            x = Config.BOARD_OFFSET_X + 34 + col0 * Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + 31 + row0 * Config.CELL_SIZE
            screen.blit(ship.image, (x, y))

        # Ships Left Counter
        ships_left = len(self.logic.ship_queue) + (1 if self.logic.active_ship else 0)
        draw_text_center(
            screen,
            f"Ships Left: {ships_left}",
            Config.WIDTH - 300, 100, 28,
            Config.DARK_GRAY
        )

        # Live Placement Preview
        if self.logic.active_ship and self.logic.active_ship.dragging:
            mx, my = self.logic.active_ship.rect.center
            row = (my - (Config.BOARD_OFFSET_Y + 31)) // Config.CELL_SIZE
            col = (mx - (Config.BOARD_OFFSET_X + 34)) // Config.CELL_SIZE

            preview_cells = self.logic.active_ship.get_preview_cells(
                Config.BOARD_OFFSET_X + 34,
                Config.BOARD_OFFSET_Y + 31
            )
            if preview_cells:
                valid = all(
                    state.player_board[r][c] == Cell.EMPTY
                    for r, c in preview_cells
                )
                self.draw_preview(preview_cells, screen, valid)

        # Draw Active Ship (dragging)
        if self.logic.active_ship:
            self.logic.active_ship.draw(screen)

        # Draw Preview Ship (next in queue)
        if self.logic.preview_ship:
            pos = self.logic.preview_area_position()
            self.logic.preview_ship.rect.topleft = pos
            self.logic.preview_ship.draw(screen)

        # Rotate and Undo Buttons
        draw_button(
            screen, "Rotate Ship (R)",
            Config.WIDTH - 350,
            Config.HEIGHT // 2 + 100,
            140, 40,
            Config.GRAY, Config.DARK_GRAY,
            lambda: self.logic.active_ship.rotate() if self.logic.active_ship else None, 3
        )
        draw_button(
            screen, "Undo Last Ship",
            Config.WIDTH - 350,
            Config.HEIGHT // 2 + 160,
            140, 40,
            Config.GRAY, Config.DARK_GRAY,
            self.logic.undo_last_ship, 3
        )

        # READY BUTTON once all ships are placed
        if self.logic.ready_to_start and not state.waiting_for_sync:
            draw_button(
                screen, "READY",
                Config.WIDTH - 180,
                Config.HEIGHT - 80,
                160, 50,
                Config.GREEN, Config.DARK_GREEN,
                self.logic.on_ready_pressed, 4
            )

        # Multiplayer Waiting Overlay
        if state.network and state.waiting_for_sync:
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # semi-transparent black
            screen.blit(overlay, (0, 0))
            draw_text_center(
                screen,
                "Waiting for opponent to finish placing…",
                Config.WIDTH // 2,
                Config.HEIGHT // 2,
                28
            )
