from config import Config
import random
from enum import Enum, auto


class Cell(Enum):
    EMPTY = auto()  # was 'O'
    SHIP  = auto()  # was 'S'
    MISS  = auto()  # 'M' will be used during attack
    HIT   = auto()  # 'X' will be used when hit


def create_board():
    """Create a 2D grid initialized with Cell.EMPTY."""
    return [[Cell.EMPTY for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]


def place_ship_randomly(board, size):
    """
    Randomly places a ship of given size on the board without overlapping.
    Ships are marked with Cell.SHIP.
    """
    while True:
        orientation = random.choice(['h', 'v'])
        if orientation == 'h':
            row = random.randint(0, Config.GRID_SIZE - 1)
            col = random.randint(0, Config.GRID_SIZE - size)
            if all(board[row][col + i] is Cell.EMPTY for i in range(size)):
                for i in range(size):
                    board[row][col + i] = Cell.SHIP
                break
        else:
            row = random.randint(0, Config.GRID_SIZE - size)
            col = random.randint(0, Config.GRID_SIZE - 1)
            if all(board[row + i][col] is Cell.EMPTY for i in range(size)):
                for i in range(size):
                    board[row + i][col] = Cell.SHIP
                break
