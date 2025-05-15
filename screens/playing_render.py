import pygame
from helpers.draw_helpers import (
    draw_top_bar, draw_grid, draw_text_center,
    draw_button, draw_x
)
from core.config import Config
from game.draggable_ship import DraggableShip, SHIP_IMAGE_FILES
from game.board_helpers import Cell

_panel_raw = None
class PlayingRender:
    def __init__(self, logic):
        self.logic = logic

        # use scaled cell size
        self.cell_size = Config.PLAYING_CELL_SIZE
        grid_px = Config.GRID_SIZE * self.cell_size
        margin  = int(1.9 * self.cell_size)
        padded  = grid_px + 2 * margin

        # scale the panel once
        global _panel_raw
        if _panel_raw is None:
            _panel_raw = pygame.image.load("resources/images/grid_panel.png").convert_alpha()
        self.panel  = pygame.transform.smoothscale(_panel_raw, (padded, padded))
        self.margin = margin
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
         # --- LEFT: Player 1’s board (ships hidden) ---
        # blit grid‐panel behind it
        left_x = Config.PLAY_BOARD_OFFSET_X - self.margin
        top_y  = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT - self.margin
        screen.blit(self.panel, (left_x, top_y))
        draw_grid(
            screen,
            state.pass_play_boards[0],
            Config.PLAY_BOARD_OFFSET_X,
            Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=False,
            cell_size=self.cell_size
        )

        # RIGHT board…
        right_x = Config.PLAY_ENEMY_OFFSET_X - self.margin
        screen.blit(self.panel, (right_x, top_y))
        draw_grid(
            screen,
            state.pass_play_boards[1],
            Config.PLAY_ENEMY_OFFSET_X,
            Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=False,
            cell_size=self.cell_size
        )
        # Player names + scores
        label_y   = Config.PLAY_BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT
        cx1 = Config.PLAY_BOARD_OFFSET_X + Config.GRID_WIDTH // 2
        cx2 = Config.PLAY_ENEMY_OFFSET_X + Config.GRID_WIDTH // 2
        draw_text_center(screen,
                         f"Player 1   Score: {state.pass_play_score[0]}",
                         cx1, label_y, font_size=28)
        draw_text_center(screen,
                         f"Player 2   Score: {state.pass_play_score[1]}",
                         cx2, label_y, font_size=28)

        # Reveal sunk ships
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
                    if not horiz: ship.rotate()
                    # compute new pixel dims
                    w = size * self.cell_size if horiz else self.cell_size
                    h = self.cell_size       if horiz else size * self.cell_size
                    img_scaled = pygame.transform.smoothscale(ship.image, (w, h))
                    screen.blit(img_scaled, ( 
    (offx + c0 * self.cell_size),
    (Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r0 * self.cell_size)
))

    def _draw_standard(self, screen, state):
        # Score & timer
        draw_text_center(screen,
                         f"Score: {state.score}",
                         Config.WIDTH // 2,
                         Config.TOP_BAR_HEIGHT + 20,
                         font_size=24)
        # Attack grid + own fleet
        # --- draw “Enemy Waters” attack grid with background panel ---
        top_y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT - self.margin
        ex = Config.PLAY_ENEMY_OFFSET_X - self.margin
        screen.blit(self.panel, (ex, top_y))
        draw_grid(
            screen,
            state.player_attacks,
            Config.PLAY_ENEMY_OFFSET_X,
            Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=False,
            cell_size=self.cell_size
        )
        # --- draw “Your Fleet” board with the same panel behind it ---
        bx = Config.PLAY_BOARD_OFFSET_X - self.margin
        screen.blit(self.panel, (bx, top_y))
        draw_grid(
            screen,
            state.player_board,
            Config.PLAY_BOARD_OFFSET_X,
            Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT,
            show_ships=False,
            cell_size=self.cell_size
        )

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

         # ─── Turn indicator (single-player vs AI or network) ─────────────────
        if state.network:
            # multiplayer over network
            turn_label = "Your Turn" if self.logic.my_turn else "Opponent's Turn"
        else:
            # single-player: if AI is pending, it's AI's turn, otherwise yours
            turn_label = "AI's Turn" if state.ai_turn_pending else "Your Turn"
        draw_text_center(
            screen,
            turn_label,
            Config.WIDTH // 2,
            Config.TOP_BAR_HEIGHT + 40,
            font_size=24
        )
        # End-of-game or active placement
        if state.player_ships == 0:
            msg = f"{state.player_name or 'You'} lost! Click Restart"
            self._draw_endgame(screen, msg)
        elif state.computer_ships == 0:
            msg = f"{state.player_name or 'You'} won! Click Restart"
            self._draw_endgame(screen, msg)
        else:
            # Show labels
            draw_text_center(
            screen,
            "Your Fleet",
            Config.PLAY_BOARD_OFFSET_X + Config.PLAYING_GRID_WIDTH // 2,
            Config.PLAY_BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT,
            )
            draw_text_center(
                screen,
                "Enemy Waters",
                Config.PLAY_ENEMY_OFFSET_X + Config.PLAYING_GRID_WIDTH // 2,
                Config.PLAY_BOARD_OFFSET_Y - 30 + Config.TOP_BAR_HEIGHT,
            )
            # Overlay placed ships & markers
            for ship in state.placed_ships:
            # 1) top-left grid cell of this ship
                coords = ship.coords
                r0, c0 = min(coords, key=lambda rc: (rc[0], rc[1]))
                size    = len(coords)

                # 2) horizontal if all in same row
                horiz = all(r == coords[0][0] for r, _ in coords)

                # 3) compute scaled pixel dims
                w = size * self.cell_size if horiz else self.cell_size
                h = self.cell_size       if horiz else size * self.cell_size

                # 4) scale the sprite into those smaller cells
                img_scaled = pygame.transform.smoothscale(ship.image, (w, h))

                # 5) blit at the 90%-sized grid position
                x = Config.PLAY_BOARD_OFFSET_X + c0 * self.cell_size
                y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r0 * self.cell_size
                screen.blit(img_scaled, (x, y))
                
            for r in range(Config.GRID_SIZE):
                for c in range(Config.GRID_SIZE):
                    if state.player_board[r][c] == Cell.HIT:
                        px = Config.PLAY_BOARD_OFFSET_X + c*self.cell_size + self.cell_size//2
                        py = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + r*self.cell_size + self.cell_size//2
                        draw_x(screen, px, py, self.cell_size)

    def _reveal_sunk_standard(self, screen, state):
        """
        Reveal ships on the computer board once all their cells are HIT,
        using the exact coords recorded in state.computer_ships_coords.
        """
        cs = self.cell_size
        top_y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT

        for coords in state.computer_ships_coords:
            # have all cells of this ship been hit?
            if all(state.computer_board[r][c] == Cell.HIT for (r, c) in coords):
                # compute bounding box
                rows = [r for r, _ in coords]
                cols = [c for _, c in coords]
                min_r, max_r = min(rows), max(rows)
                min_c, max_c = min(cols), max(cols)

                # determine orientation and size
                size = len(coords)
                horiz = (min_r == max_r)

                # create & orient sprite
                ship = DraggableShip(size, 0, 0)
                if not horiz:
                    ship.rotate()

                # scale to playing‐cell size
                w = size * cs if horiz else cs
                h = cs       if horiz else size * cs
                img_scaled = pygame.transform.smoothscale(ship.image, (w, h))

                # compute pixel position
                x = Config.PLAY_ENEMY_OFFSET_X + min_c * cs
                y = top_y + min_r * cs
                screen.blit(img_scaled, (x, y))

    def _draw_endgame(self, screen, msg):
        draw_text_center(screen, msg, Config.WIDTH//2, Config.HEIGHT//2 - 50)
        draw_button(screen, "Restart",
                    Config.WIDTH//2 - 75, Config.HEIGHT//2,
                    150, 50, Config.GREEN, Config.DARK_GREEN,
                    self.logic.state.reset_all,3)

    def _draw_effects(self, screen, state):
        now = pygame.time.get_ticks()

        # ─── Explosions ─────────────────────────────────────────
        for exp in state.explosions[:]:
            elapsed = now - exp["time"]
            offx = Config.PLAY_BOARD_OFFSET_X if exp["board_idx"]==0 else Config.PLAY_ENEMY_OFFSET_X
            x = offx + exp["col"] * self.cell_size
            y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + exp["row"] * self.cell_size

            if elapsed < Config.EXPLOSION_FADE_DURATION:
                img   = Config.EXPLOSION_IMG.copy()
                alpha = int(255 * (1 - elapsed/Config.EXPLOSION_FADE_DURATION))
                img.set_alpha(alpha)
                screen.blit(img, (x, y))
            else:
                # **Drop the draw_x call** (we’ll get it for free in draw_grid) :contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}
                state.explosions.remove(exp)

        # ─── Miss splashes ───────────────────────────────────────
        for ms in state.miss_splashes[:]:
            elapsed = now - ms["time"]
            offx = Config.PLAY_BOARD_OFFSET_X if ms["board_idx"]==0 else Config.PLAY_ENEMY_OFFSET_X
            x = offx + ms["col"] * self.cell_size
            y = Config.PLAY_BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT + ms["row"] * self.cell_size

            if elapsed < Config.MISS_FADE_DURATION:
                img   = Config.MISS_IMG.copy()
                alpha = int(255 * (1 - elapsed/Config.MISS_FADE_DURATION))
                img.set_alpha(alpha)
                screen.blit(img, (x, y))
            else:
                state.miss_splashes.remove(ms)
