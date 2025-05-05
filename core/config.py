import random

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

    USE_SMART_SHIP_GENERATOR = False

    @staticmethod
    def generate_ships_for_grid():
        """Dynamically generate ship sizes based on grid size."""
        if Config.USE_SMART_SHIP_GENERATOR:
            Config.SHIP_SIZES = []
            total_cells = Config.GRID_SIZE * Config.GRID_SIZE

            # Target 25%-30% of cells covered
            min_coverage = int(total_cells * 0.25)
            max_coverage = int(total_cells * 0.30)
            target_coverage = random.randint(min_coverage, max_coverage)

            current_coverage = 0
            possible_ship_sizes = list(range(2, min(7, Config.GRID_SIZE // 2 + 1)))  # Ships between size 2 and 6

            while current_coverage < target_coverage and possible_ship_sizes:
                ship_size = random.choice(possible_ship_sizes)

                # Don't overfill too much
                if current_coverage + ship_size <= target_coverage + 2:
                    Config.SHIP_SIZES.append(ship_size)
                    current_coverage += ship_size

            random.shuffle(Config.SHIP_SIZES)  # Mix order randomly

        else:
            # Default normal
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
        """Update layout and regenerate ships."""
        padding = 3
        max_cell_w = Config.WIDTH // (2 * Config.GRID_SIZE + padding)
        max_cell_h = Config.HEIGHT // (Config.GRID_SIZE + 4)

        raw_cell_size = min(max_cell_w, max_cell_h)
        Config.CELL_SIZE = max(20, min(raw_cell_size, 60))

        Config.GRID_WIDTH = Config.GRID_SIZE * Config.CELL_SIZE
        Config.BOARD_OFFSET_X = (Config.WIDTH - (2 * Config.GRID_WIDTH + Config.SPACE_BETWEEN)) // 2
        Config.ENEMY_OFFSET_X = Config.BOARD_OFFSET_X + Config.GRID_WIDTH + Config.SPACE_BETWEEN
        Config.BOARD_OFFSET_Y = (Config.HEIGHT - Config.GRID_WIDTH) // 2

        Config.generate_ships_for_grid()
