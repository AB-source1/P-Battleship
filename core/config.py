import random
import os
import pygame

class Config:
    # ─── Window & Grid Defaults ───
    WIDTH, HEIGHT         = 1000, 600
    CELL_SIZE             = 40

    DEFAULT_GRID_SIZE     = 10
    GRID_SIZE             = DEFAULT_GRID_SIZE

    # ─── Ship Sizes (auto-filled) ───
    SHIP_SIZES            = []  # populated by generate_ships_for_grid()

    # ─── Layout Params (auto–updated) ───
    SPACE_BETWEEN         = 100
    GRID_WIDTH            = None
    BOARD_OFFSET_X        = None
    ENEMY_OFFSET_X        = None
    BOARD_OFFSET_Y        = None
    TOP_BAR_HEIGHT        = 40

    # ─── SCORING PARAMETERS ──────────────────────────────────────
    BASE_HIT_POINTS      = 10    # Award for every successful hit
    MISS_PENALTY         =  2    # Deduct for every miss
    TIME_BONUS_FACTOR    =  5    # Multiplier for “quick‐hit” bonus
    MAX_SHOT_TIME_MS     = 5000  # After this delay, no time bonus
    SHIP_SUNK_BONUS      = 50    # Flat bonus for sinking any ship
    SHIP_LENGTH_BONUS    = 10    # Additional per‐cell bonus (e.g. length×10)

    # ─── Colors ───
    WHITE       = (255, 255, 255)
    RED         = (255,   0,   0)
    BLUE        = (  0, 100, 255)
    GREEN       = (  0, 128,   0)
    DARK_GREEN  = (  0, 180,   0)
    GRAY        = ( 70,  70,  70)
    DARK_GRAY   = (100, 100, 100)
    BLACK       = (  0,   0,   0)
    PREVIEW_GREEN = (0, 255, 0, 100)
    PREVIEW_RED   = (255, 0, 0, 100)

    # ─── Optional Smart‐placement Toggle ───
    USE_SMART_SHIP_GENERATOR = False

    # ─── AI Difficulty Settings ───
    DIFFICULTIES        = ['Easy', 'Medium', 'Hard']
    DEFAULT_DIFFICULTY  = 'Easy'

    ASSET_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "images")

    EXPLOSION_IMG = pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, "explosion.png")),
        (CELL_SIZE, CELL_SIZE)
    )
    EXPLOSION_FADE_DURATION = 500  # milliseconds


    @staticmethod
    def generate_ships_for_grid():
        """Populate Config.SHIP_SIZES based on grid size or smart toggle."""
        if Config.USE_SMART_SHIP_GENERATOR:
            # (Your existing smart‐placement logic)
            pass
        else:
            # Simple presets
            if Config.GRID_SIZE <= 6:
                Config.SHIP_SIZES = [3]
            elif Config.GRID_SIZE <= 8:
                Config.SHIP_SIZES = [4, 3]
            elif Config.GRID_SIZE <= 12:
                Config.SHIP_SIZES = [5, 4, 3]
            else:
                Config.SHIP_SIZES = [6, 5, 4, 3]

    @staticmethod
    def update_layout():
        """
        Call after changing GRID_SIZE:
         • Recompute CELL_SIZE, GRID_WIDTH
         • Recompute board offsets
         • Regenerate SHIP_SIZES
        """
        padding = 3
        max_w   = Config.WIDTH  // (2 * Config.GRID_SIZE + padding)
        max_h   = Config.HEIGHT // (Config.GRID_SIZE + 4)
        raw_cs  = min(max_w, max_h)
        Config.CELL_SIZE      = max(20, min(raw_cs, 60))
        Config.GRID_WIDTH     = Config.CELL_SIZE * Config.GRID_SIZE
        Config.BOARD_OFFSET_X = (Config.WIDTH - (2 * Config.GRID_WIDTH + Config.SPACE_BETWEEN)) // 2
        Config.ENEMY_OFFSET_X = Config.BOARD_OFFSET_X + Config.GRID_WIDTH + Config.SPACE_BETWEEN
        Config.BOARD_OFFSET_Y = (Config.HEIGHT - Config.GRID_WIDTH) // 2

        Config.generate_ships_for_grid()
