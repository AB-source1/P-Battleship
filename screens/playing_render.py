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

        # ─── PASS & PLAY MODE ───────────────────────────────
        if state.pass_play_mode:
            # Top‐center label: whose turn is it
            draw_text_center(
                screen,
                f"Player {state.current_player+1}'s Turn",
                Config.WIDTH // 2,
                Config.TOP_BAR_HEIGHT + 50
            )

            # --- LEFT: Player 1’s board (ships hidden) ---
            draw_grid(
                screen,
                state.pass_play_boards[0],
                Config.BOARD_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                show_ships=False
            )

            # --- RIGHT: Player 2’s board (ships hidden) ---
            draw_grid(
                screen,
                state.pass_play_boards[1],
                Config.ENEMY_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                show_ships=False
            )
            # quit here so none of your old single-/multi-player draws run
            return
        # ──────────────────────────────────────────────────────
 
        score_str = f"Score: {state.score}"
        draw_text_center(
            screen,
            score_str,
            Config.WIDTH  // 2,
            Config.TOP_BAR_HEIGHT + 20,
            font_size=24
        )


        
        # Your fleet (hidden ships)
        draw_grid(
            screen,
            state.pass_play_boards[state.current_player],
            Config.BOARD_OFFSET_X,
            Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=False
        )
        return

        rows = Config.GRID_SIZE
        cols = Config.GRID_SIZE
        visited = set()
        for r in range(rows):
            for c in range(cols):
                # find each unvisited hit cell
                if state.computer_board[r][c] == Cell.HIT and (r, c) not in visited:
                    # BFS to collect contiguous hits
                    cluster = [(r, c)]
                    queue = [(r, c)]
                    visited.add((r, c))
                    while queue:
                        rr, cc = queue.pop(0)
                        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                            nr, nc = rr+dr, cc+dc
                            if (0 <= nr < rows and 0 <= nc < cols
                                and state.computer_board[nr][nc] == Cell.HIT
                                and (nr, nc) not in visited):
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                                cluster.append((nr, nc))

                    size = len(cluster)
                    # only reveal real ships (we have art for sizes 3,4,5)
                    from game.draggable_ship import SHIP_IMAGE_FILES
                    if size not in SHIP_IMAGE_FILES:
                        continue
                    # determine orientation
                    horiz = all(r0 == cluster[0][0] for r0, _ in cluster)

                    # find top-left cell
                    # find the min/max row/col of this hit cluster
                    min_r = min(r0 for r0, _ in cluster)
                    max_r = max(r0 for r0, _ in cluster)
                    min_c = min(c0 for _, c0 in cluster)
                    max_c = max(c0 for _, c0 in cluster)

                    # ─── only reveal once **all** segments are hit ─────────
                    # if horizontal, check cell immediately left/right
                    if horiz:
                        left  = (min_c - 1)
                        right = (max_c + 1)
                        if (0 <= left  < cols and state.computer_board[min_r][left ] == Cell.SHIP) or \
                           (0 <= right < cols and state.computer_board[min_r][right] == Cell.SHIP):
                            continue  # still part unhit
                    else:
                        up   = (min_r - 1)
                        down = (max_r + 1)
                        if (0 <= up   < rows and state.computer_board[up  ][min_c] == Cell.SHIP) or \
                           (0 <= down < rows and state.computer_board[down][min_c] == Cell.SHIP):
                            continue  # still part unhit

                    # now all segments are HIT ⇒ reveal the sunk ship

                    # create a throwaway ship sprite of that size
                    ship = DraggableShip(size, 0, 0)
                    if not horiz:
                        ship.rotate()  # make it vertical

                    # compute pixel pos (account for top bar offset)
                    x = Config.ENEMY_OFFSET_X + min_c * Config.CELL_SIZE
                    y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + min_r * Config.CELL_SIZE

                    # blit the ship image under the X’s
                    screen.blit(ship.image, (x, y))

        # ─── NEW: draw elapsed play-time as MM:SS ───────────────
        if state.timer_start is not None:
            # milliseconds since play began
            elapsed_ms = pygame.time.get_ticks() - state.timer_start
            total_sec = elapsed_ms // 1000
            mins, secs = divmod(total_sec, 60)
            timer_str = f"{mins:02d}:{secs:02d}"
            # center it in the top bar (adjust font_size as needed)
            draw_text_center(
                screen,
                timer_str,
                Config.WIDTH // 2,
                Config.TOP_BAR_HEIGHT // 2,
                font_size=24
            )

        if state.player_ships == 0:
            draw_text_center(screen,
                            f"{state.player_name or 'You'} lost! Click Restart",
                            Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart",
                        Config.WIDTH // 2 - 75, Config.HEIGHT // 2,
                        150, 50, Config.GREEN, Config.DARK_GREEN,
                        state.reset_all)

        elif state.computer_ships == 0:
            draw_text_center(screen,
                            f"{state.player_name or 'You'} won! Click Restart",
                            Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart",
                        Config.WIDTH // 2 - 75, Config.HEIGHT // 2,
                        150, 50, Config.GREEN, Config.DARK_GREEN,
                        state.reset_all)

        else:
            draw_text_center(screen, "Your Fleet",
                            Config.BOARD_OFFSET_X + Config.GRID_WIDTH // 2,
                            Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT)

            draw_text_center(screen, "Enemy Waters",
                            Config.ENEMY_OFFSET_X + Config.GRID_WIDTH // 2,
                            Config.BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT)

                        # draw the grid without the default blue‐ship squares
            # 1) draw your fleet grid (no blue ship‐blocks)
            
            draw_grid(
                screen,
                state.player_attacks,
                Config.ENEMY_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                show_ships=False
            )
            
            
            draw_grid(
                screen,
                state.player_board,
                Config.BOARD_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
                show_ships=False
            )
    
            # 2) overlay each placed ship sprite
            for ship in state.placed_ships:
                rows = [r for r,c in ship.coords]
                cols = [c for r,c in ship.coords]
                row0, col0 = min(rows), min(cols)
                x = Config.BOARD_OFFSET_X + col0 * Config.CELL_SIZE
                y = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + row0 * Config.CELL_SIZE
                screen.blit(ship.image, (x, y))
    
            # 3) now draw your hit/miss markers on top of the ships
            for r in range(Config.GRID_SIZE):
                for c in range(Config.GRID_SIZE):
                    cell = state.player_board[r][c]
                    px = Config.BOARD_OFFSET_X + c * Config.CELL_SIZE + Config.CELL_SIZE//2
                    py = Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r * Config.CELL_SIZE + Config.CELL_SIZE//2
                    if cell == Cell.MISS:
                        pygame.draw.circle(screen, Config.BLUE, (px, py), 5)
                    elif cell == Cell.HIT:
                        draw_x(screen, px, py, Config.CELL_SIZE)
