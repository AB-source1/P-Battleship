# screens/placing_logic.py

import pygame
import time
from game.draggable_ship      import DraggableShip
from game.board_helpers      import Cell, get_grid_pos, place_ship_randomly
from core.config             import Config
from core.game_state         import GameState

class PlacingLogic:
    """
    Handles both manual drag-and-drop placement and automatic “smart” placement.
    In manual mode, the player drags ships onto the grid. In smart mode, all
    ships are randomly placed at once and the game immediately advances.
    """

    def __init__(self, screen, state: GameState):
        self.screen       = screen
        self.state        = state
        self.active_ship  = None
        self.preview_ship = None
        self.ship_queue   = []
        self.placed_ships = []
        self.setup_ships()

    def setup_ships(self):
        """Initial population of ship_queue from Config.SHIP_SIZES."""
        self.ship_queue = [
            DraggableShip(size, *self.main_area_position())
            for size in Config.SHIP_SIZES
        ]
        self.update_active_and_preview()

    def update_active_and_preview(self):
        """Rotate the next ship into active_ship, peek the next as preview_ship."""
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
        """Where the active ship sits when not dragged."""
        return (Config.WIDTH - 350, Config.HEIGHT // 2 - 40)

    def preview_area_position(self):
        """Where the preview ship sits in the sidebar."""
        return (Config.WIDTH - 250, Config.HEIGHT // 2 - 100)

    def reset(self):
        """
        Called on new game or restart. Clears the board and UI state,
        then either auto-places ships (smart mode) or resets for manual placement.
        """
        # 1) Clear the board data
        self.state.player_board = [
            [Cell.EMPTY for _ in range(Config.GRID_SIZE)]
            for _ in range(Config.GRID_SIZE)
        ]

        # 2) Clear drag/drop UI state
        self.active_ship  = None
        self.preview_ship = None
        self.ship_queue   = []
        self.placed_ships = []

        # 3) Re-setup ship_queue
        self.setup_ships()

        # 4) Smart mode: auto-place and advance immediately
        if Config.USE_SMART_SHIP_GENERATOR:
            for size in Config.SHIP_SIZES:
                place_ship_randomly(self.state.player_board, size)
            # Count ships for win condition
            self.state.player_ships = self.state.count_ships(self.state.player_board)

            if not self.state.network:
                # Single-player: go directly to playing
                self.state.game_state = "playing"
            else:
                # Multiplayer: handshake then wait
                self.state.network.send({"type":"placement_done"})
                self.state.local_ready      = True
                self.state.waiting_for_sync = True

    def try_place_on_grid(self, ship: DraggableShip) -> bool:
        """
        Attempt to place 'ship' at its current center position.
        Returns True if placement succeeded.
        """
        row, col = get_grid_pos(
            (ship.image.centerx, ship.image.centery),
            Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y
        )
        if row is None or col is None:
            return False

        # Adjust origin so the ship’s center aligns properly
        if ship.orientation == 'h':
            col -= ship.size // 2
        else:
            row -= ship.size // 2

        size   = ship.size
        coords = []
        fits   = True

        # Check bounds and emptiness
        if ship.orientation == 'h':
            if col < 0 or col + size > Config.GRID_SIZE:
                fits = False
            else:
                for i in range(size):
                    if self.state.player_board[row][col+i] != Cell.EMPTY:
                        fits = False
                        break
                if fits:
                    for i in range(size):
                        self.state.player_board[row][col+i] = Cell.SHIP
                        coords.append((row, col+i))
        else:
            if row < 0 or row + size > Config.GRID_SIZE:
                fits = False
            else:
                for i in range(size):
                    if self.state.player_board[row+i][col] != Cell.EMPTY:
                        fits = False
                        break
                if fits:
                    for i in range(size):
                        self.state.player_board[row+i][col] = Cell.SHIP
                        coords.append((row+i, col))

        if fits:
            ship.place(coords)
            return True
        return False

    def snap_back(self):
        """Return the active ship to its sidebar position."""
        if self.active_ship:
            self.active_ship.image.topleft = self.main_area_position()

    def handle_event(self, event: pygame.event.Event, state: GameState):
        """
        Manual-placement input. Ignored entirely if smart mode is on.
        """
        # In smart mode, bypass manual events
        if Config.USE_SMART_SHIP_GENERATOR:
            return

        # Mouse down: start dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.active_ship and self.active_ship.image.collidepoint(event.pos):
                self.active_ship.start_dragging(*event.pos)

        # Mouse move: update drag
        elif event.type == pygame.MOUSEMOTION:
            if self.active_ship and self.active_ship.dragging:
                self.active_ship.update_position(*event.pos)

        # Mouse up: attempt to place
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active_ship and self.active_ship.dragging:
                self.active_ship.stop_dragging()

                # Snap visually to grid cell
                mx, my = self.active_ship.image.center
                col = (mx - Config.BOARD_OFFSET_X) // Config.CELL_SIZE
                row = (my - Config.BOARD_OFFSET_Y) // Config.CELL_SIZE
                if self.active_ship.orientation == 'h':
                    col -= self.active_ship.size // 2
                else:
                    row -= self.active_ship.size // 2

                if (0 <= row < Config.GRID_SIZE
                    and 0 <= col < Config.GRID_SIZE):
                    self.active_ship.image.topleft = (
                        Config.BOARD_OFFSET_X + col * Config.CELL_SIZE,
                        Config.BOARD_OFFSET_Y + row * Config.CELL_SIZE
                    )
                    if self.try_place_on_grid(self.active_ship):
                        self.placed_ships.append(self.active_ship)
                        self.update_active_and_preview()

                        # If all ships placed, advance
                        if not self.active_ship and not self.preview_ship:
                            if not state.network:
                                state.player_ships = state.count_ships(self.state.player_board)
                                state.game_state   = "playing"
                            else:
                                state.network.send({"type":"placement_done"})
                                state.local_ready      = True
                                state.waiting_for_sync = True
                    else:
                        self.snap_back()
                else:
                    self.snap_back()

        # Rotate with R
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if self.active_ship:
                self.active_ship.rotate()

    def update(self, state: GameState):
        """
        In multiplayer manual mode, poll for the opponent’s ready/disconnect
        and transition to playing when both sides have called placement_done.
        """
        if state.network and state.waiting_for_sync:
            msg = state.network.recv()
            if msg:
                if msg.get("type") == "placement_done":
                    state.remote_ready = True
                if msg.get("type") == "disconnect":
                    state.opponent_left = True

                if state.local_ready and state.remote_ready:
                    state.waiting_for_sync = False
                    state.player_ships     = state.count_ships(self.state.player_board)
                    state.game_state       = "playing"
