from game.board_helpers import create_board, place_ship_randomly, Cell
from core.config import Config

class GameState:
    def __init__(self, reset_callback):
        self.reset_callback = reset_callback

        # Persistent UI toggles & flags
        self.show_restart_modal = False
        self.show_quit_modal    = False
        self.audio_enabled      = True  # safe to read in draw_top_bar
        self.sfxenabled = True

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

        self.timer_start = None    # will hold pygame.time.get_ticks() when play begins

                # ─── SCORING STATE ───────────────────────────────────
        self.score            = 0       # running total
        self.last_shot_time   = None    # when the player last fired (ms)
        self.hit_count        = 0       # total hits this round

        # Reset Pass&Play back to off, too
        self.pass_play_mode         = False
        self.pass_play_stage        = 0
        self.pass_play_boards       = [None, None]
        self.pass_play_attacks      = [None, None]
        self.pass_play_placed_ships = [None, None]

        # per-player Pass&Play stats
        self.pass_play_shots         = [0, 0]
        self.pass_play_hits          = [0, 0]
        self.pass_play_shot_times    = [[], []]

        # Kick off first full reset
        self.reset_all()
        # Main loop flag
        self.running = True

        self.network = None       # will hold our Network instance
        self.is_host = False      # True if this client is the host
        self.local_ready    = False   # we’ve finished placement
        self.remote_ready   = False   # peer has signaled ready
        self.waiting_for_sync = False # show waiting overlay
        self.opponent_left  = False   # peer disconnected

        self.history = []       # stack of previous scenes
        self.skip_push = False


        #explostion
        self.explosions             = []
        self.miss_splashes  = []



    def reset(self):
        """(Re)create both boards and the player's attack grid."""
        self.player_board   = create_board()
        self.computer_board = create_board()
        self.computer_ships_coords = []
        self.player_attacks = [
            [Cell.EMPTY for _ in range(Config.GRID_SIZE)]
            for _ in range(Config.GRID_SIZE)
        ]
        # Place the computer’s ships randomly
        for size in Config.SHIP_SIZES:
            coords = place_ship_randomly(self.computer_board, size)
            self.computer_ships_coords.append(coords)

        self.pass_play_mode    = False
        self.pass_play_stage   = 0
        self.current_player    = 0
        self.pass_play_boards  = [None, None]
        self.pass_play_attacks = [None, None]

        

        # … invoke placement callback …
        self.reset_callback()

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

        self.pass_play_boards         = [None, None]
        self.pass_play_attacks        = [None, None]
        self.pass_play_placed_ships   = [None, None]

        # clear per-player stats
        self.pass_play_shots         = [0, 0]
        self.pass_play_hits          = [0, 0]
        self.pass_play_shot_times    = [[], []]


        self.pass_play_shots      = [0, 0]
        self.pass_play_score           = [0, 0]
        self.pass_play_last_shot_time  = [0, 0]
        self.pass_play_shot_times = [[], []]

        # Invoke placement logic callback (e.g. PlacingLogic.reset)
        self.reset_callback()

        # clear explosion history
        self.explosions             = []
        self.miss_splashes  = []

        
