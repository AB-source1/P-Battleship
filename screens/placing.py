import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos
 
class PlacingScreen:
    def __init__(self,screen,state:GameState):
        self.screen = screen
        self.state = state
        self.orientation = 'h'
        
    def toggle_orientation(self):
        self.orientation = 'v' if self.orientation == 'h' else 'h'

    def undo_last_ship(self):
        if self.state.placed_ships:
            ship = self.state.placed_ships.pop()
            for row, col in ship:
                self.state.player_board[row][col] = 'O'
            self.state.ship_index -= 1

    
    def handleEvent(self,event: pygame.event,state:GameState):
       if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            row, col = get_grid_pos(event.pos, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row is not None and state.ship_index < len(Config.SHIP_SIZES):
                size = Config.SHIP_SIZES[state.ship_index]
                coords = []
                fits = True
                if self.orientation == 'h':
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
   
    def draw(self,screen,state:GameState):
        
        draw_grid(screen, state.player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y, show_ships=True)
        draw_text_center(screen, f"Place ship of length {Config.SHIP_SIZES[state.ship_index]} ({'H' if self.orientation == 'h' else 'V'})", Config.WIDTH // 2, 50)
        draw_button(screen, "Toggle H/V", Config.WIDTH - 160, 50, 140, 40, Config.GRAY, Config.DARK_GRAY, self.toggle_orientation)
        draw_button(screen, "Undo Last Ship", Config.WIDTH - 160, 100, 140, 40, Config.GRAY, Config.DARK_GRAY, self.undo_last_ship)

        return
    
