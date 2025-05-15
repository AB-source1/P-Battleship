import pygame
from helpers.draw_helpers import draw_top_bar, draw_text_center, draw_button
from core.config import Config

class StatsRender:
    def __init__(self, logic):
        self.logic = logic
        global _stats_panel_raw
        try:
            _stats_panel_raw
        except NameError:
            _stats_panel_raw = pygame.image.load("resources/images/grid_panel.png").convert_alpha()
        self.panel_raw = _stats_panel_raw

    def draw(self, screen, state):
        # Draw the top bar (title, restart/quit buttons)
        draw_top_bar(screen, state)

        # ─── Draw a scaled frame around the stats area ───────────────────────────
        # Compute the panel size: leave 50px margin on left/right, top under the bar
        panel_w = Config.WIDTH  - 100
        panel_h = Config.HEIGHT - Config.TOP_BAR_HEIGHT + 50
        panel = pygame.transform.smoothscale(self.panel_raw, (panel_w, panel_h))
        panel_x = 50
        panel_y = Config.TOP_BAR_HEIGHT -20
        screen.blit(panel, (panel_x, panel_y))

        # Now all subsequent text/buttons will render on top of this panel

        # ─── PASS & PLAY vs AI/Network split ────────────────────
        if state.pass_play_mode:
            # Pass & Play banner + per-player scores
            title_y = 120
            draw_text_center(screen, "Pass & Play Results", Config.WIDTH // 2, title_y, 48)

            # Draw each player's total score
            score_y = title_y + 40
            draw_text_center(
                screen,
                f"Player 1 Score: {state.pass_play_score[0]}",
                Config.WIDTH // 4, score_y, font_size=28
            )
            draw_text_center(
                screen,
                f"Player 2 Score: {state.pass_play_score[1]}",
                Config.WIDTH * 3 // 4, score_y, font_size=28
            )
            # Shift down the stats table start
            stats_start_y = score_y + 50

            # Skip the single‐player banner and final‐score
        else:
            # Existing Winner/Score banner for AI/online
            if state.winner == "Player":
                msg = "You won!"
            else:
                msg = "You lost!"
            draw_text_center(screen, msg, Config.WIDTH // 2, 120, 48)
            draw_text_center(screen, msg, Config.WIDTH // 2, 120, 48)

            draw_text_center(
                screen,
                f"Final Score: {state.score}",
                Config.WIDTH // 2,
                180,
                32
            )
 

        # Compute stats summary dictionaries
        def compute_stats(shots, hits, times):
            accuracy = (hits / shots * 100) if shots else 0
            if len(times) > 1:
                total_ms = times[-1] - times[0]
                avg_ms   = total_ms / (len(times) - 1)
            else:
                total_ms = 0
                avg_ms   = 0
            return {
                "Shots": shots,
                "Hits": hits,
                "Accuracy": f"{accuracy:.1f}%",
                "Avg/Shot": f"{avg_ms/1000:.2f}s",
                "Total": f"{total_ms/1000:.2f}s"
            }

        if state.pass_play_mode:
            # Per-player stats from pass_play arrays
            p_stats = compute_stats(
                state.pass_play_shots[0],
                state.pass_play_hits[0],
                state.pass_play_shot_times[0]
            )
            o_stats = compute_stats(
                state.pass_play_shots[1],
                state.pass_play_hits[1],
                state.pass_play_shot_times[1]
            )
        else:
            # AI / network stats as before
            p_stats = compute_stats(
                state.player_shots,
                state.player_hits,
                state.player_shot_times
            )
            o_stats = compute_stats(
                state.ai_shots,
                state.ai_hits,
                state.ai_shot_times
            )

        # Layout: two columns
        left_x = Config.WIDTH // 4
        right_x = Config.WIDTH * 3 // 4
        start_y  = locals().get('stats_start_y', 200)
        line_h = 40

        # Column headers: always “Player 1” / “Player 2” in Pass&Play,
        # else the usual You/Computer or You/Opponent
        if state.pass_play_mode:
            left_label  = "Player 1"
            right_label = "Player 2"
        elif state.network:
            left_label  = "You"
            right_label = "Opponent"
        else:
            left_label  = "Player"
            right_label = "Computer"

        draw_text_center(screen, left_label, left_x, start_y, 36)
        draw_text_center(screen, right_label, right_x, start_y, 36)

        # Draw each stat row
        for i, key in enumerate(p_stats.keys()):
            y = start_y + line_h * (i + 1)
            draw_text_center(screen, f"{key}: {p_stats[key]}", left_x, y, 28)
            draw_text_center(screen, f"{key}: {o_stats[key]}", right_x, y, 28)

        # Action buttons: Play Again and Main Menu
        btn_y = Config.HEIGHT - 100
        btn_x = Config.WIDTH // 2 - 80
        if not state.pass_play_mode:
            draw_button(
                screen,
                "Play Again",
                Config.WIDTH // 2 - 180,
                btn_y,
                160,
                50,
                Config.GREEN,
                Config.DARK_GREEN,
                self.logic.play_again,3
            )
            btn_x = Config.WIDTH // 2 + 20
        draw_button(
            screen,
            "Main Menu",
            btn_x,
            btn_y,
            160,
            50,
            Config.GRAY,
            Config.DARK_GRAY,
            self.logic.to_menu,3
        )