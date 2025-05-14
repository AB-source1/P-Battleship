import pygame
from helpers.draw_helpers import draw_top_bar, draw_text_center, draw_button, draw_text_input_box
from core.config import Config

class SettingsRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        draw_top_bar(screen, state)

        def back():
            if state.history:
                state.skip_push = True
                state.game_state = state.history.pop()
            else:
                state.game_state = "menu"
        draw_button(screen, "Back (esc)", 10, Config.TOP_BAR_HEIGHT + 5, 140, 30,
                    Config.GRAY, Config.DARK_GRAY, back,3)

        draw_text_center(screen, "Select Grid Size", Config.WIDTH // 2, 80, 40)

        if not self.logic.show_custom_input:
            draw_button(screen, "5x5", Config.WIDTH // 2 - 200, 150, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, lambda: self.logic.apply_grid_size(5),3)

            draw_button(screen, "10x10", Config.WIDTH // 2 - 50, 150, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, lambda: self.logic.apply_grid_size(10),3)

            draw_button(screen, "15x15", Config.WIDTH // 2 + 100, 150, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, lambda: self.logic.apply_grid_size(15),3)

            draw_button(screen, "Custom", Config.WIDTH // 2 - 75, 220, 150, 40,
                        Config.GREEN, Config.DARK_GREEN, self.logic.toggle_custom_input,3)

            # 🛠 NEW: Smart ship generator toggle
            smart_label = "Smart Ships: ON" if Config.USE_SMART_SHIP_GENERATOR else "Smart Ships: OFF"
            draw_button(screen, smart_label, Config.WIDTH // 2 - 100, 300, 200, 40,
                        Config.GREEN if Config.USE_SMART_SHIP_GENERATOR else Config.GRAY,
                        Config.DARK_GREEN if Config.USE_SMART_SHIP_GENERATOR else Config.DARK_GRAY,
                        self.toggle_smart_ship_generator,3)
            
            draw_text_center(screen, "AI Difficulty", Config.WIDTH // 2, 380, 28)
            for i, level in enumerate(Config.DIFFICULTIES):
                x = Config.WIDTH // 2 - 150 + i * 150
                is_selected = (state.difficulty == level)
                draw_button(
                    screen, level,
                    x, 420, 140, 40,
                    Config.GREEN if is_selected else Config.GRAY,
                    Config.DARK_GREEN if is_selected else Config.DARK_GRAY,
                    lambda lvl=level: self.logic.apply_difficulty(lvl),3
                )

        else:
            draw_text_center(screen, "Enter size (5-20):", Config.WIDTH // 2, 280, 24)
            draw_text_input_box(screen, self.logic.grid_size_input)

            draw_button(screen, "Back", Config.WIDTH // 2 - 50, 350, 100, 40,
                        Config.GRAY, Config.DARK_GRAY, self.logic.toggle_custom_input,3)

    def toggle_smart_ship_generator(self):
        Config.USE_SMART_SHIP_GENERATOR = not Config.USE_SMART_SHIP_GENERATOR
        Config.generate_ships_for_grid()
