# screens/menu_logic.py

import pygame
from core.game_state import GameState
from game.board_helpers import create_board

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

             # Pass and Play button
            if 100 < x < 300 and 410 < y < 460:
                self.start_pass_and_play()

            # Quit button
            if 100 < x < 300 and 480 < y < 530:
                self.quit()

    def start_pass_and_play(self):
        """
        Kick off a local two-player Pass & Play game:
         - flip on pass_play_mode
         - zero out the placement stage
         - allocate two empty boards (ships + attacks)
         - jump into the placing phase
        """
        # 1) Turn on pass & play
        self.state.pass_play_mode   = True

        # 2) We're about to place Player 1 first
        self.state.pass_play_stage  = 0
        self.state.current_player   = 0

        # 3) Build two fresh boards for ships & two for attacks
        self.state.pass_play_boards  = [create_board(), create_board()]
        self.state.pass_play_attacks = [create_board(), create_board()]

        # 4) Switch to the placement screen
        self.state.game_state       = "placing"