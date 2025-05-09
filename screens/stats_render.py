import pygame
from helpers.draw_helpers import draw_top_bar, draw_text_center, draw_button
from core.config import Config

class StatsRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        # ─── Top bar with Restart/Close ───
        draw_top_bar(screen, state)

        # ─── Compute accuracies ───
        ps, ph = state.player_shots, state.player_hits
        ais, aih = state.ai_shots, state.ai_hits
        p_acc  = (ph / ps * 100) if ps else 0
        ai_acc = (aih / ais * 100) if ais else 0

        # ─── Draw text ───
        draw_text_center(screen,
                        f"Your Accuracy: {ph}/{ps} ({p_acc:.1f}%)",
                        Config.WIDTH // 2, Config.HEIGHT // 2 - 40, 36)
        draw_text_center(screen,
                        f"AI Accuracy:   {aih}/{ais} ({ai_acc:.1f}%)",
                        Config.WIDTH // 2, Config.HEIGHT // 2 + 10, 36)

        # ─── Action buttons ───
        draw_button(screen, "Play Again",
                    Config.WIDTH//2 - 180, Config.HEIGHT - 150,
                    160, 50, Config.GREEN, Config.DARK_GREEN,
                    self.logic.play_again)
        draw_button(screen, "Main Menu",
                    Config.WIDTH//2 + 20, Config.HEIGHT - 150,
                    160, 50, Config.GRAY, Config.DARK_GRAY,
                    self.logic.to_menu)
