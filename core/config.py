import random
import os
import pygame


"""
Module: config.py
Purpose:
  - Global constants for window, grid, scoring, asset paths.
  - Layout recalculation when grid size changes.
  - Stub for smart ship generator.
Future Hooks:
  - Sync Config changes over network.
  - Plug in advanced packing algorithm in generate_ships_for_grid().
"""

class Config:
    # ─── Window & Grid Defaults ───
    WIDTH, HEIGHT         = 1000, 600
    CELL_SIZE             = 40

    DEFAULT_GRID_SIZE     = 10
    GRID_SIZE             = DEFAULT_GRID_SIZE

    PLAYING_BOARD_SCALE   = 0.9   # 90% of placement-screen size

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

    MISS_IMG = pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, "Miss.png")),
        (CELL_SIZE, CELL_SIZE))

    EXPLOSION_FADE_DURATION = 500  # milliseconds
    MISS_FADE_DURATION      = 500  # ms (same fade duration for splashes)

    FPS = 60

    PLAYING_CELL_SIZE      = None
    PLAYING_GRID_WIDTH     = None
    PLAY_BOARD_OFFSET_X    = None
    PLAY_ENEMY_OFFSET_X    = None
    PLAY_BOARD_OFFSET_Y    = None

    @staticmethod
    def generate_ships_for_grid():
        """
        Populate Config.SHIP_SIZES for current GRID_SIZE.
        Stub: implement smarter packing (e.g. minimal clustering).
        """
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
                Config.SHIP_SIZES = [ 5, 4, 3, 3]

    @staticmethod
    def update_layout():
        """
        After changing GRID_SIZE:
        - Recompute CELL_SIZE to fit viewport
        - Update grid offsets for placement & play
        - Regenerate SHIP_SIZES via generate_ships_for_grid()
        """
        padding = 3
        max_w   = Config.WIDTH  // (2 * Config.GRID_SIZE + padding)
        max_h   = Config.HEIGHT // (Config.GRID_SIZE + 4)
        raw_cs  = min(max_w, max_h)

        # base cell for placement & menu
        Config.CELL_SIZE      = max(20, min(raw_cs, 60))
        Config.GRID_WIDTH     = Config.CELL_SIZE * Config.GRID_SIZE
        Config.BOARD_OFFSET_X = (Config.WIDTH - (2 * Config.GRID_WIDTH + Config.SPACE_BETWEEN)) // 2
        Config.ENEMY_OFFSET_X = Config.BOARD_OFFSET_X + Config.GRID_WIDTH + Config.SPACE_BETWEEN
        Config.BOARD_OFFSET_Y = (Config.HEIGHT - Config.GRID_WIDTH) // 2

        # ─── NEW: compute playing-screen sizes ───
        Config.PLAYING_CELL_SIZE = int(Config.CELL_SIZE * Config.PLAYING_BOARD_SCALE)
        Config.PLAYING_GRID_WIDTH = Config.PLAYING_CELL_SIZE * Config.GRID_SIZE

        diff = (Config.GRID_WIDTH - Config.PLAYING_GRID_WIDTH) // 2
        Config.PLAY_BOARD_OFFSET_X  = Config.BOARD_OFFSET_X + diff
        Config.PLAY_ENEMY_OFFSET_X  = Config.ENEMY_OFFSET_X + diff
        Config.PLAY_BOARD_OFFSET_Y  = Config.BOARD_OFFSET_Y + diff

        Config.generate_ships_for_grid()