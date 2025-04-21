class Config:
    WIDTH, HEIGHT = 1000, 600
    CELL_SIZE = 40

    DEFAULT_GRID_SIZE = 10
    GRID_SIZE = DEFAULT_GRID_SIZE
    SHIP_SIZES = [5, 4, 3]

    # Layout (recomputed dynamically)
    SPACE_BETWEEN = 100
    GRID_WIDTH = None
    BOARD_OFFSET_X = None
    ENEMY_OFFSET_X = None
    BOARD_OFFSET_Y = None
    TOP_BAR_HEIGHT = 40

    # Colors
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 100, 255)
    GREEN = (0, 128, 0)
    DARK_GREEN = (0, 180, 0)
    GRAY = (70, 70, 70)
    DARK_GRAY = (100, 100, 100)
    BLACK = (0, 0, 0)
    PREVIEW_GREEN = (0, 255, 0, 100)
    PREVIEW_RED = (255, 0, 0, 100)

    @staticmethod
    def update_layout():
        padding = 3  # space between boards in cells
        max_cell_w = Config.WIDTH // (2 * Config.GRID_SIZE + padding)
        max_cell_h = Config.HEIGHT // (Config.GRID_SIZE + 4)  # leave space for UI

        raw_cell_size = min(max_cell_w, max_cell_h)
        Config.CELL_SIZE = max(20, min(raw_cell_size, 60))  # ✅ clamp between 20 and 60

        Config.GRID_WIDTH = Config.GRID_SIZE * Config.CELL_SIZE
        Config.BOARD_OFFSET_X = (Config.WIDTH - (2 * Config.GRID_WIDTH + Config.SPACE_BETWEEN)) // 2
        Config.ENEMY_OFFSET_X = Config.BOARD_OFFSET_X + Config.GRID_WIDTH + Config.SPACE_BETWEEN
        Config.BOARD_OFFSET_Y = (Config.HEIGHT - Config.GRID_WIDTH) // 2

