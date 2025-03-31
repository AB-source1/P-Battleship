import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos
 
class PlayingScreen:
    def handleEvent(event: pygame.event,state:GameState):
        if  event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not state.ai_turn_pending:
            row, col = get_grid_pos(event.pos, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row is not None and state.player_attacks[row][col] == '':
                if state.computer_board[row][col] == 'S':
                    state.player_attacks[row][col] = 'X'
                    state.computer_board[row][col] = 'X'
                    state.computer_ships -= 1
                else:
                    state.player_attacks[row][col] = 'M'
                state.ai_turn_pending = True
                state.ai_turn_start_time = pygame.time.get_ticks() # current time
        return
    
    def draw(screen,state:GameState):
        draw_text_center(screen, "Your Fleet", Config.BOARD_OFFSET_X + Config.GRID_WIDTH // 2, Config.BOARD_OFFSET_Y - 30)
        draw_text_center(screen, "Enemy Waters", Config.ENEMY_OFFSET_X + Config.GRID_WIDTH // 2, Config.BOARD_OFFSET_Y - 30)
        draw_grid(screen, state.player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y, show_ships=True)
        draw_grid(screen, state.player_attacks, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y)
        draw_text_center(screen, f"Admiral {state.player_name}", 100, 20)
        if state.computer_ships == 0:
            draw_text_center(screen, f"{state.player_name or 'You'} win! Click Restart", Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart", Config.WIDTH // 2 - 75, Config.HEIGHT // 2, 150, 50, Config.GREEN, Config.DARK_GREEN, restart_game)
        elif state.player_ships == 0:
            draw_text_center(screen, f"{state.player_name or 'You'} lost! Click Restart", Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart", Config.WIDTH // 2 - 75, Config.HEIGHT // 2, 150, 50, Config.GREEN, Config.DARK_GREEN, restart_game)

        return