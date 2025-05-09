from game.board_helpers import create_board, place_ship_randomly, Cell
from core.config import Config

class GameState:
    def __init__(self, reset_callback):
        self.reset_callback = reset_callback
        # Initialize everything (boards, stats, UI flags, etc.)
        self.reset_all()

    def reset(self):
        # ─── Board setup ───
        self.player_board   = create_board()
        self.computer_board = create_board()
        self.player_attacks = [[Cell.EMPTY for _ in range(Config.GRID_SIZE)]
                               for _ in range(Config.GRID_SIZE)]
        # Place AI ships randomly
        for size in Config.SHIP_SIZES:
            place_ship_randomly(self.computer_board, size)

    def count_ships(self, board):
        return sum(row.count(Cell.SHIP) for row in board)

    def reset_with_counts(self):
        # Reset boards and then count remaining ships
        self.reset()
        self.player_ships   = 0  # will be set when placement ends
        self.computer_ships = self.count_ships(self.computer_board)

    def reset_all(self):
        # ─── Core reset ───
        self.reset_with_counts()
        self.user_text       = ""
        self.player_name     = ""
        self.ship_index      = 0
        self.ai_turn_pending = False
        self.ai_turn_start_time = 0

        # ─── Stats reset ───
        self.player_shots = 0   # total shots you fired
        self.player_hits  = 0   # of those, how many were hits
        self.ai_shots     = 0   # total shots AI fired
        self.ai_hits      = 0   # of those, how many were hits

        # ─── UI state ───
        self.game_state       = "menu"
        self.show_restart_modal = False
        self.show_quit_modal    = False
        self.running           = True

        # Finally, re-invoke placement/reset callback
        self.reset_callback()
