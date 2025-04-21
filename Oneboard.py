import pygame
import random
import sys
from config import Config
from game_state import GameState
from screens.playing import PlayingScreen
from screens.placing import PlacingScreen
from screens.settings import SettingsScreen
from screens.menu import MenuScreen
from board import Cell
from ui import draw_restart_modal  # ✅ NEW

pygame.init()

screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Battleship")
background = pygame.image.load("resources\\images\\image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))

placingScreen = None

def restart_game():
    if placingScreen:
        placingScreen.reset_ship()

state = GameState(restart_game)
placingScreen = PlacingScreen(screen, state)
playingScreen = PlayingScreen(screen, state)
settingsScreen = SettingsScreen(screen, state)
menuScreen = MenuScreen(screen, state)

while state.running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        if state.show_restart_modal:
            continue  # skip normal game input when modal is open

        if state.game_state == "settings":
            settingsScreen.handleEvent(event, state)
        elif state.game_state == "placing":
            placingScreen.handleEvent(event, state)
        elif state.game_state == "playing":
            playingScreen.handleEvent(event, state)

    if state.ai_turn_pending and current_time - state.ai_turn_start_time >= 1000:
        while True:
            r = random.randint(0, Config.GRID_SIZE - 1)
            c = random.randint(0, Config.GRID_SIZE - 1)
            if state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP):
                if state.player_board[r][c] == Cell.SHIP:
                    state.player_board[r][c] = Cell.HIT
                    state.player_ships -= 1
                else:
                    state.player_board[r][c] = Cell.MISS
                break
        state.ai_turn_pending = False

    # Draw current screen
    if state.game_state == "menu":
        menuScreen.draw(screen, state)
    elif state.game_state == "settings":
        settingsScreen.draw(screen, state)
    elif state.game_state == "placing":
        placingScreen.draw(screen, state)
    elif state.game_state == "playing":
        playingScreen.draw(screen, state)

    # Draw modal if active
    if state.show_restart_modal:
        def confirm():
            state.show_restart_modal = False
            state.reset_all()

        def cancel():
            state.show_restart_modal = False

        draw_restart_modal(screen, confirm, cancel)

    pygame.display.flip()

pygame.quit()
sys.exit()
