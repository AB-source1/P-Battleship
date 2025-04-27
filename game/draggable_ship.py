import pygame
from core.config import Config

class DraggableShip:
    def __init__(self, size, x, y):
        self.size = size
        self.orientation = 'h'
        self.image = pygame.Rect(x, y, size * Config.CELL_SIZE, Config.CELL_SIZE)
        self.dragging = False
        self.drag_offset = (0, 0)  # NEW
        self.coords = []

    def draw(self, surface):
        pygame.draw.rect(surface, Config.BLUE, self.image)
        pygame.draw.rect(surface, Config.WHITE, self.image, 2)

    def rotate(self):
        center = self.image.center  # ✅ Save center
        w, h = self.image.size
        self.image.size = (h, w)    # Swap width and height
        self.image.center = center  # ✅ Restore center
        self.orientation = 'v' if self.orientation == 'h' else 'h'

    def place(self, coords):
        self.coords = coords

    def start_dragging(self, mx, my):
        # Save mouse offset when clicking the ship
        self.dragging = True
        self.drag_offset = (self.image.x - mx, self.image.y - my)

    def stop_dragging(self):
        self.dragging = False
        self.drag_offset = (0, 0)

    def update_position(self, mx, my):
        if self.dragging:
            # Move smoothly respecting where the ship was clicked
            self.image.x = mx + self.drag_offset[0]
            self.image.y = my + self.drag_offset[1]

    def get_preview_cells(self, offset_x, offset_y):
        # Calculate grid cells that the ship would occupy
        col = (self.image.x - offset_x + Config.CELL_SIZE // 2) // Config.CELL_SIZE
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
