from helpers.draw_helpers import draw_top_bar, draw_button
from core.config import Config

class MenuRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        draw_top_bar(screen, state)

        draw_button(screen, "Play",
                    Config.WIDTH // 2 - 75, Config.HEIGHT // 2 - 50,
                    150, 50, Config.GREEN, Config.DARK_GREEN,
                    self.logic.start_game)

        draw_button(screen, "Settings",
                    Config.WIDTH // 2 - 75, Config.HEIGHT // 2 + 20,
                    150, 50, Config.GRAY, Config.DARK_GRAY,
                    self.logic.show_settings)
