from game.board_helpers import create_board, place_ship_randomly, Cell  # UPDATED
from core.config import Config


class GameState:
    def __init__(self, reset_callback):
        self.reset_callback = reset_callback
        self.reset_with_counts()
        self.show_restart_modal = False 
        self.show_quit_modal = False
        self.audio_enabled = True
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.running = True
        self.game_state = "menu"
        self.ai_turn_pending = False
        self.ai_turn_start_time = 0



    def reset(self):
        self.player_board = create_board()
        self.computer_board = create_board()
        self.player_attacks = [[Cell.EMPTY for _ in range(Config.GRID_SIZE)]  # UPDATED
                               for _ in range(Config.GRID_SIZE)]
        for size in Config.SHIP_SIZES:
            place_ship_randomly(self.computer_board, size)

    def count_ships(self, board):
        return sum(row.count(Cell.SHIP) for row in board)  # UPDATED

    def reset_with_counts(self):
        self.reset()
        self.player_ships = 0
        self.computer_ships = self.count_ships(self.computer_board)

    def reset_all(self):
        self.reset_with_counts()
        self.user_text = ""
        self.player_name = ""
        self.ship_index = 0
        self.ai_turn_pending = False
        self.ai_turn_start_time = 0
        self.game_state = "menu"
        self.show_restart_modal = False 
        self.show_quit_modal = False
        self.running = True
        self.reset_callback()
    def reset_score(self):
        self.score = 0
        self.hits = 0
        self.misses = 0
