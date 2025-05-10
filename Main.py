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

# ─── Initialization ───────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("P-Battleship")
background = pygame.image.load("resources/images/image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))
Config.update_layout()

# 1️⃣ Create GameState with a no-op reset callback; we'll wire it to PlacingLogic next
state = GameState(lambda: None)

# 2️⃣ Instantiate PlacingLogic first, then hook it into state.reset_callback
placing_logic  = PlacingLogic(screen, state)
placing_render = PlacingRender(placing_logic)
state.reset_callback = placing_logic.reset
#    ▶ This ensures state.reset_all() calls placing_logic.reset() to re-place ships.

# 3️⃣ Instantiate the rest of your screens
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

# 4️⃣ Define a helper to restart: resets boards & AI memory (but keeps network)
def restart_game():
    state.reset_all()      # clears boards, stats, UI, and calls placing_logic.reset()
    playing_logic.reset()  # clears Hard-mode AI state, resets my_turn

# ─── Main Loop ────────────────────────────────────────────────────────────────
while state.running:
    screen.blit(background, (0, 0))
    now = pygame.time.get_ticks()

    # ─── Event Handling ───────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True

        # Block input when a modal is visible
        if state.show_restart_modal or state.show_quit_modal:
            continue

        # Delegate to current scene
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

    # ─── Turn Logic ────────────────────────────────────────────────────────────
    if state.game_state == "playing":
        if state.network:
            # Peer-to-peer multiplayer turn handling
            playing_logic.handle_network_turn(now)
        else:
            # Single-player vs. AI
            playing_logic.handle_ai_turn(now)

    # ─── Drawing ───────────────────────────────────────────────────────────────
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

    # ─── Restart Confirmation Modal ───────────────────────────────────────────
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

    # ─── Quit Confirmation Modal ───────────────────────────────────────────────
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
