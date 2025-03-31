from config import Config
import random

def create_board():
    """Create a 2D grid initialized with 'O'."""
    return [['O' for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]

def place_ship_randomly(board, size):
    """
    Randomly places a ship of given size on the board without overlapping.
    Ships are marked with 'S'.
    """
    while True:
        orientation = random.choice(['h', 'v'])
        if orientation == 'h':
            row = random.randint(0, Config.GRID_SIZE - 1)
            col = random.randint(0, Config.GRID_SIZE - size)
            if all(board[row][col + i] == 'O' for i in range(size)):
                for i in range(size):
                    board[row][col + i] = 'S'
                break
        else:
            row = random.randint(0, Config.GRID_SIZE - size)
            col = random.randint(0, Config.GRID_SIZE - 1)
            if all(board[row + i][col] == 'O' for i in range(size)):
                for i in range(size):
                    board[row + i][col] = 'S'
                break
