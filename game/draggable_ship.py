import pygame
import os
from core.config import Config

# --- Load and prepare ship images ---
base_ship_images = {
    3: pygame.image.load(os.path.join("images", "ShipDestroyerHull.png")),
    4: pygame.image.load(os.path.join("images", "ShipSubMarineHull.png")),
    5: pygame.image.load(os.path.join("images", "ShipBattleshipHull.png"))
}

ship_images = {}
for size, base_img in base_ship_images.items():
    vert_scaled = pygame.transform.scale(base_img, (Config.CELL_SIZE, Config.CELL_SIZE * size))
    horiz_scaled = pygame.transform.rotate(
        pygame.transform.scale(base_img, (Config.CELL_SIZE, Config.CELL_SIZE * size)), -90
    )
    ship_images[size] = {'v': vert_scaled, 'h': horiz_scaled}


# --- DraggableShip Class ---
class DraggableShip:
    def __init__(self, size, x, y):
        self.size = size
        self.image = pygame.Rect(x, y, Config.CELL_SIZE, Config.CELL_SIZE * size)
        self.dragging = False
        self.orientation = 'v'
        self.placed = False
        self.coords = []

    def draw(self, surface):
        ship_img = ship_images[self.size][self.orientation]
        img_rect = ship_img.get_rect(center=self.image.center)
        surface.blit(ship_img, img_rect)

    def rotate(self):
        self.orientation = 'h' if self.orientation == 'v' else 'v'

        if self.orientation == 'h':
            self.image.width = Config.CELL_SIZE * self.size
            self.image.height = Config.CELL_SIZE
        else:
            self.image.width = Config.CELL_SIZE
            self.image.height = Config.CELL_SIZE * self.size

    def start_dragging(self, x, y):
        self.dragging = True
        self.offset_x = self.image.x - x
        self.offset_y = self.image.y - y

    def update_position(self, x, y):
        self.image.x = x + self.offset_x
        self.image.y = y + self.offset_y

    def stop_dragging(self):
        self.dragging = False

    def place(self, coords):
        self.placed = True
        self.dragging = False
        self.coords = coords

    def get_preview_cells(self, offset_x, offset_y):
        """Return list of (row, col) tuples this ship would occupy if dropped now."""
        x, y = self.image.center
        col = (x - offset_x) // Config.CELL_SIZE
        row = (y - offset_y) // Config.CELL_SIZE

        if self.orientation == 'h':
            col -= self.size // 2
        else:
            row -= self.size // 2

        cells = []
        for i in range(self.size):
            r = row + i if self.orientation == 'v' else row
            c = col + i if self.orientation == 'h' else col
            cells.append((r, c))

        return cells
