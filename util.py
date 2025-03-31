from config import Config

def get_grid_pos(pos, offset_x, offset_y):
    mx, my = pos
    col = (mx - offset_x) // Config.CELL_SIZE
    row = (my - offset_y) // Config.CELL_SIZE
    if 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE:
        return row, col
    return None, None