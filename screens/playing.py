import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box, draw_top_bar
from config import Config
from game_state import GameState
from util import get_grid_pos
from board import Cell  # NEW

class PlayingScreen:

    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state

    def handleEvent(self, event: pygame.event, state: GameState):
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not state.ai_turn_pending):

            row, col = get_grid_pos(event.pos, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT)

            if row is not None and state.player_attacks[row][col] == Cell.EMPTY:
                if state.computer_board[row][col] == Cell.SHIP:
                    state.player_attacks[row][col] = Cell.HIT
                    state.computer_board[row][col] = Cell.HIT
                    state.computer_ships -= 1
                else:
                    state.player_attacks[row][col] = Cell.MISS

                state.ai_turn_pending = True
                state.ai_turn_start_time = pygame.time.get_ticks()

        return

    def draw(self, screen, state: GameState):
        draw_top_bar(screen, state)

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
                            f"{state.player_name or 'You'} win! Click Restart",
                            Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart",
                        Config.WIDTH // 2 - 75, Config.HEIGHT // 2,
                        150, 50, Config.GREEN, Config.DARK_GREEN,
                        state.reset_all)

        else:
            # Only draw the boards while the game is still in progress
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


        return
