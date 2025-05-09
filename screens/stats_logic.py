import pygame
from core.game_state import GameState

class StatsLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state  = state

    def play_again(self):
        """
        Clear boards & stats, then go back to placing ships.
        """
        self.state.reset_all()
        self.state.game_state = "placing"

    def to_menu(self):
        """
        Clear boards & stats, then return to the main menu.
        """
        self.state.reset_all()
        self.state.game_state = "menu"

    def handle_event(self, event: pygame.event.Event):
        # Buttons are handled via their callbacks in StatsRender
        pass
