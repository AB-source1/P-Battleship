from core.config import Config
import random
from enum import Enum, auto

class Cell(Enum):
    EMPTY = auto()
    SHIP  = auto()
    MISS  = auto()
    HIT   = auto()

def create_board():
    """Create a 2D board grid initialized with EMPTY cells."""
    return [[Cell.EMPTY for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]

def place_ship_randomly(board, size):
    """Randomly place a ship of given size onto the board."""
    while True:
        orientation = random.choice(['h', 'v'])
        if orientation == 'h':
            row = random.randint(0, Config.GRID_SIZE - 1)
            col = random.randint(0, Config.GRID_SIZE - size)
            if all(board[row][col + i] == Cell.EMPTY for i in range(size)):
                for i in range(size):
                    board[row][col + i] = Cell.SHIP
                break
        else:
            row = random.randint(0, Config.GRID_SIZE - size)
            col = random.randint(0, Config.GRID_SIZE - 1)
            if all(board[row + i][col] == Cell.EMPTY for i in range(size)):
                for i in range(size):
                    board[row + i][col] = Cell.SHIP
                break

def get_grid_pos(mouse_pos, offset_x, offset_y):
    """Convert pixel position to grid (row, col) based on offsets."""
    mx, my = mouse_pos
    col = (mx - offset_x) // Config.CELL_SIZE
    row = (my - offset_y) // Config.CELL_SIZE
    if 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE:
        return row, col
    return None, None
