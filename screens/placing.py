import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos
 
class PlacingScreen:
    def handleEvent(event: pygame.event,state:GameState):
       if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            row, col = get_grid_pos(event.pos, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row is not None and state.ship_index < len(Config.SHIP_SIZES):
                size = Config.SHIP_SIZES[state.ship_index]
                coords = []
                fits = True
                if state.orientation == 'h':
                    if col + size > Config.GRID_SIZE:
                        fits = False
                    else:
                        for i in range(size):
                            if state.player_board[row][col + i] != 'O':
                                fits = False
                                break
                        if fits:
                            for i in range(size):
                                state.player_board[row][col + i] = 'S'
                                coords.append((row, col + i))
                else:
                    if row + size > Config.GRID_SIZE:
                        fits = False
                    else:
                        for i in range(size):
                            if state.player_board[row + i][col] != 'O':
                                fits = False
                                break
                        if fits:
                            for i in range(size):
                                state.player_board[row + i][col] = 'S'
                                coords.append((row + i, col))
                if fits:
                    state.placed_ships.append(coords)
                    state.ship_index += 1
                    if state.ship_index == len(Config.SHIP_SIZES):
                        state.game_state = "playing"
                        state.player_ships = state.count_ships(state.player_board)
       return
   
    def draw(screen,state:GameState):
        return
    
