from core.config import Config
import random
from enum import Enum, auto

"""
Module: board_helpers.py
Purpose:
  - Pure-logic helpers for board grid management.
  - Cell Enum for EMPTY, SHIP, MISS, HIT.
  - Functions: create_board, place_ship_randomly, get_grid_pos, fire_at.
Future Hooks:
  - fire_at could return Ship objects for sunk detection and network notification.
"""

class Cell(Enum):
    EMPTY = auto()
    SHIP  = auto()
    MISS  = auto()
    HIT   = auto()

def create_board():
    """Create a 2D board grid initialized with EMPTY cells."""
    return [[Cell.EMPTY for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]

def place_ship_randomly(board, size):
    """Place a ship of given size randomly without overlap."""
    while True:
        orientation = random.choice(['h', 'v'])
        if orientation == 'h':
            row = random.randint(0, Config.GRID_SIZE - 1)
            col = random.randint(0, Config.GRID_SIZE - size)
            if all(board[row][col + i] == Cell.EMPTY for i in range(size)):
                coords = []
                for i in range(size):
                    board[row][col + i] = Cell.SHIP
                    coords.append((row, col + i))
                return coords
        else:
            row = random.randint(0, Config.GRID_SIZE - size)
            col = random.randint(0, Config.GRID_SIZE - 1)
            if all(board[row + i][col] == Cell.EMPTY for i in range(size)):
                coords = []
                for i in range(size):
                    board[row + i][col] = Cell.SHIP
                    coords.append((row + i, col))
                return coords
            
def get_grid_pos(mouse_pos, offset_x, offset_y, cell_size=None):
    """Convert pixel coords to grid (row, col)."""
    cs = cell_size or Config.CELL_SIZE
    mx, my = mouse_pos
    col = (mx - offset_x) // cs
    row = (my - offset_y) // cs
    if 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE:
        return row, col
    return None, None

def fire_at(row: int, col: int, board: list[list[Cell]]) -> tuple[bool, None]:
    """Mark cell as HIT or MISS on board; return hit status."""
    if board[row][col] == Cell.SHIP:
        board[row][col] = Cell.HIT
        return True, None
    else:
        board[row][col] = Cell.MISS
        return False, None