import pygame
from ui import draw_text_center, draw_button, draw_text_input_box, draw_top_bar
from config import Config
from game_state import GameState


class SettingsScreen:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state
        self.grid_size_input = ""
        self.show_custom_input = False

    def handleEvent(self, event: pygame.event.Event, state: GameState):
        if self.show_custom_input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.apply_custom_size()
                elif event.key == pygame.K_BACKSPACE:
                    self.grid_size_input = self.grid_size_input[:-1]
                elif event.unicode.isdigit():
                    if len(self.grid_size_input) < 2:
                        self.grid_size_input += event.unicode

    def apply_grid_size(self, size):
        Config.GRID_SIZE = size
        Config.update_layout()
        self.state.reset_all()

    def apply_custom_size(self):
        try:
            val = int(self.grid_size_input)
            if 5 <= val <= 20:
                self.apply_grid_size(val)
            else:
                print("Grid size must be between 5 and 20")
        except ValueError:
            print("Invalid input for grid size")
        self.grid_size_input = ""
        self.show_custom_input = False

    def draw(self, screen, state: GameState):
        draw_top_bar(screen, state)

        draw_text_center(screen, "Select Grid Size", Config.WIDTH // 2, 80, 40)

        # Preset buttons
        draw_button(screen, "5x5", Config.WIDTH // 2 - 200, 150, 100, 40,
            Config.GRAY, Config.DARK_GRAY, lambda: self.apply_grid_size(5))

        draw_button(screen, "10x10", Config.WIDTH // 2 - 50, 150, 100, 40,
                    Config.GRAY, Config.DARK_GRAY, lambda: self.apply_grid_size(10))

        draw_button(screen, "15x15", Config.WIDTH // 2 + 100, 150, 100, 40,
                    Config.GRAY, Config.DARK_GRAY, lambda: self.apply_grid_size(15))


        # Custom size logic
        draw_button(screen, "Custom", Config.WIDTH // 2 - 75, 220, 150, 40,
                    Config.GREEN, Config.DARK_GREEN, self.toggle_custom_input)

        if self.show_custom_input:
            draw_text_center(screen, "Enter size (5-20):", Config.WIDTH // 2, 280, 24)
            draw_text_input_box(screen, self.grid_size_input)

    def toggle_custom_input(self):
        self.show_custom_input = not self.show_custom_input
        self.grid_size_input = ""
