import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos
 
class MenuScreen:
    def __init__(self,screen,state:GameState):
        self.screen = screen
        self.state = state
 
    def start_game(self):
        self.state.game_state = "placing"

    def show_settings(self):
        self.state.game_state = "settings"
    
    def handleEvent(self,event: pygame.event,state:GameState):
        
        return
   
    def draw(self,screen,state:GameState):
        draw_button(screen, "Play", Config.WIDTH // 2 - 75, Config.HEIGHT // 2 - 50, 150, 50, Config.GREEN, Config.DARK_GREEN, self.start_game)
        draw_button(screen, "Settings", Config.WIDTH // 2 - 75, Config.HEIGHT // 2 + 20, 150, 50, Config.GRAY, Config.DARK_GRAY, self.show_settings)

        return
    
