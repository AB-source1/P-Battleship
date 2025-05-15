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

def get_grid_pos(mouse_pos, offset_x, offset_y, cell_size=None):
    cs = cell_size or Config.CELL_SIZE
    mx, my = mouse_pos
    col = (mx - offset_x) // cs
    row = (my - offset_y) // cs
    if 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE:
        return row, col
    return None, None

def fire_at(row: int, col: int, board: list[list[Cell]]) -> tuple[bool, None]:
    """
    Mark board[row][col] as HIT or MISS.
    Returns (hit, None) since we don't track ship objects here.
    """
    if board[row][col] == Cell.SHIP:
        board[row][col] = Cell.HIT
        return True, None
    else:
        board[row][col] = Cell.MISS
        return False, None