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
placing_logic  = PlacingLogic(screen, state)
placing_render = PlacingRender(placing_logic)
state.reset_callback = placing_logic.reset
# Now state.reset_all() will call placing_logic.reset() for ship placement

menu_logic      = MenuLogic(screen, state)
menu_render     = MenuRender(menu_logic)

settings_logic  = SettingsLogic(screen, state)
settings_render = SettingsRender(settings_logic)

lobby_logic     = LobbyLogic(screen, state)
lobby_render    = LobbyRender(lobby_logic)

playing_logic   = PlayingLogic(screen, state)
playing_render  = PlayingRender(playing_logic)

stats_logic     = StatsLogic(screen, state)
stats_render    = StatsRender(stats_logic)

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
    state.waiting_for_sync = False
    state.opponent_left    = False

prev_scene = state.game_state
clock = pygame.time.Clock()

# ─── Main Loop ────────────────────────────────────────────────────────────────
while state.running:
    now = pygame.time.get_ticks()

    # 1) Turn logic first so `my_turn` is updated before click handling
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

        # block input when any modal is visible
        if state.show_restart_modal or state.show_quit_modal:
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state.history:
                # pop last scene
                prev = state.history.pop()
                state.skip_push = True
                state.game_state = prev
            else:
                # nothing to go back to ⇒ quit modal
                state.show_quit_modal = True
            continue

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

    # 3) Detect entering "playing" to reinitialize turn flags
    if prev_scene != state.game_state:
        if not state.skip_push:
            state.history.append(prev_scene)
        state.skip_push = False

        # preserve your existing “entering playing ⇒ reset AI” hook
        if state.game_state == "playing":
            playing_logic.reset()

    prev_scene = state.game_state

    # 4) Draw background and active scene
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

    # 7) Opponent-left modal
    if state.opponent_left:
        def _back_to_menu():
            state.opponent_left = False
            state.game_state    = "menu"
        def _close_modal():
            state.opponent_left = False

        draw_modal(
            screen,
            title="Opponent Disconnected",
            subtitle="The other player has left the game.",
            on_yes=_back_to_menu,
            on_no=_close_modal,
            yes_text="Main Menu",
            no_text="Close"
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
