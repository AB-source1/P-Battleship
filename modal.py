import sys 
import pygame
from functools import partial # new <----- figure this out
from config import Config
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box, draw_top_bar

class Modal:
    """Simple blocking dialog with custom message & 2 buttons."""

    WIDTH, HEIGHT = 420, 190

    def __init__(self, prompt: str, on_yes, on_no):
        self.prompt = prompt
        self.on_yes = on_yes
        self.on_no  = on_no

        # pre‑compute rects so we can also use them for hit‑testing
        self.box_rect = pygame.Rect(
            (Config.WIDTH  - self.WIDTH)  // 2,
            (Config.HEIGHT - self.HEIGHT) // 2,
            self.WIDTH, self.HEIGHT
        )
        # Yes / No button rectangles
        self.yes_rect = pygame.Rect(self.box_rect.x + 60,
                                    self.box_rect.y + 120, 110, 40)
        self.no_rect  = pygame.Rect(self.box_rect.right - 170,
                                    self.box_rect.y + 120, 110, 40)

    # ── drawing ────────────────────────────────────────────────
    def draw(self, screen):
        # dark overlay
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # dialog box
        pygame.draw.rect(screen, Config.DARK_GRAY, self.box_rect)
        pygame.draw.rect(screen, Config.WHITE,     self.box_rect, 3)

        draw_text_center(screen, self.prompt,
                         self.box_rect.centerx, self.box_rect.y + 50, 28)
        draw_text_center(screen, "All progress will be lost.",
                         self.box_rect.centerx, self.box_rect.y + 85, 22)

        draw_button(screen, "Yes", *self.yes_rect, Config.GREEN, Config.DARK_GREEN)
        draw_button(screen, "No",  *self.no_rect,  Config.RED,   Config.DARK_GRAY)

    # ── event handling ─────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.yes_rect.collidepoint(event.pos):
                self.on_yes()
            elif self.no_rect.collidepoint(event.pos):
                self.on_no()