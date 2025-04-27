import pygame
from core.config import Config
from core.game_state import GameState

class SettingsLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state
        self.grid_size_input = ""
        self.show_custom_input = False

    def handle_event(self, event: pygame.event.Event):
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

    def toggle_custom_input(self):
        self.show_custom_input = not self.show_custom_input
        self.grid_size_input = ""
