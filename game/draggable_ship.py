import pygame
from core.config import Config

class DraggableShip:
    def __init__(self, size, x, y):
        self.size = size
        self.orientation = 'h'
        self.image = pygame.Rect(x, y, size * Config.CELL_SIZE, Config.CELL_SIZE)
        self.dragging = False
        self.drag_offset = (0, 0)
        self.coords = []

    def draw(self, surface):
        pygame.draw.rect(surface, Config.BLUE, self.image)
        pygame.draw.rect(surface, Config.WHITE, self.image, 2)

    def rotate(self):
        center = self.image.center
        w, h = self.image.size
        self.image.size = (h, w)
        self.image.center = center
        self.orientation = 'v' if self.orientation == 'h' else 'h'

    def place(self, coords):
        self.coords = coords

    def start_dragging(self, mx, my):
        self.dragging = True
        self.drag_offset = (self.image.x - mx, self.image.y - my)

    def stop_dragging(self):
        self.dragging = False
        self.drag_offset = (0, 0)

    def update_position(self, mx, my):
        if self.dragging:
            self.image.center = (mx, my)

    def get_preview_cells(self, offset_x, offset_y):
        col = (self.image.centerx - offset_x) // Config.CELL_SIZE
        row = (self.image.centery - offset_y) // Config.CELL_SIZE

        if self.orientation == 'h':
            col -= self.size // 2
        else:
            row -= self.size // 2

        cells = []

        if self.orientation == 'h':
            if col < 0 or col + self.size > Config.GRID_SIZE or row < 0 or row >= Config.GRID_SIZE:
                return None
            for i in range(self.size):
                cells.append((row, col + i))
        else:
            if row < 0 or row + self.size > Config.GRID_SIZE or col < 0 or col >= Config.GRID_SIZE:
                return None
            for i in range(self.size):
                cells.append((row + i, col))

        return cells
