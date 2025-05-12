import pygame
from helpers.draw_helpers import draw_grid, draw_text_center, draw_top_bar
from core.config import Config

class PlayingRender:
    def __init__(self, screen, state):
        self.screen = screen
        self.state = state

        # Load gameplay-specific background image
        self.background = pygame.image.load("resources/images/cartoon_battle_bg.png")
        self.background = pygame.transform.smoothscale(self.background, (Config.WIDTH, Config.HEIGHT))

    def draw(self, screen, state):
        # Draw gameplay-specific background
        screen.blit(self.background, (0, 0))

        draw_top_bar(screen, state)

        # Draw the player's board with ships visible
        draw_text_center(
            screen,
            "Your Fleet",
            Config.BOARD_OFFSET_X + Config.GRID_SIZE * Config.CELL_SIZE // 2,
            100, 28
        )
        draw_grid(
            screen,
            state.player_board,
            Config.BOARD_OFFSET_X,
            Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=True
        )

        # Draw the enemy board (no ships shown)
        draw_text_center(
            screen,
            "Enemy Waters",
            Config.ENEMY_OFFSET_X + Config.GRID_SIZE * Config.CELL_SIZE // 2,
            100, 28
        )
        draw_grid(
            screen,
            state.player_attacks,
            Config.ENEMY_OFFSET_X,
            Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=True
        )

        # Optional: If you want debug info (hits/shots), add:
        # self.logic.draw_debug_info()

