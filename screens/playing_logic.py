import pygame
from core.config import Config
from core.game_state import GameState
from game.board_helpers import Cell, get_grid_pos

class PlayingLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state

    def handle_event(self, event: pygame.event.Event, state: GameState):
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not state.ai_turn_pending):

            row, col = get_grid_pos(event.pos, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT)

            if row is not None and col is not None and state.player_attacks[row][col] == Cell.EMPTY:
                if state.computer_board[row][col] == Cell.SHIP:
                    state.player_attacks[row][col] = Cell.HIT
                    state.computer_board[row][col] = Cell.HIT
                    state.computer_ships -= 1
                else:
                    state.player_attacks[row][col] = Cell.MISS

                state.ai_turn_pending = True
                state.ai_turn_start_time = pygame.time.get_ticks()

    def handle_ai_turn(self, current_time):
        if self.state.ai_turn_pending and current_time - self.state.ai_turn_start_time >= 1000:
            from random import randint

            while True:
                r = randint(0, Config.GRID_SIZE - 1)
                c = randint(0, Config.GRID_SIZE - 1)
                if self.state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP):
                    if self.state.player_board[r][c] == Cell.SHIP:
                        self.state.player_board[r][c] = Cell.HIT
                        self.state.player_ships -= 1
                    else:
                        self.state.player_board[r][c] = Cell.MISS
                    break

            self.state.ai_turn_pending = False
