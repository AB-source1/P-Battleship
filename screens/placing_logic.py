import pygame
from game.draggable_ship import DraggableShip
from game.board_helpers import Cell, get_grid_pos
from core.config import Config
from helpers.draw_helpers import draw_top_bar

class PlacingLogic:
    def __init__(self, screen, state):
        self.screen = screen
        self.state = state
        self.active_ship = None
        self.preview_ship = None
        self.ship_queue = []
        self.placed_ships = []

        self.setup_ships()

    def reset(self):
        """Reset all ship placement state."""
        self.active_ship = None
        self.preview_ship = None
        self.ship_queue = []
        self.placed_ships = []
        self.setup_ships()

    def setup_ships(self):
        # Create ships and prepare queue
        self.ship_queue = [DraggableShip(size, *self.main_area_position()) for size in Config.SHIP_SIZES]
        self.update_active_and_preview()

    def update_active_and_preview(self):
        if self.ship_queue:
            self.active_ship = self.ship_queue.pop(0)
            self.active_ship.image.topleft = self.main_area_position()
        else:
            self.active_ship = None

        if self.ship_queue:
            self.preview_ship = self.ship_queue[0]
            self.preview_ship.image.topleft = self.preview_area_position()
        else:
            self.preview_ship = None

    def main_area_position(self):
        return (Config.WIDTH - 350, Config.HEIGHT // 2 - 40)

    def preview_area_position(self):
        return (Config.WIDTH - 250, Config.HEIGHT // 2 - 100)

    def try_place_on_grid(self, ship):
        row, col = get_grid_pos((ship.image.centerx, ship.image.centery),
                                Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
        if row is None or col is None:
            return False

        size = ship.size
        coords = []
        fits = True

        if ship.orientation == 'h':
            if col + size > Config.GRID_SIZE:
                fits = False
            else:
                for i in range(size):
                    if self.state.player_board[row][col + i] != Cell.EMPTY:
                        fits = False
                        break
                if fits:
                    for i in range(size):
                        self.state.player_board[row][col + i] = Cell.SHIP
                        coords.append((row, col + i))
        else:
            if row + size > Config.GRID_SIZE:
                fits = False
            else:
                for i in range(size):
                    if self.state.player_board[row + i][col] != Cell.EMPTY:
                        fits = False
                        break
                if fits:
                    for i in range(size):
                        self.state.player_board[row + i][col] = Cell.SHIP
                        coords.append((row + i, col))

        if fits:
            ship.place(coords)
            return True
        return False

    def snap_back(self):
        if self.active_ship:
            self.active_ship.image.topleft = self.main_area_position()

    def handle_event(self, event: pygame.event.Event, state):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.active_ship and self.active_ship.image.collidepoint(event.pos):
                self.active_ship.start_dragging(*event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.active_ship and self.active_ship.dragging:
                self.active_ship.update_position(*event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active_ship and self.active_ship.dragging:
                self.active_ship.stop_dragging()

                if self.try_place_on_grid(self.active_ship):
                    self.placed_ships.append(self.active_ship)
                    self.update_active_and_preview()
                    if not self.active_ship and not self.preview_ship:
                        # Done placing all ships
                        state.game_state = "playing"
                        state.player_ships = state.count_ships(state.player_board)
                else:
                    self.snap_back()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.active_ship:
                self.active_ship.rotate()

    def undo_last_ship(self):
        if self.placed_ships:
            last_ship = self.placed_ships.pop()

            # ✅ Clear last ship's cells from the board
            for (row, col) in last_ship.coords:
                self.state.player_board[row][col] = Cell.EMPTY

            # If there is an active ship, push it back to queue
            if self.active_ship:
                self.ship_queue.insert(0, self.active_ship)

            # Set last ship as the new active ship
            self.active_ship = last_ship
            self.active_ship.image.topleft = self.main_area_position()

            # Update preview
            if self.ship_queue:
                self.preview_ship = self.ship_queue[0]
                self.preview_ship.image.topleft = self.preview_area_position()
            else:
                self.preview_ship = None
