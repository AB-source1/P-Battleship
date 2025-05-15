# Main.py
import os
os.environ["SDL_VIDEO_CENTERED"] = "1"
import pygame
import sys
from core.config            import Config
from core.game_state        import GameState

from screens.settings_logic import SettingsLogic
from screens.settings_render import SettingsRender
from screens.settings_tk import SettingsTk
from screens.lobby_logic    import LobbyLogic
from screens.lobby_render   import LobbyRender
from screens.placing_logic  import PlacingLogic
from screens.placing_render import PlacingRender
from screens.playing_logic  import PlayingLogic
from screens.playing_render import PlayingRender
from screens.stats_logic    import StatsLogic
from screens.stats_render   import StatsRender
from helpers.draw_helpers   import draw_modal,draw_button,draw_text_center
from game.board_helpers     import create_board
from screens.menu_tk import MenuTk  

def show_tk_menu(state=None):
    def start_play():
        # Ship placement screen
        run_game(initial_state="placing",state=state)

    def open_settings():
        # Settings screen
        run_game(initial_state="settings",state=state)

    def start_multiplayer():
        # Networked lobby screen
        run_game(initial_state="lobby",state=state)

    def start_pass_and_play():
        # Local hot-seat placement
        run_game(initial_state="placing_multi",state=state)

    def quit_app():
        # Exit the whole application
        import sys
        sys.exit()

    # — Instantiate your Tk menu, giving it exactly those callbacks —
    menu = MenuTk(
        state,
        on_play=start_play,
        on_settings=open_settings,
        on_multiplayer=start_multiplayer,
        on_pass_and_play=start_pass_and_play,
        on_quit=quit_app
    )
    menu.run()

def run_game(initial_state="menu", state=None):
    # ─── Pygame Initialization ───────────────────────────────────────────────────
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
 
    # -----------------------------------------
    VW, VH = Config.WIDTH, Config.HEIGHT
    canvas = pygame.Surface((VW, VH))
    screen = pygame.display.set_mode((VW, VH), pygame.RESIZABLE)
    pygame.display.set_caption("Battleship")

     # ─── Load & start background music ─────────────────────────
    bgm_path = "resources/music/background_music.mp3"
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.5)       # 50% volume
    pygame.mixer.music.play(loops=-1)        # loop forever
    # ─── Load both menu & battle backgrounds ────────────────────────────────────
    bg_menu_img   = pygame.image.load("resources/images/cartoon_loading.png").convert()
    battle_bg_img = pygame.image.load("resources/images/cartoon_battle_bg.png").convert()

    # initial scale
    menu_background   = pygame.transform.smoothscale(bg_menu_img,   (VW, VH))
    battle_background = pygame.transform.smoothscale(battle_bg_img, (VW, VH))


    Config.update_layout()

    # ─── GameState & Reset Wiring ────────────────────────────────────────────────
    # ─── GameState & Reset Wiring ────────────────────────────────────────────────
    if state is None:
        # first time through: no state passed in, so create one
        state = GameState(lambda: None)
    # remember initial state (menu, settings, etc.)
    state.game_state = initial_state
    placing_logic  = PlacingLogic(screen, state)
    placing_render = PlacingRender(placing_logic)
    state.reset_callback = placing_logic.reset
    state.is_fullscreen = False
    # Now state.reset_all() will call placing_logic.reset() for ship placement

 
    settings_logic  = SettingsLogic(screen, state)
    settings_render = SettingsRender(settings_logic)

    lobby_logic     = LobbyLogic(screen, state)
    lobby_render    = LobbyRender(lobby_logic)

    
     # create the two SFX
    hit_sfx  = pygame.mixer.Sound("resources/music/hit.mp3")
    miss_sfx = pygame.mixer.Sound("resources/music/ship-miss.mp3")
    hit_sfx.set_volume(0.7)
    miss_sfx.set_volume(0.7)
    playing_logic   = PlayingLogic(screen, state, hit_sfx=hit_sfx, miss_sfx=miss_sfx)
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

   
    clock = pygame.time.Clock()
    
    if state.game_state == "placing_multi":
        state.pass_play_mode   = True

        # 2) We're about to place Player 1 first
        state.pass_play_stage  = 0
        state.current_player   = 0

        # 3) Build two fresh boards for ships & two for attacks
        state.pass_play_boards  = [create_board(), create_board()]
        state.pass_play_attacks = [create_board(), create_board()]

        # 4) Switch to the placement screen
        state.game_state       = "placing"

    prev_scene = state.game_state

    # ─── Main Loop ────────────────────────────────────────────────────────────────
    while state.running:
        now = pygame.time.get_ticks()
        if state.game_state == "menu":
            pygame.quit()
            show_tk_menu(state)
            return
        if state.game_state == "settings":
            # 1) Tear down Pygame entirely
            pygame.quit()
            # 2) Launch the standalone Tk Settings window
            SettingsTk(
                state,
                on_back=lambda: None   # we will manually pop back to menu below
            ).run()
            # 3) When SettingsTk closes, return to the main Tk menu
            show_tk_menu(state)
            return
            
           
        # 1) Turn logic first so `my_turn` is updated before click handling
        if state.game_state == "playing":
            if state.network:
                playing_logic.handle_network_turn(now)
            else:
                playing_logic.handle_ai_turn(now)
        if state.game_state == "placing" and state.network:
            placing_logic.update(state)

        raw_events = pygame.event.get()
        win_w, win_h = screen.get_size()
        scale_x = VW / win_w
        scale_y = VH / win_h

        events = []
        for ev in raw_events:
            # remap any mouse position into canvas space
            if hasattr(ev, "pos"):
                mx, my = ev.pos
                ev.pos = (int(mx * scale_x), int(my * scale_y))
            events.append(ev)

        for event in events:
            # Quit → show modal
            if event.type == pygame.QUIT:
                state.show_quit_modal = True

            # Handle actual OS window‐resize (keep canvas size fixed)
            elif event.type == pygame.VIDEORESIZE:
                # update your window dims
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # optionally re-rescale backgrounds, if you want crisp edges
                # (but with canvas scaling you can skip this)
                menu_background   = pygame.transform.smoothscale(bg_menu_img,   (VW, VH))
                battle_background = pygame.transform.smoothscale(battle_bg_img, (VW, VH))
                continue

            # Block input while a modal is open
            if state.show_restart_modal or state.show_quit_modal:
                continue

            # ESC to back out
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state.history:
                    prev = state.history.pop()
                    state.skip_push = True
                    state.game_state = prev
                else:
                    state.show_quit_modal = True
                continue

            # Dispatch to each screen’s logic
          
            if state.game_state == "lobby":
                lobby_logic.handle_event(event)
            elif state.game_state == "settings":
                settings_logic.handle_event(event)
            elif state.game_state == "placing":
                placing_logic.handle_event(event, state)
            elif state.game_state == "playing":
                playing_logic.handle_event(event, state)
            elif state.game_state == "stats":
                stats_logic.handle_event(event)

        # ─── 2) Scene‐change bookkeeping ─────────────────────────────────────────
        if prev_scene != state.game_state:
            if not state.skip_push:
                state.history.append(prev_scene)
            state.skip_push = False

            if state.game_state == "playing":
                playing_logic.reset()
                state.timer_start = pygame.time.get_ticks()
                state.score = 0
                state.hit_count = 0
                state.last_shot_time = state.timer_start

        prev_scene = state.game_state

        # ─── 3) DRAW EVERYTHING INTO THE CANVAS ────────────────────────────────
        # Background
        if state.game_state == "menu":
            canvas.blit(menu_background, (0, 0))
        else:
            canvas.blit(battle_background, (0, 0))

        # UI layer
        
        if state.game_state == "lobby":
            lobby_render.draw(canvas, state)
        elif state.game_state == "settings":
            settings_render.draw(canvas, state)
        elif state.game_state == "placing":
            placing_render.draw(canvas, state)
        elif state.game_state == "playing":
            playing_render.draw(canvas, state)
        elif state.game_state == "stats":
            stats_render.draw(canvas, state)

        # Modals (draw *into* canvas so they scale, not onto screen)
        if state.show_restart_modal:
            def _ok():    state.show_restart_modal = False; restart_game()
            def _no():    state.show_restart_modal = False
            draw_modal(canvas, "Restart game?", "All progress will be lost.", _ok, _no)
        elif state.show_quit_modal:
            def _yes():   pygame.quit(); sys.exit()
            def _no2():   state.show_quit_modal = False
            draw_modal(canvas, "Quit game?", "Are you sure?", _yes, _no2)
        if state.opponent_left:
            def _goto_menu(): state.opponent_left=False; state.game_state="menu"
            draw_modal(canvas,
                    "Opponent Disconnected",
                    "Other player left.",
                    _goto_menu, _goto_menu)
        if getattr(state, "show_pass_modal", False):
            def confirm_pass():
                state.show_pass_modal   = False
                state.player_board     = create_board()
                placing_logic.reset()
                state.pass_play_stage   = 2
                state.game_state        = "placing"

            # 2) Snapshot & blur the battlefield behind
            bg      = canvas.copy()
            # 1) Show the static battle background (no ships visible)
            canvas.blit(battle_background, (0, 0))
            w, h = canvas.get_size()

            # 3) Dark translucent overlay
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            canvas.blit(overlay, (0, 0))

            # 4) Draw the modal box
            box_w, box_h = 400, 180
            box_rect = pygame.Rect(
                (Config.WIDTH  - box_w) // 2,
                (Config.HEIGHT - box_h) // 2,
                box_w, box_h
            )
            pygame.draw.rect(canvas, Config.DARK_GRAY, box_rect)
            pygame.draw.rect(canvas, Config.WHITE,    box_rect, 2)

            draw_text_center(
                canvas, "Pass to Player 2",
                box_rect.centerx, box_rect.y + 40, 36
            )
            draw_text_center(
                canvas, "Press Yes when ready",
                box_rect.centerx, box_rect.y + 80, 24
            )

            # 5) Single “Yes” button
            draw_button(
                canvas, "Yes",
                box_rect.centerx - 50,
                box_rect.y + 120,
                100, 40,
                Config.GREEN, Config.DARK_GREEN,
                confirm_pass,
                3
            )

        # ─── 4) STRETCH + FLIP ONCE ─────────────────────────────────────────────
        win_w, win_h = screen.get_size()
        scaled = pygame.transform.smoothscale(canvas, (win_w, win_h))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()

        clock.tick(Config.FPS)

    # ─── Shutdown ─────────────────────────────────────────────────────────────
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    
    show_tk_menu(None)

