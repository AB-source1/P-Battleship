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
# Create the window at the configured size
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("P-Battleship")

# Load and scale the background image once
background = pygame.image.load("resources/images/image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))

# Compute positions & sizes based on the current grid size
Config.update_layout()

# ─── GameState & Reset Wiring ────────────────────────────────────────────────
# We start with a dummy reset_callback; we'll override it after creating PlacingLogic
state = GameState(lambda: None)

# Instantiate PlacingLogic first, then wire GameState.reset_callback to it.
placing_logic  = PlacingLogic(screen, state)
placing_render = PlacingRender(placing_logic)
state.reset_callback = placing_logic.reset
# Why? This ensures that every time state.reset_all() is called,
# PlacingLogic.reset() runs to re-place ships on a fresh board.

# ─── Instantiate All Screens ─────────────────────────────────────────────────
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

# ─── Restart Helper ──────────────────────────────────────────────────────────
def restart_game():
    """
    Called by the Restart modal:
    1) state.reset_all() clears boards, stats, UI flags, and invokes PlacingLogic.reset().
    2) playing_logic.reset() clears AI hunt/destroy state and reinitializes multiplayer turn flags.
    """
    state.reset_all()
    playing_logic.reset()

# ─── Main Loop ───────────────────────────────────────────────────────────────
prev_scene = state.game_state
while state.running:
    # Draw the static background
    screen.blit(background, (0, 0))
    now = pygame.time.get_ticks()

    # ─── Event Handling ───────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            state.show_quit_modal = True

        # When a modal is up, block other input
        if state.show_restart_modal or state.show_quit_modal:
            continue

        # Delegate events based on current scene
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

    # ─── Scene Transitions ────────────────────────────────────────────────────
    # If we just switched into "playing", reinitialize the playing_logic
    if prev_scene != state.game_state and state.game_state == "playing":
        playing_logic.reset()
    prev_scene = state.game_state

    # ─── Turn Logic ───────────────────────────────────────────────────────────
    if state.game_state == "playing":
        if state.network:
            # Multiplayer mode: exchange shots/results
            playing_logic.handle_network_turn(now)
        else:
            # Single-player mode: AI takes its turn after a delay
            playing_logic.handle_ai_turn(now)

    # ─── Drawing ──────────────────────────────────────────────────────────────
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

    # ─── Restart Confirmation Modal ────────────────────────────────────────────
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

    # Flip the display buffers
    pygame.display.flip()

# Clean up on exit
pygame.quit()
sys.exit()
