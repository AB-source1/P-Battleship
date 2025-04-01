import pygame
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos
 
class SettingsScreen:
    def __init__(self,screen,state:GameState):
        self.screen = screen
        self.state = state
    
    def handleEvent(self,event: pygame.event,state:GameState):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and state.user_text.strip():
                state.player_name = state.user_text.strip()
                state.user_text = ""
                state.game_state = "placing"
            elif event.key == pygame.K_BACKSPACE:
                state.user_text = state.user_text[:-1]
            else:
                if len(state.user_text) < 15:
                    state.user_text += event.unicode

        return
   
    def draw(self,screen,state:GameState):
        draw_text_input_box(screen, state.user_text)        

        return
    
