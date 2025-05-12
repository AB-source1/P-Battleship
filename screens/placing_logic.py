# screens/placing_logic.py

import pygame
from game.draggable_ship import DraggableShip
from game.board_helpers import Cell, get_grid_pos
from core.config import Config
from helpers.draw_helpers import draw_top_bar

class PlacingLogic:
    def __init__(self, screen, state):
        self.screen       = screen
        self.state        = state
        self.active_ship  = None
        self.preview_ship = None
        self.ship_queue   = []
        self.placed_ships = []
        self.setup_ships()

    def setup_ships(self):
        """Fill ship_queue from Config.SHIP_SIZES and set active/preview."""
        self.ship_queue = [
            DraggableShip(size, *self.main_area_position())
            for size in Config.SHIP_SIZES
        ]
        self.update_active_and_preview()  

    def update_active_and_preview(self):
        """Pop the next ship as active and peek the one after as preview."""
        if self.ship_queue:
            self.active_ship = self.ship_queue.pop(0)
            self.active_ship.rect.topleft = self.main_area_position()
        else:
            self.active_ship = None

        if self.ship_queue:
            self.preview_ship = self.ship_queue[0]
            self.preview_ship.rect.topleft = self.preview_area_position()
        else:
            self.preview_ship = None  

    def main_area_position(self):
        return (Config.WIDTH - 350, Config.HEIGHT // 2 - 40)

    def preview_area_position(self):
        return (Config.WIDTH - 250, Config.HEIGHT // 2 - 100)

    def try_place_on_grid(self, ship):
        """
        Attempt to lock the ship onto the grid.
        Returns True on success, False otherwise.
        """
        row, col = get_grid_pos(
            (ship.rect.centerx, ship.rect.centery),
            Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y
        )
        if row is None or col is None:
            return False

        # Center the placement coords based on orientation
        if ship.orientation == 'h':
            col -= ship.size // 2
        else:
            row -= ship.size // 2

        size   = ship.size
        coords = []
        fits   = True

        if ship.orientation == 'h':
            if col < 0 or col + size > Config.GRID_SIZE or not (0 <= row < Config.GRID_SIZE):
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
            if row < 0 or row + size > Config.GRID_SIZE or not (0 <= col < Config.GRID_SIZE):
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
            self.active_ship.rect.topleft = self.main_area_position()

    def handle_event(self, event: pygame.event.Event, state):
        """
        Handle dragging/rotation/placement of ships.
        Once all ships are placed, in multiplayer send a 'placement_done'
        handshake; otherwise jump to 'playing'.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.active_ship and self.active_ship.rect.collidepoint(event.pos):
                self.active_ship.start_dragging(*event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.active_ship and self.active_ship.dragging:
                self.active_ship.update_position(*event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.active_ship and self.active_ship.dragging:
                self.active_ship.stop_dragging()
                mx, my = self.active_ship.rect.center

                col = (mx - Config.BOARD_OFFSET_X) // Config.CELL_SIZE
                row = (my - Config.BOARD_OFFSET_Y) // Config.CELL_SIZE

                if self.active_ship.orientation == 'h':
                    col -= self.active_ship.size // 2
                else:
                    row -= self.active_ship.size // 2

                if 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE:
                    # Snap visually to the grid
                    self.active_ship.rect.topleft = (
                        Config.BOARD_OFFSET_X + col * Config.CELL_SIZE,
                        Config.BOARD_OFFSET_Y + row * Config.CELL_SIZE
                    )

                    if self.try_place_on_grid(self.active_ship):
                        self.placed_ships.append(self.active_ship)
                        self.update_active_and_preview()

                        # All ships placed?
                        if not self.active_ship and not self.preview_ship:
                            # Single-player: go straight to playing
                            if not state.network:
                                state.player_ships  = state.count_ships(state.player_board)
                                # save the sprite objects for the playing screen
                                state.placed_ships  = self.placed_ships.copy()
                                state.game_state    = "playing"
                            # Multiplayer: send handshake and wait
                            else:
                                state.network.send({"type":"placement_done"})
                                state.local_ready      = True
                                state.waiting_for_sync = True
                                # also persist sprites for when multiplayer actually starts
                                state.placed_ships    = self.placed_ships.copy()
                    else:
                        self.snap_back()
                else:
                    self.snap_back()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.active_ship:
                self.active_ship.rotate()  

    def update(self, state):
        """
        In multiplayer, poll for the peer's 'placement_done' or 'disconnect'.
        Transition to 'playing' once both are ready.
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
                    state.player_ships     = state.count_ships(state.player_board)
                    state.game_state       = "playing"

    def undo_last_ship(self):
        """Remove the most recently placed ship and return it to the queue."""
        if self.placed_ships:
            last_ship = self.placed_ships.pop()
            for (r, c) in last_ship.coords:
                self.state.player_board[r][c] = Cell.EMPTY

            # Put the undone ship back at the front
            if self.active_ship:
                self.ship_queue.insert(0, self.active_ship)
            self.active_ship = last_ship
            self.active_ship.image.topleft = self.main_area_position()

            if self.ship_queue:
                self.preview_ship = self.ship_queue[0]
                self.preview_ship.image.topleft = self.preview_area_position()
            else:
                self.preview_ship = None  

    def reset(self):
        """Clear all placement state and re-populate the ship queue."""
        self.active_ship  = None
        self.preview_ship = None
        self.ship_queue   = []
        self.placed_ships = []
        self.setup_ships()  
