import pygame
import random
import sys
import time
from config import Config
from board import place_ship_randomly
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from game_state import GameState
from util import get_grid_pos
from screens.playing import PlayingScreen
from screens.placing import PlacingScreen

pygame.init()

# === Pygame Setup ===
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Battleship")
background = pygame.image.load("image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))

# === Game State Instance ===
state = GameState()



# === Button Actions ===
def start_game():
    state.game_state = "placing"

def show_settings():
    state.game_state = "settings"

def toggle_orientation():
    state.orientation = 'v' if state.orientation == 'h' else 'h'

def undo_last_ship():
    if state.placed_ships:
        ship = state.placed_ships.pop()
        for row, col in ship:
            state.player_board[row][col] = 'O'
        state.ship_index -= 1

def restart_game():
    state.reset_all()



# === Main Loop ===
while state.running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.running = False

        if state.game_state == "settings":
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

        elif state.game_state == "placing":
            PlacingScreen.handleEvent(event,state)

        elif state.game_state == "playing": 
            PlayingScreen.handleEvent(event,state)

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
        draw_button(screen, "Play", Config.WIDTH // 2 - 75, Config.HEIGHT // 2 - 50, 150, 50, Config.GREEN, Config.DARK_GREEN, start_game)
        draw_button(screen, "Settings", Config.WIDTH // 2 - 75, Config.HEIGHT // 2 + 20, 150, 50, Config.GRAY, Config.DARK_GRAY, show_settings)

    elif state.game_state == "settings":
        draw_text_input_box(screen, state.user_text)

    elif state.game_state == "placing":
        draw_grid(screen, state.player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y, show_ships=True)
        draw_text_center(screen, f"Place ship of length {Config.SHIP_SIZES[state.ship_index]} ({'H' if state.orientation == 'h' else 'V'})", Config.WIDTH // 2, 50)
        draw_button(screen, "Toggle H/V", Config.WIDTH - 160, 50, 140, 40, Config.GRAY, Config.DARK_GRAY, toggle_orientation)
        draw_button(screen, "Undo Last Ship", Config.WIDTH - 160, 100, 140, 40, Config.GRAY, Config.DARK_GRAY, undo_last_ship)

    elif state.game_state == "playing":
        PlayingScreen.draw(screen,state)
        
    pygame.display.flip()

pygame.quit()
sys.exit()