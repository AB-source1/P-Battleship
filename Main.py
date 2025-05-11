# Main.py

import pygame
import sys
from core.config            import Config
from core.game_state        import GameState
from screens.menu_logic     import MenuLogic
from screens.menu_render    import MenuRender
from screens.settings_logic import SettingsLogic
from screens.settings_render import SettingsRender
from screens.lobby_logic    import LobbyLogic
from screens.lobby_render   import LobbyRender
from screens.placing_logic  import PlacingLogic
from screens.placing_render import PlacingRender
from screens.playing_logic  import PlayingLogic
from screens.playing_render import PlayingRender
from screens.stats_logic    import StatsLogic
from screens.stats_render   import StatsRender
from helpers.draw_helpers   import draw_modal

# ─── Pygame Initialization ───────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("P-Battleship")
background = pygame.image.load("resources/images/image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))
Config.update_layout()

# ─── GameState & Reset Wiring ────────────────────────────────────────────────
state = GameState(lambda: None)
prev_scene = state.game_state

# ─── Logic & Renderers ───────────────────────────────────────────────────────
menu_logic      = MenuLogic(screen, state)
menu_render     = MenuRender(menu_logic)

settings_logic  = SettingsLogic(screen, state)
settings_render = SettingsRender(settings_logic)

lobby_logic     = LobbyLogic(screen, state)
lobby_render    = LobbyRender(lobby_logic)

placing_logic   = PlacingLogic(screen, state)
placing_render  = PlacingRender(placing_logic)

playing_logic   = PlayingLogic(screen, state)
playing_render  = PlayingRender(playing_logic)

stats_logic     = StatsLogic(screen, state)
stats_render    = StatsRender(stats_logic)

clock = pygame.time.Clock()

def restart_game():
    """
    Reset boards, stats, AI/multiplayer state, and clear networking/lobby UI.
    """
    state.reset_all()
    playing_logic.reset()
    # clear networking so we can host/join again
    state.network   = None
    state.is_host   = False
    # reset lobby UI fields
    lobby_logic.mode        = None
    lobby_logic.waiting     = False
    lobby_logic.ip_input    = ""
    lobby_logic.host_ip_str = ""
    state.local_ready      = False
    state.remote_ready     = False

# ─── Main Loop ────────────────────────────────────────────────────────────────
while True:
    # 1) Update AI/Network logic before handling input
    now = pygame.time.get_ticks()
    if state.game_state == "playing":
        if state.network:
            playing_logic.handle_network_turn(now)
        else:
            playing_logic.handle_ai_turn(now)
    if state.game_state == "placing" and state.network:
        placing_logic.update(state)

    # 2) Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True

        # ─── Handle Esc ────────────────────────────────────────
        # Pressing Esc from any screen always jumps back to the main menu.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state.game_state != "menu":
                state.game_state = "menu"   # Jump straight back
            continue                          # Skip that event for the screen handlers

        # Block input when any modal is visible
        if state.show_restart_modal or state.show_quit_modal:
            continue

        # Dispatch to the current screen’s logic handler
        if   state.game_state == "menu":
            menu_logic.handle_event(event, state)
        elif state.game_state == "lobby":
            lobby_logic.handle_event(event)
        elif state.game_state == "settings":
            settings_logic.handle_event(event)
        elif state.game_state == "placing":
            placing_logic.handle_event(event, state)
        elif state.game_state == "playing":
            playing_logic.handle_event(event, state)
        elif state.game_state == "stats":
            stats_logic.handle_event(event)

    # 3) Reset flags when entering “playing”
    if prev_scene != state.game_state and state.game_state == "playing":
        playing_logic.reset()
    prev_scene = state.game_state

    # 4) Draw background and the active scene
    screen.blit(background, (0, 0))
    if   state.game_state == "menu":
        menu_render.draw(screen, state)
    elif state.game_state == "lobby":
        lobby_render.draw(screen, state)
    elif state.game_state == "settings":
        settings_render.draw(screen, state)
    elif state.game_state == "placing":
        placing_render.draw(screen, state)
    elif state.game_state == "playing":
        playing_render.draw(screen, state)
    elif state.game_state == "stats":
        stats_render.draw(screen, state)

    # 5) Restart confirmation modal
    if state.show_restart_modal:
        def _confirm_restart():
            state.show_restart_modal = False
            restart_game()
        def _cancel_restart():
            state.show_restart_modal = False
        draw_modal(
            screen,
            title="Restart game?",
            subtitle="All progress will be lost.",
            on_yes=_confirm_restart,
            on_no=_cancel_restart
        )
    # 6) Quit confirmation modal
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
    clock.tick(60)

pygame.quit()
sys.exit()
