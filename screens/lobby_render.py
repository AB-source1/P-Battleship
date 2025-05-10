# screens/lobby_render.py

import pygame
from helpers.draw_helpers import (
    draw_text_center,
    draw_button,
    draw_text_input_box
)
from core.config import Config

class LobbyRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        # Title
        draw_text_center(screen, "Multiplayer Lobby",
                         Config.WIDTH//2, 80, 48)

        # Host Game button
        draw_button(screen, "Host Game",
                    100, 200, 160, 50,
                    Config.GREEN, Config.DARK_GREEN,
                    lambda: setattr(self.logic, "mode", "host"))

        # Join Game button
        draw_button(screen, "Join Game",
                    100, 300, 160, 50,
                    Config.BLUE, Config.DARK_GRAY,
                    lambda: setattr(self.logic, "mode", "join"))

        # Join-mode: label, input box & Connect button
        if self.logic.mode == "join":
            draw_text_center(screen, "Host IP:", 180, 340, 24)
            # Only two args: screen and the current text
            draw_text_input_box(screen, self.logic.ip_input)
            draw_button(screen, "Connect",
                        100, 380, 160, 40,
                        Config.GREEN, Config.DARK_GREEN,
                        self.logic.start_join)

        # Host-mode waiting: show IP + waiting message
        if self.logic.mode == "host" and self.logic.waiting:
            # Show the host IP for sharing
            draw_text_center(screen,
                             f"Your IP: {self.logic.host_ip_str}",
                             Config.WIDTH//2, 260, 24)
            draw_text_center(screen,
                             "Waiting for player to connect…",
                             Config.WIDTH//2, 300, 24)
