import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos


class DraggableShip:
    def __init__(self, size, x, y):
        self.size = size
        self.orientation = 'h'
        self.image = pygame.Rect(
            x, y, size * Config.CELL_SIZE, Config.CELL_SIZE)
        self.dragging = False
        self.coords = []

    def draw(self, surface):
        pygame.draw.rect(surface, Config.BLUE, self.image)
        pygame.draw.rect(surface, Config.WHITE, self.image, 2)

    def rotate(self):
        w, h = self.image.size
        self.image.size = (h, w)
        self.orientation = 'v' if self.orientation == 'h' else 'h'

    def place(self,coords):
        self.coords = coords


    def update_position(self, mx, my):
        self.image.center = (mx, my)

    def get_preview_cells(self, offset_x, offset_y):
        col = (self.image.x - offset_x +
               Config.CELL_SIZE // 2) // Config.CELL_SIZE
        row = (self.image.y - offset_y + Config.CELL_SIZE // 2) // Config.CELL_SIZE
        cells = []
        if self.orientation == 'h':
            if col + self.size > Config.GRID_SIZE or row < 0 or row >= Config.GRID_SIZE:
                return None
            for i in range(self.size):
                cells.append((row, col + i))
        else:
            if row + self.size > Config.GRID_SIZE or col < 0 or col >= Config.GRID_SIZE:
                return None
            for i in range(self.size):
                cells.append((row + i, col))
        return cells
