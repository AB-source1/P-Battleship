import os
import pygame
from core.config import Config

# ─── Map only the sizes you generate (SHIP_SIZES = [5,4,3] for GRID≤12) :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
SHIP_IMAGE_FILES = {
    3: "ShipSubMarineHull.png",    # size-3 ship
    4: "ShipDestroyerHull.png",    # size-4 ship
    5: "ShipBattleshipHull.png",   # size-5 ship
}


class DraggableShip:
    def __init__(self, size: int, x: int, y: int):
        """
        size: number of cells this ship spans (3, 4, or 5)
        x, y: initial top-left pixel coords for the sprite
        """
        self.size = size
        self.orientation = 'h'

        # ─── Load & validate the correct sprite ─────────────────────────────────
        filename = SHIP_IMAGE_FILES.get(size)
        if filename is None:
            raise ValueError(f"No ship image configured for size {size}")
        image_path = os.path.join("resources", "images", filename)
        raw = pygame.image.load(image_path).convert_alpha()

        # ─── 2) Scale it as a VERTICAL strip: CELL_SIZE×(size × CELL_SIZE)
        vertical = pygame.transform.scale(
            raw,
            (Config.CELL_SIZE, size * Config.CELL_SIZE)
        )

        # ─── 3) Rotate once (–90°) to create a horizontal base image
        self.base_image = pygame.transform.rotate(vertical, -90)
        # ─── Start unrotated
        self.image = self.base_image
        self.rect  = self.image.get_rect(topleft=(x, y))

        # ─── Drag state (unchanged API) ─────────────────────────────────────────
        self.dragging   = False
        self.drag_offset = (0, 0)
        self.coords     = []  # filled when the ship is finally placed

    def draw(self, surface: pygame.Surface):
        """Blit the ship sprite at its current position."""
        surface.blit(self.image, self.rect)

    def rotate(self):
        """
        Toggle orientation and rotate the sprite by ±90° around its center.
        Always rotates the original horizontal `base_image` to avoid blurring.
        """
        self.orientation = 'v' if self.orientation == 'h' else 'h'
        angle = 90 if self.orientation == 'v' else -90
        self.image = pygame.transform.rotate(self.base_image, angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

    def start_dragging(self, mx: int, my: int):
        """Begin dragging; record offset so the sprite follows the mouse."""
        self.dragging = True
        self.drag_offset = (self.rect.x - mx, self.rect.y - my)

    def stop_dragging(self):
        """Stop dragging."""
        self.dragging = False
        self.drag_offset = (0, 0)

    def update_position(self, mx: int, my: int):
        """While dragging, reposition the sprite under the cursor."""
        if self.dragging:
            ox, oy = self.drag_offset
            self.rect.topleft = (mx + ox, my + oy)

    def place(self, coords: list[tuple[int, int]]):
        """
        Finalize placement.
        coords: list of (row, col) grid cells the ship occupies.
        """
        self.coords = coords

    def get_preview_cells(self, offset_x: int, offset_y: int):
        """
        Return the grid cells this ship would occupy based on
        its current screen position & orientation.
        (Unchanged logic from your previous implementation.)
        """
        col = (self.rect.centerx - offset_x) // Config.CELL_SIZE
        row = (self.rect.centery  - offset_y) // Config.CELL_SIZE

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
