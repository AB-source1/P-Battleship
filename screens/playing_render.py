import pygame
from helpers.draw_helpers import draw_top_bar, draw_grid, draw_text_center, draw_button
from core.config import Config

class PlayingRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        draw_top_bar(screen, state)

        start = getattr(state, 'play_start_time', 0)
        elapsed_ms = pygame.time.get_ticks() - start
        elapsed_s  = elapsed_ms // 1000
        mins, secs = divmod(elapsed_s, 60)
        timer_str  = f"{mins:02d}:{secs:02d}"
        # Position it in the upper‐right, vertically centered in the bar
        timer_x = Config.WIDTH - 280
        
        draw_text_center(
            screen,
            timer_str,
            timer_x,
            Config.TOP_BAR_HEIGHT // 2,
            24
        )

        if state.player_ships == 0:
            draw_text_center(screen,
                            f"{state.player_name or 'You'} lost! Click Restart",
                            Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart",
                        Config.WIDTH // 2 - 75, Config.HEIGHT // 2,
                        150, 50, Config.GREEN, Config.DARK_GREEN,
                        state.reset_all)

        elif state.computer_ships == 0:
            draw_text_center(screen,
                            f"{state.player_name or 'You'} won! Click Restart",
                            Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart",
                        Config.WIDTH // 2 - 75, Config.HEIGHT // 2,
                        150, 50, Config.GREEN, Config.DARK_GREEN,
                        state.reset_all)

        else:
            draw_text_center(screen, "Your Fleet",
                            Config.BOARD_OFFSET_X + Config.GRID_WIDTH // 2,
                            Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT)

            draw_text_center(screen, "Enemy Waters",
                            Config.ENEMY_OFFSET_X + Config.GRID_WIDTH // 2,
                            Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT)

            draw_grid(screen, state.player_board,
                      Config.BOARD_OFFSET_X,
                      Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                      show_ships=True)

            draw_grid(screen, state.player_attacks,
                      Config.ENEMY_OFFSET_X,
                      Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT)

            draw_text_center(screen,
                            f"Admiral {state.player_name}",
                            100, 20 + Config.TOP_BAR_HEIGHT)
