import pygame
from helpers.draw_helpers import draw_top_bar, draw_grid, draw_text_center, draw_button
from core.config import Config

class PlayingRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        draw_top_bar(screen, state)

        score_str = f"Score: {state.score}"
        draw_text_center(
            screen,
            score_str,
            Config.WIDTH  // 2,
            Config.TOP_BAR_HEIGHT + 20,
            font_size=24
        )

        # ─── NEW: draw elapsed play-time as MM:SS ───────────────
        if state.timer_start is not None:
            # milliseconds since play began
            elapsed_ms = pygame.time.get_ticks() - state.timer_start
            total_sec = elapsed_ms // 1000
            mins, secs = divmod(total_sec, 60)
            timer_str = f"{mins:02d}:{secs:02d}"
            # center it in the top bar (adjust font_size as needed)
            draw_text_center(
                screen,
                timer_str,
                Config.WIDTH // 2,
                Config.TOP_BAR_HEIGHT // 2,
                font_size=24
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

                        # draw the grid without the default blue‐ship squares
            draw_grid(
                screen,
                state.player_board,
                Config.BOARD_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                show_ships=False
            )

            # overlay each placed ship’s image sprite
            for ship in getattr(state, 'placed_ships', []):
                # find its top-left grid cell
                rows = [r for r, c in ship.coords]
                cols = [c for r, c in ship.coords]
                row0, col0 = min(rows), min(cols)

                # compute pixel position on the playing board
                x = Config.BOARD_OFFSET_X + col0 * Config.CELL_SIZE
                y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + row0 * Config.CELL_SIZE

                # blit the ship sprite exactly as it was placed
                screen.blit(ship.image, (x, y))

            draw_grid(screen, state.player_attacks,
                      Config.ENEMY_OFFSET_X,
                      Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT)

            draw_text_center(screen,
                            f"Admiral {state.player_name}",
                            100, 20 + Config.TOP_BAR_HEIGHT)
