import pygame
from helpers.draw_helpers import draw_top_bar, draw_text_center, draw_button
from core.config import Config

class StatsRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        # Draw the top bar (title, restart/quit buttons)
        draw_top_bar(screen, state)

        # Compute stats summary dictionaries
        def compute_stats(shots, hits, times):
            accuracy = (hits / shots * 100) if shots else 0
            if len(times) > 1:
                total_ms = times[-1] - times[0]
                avg_ms = total_ms / (len(times) - 1)
            else:
                total_ms = 0
                avg_ms = 0
            return {
                "Shots": shots,
                "Hits": hits,
                "Accuracy": f"{accuracy:.1f}%",
                "Avg/Shot": f"{avg_ms / 1000:.2f}s",
                "Total": f"{total_ms / 1000:.2f}s"
            }

        p_stats = compute_stats(state.player_shots, state.player_hits, state.player_shot_times)
        o_stats = compute_stats(state.ai_shots, state.ai_hits, state.ai_shot_times)

        # Layout values
        stats_box_width = 700
        stats_box_height = 380
        stats_box_x = (Config.WIDTH - stats_box_width) // 2
        stats_box_y = 100

        # ─── Draw background box ───────────────────────────
        outer_rect = pygame.Rect(stats_box_x, stats_box_y, stats_box_width, stats_box_height)
        pygame.draw.rect(screen, (255, 220, 0), outer_rect)  # Yellow border
        inner_rect = outer_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (10, 40, 80), inner_rect)   # Dark blue fill

        # ─── Header inside the box ─────────────────────────
        msg = "You won!" if state.winner == "Player" else "You lost!"
        draw_text_center(screen, msg, Config.WIDTH // 2, stats_box_y + 30, 42)
        draw_text_center(screen, f"Final Score: {state.score}", Config.WIDTH // 2, stats_box_y + 75, 30)

        # ─── Stat labels ───────────────────────────────────
        left_x = Config.WIDTH // 4
        right_x = Config.WIDTH * 3 // 4
        start_y = stats_box_y + 120
        line_h = 40

        left_label = "You" if state.network else "Player"
        right_label = "Opponent" if state.network else "Computer"
        draw_text_center(screen, left_label, left_x, start_y, 36)
        draw_text_center(screen, right_label, right_x, start_y, 36)

        # ─── Each stat row ─────────────────────────────────
        for i, key in enumerate(p_stats.keys()):
            y = start_y + line_h * (i + 1)
            draw_text_center(screen, f"{key}: {p_stats[key]}", left_x, y, 28)
            draw_text_center(screen, f"{key}: {o_stats[key]}", right_x, y, 28)

        # ─── Buttons ───────────────────────────────────────
        btn_y = Config.HEIGHT - 100
        draw_button(
            screen,
            "Play Again",
            Config.WIDTH // 2 - 180,
            btn_y,
            160,
            50,
            Config.GREEN,
            Config.DARK_GREEN,
            self.logic.play_again
        )
        draw_button(
            screen,
            "Main Menu",
            Config.WIDTH // 2 + 20,
            btn_y,
            160,
            50,
            Config.GRAY,
            Config.DARK_GRAY,
            self.logic.to_menu
        )
