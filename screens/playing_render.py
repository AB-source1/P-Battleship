import pygame
from helpers.draw_helpers import (
    draw_top_bar, draw_grid, draw_text_center,
    draw_button, draw_x
)
from core.config import Config
from game.draggable_ship import DraggableShip, SHIP_IMAGE_FILES
from game.board_helpers import Cell


class PlayingRender:
    def __init__(self, logic):
        self.logic = logic

    def draw(self, screen, state):
        # 1) Always draw top bar
        draw_top_bar(screen, state)

        # 2) Choose mode-specific rendering
        if state.pass_play_mode and state.pass_play_stage == 3:
            self._draw_pass_play(screen, state)
        else:
            self._draw_standard(screen, state)

        # 3) Overlay any hit/miss effects (explosions, splashes)
        self._draw_effects(screen, state)

    def _draw_pass_play(self, screen, state):
        # Turn label
        draw_text_center(screen,
                         f"Player {state.current_player+1}'s Turn",
                         Config.WIDTH // 2,
                         Config.TOP_BAR_HEIGHT + 50)

        # Two hidden boards
        draw_grid(screen, state.pass_play_boards[0],
                  Config.BOARD_OFFSET_X,
                  Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False)
        draw_grid(screen, state.pass_play_boards[1],
                  Config.ENEMY_OFFSET_X,
                  Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False)

        # Player names + scores
        label_y   = Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT
        cx1 = Config.BOARD_OFFSET_X + Config.GRID_WIDTH // 2
        cx2 = Config.ENEMY_OFFSET_X + Config.GRID_WIDTH // 2
        draw_text_center(screen,
                         f"Player 1   Score: {state.pass_play_score[0]}",
                         cx1, label_y, font_size=28)
        draw_text_center(screen,
                         f"Player 2   Score: {state.pass_play_score[1]}",
                         cx2, label_y, font_size=28)

        # Reveal sunk ships
        for idx, (ships, offx) in enumerate([
            (state.pass_play_placed_ships[0], Config.BOARD_OFFSET_X),
            (state.pass_play_placed_ships[1], Config.ENEMY_OFFSET_X)
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
                    x = offx + c0 * Config.CELL_SIZE
                    y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r0 * Config.CELL_SIZE
                    screen.blit(ship.image, (x, y))

    def _draw_standard(self, screen, state):
        # Score & timer
        draw_text_center(screen,
                         f"Score: {state.score}",
                         Config.WIDTH // 2,
                         Config.TOP_BAR_HEIGHT + 20,
                         font_size=24)
        # Attack grid + own fleet
        draw_grid(screen, state.player_attacks,
                  Config.ENEMY_OFFSET_X,
                  Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False)
        draw_grid(screen, state.player_board,
                  Config.BOARD_OFFSET_X,
                  Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                  show_ships=False)

        # Reveal sunk ships on computer board
        self._reveal_sunk_standard(screen, state)

        # Timer display
        if state.timer_start is not None:
            elapsed = pygame.time.get_ticks() - state.timer_start
            mins, secs = divmod(elapsed // 1000, 60)
            draw_text_center(screen,
                             f"{mins:02}:{secs:02}",
                             Config.WIDTH // 2,
                             Config.TOP_BAR_HEIGHT // 2,
                             font_size=24)

        # End-of-game or active placement
        if state.player_ships == 0:
            msg = f"{state.player_name or 'You'} lost! Click Restart"
            self._draw_endgame(screen, msg)
        elif state.computer_ships == 0:
            msg = f"{state.player_name or 'You'} won! Click Restart"
            self._draw_endgame(screen, msg)
        else:
            # Show labels
            draw_text_center(screen, "Your Fleet",
                             Config.BOARD_OFFSET_X + Config.GRID_WIDTH//2,
                             Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT)
            draw_text_center(screen, "Enemy Waters",
                             Config.ENEMY_OFFSET_X + Config.GRID_WIDTH//2,
                             Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT)
            # Overlay placed ships & markers
            for ship in state.placed_ships:
                r0 = min(r for r, c in ship.coords)
                c0 = min(c for r, c in ship.coords)
                x = Config.BOARD_OFFSET_X + c0 * Config.CELL_SIZE
                y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r0 * Config.CELL_SIZE
                screen.blit(ship.image, (x, y))
            for r in range(Config.GRID_SIZE):
                for c in range(Config.GRID_SIZE):
                    px = Config.BOARD_OFFSET_X + c*Config.CELL_SIZE + Config.CELL_SIZE//2
                    py = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r*Config.CELL_SIZE + Config.CELL_SIZE//2
                    cell = state.player_board[r][c]
                    if cell == Cell.MISS:
                        pygame.draw.circle(screen, Config.BLUE, (px, py), 5)
                    elif cell == Cell.HIT:
                        draw_x(screen, px, py, Config.CELL_SIZE)

    def _reveal_sunk_standard(self, screen, state):
        rows = cols = Config.GRID_SIZE
        visited = set()
        board = state.computer_board
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == Cell.HIT and (r, c) not in visited:
                    # BFS cluster
                    cluster = [(r,c)]
                    queue = [(r,c)]
                    visited.add((r,c))
                    while queue:
                        rr, cc = queue.pop(0)
                        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                            nr, nc = rr+dr, cc+dc
                            if (0 <= nr < rows and 0 <= nc < cols and
                                board[nr][nc] == Cell.HIT and (nr,nc) not in visited):
                                visited.add((nr,nc))
                                queue.append((nr,nc))
                                cluster.append((nr,nc))
                    size = len(cluster)
                    if size not in SHIP_IMAGE_FILES: 
                        continue
                    horiz = all(r0 == cluster[0][0] for r0, _ in cluster)
                    
                    # ─── ENSURE NO UNHIT NEIGHBORS FOR THIS CLUSTER ───
                    # if there’s an unhit ship-cell just off either end, skip it
                    if horiz:
                        r0       = cluster[0][0]
                        cols_hit = sorted(c0 for _,c0 in cluster)
                        if ((cols_hit[0] - 1 >= 0 and state.computer_board[r0][cols_hit[0]-1] == Cell.SHIP)
                        or (cols_hit[-1]+1 < cols and state.computer_board[r0][cols_hit[-1]+1] == Cell.SHIP)):
                            continue
                    else:
                        c0       = cluster[0][1]
                        rows_hit = sorted(r0 for r0,_ in cluster)
                        if ((rows_hit[0] - 1 >= 0 and state.computer_board[rows_hit[0]-1][c0] == Cell.SHIP)
                        or (rows_hit[-1]+1 < rows and state.computer_board[rows_hit[-1]+1][c0] == Cell.SHIP)):
                            continue

                    min_r = min(r0 for r0,_ in cluster)
                    min_c = min(c0 for _,c0 in cluster)
                    ship = DraggableShip(size,0,0)
                    if not horiz: ship.rotate()
                    x = Config.ENEMY_OFFSET_X + min_c*Config.CELL_SIZE
                    y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + min_r*Config.CELL_SIZE
                    screen.blit(ship.image, (x,y))

    def _draw_endgame(self, screen, msg):
        draw_text_center(screen, msg, Config.WIDTH//2, Config.HEIGHT//2 - 50)
        draw_button(screen, "Restart",
                    Config.WIDTH//2 - 75, Config.HEIGHT//2,
                    150, 50, Config.GREEN, Config.DARK_GREEN,
                    self.logic.state.reset_all)

    def _draw_effects(self, screen, state):
        now = pygame.time.get_ticks()
        # explosions
        for exp in state.explosions[:]:
            elapsed = now - exp["time"]
            offx = Config.BOARD_OFFSET_X if exp["board_idx"]==0 else Config.ENEMY_OFFSET_X
            x = offx + exp["col"]*Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + exp["row"]*Config.CELL_SIZE
            if elapsed < Config.EXPLOSION_FADE_DURATION:
                img = Config.EXPLOSION_IMG.copy()
                alpha = int(255*(1 - elapsed/Config.EXPLOSION_FADE_DURATION))
                img.set_alpha(alpha)
                screen.blit(img, (x,y))
            else:
                draw_x(screen, x, y, Config.CELL_SIZE)
                state.explosions.remove(exp)
        # miss splashes (identical pattern)
        for ms in state.miss_splashes[:]:
            elapsed = now - ms["time"]
            offx = Config.BOARD_OFFSET_X if ms["board_idx"]==0 else Config.ENEMY_OFFSET_X
            x = offx + ms["col"]*Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + ms["row"]*Config.CELL_SIZE
            if elapsed < Config.MISS_FADE_DURATION:
                img = Config.MISS_IMG.copy()
                alpha = int(255*(1 - elapsed/Config.MISS_FADE_DURATION))
                img.set_alpha(alpha)
                screen.blit(img, (x,y))
            else:
                state.miss_splashes.remove(ms)