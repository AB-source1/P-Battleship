from game.board_helpers import create_board, place_ship_randomly, Cell
from core.config import Config

class GameState:
    def __init__(self, reset_callback):
        self.reset_callback = reset_callback

        # Persistent UI toggles & flags
        self.show_restart_modal = False
        self.show_quit_modal    = False
        self.audio_enabled      = True  # safe to read in draw_top_bar

        # AI difficulty & memory
        self.difficulty       = Config.DEFAULT_DIFFICULTY
        self.ai_targets       = []      # for Medium/Hard hunt modes
        self.last_player_hit  = None    # last successful AI hit

        # Stats counters & timestamps
        self.player_shots      = 0
        self.player_hits       = 0
        self.ai_shots          = 0
        self.ai_hits           = 0
        self.player_shot_times = []     # list of pygame.time.get_ticks()
        self.ai_shot_times     = []     # same for AI
        self.winner            = None   # "Player" or "AI"

        self.final_player_board = None  # ✅ Holds placed ships from placement phase

        # Kick off first full reset
        self.reset_all()
        self.running = True

        self.network = None
        self.is_host = False
        self.local_ready = False
        self.remote_ready = False
        self.waiting_for_sync = False
        self.opponent_left = False

    def reset(self):
        """(Re)create both boards and the player's attack grid."""
        # ✅ Restore board from placement if it exists
        if self.final_player_board:
            self.player_board = [row[:] for row in self.final_player_board]
        else:
            self.player_board = create_board()

        self.computer_board = create_board()
        self.player_attacks = [
            [Cell.EMPTY for _ in range(Config.GRID_SIZE)]
            for _ in range(Config.GRID_SIZE)
        ]

        for size in Config.SHIP_SIZES:
            place_ship_randomly(self.computer_board, size)

    def count_ships(self, board):
        """Return number of SHIP cells remaining on `board`."""
        return sum(row.count(Cell.SHIP) for row in board)

    def reset_with_counts(self):
        """Reset boards and initialize ship‐count trackers."""
        self.reset()
        self.player_ships   = self.count_ships(self.player_board)
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
