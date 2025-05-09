import pygame
from random import randint
from core.config import Config
from core.game_state import GameState
from game.board_helpers import Cell, get_grid_pos

class PlayingLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state  = state
        self.reset()

    def reset(self) -> None:
        """
        Clear any in-flight hunt-and-destroy data so Hard mode
        always starts in 'search' on a fresh game.
        """
        self.ai_mode            = 'search'     # 'search' or 'destroy'
        self.destroy_origin     = None         # first-hit coord
        self.destroy_directions = []           # orthogonal probes
        self.current_direction  = None         # locked-in (dr,dc)

    def handle_event(self, event: pygame.event.Event, state: GameState):
        # Player click logic
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not state.ai_turn_pending):

            row, col = get_grid_pos(
                event.pos,
                Config.ENEMY_OFFSET_X,
                Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT
            )
            if row is None or col is None:
                return
            if state.player_attacks[row][col] != Cell.EMPTY:
                return

            # 1) Timestamp & count the shot
            now = pygame.time.get_ticks()
            state.player_shots += 1
            state.player_shot_times.append(now)

            # 2) Resolve hit or miss
            if state.computer_board[row][col] == Cell.SHIP:
                state.player_hits += 1
                state.player_attacks[row][col]  = Cell.HIT
                state.computer_board[row][col]  = Cell.HIT
                state.computer_ships           -= 1
            else:
                state.player_attacks[row][col] = Cell.MISS

            # 3) Victory check
            if state.computer_ships == 0:
                state.winner     = "Player"
                state.game_state = "stats"
                return

            # 4) Schedule AI turn
            state.ai_turn_pending    = True
            state.ai_turn_start_time = now

    def handle_ai_turn(self, current_time: int) -> None:
        # Wait the “thinking” delay
        if (not self.state.ai_turn_pending
                or (current_time - self.state.ai_turn_start_time) < 1000):
            return

        diff = self.state.difficulty  # 'Easy', 'Medium', 'Hard'

        if diff == 'Easy':
            self._ai_shot_random(seed_next=False)

        elif diff == 'Medium':
            if self.state.ai_targets:
                self._ai_shot_from_targets()
            else:
                self._ai_shot_random(seed_next=True)

        else:  # Hard
            self._ai_advanced_shot()

        # Clear pending so player can act next
        self.state.ai_turn_pending = False

    # ─── Easy & Medium helpers ───

    def _ai_shot_random(self, seed_next: bool=False) -> None:
        size = Config.GRID_SIZE
        while True:
            r, c = randint(0, size-1), randint(0, size-1)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                # 1) Timestamp & count AI shot
                now = pygame.time.get_ticks()
                self.state.ai_shots += 1
                self.state.ai_shot_times.append(now)

                hit = (cell == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1

                # 2) Apply result
                self._apply_shot_result(r, c, hit, seed_next)

                # 3) Victory check
                if hit and self.state.player_ships == 0:
                    self.state.winner     = "AI"
                    self.state.game_state = "stats"
                break

    def _ai_shot_from_targets(self) -> None:
        while self.state.ai_targets:
            r, c = self.state.ai_targets.pop(0)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                # 1) Timestamp & count AI shot
                now = pygame.time.get_ticks()
                self.state.ai_shots += 1
                self.state.ai_shot_times.append(now)

                hit = (cell == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1

                # 2) Apply result
                self._apply_shot_result(r, c, hit, seed_next=True)

                # 3) Victory check
                if hit and self.state.player_ships == 0:
                    self.state.winner     = "AI"
                    self.state.game_state = "stats"
                return

        # Fallback
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

    # ─── Hard-mode: Advanced hunt-and-destroy ───

    def _ai_advanced_shot(self) -> None:
        if self.ai_mode == 'search':
            # Initial random shot (with result)
            r, c = None, None
            # reuse _ai_shot_random to record stats:
            # but we need hit result and coords, so:
            while True:
                rr, cc = randint(0, Config.GRID_SIZE-1), randint(0, Config.GRID_SIZE-1)
                cell = self.state.player_board[rr][cc]
                if cell in (Cell.EMPTY, Cell.SHIP):
                    now = pygame.time.get_ticks()
                    self.state.ai_shots += 1
                    self.state.ai_shot_times.append(now)
                    hit = (cell == Cell.SHIP)
                    if hit: self.state.ai_hits += 1
                    self._apply_shot_result(rr, cc, hit, seed_next=True)
                    r, c = rr, cc
                    if hit:
                        # enter destroy
                        self.ai_mode            = 'destroy'
                        self.destroy_origin     = (r, c)
                        self.destroy_directions = [(-1,0),(1,0),(0,-1),(0,1)]
                        self.current_direction  = None
                    if hit and self.state.player_ships == 0:
                        self.state.winner     = "AI"
                        self.state.game_state = "stats"
                    break
        else:
            # destroy mode
            if self.current_direction is None:
                # probe each direction once
                while self.destroy_directions:
                    dr, dc = self.destroy_directions.pop(0)
                    r0, c0 = self.destroy_origin
                    nr, nc = r0+dr, c0+dc
                    if self._valid_target(nr, nc):
                        # shot with stats
                        now = pygame.time.get_ticks()
                        self.state.ai_shots += 1
                        self.state.ai_shot_times.append(now)
                        hit = (self.state.player_board[nr][nc] == Cell.SHIP)
                        if hit: self.state.ai_hits += 1
                        self._apply_shot_result(nr, nc, hit, seed_next=False)
                        if hit:
                            self.current_direction = (dr, dc)
                        if hit and self.state.player_ships == 0:
                            self.state.winner     = "AI"
                            self.state.game_state = "stats"
                        return
                # no directions → reset to search
                self._reset_destroy_mode()
                self._ai_shot_random(seed_next=True)
                return

            # follow locked direction
            dr, dc = self.current_direction
            lr, lc = self.state.last_player_hit
            nr, nc = lr+dr, lc+dc
            if self._valid_target(nr, nc):
                now = pygame.time.get_ticks()
                self.state.ai_shots += 1
                self.state.ai_shot_times.append(now)
                hit = (self.state.player_board[nr][nc] == Cell.SHIP)
                if hit: self.state.ai_hits += 1
                self._apply_shot_result(nr, nc, hit, seed_next=False)
                if hit:
                    if self.state.player_ships == 0:
                        self.state.winner     = "AI"
                        self.state.game_state = "stats"
                    return
                # reverse direction
                odr, odc = -dr, -dc
                self.current_direction      = (odr, odc)
                self.state.last_player_hit  = self.destroy_origin
                rr, rc = self.destroy_origin[0]+odr, self.destroy_origin[1]+odc
                if self._valid_target(rr, rc):
                    now = pygame.time.get_ticks()
                    self.state.ai_shots += 1
                    self.state.ai_shot_times.append(now)
                    hit = (self.state.player_board[rr][rc] == Cell.SHIP)
                    if hit: self.state.ai_hits += 1
                    self._apply_shot_result(rr, rc, hit, seed_next=False)
                    if hit and self.state.player_ships == 0:
                        self.state.winner     = "AI"
                        self.state.game_state = "stats"

            # done destroying
            self._reset_destroy_mode()
            self._ai_shot_random(seed_next=True)

    def _valid_target(self, r:int, c:int) -> bool:
        return (0 <= r < Config.GRID_SIZE
                and 0 <= c < Config.GRID_SIZE
                and self.state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP))

    def _reset_destroy_mode(self) -> None:
        self.ai_mode            = 'search'
        self.destroy_origin     = None
        self.destroy_directions = []
        self.current_direction  = None
