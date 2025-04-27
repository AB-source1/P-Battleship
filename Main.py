import pygame
import sys
from core.config import Config
from core.game_state import GameState
from screens.placing_logic import PlacingLogic
from screens.placing_render import PlacingRender
from screens.playing_logic import PlayingLogic
from screens.playing_render import PlayingRender
from screens.settings_logic import SettingsLogic
from screens.settings_render import SettingsRender
from screens.menu_logic import MenuLogic
from screens.menu_render import MenuRender
from helpers.draw_helpers import draw_modal

pygame.init()

# Setup
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("P-Battleship")
background = pygame.image.load("resources/images/image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))

Config.update_layout()

# Temporary function that will be updated later
def dummy_restart_game():
    pass

# Create state first with dummy restart
state = GameState(dummy_restart_game)

# Initialize all screens
placing_logic = PlacingLogic(screen, state)
placing_render = PlacingRender(placing_logic)

playing_logic = PlayingLogic(screen, state)
playing_render = PlayingRender(playing_logic)

settings_logic = SettingsLogic(screen, state)
settings_render = SettingsRender(settings_logic)

menu_logic = MenuLogic(screen, state)
menu_render = MenuRender(menu_logic)

# Now fix real restart function
def restart_game():
    placing_logic.reset_ships()

state.reset_callback = restart_game  # Update GameState to use correct restart

# ──────────────────────────────────────────────────────────────────────────
# Main Loop
while state.running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True

        if state.show_restart_modal or state.show_quit_modal:
            continue  # Pause input while modal open

        # Handle events by active logic
        if state.game_state == "menu":
            menu_logic.handle_event(event, state)
        elif state.game_state == "settings":
            settings_logic.handle_event(event)
        elif state.game_state == "placing":
            placing_logic.handle_event(event, state)
        elif state.game_state == "playing":
            playing_logic.handle_event(event, state)

    # AI turn logic
    if state.game_state == "playing":
        playing_logic.handle_ai_turn(current_time)

    # Draw correct screen
    if state.game_state == "menu":
        menu_render.draw(screen, state)
    elif state.game_state == "settings":
        settings_render.draw(screen, state)
    elif state.game_state == "placing":
        placing_render.draw(screen, state)
    elif state.game_state == "playing":
        playing_render.draw(screen, state)

    # Modal dialogs
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
