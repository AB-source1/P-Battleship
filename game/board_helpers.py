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
    """Randomly place a ship of given size onto the board with 1-cell buffer zone."""

    def is_clear_area(r, c):
        """Check surrounding 3x3 area to ensure no other ships are nearby."""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < Config.GRID_SIZE and 0 <= nc < Config.GRID_SIZE:
                    if board[nr][nc] == Cell.SHIP:
                        return False
        return True

    while True:
        orientation = random.choice(['h', 'v'])
        if orientation == 'h':
            row = random.randint(0, Config.GRID_SIZE - 1)
            col = random.randint(0, Config.GRID_SIZE - size)
            positions = [(row, col + i) for i in range(size)]
        else:
            row = random.randint(0, Config.GRID_SIZE - size)
            col = random.randint(0, Config.GRID_SIZE - 1)
            positions = [(row + i, col) for i in range(size)]

        # Ensure all positions and surrounding area are clear
        if all(board[r][c] == Cell.EMPTY and is_clear_area(r, c) for r, c in positions):
            for r, c in positions:
                board[r][c] = Cell.SHIP
            break

def get_grid_pos(mouse_pos, offset_x, offset_y):
    """Convert pixel position to grid (row, col) based on offsets."""
    mx, my = mouse_pos
    col = (mx - offset_x) // Config.CELL_SIZE
    row = (my - offset_y) // Config.CELL_SIZE
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
