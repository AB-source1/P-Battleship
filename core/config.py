class Config:
    WIDTH, HEIGHT = 1000, 600
    CELL_SIZE = 40

    DEFAULT_GRID_SIZE = 10
    GRID_SIZE = DEFAULT_GRID_SIZE
    SHIP_SIZES = []

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
    def generate_ships_for_grid():
        """Dynamically generate ship sizes based on the grid size."""
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
        """Update layout and regenerate ship list based on grid size."""
        padding = 3
        max_cell_w = Config.WIDTH // (2 * Config.GRID_SIZE + padding)
        max_cell_h = Config.HEIGHT // (Config.GRID_SIZE + 4)

        raw_cell_size = min(max_cell_w, max_cell_h)
        Config.CELL_SIZE = max(20, min(raw_cell_size, 60))

        Config.GRID_WIDTH = Config.GRID_SIZE * Config.CELL_SIZE
        Config.BOARD_OFFSET_X = (Config.WIDTH - (2 * Config.GRID_WIDTH + Config.SPACE_BETWEEN)) // 2
        Config.ENEMY_OFFSET_X = Config.BOARD_OFFSET_X + Config.GRID_WIDTH + Config.SPACE_BETWEEN
        Config.BOARD_OFFSET_Y = (Config.HEIGHT - Config.GRID_WIDTH) // 2

        Config.generate_ships_for_grid()  # ✅ Always update ships when grid size changes
