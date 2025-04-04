# config.py
class Config:
    # Screen
    WIDTH, HEIGHT = 1000, 600
    CELL_SIZE = 40
    GRID_SIZE = 10
    SHIP_SIZES = [5, 4, 3]
    GRID_WIDTH = GRID_SIZE * CELL_SIZE

    # Layout
    SPACE_BETWEEN = 100
    BOARD_OFFSET_X = (WIDTH - (2 * GRID_WIDTH + SPACE_BETWEEN)) // 2
    ENEMY_OFFSET_X = BOARD_OFFSET_X + GRID_WIDTH + SPACE_BETWEEN
    BOARD_OFFSET_Y = (HEIGHT - GRID_WIDTH) // 2

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