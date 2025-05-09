import pygame
from random import randint
from core.config import Config
from core.game_state import GameState
from game.board_helpers import Cell, get_grid_pos

class PlayingLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state  = state

        # Reset AI hunt/destroy state on creation
        self.reset()

    def reset(self) -> None:
        """
        Clear out any in-flight hunt-and-destroy data so
        Hard mode always starts in 'search' on a fresh game.
        """
        self.ai_mode           = 'search'    # or 'destroy'
        self.destroy_origin    = None        # first‐hit coord
        self.destroy_directions = []         # orthogonal probes
        self.current_direction = None        # locked‐in (dr,dc)

    def handle_event(self, event: pygame.event.Event, state: GameState):
        # ─── Player click logic ───
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not state.ai_turn_pending):

            row, col = get_grid_pos(
                event.pos,
                Config.ENEMY_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT
            )

            if row is not None and col is not None and state.player_attacks[row][col] == Cell.EMPTY:
                # ① Count this shot
                state.player_shots += 1

                if state.computer_board[row][col] == Cell.SHIP:
                    # ② It’s a hit!
                    state.player_hits += 1
                    state.player_attacks[row][col]   = Cell.HIT
                    state.computer_board[row][col]  = Cell.HIT
                    state.computer_ships           -= 1
                else:
                    # ③ Miss
                    state.player_attacks[row][col] = Cell.MISS

                # ④ Check for end-of-game (you sank all)
                if state.computer_ships == 0:
                    state.game_state = "stats"
                    return

                # ⑤ Else schedule AI turn
                state.ai_turn_pending    = True
                state.ai_turn_start_time = pygame.time.get_ticks()

    def handle_ai_turn(self, current_time: int) -> None:
        # ─── Delay until 1s has passed ───
        if (not self.state.ai_turn_pending
                or (current_time - self.state.ai_turn_start_time) < 1000):
            return

        diff = self.state.difficulty  # 'Easy'/'Medium'/'Hard'

        if diff == 'Easy':
            self._ai_shot_random(seed_next=False)
        elif diff == 'Medium':
            if self.state.ai_targets:
                self._ai_shot_from_targets()
            else:
                self._ai_shot_random(seed_next=True)
        else:
            self._ai_advanced_shot()

        # Clear flag so player can act next
        self.state.ai_turn_pending = False

    # ─── Easy & Medium helpers (unchanged except stats bump) ───

    def _ai_shot_random(self, seed_next: bool=False) -> None:
        size = Config.GRID_SIZE
        while True:
            r = randint(0, size - 1)
            c = randint(0, size - 1)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                # ① Count this AI shot
                self.state.ai_shots += 1

                hit = (cell == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1  # AI got a hit!
                # ② Mark it
                self._apply_shot_result(r, c, hit, seed_next)
                # ③ If AI just sank your last ship, go to stats
                if hit and self.state.player_ships == 0:
                    self.state.game_state = "stats"
                break

    def _ai_shot_from_targets(self) -> None:
        while self.state.ai_targets:
            r, c = self.state.ai_targets.pop(0)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                self.state.ai_shots += 1
                hit = (cell == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1
                self._apply_shot_result(r, c, hit, seed_next=True)
                if hit and self.state.player_ships == 0:
                    self.state.game_state = "stats"
                return
        # fallback
        self._ai_shot_random(seed_next=True)

    def _apply_shot_result(self, r:int, c:int, hit:bool, seed_next:bool) -> None:
        if hit:
            self.state.player_board[r][c] = Cell.HIT
            self.state.player_ships     -= 1
            self.state.last_player_hit   = (r, c)
            if seed_next:
                self._enqueue_adjacent(r, c)
        else:
            self.state.player_board[r][c] = Cell.MISS

    def _enqueue_adjacent(self, r:int, c:int) -> None:
        size = Config.GRID_SIZE
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if (0 <= nr < size and 0 <= nc < size
                    and self.state.player_board[nr][nc] == Cell.EMPTY
                    and (nr,nc) not in self.state.ai_targets):
                self.state.ai_targets.append((nr, nc))

    # ─── Hard-mode: Advanced hunt-&-destroy ───

    def _ai_advanced_shot(self) -> None:
        """
        1) 'search': random shots until a hit
        2) 'destroy': probe all 4 dirs, lock orientation, then follow line
                     (even reversing at end) until ship sinks
        """
        if self.ai_mode == 'search':
            r, c, hit = self._ai_shot_random_with_result()
            if hit:
                self.ai_mode            = 'destroy'
                self.destroy_origin     = (r, c)
                self.destroy_directions = [(-1,0),(1,0),(0,-1),(0,1)]
                self.current_direction  = None

        else:  # destroy mode
            # Probe each direction to find orientation
            if self.current_direction is None:
                while self.destroy_directions:
                    dr, dc = self.destroy_directions.pop(0)
                    r0, c0 = self.destroy_origin
                    nr, nc = r0+dr, c0+dc
                    if self._valid_target(nr, nc):
                        hit = self._shoot_cell(nr, nc)
                        if hit:
                            self.current_direction = (dr, dc)
                        return
                # no valid probe → abort destroy
                self._reset_destroy_mode()
                self._ai_shot_random(seed_next=True)
                return

            # Follow the locked direction
            dr, dc      = self.current_direction
            lr, lc      = self.state.last_player_hit
            nr, nc      = lr+dr, lc+dc
            if self._valid_target(nr, nc):
                hit = self._shoot_cell(nr, nc)
                if hit:
                    return  # keep going
                # overshoot → reverse
                odr, odc = -dr, -dc
                self.current_direction = (odr, odc)
                self.state.last_player_hit = self.destroy_origin
                rr, rc = self.destroy_origin[0]+odr, self.destroy_origin[1]+odc
                if self._valid_target(rr, rc):
                    self._shoot_cell(rr, rc)

            # Done with this ship
            self._reset_destroy_mode()
            self._ai_shot_random(seed_next=True)

    def _ai_shot_random_with_result(self) -> tuple[int,int,bool]:
        """
        Like _ai_shot_random, but returns (r,c,hit) so advanced logic
        can transition to destroy mode.
        """
        size = Config.GRID_SIZE
        while True:
            r = randint(0, size - 1)
            c = randint(0, size - 1)
            if self.state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP):
                self.state.ai_shots += 1
                hit = (self.state.player_board[r][c] == Cell.SHIP)
                if hit: self.state.ai_hits += 1
                self._apply_shot_result(r, c, hit, seed_next=False)
                if hit and self.state.player_ships == 0:
                    self.state.game_state = "stats"
                return r, c, hit

    def _shoot_cell(self, r:int, c:int) -> bool:
        """
        Fire at (r,c). Return True on hit. Already counted in the caller.
        """
        if not self._valid_target(r, c):
            return False
        hit = (self.state.player_board[r][c] == Cell.SHIP)
        self._apply_shot_result(r, c, hit, seed_next=False)
        if hit and self.state.player_ships == 0:
            self.state.game_state = "stats"
        return hit

    def _valid_target(self, r:int, c:int) -> bool:
        size = Config.GRID_SIZE
        return (0 <= r < size and 0 <= c < size
                and self.state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP))

    def _reset_destroy_mode(self) -> None:
        self.ai_mode            = 'search'
        self.destroy_origin     = None
        self.destroy_directions = []
        self.current_direction  = None
