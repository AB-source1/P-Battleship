import pygame
from random import randint
from core.config import Config
from core.game_state import GameState
from game.board_helpers import Cell, get_grid_pos

class PlayingLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state

        # ① Initialize all AI‐mode state in one place
        self.reset()

    def reset(self) -> None:
        """
        Clear any in-flight hunt-and-destroy data so we always start
        the AI in pure 'search' mode on a fresh game.
        """
        self.ai_mode = 'search'            # either 'search' or 'destroy'
        self.destroy_origin = None         # (r,c) of first hit on a ship
        self.destroy_directions = []       # orthogonal deltas yet to try
        self.current_direction = None      # locked-in (dr,dc) once orientation found

    def handle_event(self, event: pygame.event.Event, state: GameState):
        # — Player click logic (unchanged) —
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not state.ai_turn_pending):

            row, col = get_grid_pos(
                event.pos,
                Config.ENEMY_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT
            )

            if row is not None and col is not None and state.player_attacks[row][col] == Cell.EMPTY:
                if state.computer_board[row][col] == Cell.SHIP:
                    state.player_attacks[row][col] = Cell.HIT
                    state.computer_board[row][col] = Cell.HIT
                    state.computer_ships -= 1
                else:
                    state.player_attacks[row][col] = Cell.MISS

                # schedule AI turn after 1s
                state.ai_turn_pending = True
                state.ai_turn_start_time = pygame.time.get_ticks()

    def handle_ai_turn(self, current_time: int) -> None:
        """
        Called each frame. After the 1s delay, fire according
        to the selected difficulty.
        """
        if (not self.state.ai_turn_pending
                or (current_time - self.state.ai_turn_start_time) < 1000):
            return

        diff = self.state.difficulty  # 'Easy', 'Medium', or 'Hard'

        if diff == 'Easy':
            # 🔴 Pure random shots
            self._ai_shot_random(seed_next=False)

        elif diff == 'Medium':
            # 🟡 Hunt‐once: random until hit, then try queued neighbors
            if self.state.ai_targets:
                self._ai_shot_from_targets()
            else:
                self._ai_shot_random(seed_next=True)

        else:
            # 🔵 Hard: advanced search → destroy
            self._ai_advanced_shot()

        # clear pending so player can move next
        self.state.ai_turn_pending = False


    # ───── Hard-mode: Advanced Hunt‐and‐Destroy ─────

    def _ai_advanced_shot(self) -> None:
        """
        Two sub-modes:
        - search: random until the first hit, then switch to destroy
        - destroy: probe all four directions, lock orientation, then follow
                   (even reversing at the end) until the ship is sunk
        """
        if self.ai_mode == 'search':
            r, c, hit = self._ai_shot_random_with_result()
            if hit:
                # 1) we hit: enter destroy mode
                self.ai_mode = 'destroy'
                self.destroy_origin = (r, c)
                self.destroy_directions = [(-1,0), (1,0), (0,-1), (0,1)]
                self.current_direction = None

        else:  # destroy mode
            # 2) If orientation unknown, probe each direction once
            if self.current_direction is None:
                while self.destroy_directions:
                    dr, dc = self.destroy_directions.pop(0)
                    r0, c0 = self.destroy_origin
                    nr, nc = r0 + dr, c0 + dc
                    if self._valid_target(nr, nc):
                        hit = self._shoot_cell(nr, nc)
                        if hit:
                            # orientation locked
                            self.current_direction = (dr, dc)
                        return

                # no valid adjacent direction → abort destroy
                self._reset_destroy_mode()
                self._ai_shot_random(seed_next=True)

            # 3) Follow the locked direction until we miss
            else:
                dr, dc = self.current_direction
                lr, lc = self.state.last_player_hit
                nr, nc = lr + dr, lc + dc

                if self._valid_target(nr, nc):
                    hit = self._shoot_cell(nr, nc)
                    if hit:
                        return  # keep going in same direction
                    else:
                        # overshoot → reverse once from origin
                        odr, odc = -dr, -dc
                        self.current_direction = (odr, odc)
                        self.state.last_player_hit = self.destroy_origin
                        rr, rc = self.destroy_origin[0] + odr, self.destroy_origin[1] + odc
                        if self._valid_target(rr, rc):
                            self._shoot_cell(rr, rc)

                # destroy complete
                self._reset_destroy_mode()
                self._ai_shot_random(seed_next=True)


    # ───── Core shooting helpers ─────

    def _ai_shot_random(self, seed_next: bool = False) -> None:
        size = Config.GRID_SIZE
        while True:
            r = randint(0, size - 1)
            c = randint(0, size - 1)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                hit = (cell == Cell.SHIP)
                self._apply_shot_result(r, c, hit, seed_next)
                break

    def _ai_shot_random_with_result(self) -> tuple[int,int,bool]:
        size = Config.GRID_SIZE
        while True:
            r = randint(0, size - 1)
            c = randint(0, size - 1)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                hit = (cell == Cell.SHIP)
                self._apply_shot_result(r, c, hit, seed_next=False)
                return r, c, hit

    def _shoot_cell(self, r: int, c: int) -> bool:
        if not self._valid_target(r, c):
            return False
        hit = (self.state.player_board[r][c] == Cell.SHIP)
        self._apply_shot_result(r, c, hit, seed_next=False)
        return hit

    def _apply_shot_result(self, r: int, c: int, hit: bool, seed_next: bool) -> None:
        if hit:
            self.state.player_board[r][c] = Cell.HIT
            self.state.player_ships -= 1
            self.state.last_player_hit = (r, c)
            if seed_next:
                self._enqueue_adjacent(r, c)
        else:
            self.state.player_board[r][c] = Cell.MISS

    def _valid_target(self, r: int, c: int) -> bool:
        size = Config.GRID_SIZE
        return (0 <= r < size and 0 <= c < size
                and self.state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP))


    # ───── Medium-mode helpers ─────

    def _ai_shot_from_targets(self) -> None:
        while self.state.ai_targets:
            r, c = self.state.ai_targets.pop(0)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                hit = (cell == Cell.SHIP)
                self._apply_shot_result(r, c, hit, seed_next=True)
                return
        self._ai_shot_random(seed_next=True)

    def _enqueue_adjacent(self, r: int, c: int) -> None:
        size = Config.GRID_SIZE
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < size and 0 <= nc < size
                    and self.state.player_board[nr][nc] == Cell.EMPTY
                    and (nr, nc) not in self.state.ai_targets):
                self.state.ai_targets.append((nr, nc))


    # ───── Cleanup ─────

    def _reset_destroy_mode(self) -> None:
        """
        Exit destroy mode and return to pure search.
        """
        self.ai_mode = 'search'
        self.destroy_origin = None
        self.destroy_directions = []
        self.current_direction = None
