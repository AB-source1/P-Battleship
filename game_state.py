from board import create_board, place_ship_randomly
from config import Config

class GameState:
    def __init__(self):
        self.reset_all()

    def reset(self):
        self.player_board = create_board()
        self.computer_board = create_board()
        self.player_attacks = [['' for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]
        for size in Config.SHIP_SIZES:
            place_ship_randomly(self.computer_board, size)

    def count_ships(self, board):
        return sum(row.count('S') for row in board)

    def reset_with_counts(self):
        self.reset()
        self.player_ships = 0
        self.computer_ships = self.count_ships(self.computer_board)

    def reset_all(self):
        self.reset_with_counts()
        self.user_text = ""
        self.player_name = ""
        self.ship_index = 0
        self.placed_ships = []
        self.ai_turn_pending = False
        self.ai_turn_start_time = 0
        self.game_state = "menu"
        self.running = True
    