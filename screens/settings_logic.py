
import pygame
from core.config import Config
from core.game_state import GameState

"""
Module: settings_logic.py
Purpose:
  - Pygame event handling for Settings screen: grid size, custom input, and difficulty.
  - Validates and applies user inputs, toggles between presets/custom UI.
Future Hooks:
  - Broadcast applied settings to network peer.
"""

class SettingsLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state
        self.grid_size_input = ""
        self.show_custom_input = False

    def handle_event(self, event: pygame.event.Event):
        """Capture keyboard/mouse for preset selection, custom input, toggles."""
        if self.show_custom_input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.apply_custom_size()
                elif event.key == pygame.K_BACKSPACE:
                    self.grid_size_input = self.grid_size_input[:-1]
                elif event.unicode.isdigit():
                    if len(self.grid_size_input) < 2:
                        self.grid_size_input += event.unicode

    def apply_grid_size(self, size: int):
        """Apply a preset grid size and update layout immediately."""
        Config.GRID_SIZE = size
        Config.update_layout()
        

    def apply_custom_size(self):
        """Validate custom grid-size input, then apply if within acceptable range."""
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
        """Switch between preset buttons and custom text input UI."""
        self.show_custom_input = not self.show_custom_input
        self.grid_size_input = ""
    
    def apply_difficulty(self, level: str):
        """Set AI difficulty level in game state."""
        self.state.difficulty = level
        
