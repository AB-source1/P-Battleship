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
from ui import draw_modal  # ✅ Unified modal drawer

pygame.init()

screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Battleship")
background = pygame.image.load("resources\\images\\image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))

placingScreen = None

Config.update_layout()

def restart_game():
    if placingScreen:
        placingScreen.reset_ship()

state = GameState(restart_game)
placingScreen = PlacingScreen(screen, state)
playingScreen = PlayingScreen(screen, state)
settingsScreen = SettingsScreen(screen, state)
menuScreen = MenuScreen(screen, state)

# ──────────────────────────────────────────────────────────────────────────
while state.running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True  # ✅ Confirm on close button

        if state.show_restart_modal or state.show_quit_modal:
            continue  # ✅ Pause input to screens while modal is open

        if state.game_state == "settings":
            settingsScreen.handleEvent(event, state)
        elif state.game_state == "placing":
            placingScreen.handleEvent(event, state)
        elif state.game_state == "playing":
            playingScreen.handleEvent(event, state)

    # ───────────────────── AI TURN ─────────────────────
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

    # ───────────────────── DRAW ACTIVE SCREEN ─────────────────────
    if state.game_state == "menu":
        menuScreen.draw(screen, state)
    elif state.game_state == "settings":
        settingsScreen.draw(screen, state)
    elif state.game_state == "placing":
        placingScreen.draw(screen, state)
    elif state.game_state == "playing":
        playingScreen.draw(screen, state)

    # ───────────────────── MODALS ─────────────────────
    if state.show_restart_modal:
        def confirm_restart():
            state.show_restart_modal = False
            state.reset_all()

        def cancel_restart():
            state.show_restart_modal = False

        draw_modal(screen,
                   title="Restart game?",
                   subtitle="All progress will be lost.",
                   on_yes=confirm_restart,
                   on_no=cancel_restart)

    elif state.show_quit_modal:
        def confirm_quit():
            state.show_quit_modal = False
            pygame.quit()
            sys.exit()

        def cancel_quit():
            state.show_quit_modal = False

        draw_modal(screen,
                   title="Quit game?",
                   subtitle="Are you sure you want to exit?",
                   on_yes=confirm_quit,
                   on_no=cancel_quit)

    pygame.display.flip()

pygame.quit()
sys.exit()
