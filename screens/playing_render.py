import pygame
from helpers.draw_helpers import draw_top_bar, draw_grid, draw_text_center, draw_button, draw_x
from core.config import Config
from game.draggable_ship import DraggableShip
from game.board_helpers import Cell


class PlayingRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        draw_top_bar(screen, state)

        font = pygame.font.SysFont("Arial", 24)
        score_str = f"Score: {state.score}"
        draw_boxed_label(screen, score_str, Config.WIDTH // 2, Config.TOP_BAR_HEIGHT + 50, font)
        draw_ships_left(screen, state.player_ships, font)

        enemy_ships_to_draw = []
        rows = Config.GRID_SIZE
        cols = Config.GRID_SIZE
        visited = set()

        for r in range(rows):
            for c in range(cols):
                if state.computer_board[r][c] == Cell.HIT and (r, c) not in visited:
                    cluster = [(r, c)]
                    queue = [(r, c)]
                    visited.add((r, c))

                    while queue:
                        rr, cc = queue.pop(0)
                        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            nr, nc = rr + dr, cc + dc
                            if (0 <= nr < rows and 0 <= nc < cols and
                                state.computer_board[nr][nc] == Cell.HIT and
                                (nr, nc) not in visited):
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                                cluster.append((nr, nc))

                    size = len(cluster)
                    from game.draggable_ship import SHIP_IMAGE_FILES
                    if size not in SHIP_IMAGE_FILES:
                        continue

                    # Fix: Only draw cluster if it forms a valid straight ship
                    rows_in_cluster = set(r0 for r0, _ in cluster)
                    cols_in_cluster = set(c0 for _, c0 in cluster)
                    horiz = len(rows_in_cluster) == 1
                    vert = len(cols_in_cluster) == 1
                    if not (horiz or vert):
                        continue

                    min_r = min(r0 for r0, _ in cluster)
                    max_r = max(r0 for r0, _ in cluster)
                    min_c = min(c0 for _, c0 in cluster)
                    max_c = max(c0 for _, c0 in cluster)

                    if horiz:
                        for col in range(min_c, max_c + 1):
                            if state.computer_board[min_r][col] != Cell.HIT:
                                break
                        else:
                            if (min_c > 0 and state.computer_board[min_r][min_c - 1] == Cell.SHIP) or \
                               (max_c < cols - 1 and state.computer_board[min_r][max_c + 1] == Cell.SHIP):
                                continue
                    elif vert:
                        for row in range(min_r, max_r + 1):
                            if state.computer_board[row][min_c] != Cell.HIT:
                                break
                        else:
                            if (min_r > 0 and state.computer_board[min_r - 1][min_c] == Cell.SHIP) or \
                               (max_r < rows - 1 and state.computer_board[max_r + 1][min_c] == Cell.SHIP):
                                continue
                    else:
                        continue

                    ship = DraggableShip(size, 0, 0)
                    if vert:
                        ship.rotate()

                    x = Config.ENEMY_OFFSET_X + min_c * Config.CELL_SIZE
                    y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + min_r * Config.CELL_SIZE
                    ship.rect.topleft = (x, y)
                    enemy_ships_to_draw.append(ship)

        # Timer
        if state.timer_start is not None:
            elapsed_ms = pygame.time.get_ticks() - state.timer_start
            total_sec = elapsed_ms // 1000
            mins, secs = divmod(total_sec, 60)
            timer_str = f"{mins:02d}:{secs:02d}"
            draw_text_center(screen, timer_str, Config.WIDTH // 2, Config.TOP_BAR_HEIGHT // 2, font_size=24)

        if state.player_ships == 0:
            draw_text_center(screen, f"{state.player_name or 'You'} lost! Click Restart", Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart", Config.WIDTH // 2 - 75, Config.HEIGHT // 2, 150, 50, Config.GREEN, Config.DARK_GREEN, state.reset_all)

        elif state.computer_ships == 0:
            draw_text_center(screen, f"{state.player_name or 'You'} won! Click Restart", Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart", Config.WIDTH // 2 - 75, Config.HEIGHT // 2, 150, 50, Config.GREEN, Config.DARK_GREEN, state.reset_all)

        else:
            draw_boxed_label(screen, "Your Fleet", Config.BOARD_OFFSET_X + 100 + Config.GRID_WIDTH // 2, Config.BOARD_OFFSET_Y - 20 + Config.TOP_BAR_HEIGHT, font)
            draw_boxed_label(screen, "Enemy Waters", Config.ENEMY_OFFSET_X + Config.GRID_WIDTH // 2, Config.BOARD_OFFSET_Y - 20 + Config.TOP_BAR_HEIGHT, font)

            draw_grid(screen, state.player_attacks, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT, show_ships=False)
            draw_grid(screen, state.player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT, show_ships=False)

            for ship in enemy_ships_to_draw:
                screen.blit(ship.image, ship.rect)

            for r in range(Config.GRID_SIZE):
                for c in range(Config.GRID_SIZE):
                    if state.computer_board[r][c] == Cell.HIT:
                        px = Config.ENEMY_OFFSET_X + c * Config.CELL_SIZE + Config.CELL_SIZE // 2
                        py = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r * Config.CELL_SIZE + Config.CELL_SIZE // 2
                        draw_x(screen, px, py, Config.CELL_SIZE)

            for ship in state.placed_ships:
                rows = [r for r, c in ship.coords]
                cols = [c for r, c in ship.coords]
                row0, col0 = min(rows), min(cols)
                x = Config.BOARD_OFFSET_X + col0 * Config.CELL_SIZE
                y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + row0 * Config.CELL_SIZE
                screen.blit(ship.image, (x, y))

            for r in range(Config.GRID_SIZE):
                for c in range(Config.GRID_SIZE):
                    cell = state.player_board[r][c]
                    px = Config.BOARD_OFFSET_X + c * Config.CELL_SIZE + Config.CELL_SIZE // 2
                    py = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r * Config.CELL_SIZE + Config.CELL_SIZE // 2
                    if cell == Cell.MISS:
                        pygame.draw.circle(screen, Config.BLUE, (px, py), 5)
                    elif cell == Cell.HIT:
                        draw_x(screen, px, py, Config.CELL_SIZE)


def draw_ships_left(screen, ships_left, font):
    text = f"Ships Left: {ships_left}"
    text_color = (255, 255, 255)
    bg_color = (10, 40, 80)
    border_color = (255, 220, 0)

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    padding = 10
    box_rect = pygame.Rect(50, 60, text_rect.width + 2 * padding, text_rect.height + 2 * padding)

    pygame.draw.rect(screen, border_color, box_rect)
    inner_rect = box_rect.inflate(-4, -4)
    pygame.draw.rect(screen, bg_color, inner_rect)

    text_pos = (
        box_rect.x + (box_rect.width - text_rect.width) // 2,
        box_rect.y + (box_rect.height - text_rect.height) // 2
    )
    screen.blit(text_surface, text_pos)


def draw_boxed_label(screen, text, center_x, center_y, font):
    text_color = (255, 255, 255)
    bg_color = (10, 40, 80)
    border_color = (255, 220, 0)

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    padding = 10
    box_rect = pygame.Rect(
        text_rect.left - padding,
        text_rect.top - padding,
        text_rect.width + 2 * padding,
        text_rect.height + 2 * padding
    )

    pygame.draw.rect(screen, border_color, box_rect)
    inner_rect = box_rect.inflate(-4, -4)
    pygame.draw.rect(screen, bg_color, inner_rect)
    screen.blit(text_surface, text_rect)
