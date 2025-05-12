# screens/lobby_render.py

import pygame
from helpers.draw_helpers import draw_text_center, draw_button, draw_text_input_box
from core.config import Config

class LobbyRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        # Title
        draw_text_center(screen, "Multiplayer Lobby", Config.WIDTH//2, 80, 48)
        
        def back():
            if state.history:
                state.skip_push = True
                state.game_state = state.history.pop()
            else:
                state.game_state = "menu (esc)"
        draw_button(screen, "Back", 10, 10, 140, 30,
                    Config.GRAY, Config.DARK_GRAY, back)

        # Host + Join buttons
        draw_button(screen, "Host Game",
                    100, 200, 160, 50,
                    Config.GREEN, Config.DARK_GREEN,
                    lambda: (setattr(self.logic, "mode", "host"),
                             self.logic.start_host()))
        draw_button(screen, "Join Game",
                    100, 300, 160, 50,
                    Config.BLUE, Config.DARK_GRAY,
                    lambda: setattr(self.logic, "mode", "join"))

        # If we have a bound socket, show our own address:port
        if self.logic.host_ip_str:
            draw_text_center(screen,
                             f"Your Address: {self.logic.host_ip_str}",
                             Config.WIDTH//2, 260, 24)

        # If we’re waiting on a client, always show waiting text
        if self.logic.waiting:
            draw_text_center(screen,
                             "Waiting for opponent to connect…",
                             Config.WIDTH//2, 300, 24)

        # Only in join‐mode: show the IP:Port input & connect button
        if self.logic.mode == "join":
            draw_text_center(screen, "Enter IP:Port", Config.WIDTH//2, 340, 24)
            draw_text_input_box(screen, self.logic.ip_input)
            draw_button(screen, "Connect",
                        Config.WIDTH//2 - 80, 380, 160, 40,
                        Config.GREEN, Config.DARK_GREEN,
                        self.logic.start_join)
