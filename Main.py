# Main.py

import pygame
import sys
from core.config           import Config
from core.game_state       import GameState
from screens.menu_logic    import MenuLogic
from screens.menu_render   import MenuRender
from screens.settings_logic import SettingsLogic
from screens.settings_render import SettingsRender
from screens.placing_logic import PlacingLogic
from screens.placing_render import PlacingRender
from screens.playing_logic import PlayingLogic
from screens.playing_render import PlayingRender
from screens.stats_logic   import StatsLogic
from screens.stats_render  import StatsRender
from helpers.draw_helpers  import draw_modal

# ─── Pygame & Window Setup ───
pygame.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("P-Battleship")
background = pygame.image.load("resources/images/image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))
Config.update_layout()

# ─── 1) Create GameState with a dummy reset callback ───
# We’ll override state.reset_callback once placing_logic exists.
def _initial_reset():
    # no-op on startup
    pass

state = GameState(_initial_reset)

# ─── 2) Instantiate the placement screen & then wire the reset callback ───
placing_logic  = PlacingLogic(screen, state)
placing_render = PlacingRender(placing_logic)

# Now that placing_logic.reset() exists, have GameState call it on every reset_all()
state.reset_callback = placing_logic.reset

# ─── 3) Instantiate the rest of your screens ───
menu_logic      = MenuLogic(screen, state)
menu_render     = MenuRender(menu_logic)

settings_logic  = SettingsLogic(screen, state)
settings_render = SettingsRender(settings_logic)

playing_logic   = PlayingLogic(screen, state)
playing_render  = PlayingRender(playing_logic)

stats_logic     = StatsLogic(screen, state)
stats_render    = StatsRender(stats_logic)

# ─── 4) Define a standalone restart helper to clear boards & AI ───
def restart_game():
    # ① Reset boards & ships (this calls placing_logic.reset via callback)
    state.reset_all()
    # ② Reset the AI’s internal hunt‐and‐destroy state
    playing_logic.reset()

# ─── Main Loop ───
while state.running:
    screen.blit(background, (0, 0))
    now = pygame.time.get_ticks()

    # ─── Handle events ───
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True

        # Block input when any modal is showing
        if state.show_restart_modal or state.show_quit_modal:
            continue

        # Delegate to the active screen
        if   state.game_state == "menu":     menu_logic.handle_event(event, state)
        elif state.game_state == "settings": settings_logic.handle_event(event)
        elif state.game_state == "placing":  placing_logic.handle_event(event, state)
        elif state.game_state == "playing":  playing_logic.handle_event(event, state)
        elif state.game_state == "stats":    stats_logic.handle_event(event)

    # ─── AI Turn in “playing” ───
    if state.game_state == "playing":
        playing_logic.handle_ai_turn(now)

    # ─── Draw the active screen ───
    if   state.game_state == "menu":     menu_render.draw(screen, state)
    elif state.game_state == "settings": settings_render.draw(screen, state)
    elif state.game_state == "placing":  placing_render.draw(screen, state)
    elif state.game_state == "playing":  playing_render.draw(screen, state)
    elif state.game_state == "stats":    stats_render.draw(screen, state)

    # ─── Restart Modal ───
    if state.show_restart_modal:
        def _confirm_restart():
            state.show_restart_modal = False
            restart_game()   # <— call our helper, not state.reset_all() directly
        def _cancel_restart():
            state.show_restart_modal = False

        draw_modal(
            screen,
            title="Restart game?",
            subtitle="All progress will be lost.",
            on_yes=_confirm_restart,
            on_no=_cancel_restart
        )

    # ─── Quit Modal ───
    elif state.show_quit_modal:
        def _confirm_quit():
            pygame.quit()
            sys.exit()
        def _cancel_quit():
            state.show_quit_modal = False

        draw_modal(
            screen,
            title="Quit game?",
            subtitle="Are you sure you want to exit?",
            on_yes=_confirm_quit,
            on_no=_cancel_quit
        )

    pygame.display.flip()

pygame.quit()
sys.exit()
