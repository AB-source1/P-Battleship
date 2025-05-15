import pygame
from helpers.draw_helpers import (
    draw_top_bar, draw_grid, draw_text_center,
    draw_button, draw_x
)
from core.config import Config
from game.draggable_ship import DraggableShip, SHIP_IMAGE_FILES
from game.board_helpers import Cell

_panel_raw = None
_backbox_raw = None

class PlayingRender:
    def __init__(self, logic):
        self.logic = logic
        self.cell_size = Config.PLAYING_CELL_SIZE
        grid_px = Config.GRID_SIZE * self.cell_size
        margin  = int(1.9 * self.cell_size)
        padded  = grid_px + 2 * margin

        global _panel_raw, _backbox_raw
        if _panel_raw is None:
            _panel_raw = pygame.image.load("resources/images/grid_panel.png").convert_alpha()
        if _backbox_raw is None:
            _backbox_raw = pygame.image.load("resources/images/Backbox.png").convert_alpha()

        self.panel = pygame.transform.smoothscale(_panel_raw, (padded, padded))
        self.backbox = pygame.transform.smoothscale(_backbox_raw, (160, 60))
        self.margin = margin

    def draw(self, screen, state):
        draw_top_bar(screen, state)
        if state.pass_play_mode and state.pass_play_stage == 3:
            self._draw_pass_play(screen, state)
        else:
            self._draw_standard(screen, state)
        self._draw_effects(screen, state)

    def _draw_standard(self, screen, state):
        draw_text_center(screen,
                         f"Score: {state.score}",
                         Config.WIDTH // 2,
                         Config.TOP_BAR_HEIGHT + 20,
                         font_size=24)

        top_y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT - self.margin
        ex = Config.PLAY_ENEMY_OFFSET_X - self.margin
        bx = Config.PLAY_BOARD_OFFSET_X - self.margin

        screen.blit(self.panel, (ex, top_y))
        screen.blit(self.panel, (bx, top_y))

        draw_grid(screen, state.player_attacks,
                  Config.PLAY_ENEMY_OFFSET_X, Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False, cell_size=self.cell_size)
        draw_grid(screen, state.player_board,
                  Config.PLAY_BOARD_OFFSET_X, Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False, cell_size=self.cell_size)

        # Label boxes
        self._draw_labels(screen, "Your Fleet", "Enemy Waters")

        self._reveal_sunk_standard(screen, state)

        if state.timer_start is not None:
            elapsed = pygame.time.get_ticks() - state.timer_start
            mins, secs = divmod(elapsed // 1000, 60)
            draw_text_center(screen, f"{mins:02}:{secs:02}",
                             Config.WIDTH // 2, Config.TOP_BAR_HEIGHT // 2, font_size=24)

        if state.player_ships == 0:
            self._draw_endgame(screen, f"{state.player_name or 'You'} lost! Click Restart")
        elif state.computer_ships == 0:
            self._draw_endgame(screen, f"{state.player_name or 'You'} won! Click Restart")
        else:
            for ship in state.placed_ships:
                coords = ship.coords
                r0, c0 = min(coords, key=lambda rc: (rc[0], rc[1]))
                size = len(coords)
                horiz = all(r == coords[0][0] for r, _ in coords)
                w = size * self.cell_size if horiz else self.cell_size
                h = self.cell_size if horiz else size * self.cell_size
                img_scaled = pygame.transform.smoothscale(ship.image, (w, h))
                x = Config.PLAY_BOARD_OFFSET_X + c0 * self.cell_size
                y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r0 * self.cell_size
                screen.blit(img_scaled, (x, y))
            for r in range(Config.GRID_SIZE):
                for c in range(Config.GRID_SIZE):
                    if state.player_board[r][c] == Cell.HIT:
                        px = Config.PLAY_BOARD_OFFSET_X + c * self.cell_size + self.cell_size // 2
                        py = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r * self.cell_size + self.cell_size // 2
                        draw_x(screen, px, py, self.cell_size)

    def _draw_pass_play(self, screen, state):
        draw_text_center(screen, f"Player {state.current_player+1}'s Turn",
                         Config.WIDTH // 2, Config.TOP_BAR_HEIGHT + 50)

        left_x = Config.PLAY_BOARD_OFFSET_X - self.margin
        right_x = Config.PLAY_ENEMY_OFFSET_X - self.margin
        top_y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT - self.margin

        screen.blit(self.panel, (left_x, top_y))
        screen.blit(self.panel, (right_x, top_y))

        draw_grid(screen, state.pass_play_boards[0],
                  Config.PLAY_BOARD_OFFSET_X, Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False, cell_size=self.cell_size)
        draw_grid(screen, state.pass_play_boards[1],
                  Config.PLAY_ENEMY_OFFSET_X, Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False, cell_size=self.cell_size)

        # Label boxes (reused)
        self._draw_labels(screen, "Player 1", "Player 2")

        label_y = Config.PLAY_BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT
        cx1 = Config.PLAY_BOARD_OFFSET_X + Config.GRID_WIDTH // 2
        cx2 = Config.PLAY_ENEMY_OFFSET_X + Config.GRID_WIDTH // 2
        draw_text_center(screen, f"Score: {state.pass_play_score[0]}", cx1, label_y, font_size=22)
        draw_text_center(screen, f"Score: {state.pass_play_score[1]}", cx2, label_y, font_size=22)

        for idx, (ships, offx) in enumerate([
            (state.pass_play_placed_ships[0], Config.PLAY_BOARD_OFFSET_X),
            (state.pass_play_placed_ships[1], Config.PLAY_ENEMY_OFFSET_X)
        ]):
            board = state.pass_play_boards[idx]
            for coords in ships:
                if all(board[r][c] == Cell.HIT for r, c in coords):
                    size = len(coords)
                    r0 = min(r for r, _ in coords)
                    c0 = min(c for _, c in coords)
                    horiz = len({r for r, _ in coords}) == 1
                    ship = DraggableShip(size, 0, 0)
                    if not horiz:
                        ship.rotate()
                    w = size * self.cell_size if horiz else self.cell_size
                    h = self.cell_size if horiz else size * self.cell_size
                    img_scaled = pygame.transform.smoothscale(ship.image, (w, h))
                    screen.blit(img_scaled, (
                        offx + c0 * self.cell_size,
                        Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r0 * self.cell_size
                    ))

    def _draw_labels(self, screen, left_text, right_text):
        backbox_w, backbox_h = self.backbox.get_size()
        label_y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT - self.margin - backbox_h + 26
        box1_x = Config.PLAY_BOARD_OFFSET_X + (Config.PLAYING_GRID_WIDTH // 2) - (backbox_w // 2)
        box2_x = Config.PLAY_ENEMY_OFFSET_X + (Config.PLAYING_GRID_WIDTH // 2) - (backbox_w // 2)

        screen.blit(self.backbox, (box1_x, label_y))
        screen.blit(self.backbox, (box2_x, label_y))

        font = pygame.font.SysFont(None, 22, bold=True)
        text1 = font.render(left_text, True, (255, 255, 255))
        text2 = font.render(right_text, True, (255, 255, 255))

        screen.blit(text1, (box1_x + (backbox_w - text1.get_width()) // 2,
                            label_y + (backbox_h - text1.get_height()) // 2 + 8))
        screen.blit(text2, (box2_x + (backbox_w - text2.get_width()) // 2,
                            label_y + (backbox_h - text2.get_height()) // 2 + 8))

    def _reveal_sunk_standard(self, screen, state):
        rows = cols = Config.GRID_SIZE
        visited = set()
        board = state.computer_board
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == Cell.HIT and (r, c) not in visited:
                    cluster = [(r, c)]
                    queue = [(r, c)]
                    visited.add((r, c))
                    while queue:
                        rr, cc = queue.pop(0)
                        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                            nr, nc = rr + dr, cc + dc
                            if (0 <= nr < rows and 0 <= nc < cols and
                                board[nr][nc] == Cell.HIT and (nr, nc) not in visited):
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                                cluster.append((nr, nc))
                    size = len(cluster)
                    if size not in SHIP_IMAGE_FILES:
                        continue
                    horiz = all(r0 == cluster[0][0] for r0, _ in cluster)
                    if horiz:
                        r0 = cluster[0][0]
                        cols_hit = sorted(c0 for _, c0 in cluster)
                        if ((cols_hit[0] - 1 >= 0 and board[r0][cols_hit[0]-1] == Cell.SHIP) or
                            (cols_hit[-1] + 1 < cols and board[r0][cols_hit[-1]+1] == Cell.SHIP)):
                            continue
                    else:
                        c0 = cluster[0][1]
                        rows_hit = sorted(r0 for r0, _ in cluster)
                        if ((rows_hit[0] - 1 >= 0 and board[rows_hit[0]-1][c0] == Cell.SHIP) or
                            (rows_hit[-1] + 1 < rows and board[rows_hit[-1]+1][c0] == Cell.SHIP)):
                            continue
                    min_r = min(r0 for r0, _ in cluster)
                    min_c = min(c0 for _, c0 in cluster)
                    ship = DraggableShip(size, 0, 0)
                    if not horiz:
                        ship.rotate()
                    w = size * self.cell_size if horiz else self.cell_size
                    h = self.cell_size if horiz else size * self.cell_size
                    img_scaled = pygame.transform.smoothscale(ship.image, (w, h))
                    offx = Config.PLAY_ENEMY_OFFSET_X
                    x = offx + min_c * self.cell_size
                    y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + min_r * self.cell_size
                    screen.blit(img_scaled, (x, y))

    def _draw_endgame(self, screen, msg):
        draw_text_center(screen, msg, Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
        draw_button(screen, "Restart",
                    Config.WIDTH // 2 - 75, Config.HEIGHT // 2,
                    150, 50, Config.GREEN, Config.DARK_GREEN,
                    self.logic.state.reset_all, 3)

    def _draw_effects(self, screen, state):
        now = pygame.time.get_ticks()
        for exp in state.explosions[:]:
            elapsed = now - exp["time"]
            offx = Config.PLAY_BOARD_OFFSET_X if exp["board_idx"] == 0 else Config.PLAY_ENEMY_OFFSET_X
            x = offx + exp["col"] * self.cell_size
            y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + exp["row"] * self.cell_size
            if elapsed < Config.EXPLOSION_FADE_DURATION:
                img = Config.EXPLOSION_IMG.copy()
                alpha = int(255 * (1 - elapsed / Config.EXPLOSION_FADE_DURATION))
                img.set_alpha(alpha)
                screen.blit(img, (x, y))
            else:
                state.explosions.remove(exp)

        for ms in state.miss_splashes[:]:
            elapsed = now - ms["time"]
            offx = Config.PLAY_BOARD_OFFSET_X if ms["board_idx"] == 0 else Config.PLAY_ENEMY_OFFSET_X
            x = offx + ms["col"] * self.cell_size
            y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + ms["row"] * self.cell_size
            if elapsed < Config.MISS_FADE_DURATION:
                img = Config.MISS_IMG.copy()
                alpha = int(255 * (1 - elapsed / Config.MISS_FADE_DURATION))
                img.set_alpha(alpha)
                screen.blit(img, (x, y))
            else:
                state.miss_splashes.remove(ms)
