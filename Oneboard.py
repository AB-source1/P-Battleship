import pygame
import random
import sys
import time
from config import Config
from game_state import GameState
from screens.playing import PlayingScreen
from screens.placing import PlacingScreen
from screens.settings import SettingsScreen
from screens.menu import MenuScreen

pygame.init()

# === Pygame Setup ===
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Battleship")
background = pygame.image.load("resources\\images\\image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))



placingScreen = None

def restart_game():
    print("restarting")
    if placingScreen:
        placingScreen.reset_ship()
    

# === Game State Instance ===
state = GameState(restart_game)
placingScreen = PlacingScreen(screen,state)
playingScreen = PlayingScreen(screen,state)
settingsScreen = SettingsScreen(screen,state)
menuScreen = MenuScreen(screen,state)


# === Main Loop ===
while state.running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        if state.game_state == "settings":
            settingsScreen.handleEvent(event,state)
            
        elif state.game_state == "placing":
            placingScreen.handleEvent(event,state)

        elif state.game_state == "playing": 
            playingScreen.handleEvent(event,state)

    if state.ai_turn_pending and current_time - state.ai_turn_start_time >= 1000:
        while True:
            r, c = random.randint(0, 9), random.randint(0, 9)
            if state.player_board[r][c] in ['O', 'S']:
                if state.player_board[r][c] == 'S':
                    state.player_board[r][c] = 'X'
                    state.player_ships -= 1
                else:
                    state.player_board[r][c] = 'M'
                break
        state.ai_turn_pending = False

    if state.game_state == "menu":
        menuScreen.draw(screen,state)
            
    elif state.game_state == "settings":
        settingsScreen.draw(screen, state)
        
    elif state.game_state == "placing":
       placingScreen.draw(screen, state)
       
    elif state.game_state == "playing":
        playingScreen.draw(screen, state)
        
    pygame.display.flip()

pygame.quit()
sys.exit()