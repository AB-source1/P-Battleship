# core/game_state.py

from game.board_helpers import create_board, place_ship_randomly, Cell
from core.config import Config

class GameState:
    def __init__(self, reset_callback):
        self.reset_callback = reset_callback

        # ─── Persistent UI Toggles & Flags ───
        self.show_restart_modal = False
        self.show_quit_modal    = False
        self.audio_enabled      = True   # for your audio toggle button

        # ─── AI Difficulty & Memory ───
        self.difficulty       = Config.DEFAULT_DIFFICULTY
        self.ai_targets       = []       # for Medium/Hard “hunt” modes
        self.last_player_hit  = None     # last successful hit coord by AI

        # ─── Stats Counters ───
        # Track total shots & hits for player and AI
        self.player_shots = 0
        self.player_hits  = 0
        self.ai_shots     = 0
        self.ai_hits      = 0

        # ─── Kick off the full reset ───
        self.reset_all()

        # ─── Main loop control ───
        self.running = True


    def reset(self):
        """
        (Re)create both boards and the player's attack grid.
        """
        # Empty boards
        self.player_board   = create_board()
        self.computer_board = create_board()
        # Where the player’s shots get marked
        self.player_attacks = [
            [Cell.EMPTY for _ in range(Config.GRID_SIZE)]
            for _ in range(Config.GRID_SIZE)
        ]
        # Place the computer’s ships randomly
        for size in Config.SHIP_SIZES:
            place_ship_randomly(self.computer_board, size)


    def count_ships(self, board):
        """Return number of SHIP cells remaining on the board."""
        return sum(row.count(Cell.SHIP) for row in board)


    def reset_with_counts(self):
        """
        Reset boards (via reset()) and initialize ship‐count trackers.
        """
        self.reset()
        # Player ships will be set by your placing logic later
        self.player_ships   = 0
        self.computer_ships = self.count_ships(self.computer_board)


    def reset_all(self):
        """
        Full match‐start reset:
          • Boards & ship counts
          • UI / turn flags
          • AI memory
          • Stats counters
          • Scene selection
        (Does NOT reset `difficulty` or `audio_enabled` so those persist.)
        """
        # ─── Boards & Counts ───
        self.reset_with_counts()

        # ─── Gameplay State ───
        self.user_text         = ""
        self.player_name       = ""
        self.ship_index        = 0
        self.ai_turn_pending   = False
        self.ai_turn_start_time= 0

        # ─── Clear any in‐flight AI memory ───
        self.ai_targets        = []
        self.last_player_hit   = None

        # ─── Reset stats for new match ───
        self.player_shots = 0
        self.player_hits  = 0
        self.ai_shots     = 0
        self.ai_hits      = 0

        # ─── Scene & Modal Flags ───
        self.game_state         = "menu"
        self.show_restart_modal = False
        self.show_quit_modal    = False

        # Finally, invoke your placement-reset callback
        self.reset_callback()
