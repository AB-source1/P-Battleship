import pygame
from helpers.draw_helpers import draw_top_bar, draw_text_center, draw_button, draw_text_input_box
from core.config import Config

class SettingsRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        draw_top_bar(screen, state)

        draw_text_center(screen, "Select Grid Size", Config.WIDTH // 2, 80, 40)

        if not self.logic.show_custom_input:
            draw_button(screen, "5x5", Config.WIDTH // 2 - 200, 150, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, lambda: self.logic.apply_grid_size(5))

            draw_button(screen, "10x10", Config.WIDTH // 2 - 50, 150, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, lambda: self.logic.apply_grid_size(10))

            draw_button(screen, "15x15", Config.WIDTH // 2 + 100, 150, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, lambda: self.logic.apply_grid_size(15))

            draw_button(screen, "Custom", Config.WIDTH // 2 - 75, 220, 150, 40,
                        Config.GREEN, Config.DARK_GREEN, self.logic.toggle_custom_input)

        else:
            draw_text_center(screen, "Enter size (5-20):", Config.WIDTH // 2, 280, 24)
            draw_text_input_box(screen, self.logic.grid_size_input)

            draw_button(screen, "Back", Config.WIDTH // 2 - 50, 350, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, self.logic.toggle_custom_input)
