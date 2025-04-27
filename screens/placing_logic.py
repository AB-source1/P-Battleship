import pygame
from game.draggable_ship import DraggableShip
from core.config import Config
from core.game_state import GameState
from game.board_helpers import Cell, get_grid_pos

class PlacingLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state
        self.orientation = 'h'
        self.draggable_ships = [DraggableShip(size, 100 + Config.GRID_WIDTH, 100 + i * 60)
                                for i, size in enumerate(Config.SHIP_SIZES)]
        self.placed_ships = []

    def toggle_orientation(self):
        self.orientation = 'v' if self.orientation == 'h' else 'h'

    def reset_ships(self):
        self.placed_ships = []
        self.draggable_ships = [DraggableShip(size, 100 + Config.GRID_WIDTH, 100 + i * 60)
                                for i, size in enumerate(Config.SHIP_SIZES)]

    def undo_last_ship(self):
        if self.placed_ships:
            ship = self.placed_ships.pop()
            for row, col in ship.coords:
                self.state.player_board[row][col] = Cell.EMPTY
            ship.place([])
            self.draggable_ships.append(ship)

    def place_ship(self, row, col, ship, state: GameState):
        if row is None or col is None or not self.draggable_ships:
            return

        size = ship.size
        coords = []
        fits = True

        if self.orientation == 'h':
            if col + size > Config.GRID_SIZE:
                fits = False
            else:
                for i in range(size):
                    if state.player_board[row][col + i] != Cell.EMPTY:
                        fits = False
                        break
                if fits:
                    for i in range(size):
                        state.player_board[row][col + i] = Cell.SHIP
                        coords.append((row, col + i))
        else:
            if row + size > Config.GRID_SIZE:
                fits = False
            else:
                for i in range(size):
                    if state.player_board[row + i][col] != Cell.EMPTY:
                        fits = False
                        break
                if fits:
                    for i in range(size):
                        state.player_board[row + i][col] = Cell.SHIP
                        coords.append((row + i, col))

        if fits:
            ship.place(coords)
            self.placed_ships.append(ship)
            self.draggable_ships.remove(ship)
            if not self.draggable_ships:
                state.game_state = "playing"
                state.player_ships = state.count_ships(state.player_board)

    def try_start_dragging(self, event: pygame.event.Event):
        for ship in self.draggable_ships:
            if ship.image.collidepoint(event.pos) and not ship.dragging:
                ship.dragging = True
                return True
        return False

    def handle_event(self, event: pygame.event.Event, state):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Start dragging the ship
            for ship in self.draggable_ships:
                if ship.image.collidepoint(event.pos) and not ship.dragging:
                    ship.start_dragging(*event.pos)
                    return

            # Place ship manually on click if not dragging
            row, col = get_grid_pos(event.pos, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row is not None and col is not None:
                self.place_ship(row, col, self.draggable_ships[0], state)

        elif event.type == pygame.MOUSEMOTION:
            for ship in self.draggable_ships:
                if ship.dragging:
                    ship.update_position(*event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for ship in self.draggable_ships:
                if ship.dragging:
                    ship.stop_dragging()
                    preview_cells = ship.get_preview_cells(Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
                    if preview_cells:
                        valid = all(state.player_board[r][c] == Cell.EMPTY for r, c in preview_cells)
                        if valid:
                            row, col = preview_cells[0]
                            self.place_ship(row, col, ship, state)
                            break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if self.draggable_ships:
                    self.draggable_ships[0].rotate()
