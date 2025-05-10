# screens/menu_logic.py

import pygame
from core.game_state import GameState

class MenuLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state  = state

    def start_game(self):
        self.state.game_state = "placing"

    def open_settings(self):
        self.state.game_state = "settings"

    def go_to_lobby(self):
        """Switch into the multiplayer lobby scene."""
        self.state.game_state = "lobby"

    def quit(self):
        self.state.show_quit_modal = True

    def handle_event(self, event: pygame.event.Event, state: GameState):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos

            # Play button (example coords)
            if 100 < x < 300 and 200 < y < 250:
                self.start_game()

            # Settings button
            if 100 < x < 300 and 270 < y < 320:
                self.open_settings()

            # Multiplayer button
            if 100 < x < 300 and 340 < y < 390:
                self.go_to_lobby()

            # Quit button
            if 100 < x < 300 and 410 < y < 460:
                self.quit()
