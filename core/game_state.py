from game.board_helpers import create_board, place_ship_randomly, Cell
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
        """(Re)create both boards and the player's attack grid."""
        self.player_board   = create_board()
        self.computer_board = create_board()
        self.player_attacks = [
            [Cell.EMPTY for _ in range(Config.GRID_SIZE)]
            for _ in range(Config.GRID_SIZE)
        ]
        # Place the computer’s ships randomly
        for size in Config.SHIP_SIZES:
            place_ship_randomly(self.computer_board, size)

    def count_ships(self, board):
        """Return number of SHIP cells remaining on `board`."""
        return sum(row.count(Cell.SHIP) for row in board)

    def reset_with_counts(self):
        """Reset boards and initialize ship‐count trackers."""
        self.reset()
        # Player ships set later by placing logic
        self.player_ships   = 0
        self.computer_ships = self.count_ships(self.computer_board)

    def reset_all(self):
        """
        Full match-start reset:
          • Boards & ship counts
          • UI / turn flags
          • AI memory
          • Stats counters & timestamps
          • Scene selection
        (Does NOT touch `difficulty` or `audio_enabled` so those persist.)
        """
        # Boards & counts
        self.reset_with_counts()

        self.placed_ships = []

        # Gameplay & UI state
        self.user_text         = ""
        self.player_name       = ""
        self.ship_index        = 0
        self.ai_turn_pending   = False
        self.ai_turn_start_time= 0

        # Clear any in‐flight AI memory
        self.ai_targets        = []
        self.last_player_hit   = None

        # Reset stats & shot timings
        self.player_shots      = 0
        self.player_hits       = 0
        self.ai_shots          = 0
        self.ai_hits           = 0
        self.player_shot_times = []
        self.ai_shot_times     = []
        self.winner            = None

        # Scene & modal flags
        self.game_state         = "menu"
        self.show_restart_modal = False
        self.show_quit_modal    = False

        # Invoke placement logic callback (e.g. PlacingLogic.reset)
        self.reset_callback()
    def reset_score(self):
        self.score = 0
        self.hits = 0
        self.misses = 0
