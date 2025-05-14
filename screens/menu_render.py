# screens/menu_render.py

import pygame
from helpers.draw_helpers import draw_text_center, draw_button
from core.config import Config

class MenuRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        
       

        # Single-player Play
        draw_button(screen, "Play",
                    100, 200, 200, 50,
                    (255, 204, 0), (200, 160, 0),
                    self.logic.start_game)

        # Settings
        draw_button(screen, "Settings",
                    100, 270, 200, 50,
                    (255, 204, 0), (200, 160, 0),
                    self.logic.open_settings)

        # Multiplayer (new)
        draw_button(screen, "Multiplayer",
                    100, 340, 200, 50,
                    (255, 204, 0), (200, 160, 0),
                    self.logic.go_to_lobby)

        # Quit
        draw_button(screen, "Quit",
                    100, 410, 200, 50,
                    (255, 204, 0), (200, 160, 0),
                    self.logic.quit)