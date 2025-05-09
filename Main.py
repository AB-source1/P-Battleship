import pygame
import sys
from core.config          import Config
from core.game_state      import GameState
from screens.menu_logic   import MenuLogic
from screens.menu_render  import MenuRender
from screens.settings_logic import SettingsLogic
from screens.settings_render import SettingsRender
from screens.placing_logic import PlacingLogic
from screens.placing_render import PlacingRender
from screens.playing_logic import PlayingLogic
from screens.playing_render import PlayingRender
from screens.stats_logic  import StatsLogic
from screens.stats_render import StatsRender
from helpers.draw_helpers import draw_modal

# ─── Pygame init ───
pygame.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("P-Battleship")
background = pygame.image.load("resources/images/image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))
Config.update_layout()

# ─── Stub reset (to be replaced below) ───
def dummy_restart():
    pass

state = GameState(dummy_restart)

# ─── Instantiate all screens ───
menu_logic     = MenuLogic(screen, state)
menu_render    = MenuRender(menu_logic)

settings_logic = SettingsLogic(screen, state)
settings_render= SettingsRender(settings_logic)

placing_logic  = PlacingLogic(screen, state)
placing_render = PlacingRender(placing_logic)

playing_logic  = PlayingLogic(screen, state)
playing_render = PlayingRender(playing_logic)

stats_logic    = StatsLogic(screen, state)
stats_render   = StatsRender(stats_logic)

# ─── Real restart: clear boards, AI, stats ───
def restart_game():
    placing_logic.reset()  # clear & re-place ships
    playing_logic.reset()  # clear AI hunt/destroy
    state.reset_all()      # clear boards & stats

state.reset_callback = restart_game

# ─── Main Loop ───
while state.running:
    screen.blit(background, (0, 0))
    now = pygame.time.get_ticks()

    # ─── Event Handling ───
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True

        # Pause input when modal is up
        if state.show_restart_modal or state.show_quit_modal:
            continue

        # Delegate to current scene
        if   state.game_state == "menu":     menu_logic.handle_event(event, state)
        elif state.game_state == "settings": settings_logic.handle_event(event)
        elif state.game_state == "placing":  placing_logic.handle_event(event, state)
        elif state.game_state == "playing":  playing_logic.handle_event(event, state)
        elif state.game_state == "stats":    stats_logic.handle_event(event)

    # ─── AI Turn ───
    if state.game_state == "playing":
        playing_logic.handle_ai_turn(now)

    # ─── Drawing ───
    if   state.game_state == "menu":     menu_render.draw(screen, state)
    elif state.game_state == "settings": settings_render.draw(screen, state)
    elif state.game_state == "placing":  placing_render.draw(screen, state)
    elif state.game_state == "playing":  playing_render.draw(screen, state)
    elif state.game_state == "stats":    stats_render.draw(screen, state)

    # ─── Restart Modal ───
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

    # ─── Quit Modal ───
    elif state.show_quit_modal:
        def confirm_quit():
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
