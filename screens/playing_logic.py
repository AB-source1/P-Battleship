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
        Reset AI hunt/destroy state and initialize turn flags for both
        single-player and multiplayer modes.
        """
        # AI hunt-and-destroy state
        self.ai_mode            = 'search'
        self.destroy_origin     = None
        self.destroy_directions = []
        self.current_direction  = None

        # Multiplayer turn flags
        if self.state.network:
            # Host takes the first shot, client waits
            self.my_turn = bool(self.state.is_host)
        else:
            # Single-player: player always initiates
            self.my_turn = False

        self.awaiting_result = False

        # Clear any pending shot from previous match
        if hasattr(self.state, 'pending_shot'):
            del self.state.pending_shot
        
        self.state.play_start_time = pygame.time.get_ticks()

    def handle_event(self, event: pygame.event.Event, state: GameState):
        """
        Handle player clicks:
        - In multiplayer, queue a pending shot when it's our turn.
        - In single-player, resolve a shot against the AI.
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        row, col = get_grid_pos(
            event.pos,
            Config.ENEMY_OFFSET_X,
            Config.BOARD_OFFSET_Y + Config.TOP_BAR_HEIGHT
        )
        if row is None or col is None:
            return

        # Multiplayer click logic
        if state.network:
            # Only allow when it's our turn and cell is empty
            if not self.my_turn or state.player_attacks[row][col] != Cell.EMPTY:
                return

            now = pygame.time.get_ticks()
            state.player_shots += 1
            state.player_shot_times.append(now)

            # Queue the shot for network sending
            state.pending_shot = (row, col)
            self.my_turn = False
            return

        # Single-player click logic
        if not state.ai_turn_pending and state.player_attacks[row][col] == Cell.EMPTY:
            now = pygame.time.get_ticks()
            state.player_shots += 1
            state.player_shot_times.append(now)

            if state.computer_board[row][col] == Cell.SHIP:
                state.player_hits += 1
                state.player_attacks[row][col] = Cell.HIT
                state.computer_board[row][col] = Cell.HIT
                state.computer_ships -= 1
            else:
                state.player_attacks[row][col] = Cell.MISS

            # Check for player victory
            if state.computer_ships == 0:
                state.winner     = "Player"
                state.game_state = "stats"
                return

            # Schedule AI turn
            state.ai_turn_pending    = True
            state.ai_turn_start_time = now

    def handle_ai_turn(self, current_time: int) -> None:
        """
        Single-player AI logic after a fixed delay.
        Chooses behavior based on difficulty.
        """
        if (not self.state.ai_turn_pending or
            (current_time - self.state.ai_turn_start_time) < 1000):
            return

        diff = self.state.difficulty
        if diff == 'Easy':
            self._ai_shot_random(seed_next=False)
        elif diff == 'Medium':
            if self.state.ai_targets:
                self._ai_shot_from_targets()
            else:
                self._ai_shot_random(seed_next=True)
        else:  # Hard
            self._ai_advanced_shot()

        self.state.ai_turn_pending = False

    def handle_network_turn(self, current_time: int) -> None:
        """
        Multiplayer turn handling:
        - If we have a pending shot, send it and await a result.
        - Otherwise, receive opponent's shot and reply.
        """
        net = self.state.network
        if not net:
            return

        # 1) Send our pending shot and await the result
        if hasattr(self.state, 'pending_shot') and self.state.pending_shot:
            r, c = self.state.pending_shot
            if not self.awaiting_result:
                net.send({"type": "shot", "row": r, "col": c})
                self.awaiting_result = True
                return

            msg = net.recv()
            if msg and msg.get("type") == "result":
                hit = msg.get("hit", False)
                state_attacks = self.state.player_attacks
                state_attacks[r][c] = Cell.HIT if hit else Cell.MISS
                if hit:
                    self.state.player_hits += 1
                    self.state.computer_ships -= 1
                    if self.state.computer_ships == 0:
                        self.state.winner     = "Player"
                        self.state.game_state = "stats"
                self.awaiting_result = False
                del self.state.pending_shot
            return

        # 2) Receive opponent's shot and reply
        msg = net.recv()
        if not msg or msg.get("type") != "shot":
            return

        r, c = msg["row"], msg["col"]
        now = pygame.time.get_ticks()
        self.state.ai_shots += 1
        self.state.ai_shot_times.append(now)

        hit = (self.state.player_board[r][c] == Cell.SHIP)
        if hit:
            self.state.ai_hits += 1
        self._apply_shot_result(r, c, hit, seed_next=False)

        net.send({"type": "result", "hit": hit})

        # Check for opponent victory
        if hit and self.state.player_ships == 0:
            self.state.winner     = "AI"
            self.state.game_state = "stats"
            return

        # Now it's our turn
        self.my_turn = True

    # AI Helper Methods

    def _ai_shot_random(self, seed_next: bool=False) -> None:
        """
        Fire at a random untried cell.
        Optionally enqueue neighbors on a hit for hunt mode.
        """
        size = Config.GRID_SIZE
        while True:
            r, c = randint(0, size-1), randint(0, size-1)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                now = pygame.time.get_ticks()
                self.state.ai_shots += 1
                self.state.ai_shot_times.append(now)

                hit = (cell == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1
                self._apply_shot_result(r, c, hit, seed_next)

                if hit and self.state.player_ships == 0:
                    self.state.winner     = "AI"
                    self.state.game_state = "stats"
                break

    def _ai_shot_from_targets(self) -> None:
        """
        Fire at the next queued neighbor (hunt mode).
        """
        while self.state.ai_targets:
            r, c = self.state.ai_targets.pop(0)
            cell = self.state.player_board[r][c]
            if cell in (Cell.EMPTY, Cell.SHIP):
                now = pygame.time.get_ticks()
                self.state.ai_shots += 1
                self.state.ai_shot_times.append(now)

                hit = (cell == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1
                self._apply_shot_result(r, c, hit, seed_next=True)

                if hit and self.state.player_ships == 0:
                    self.state.winner     = "AI"
                    self.state.game_state = "stats"
                return
        # Fallback
        self._ai_shot_random(seed_next=True)

    def _apply_shot_result(self, r: int, c: int, hit: bool, seed_next: bool) -> None:
        """
        Mark result on player board for AI shots.
        """
        if hit:
            self.state.player_board[r][c] = Cell.HIT
            self.state.player_ships -= 1
            self.state.last_player_hit = (r, c)
            if seed_next:
                self._enqueue_adjacent(r, c)
        else:
            self.state.player_board[r][c] = Cell.MISS

    def _enqueue_adjacent(self, r: int, c: int) -> None:
        """
        Queue orthogonal neighbors for hunt mode.
        """
        size = Config.GRID_SIZE
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < size and 0 <= nc < size and
                self.state.player_board[nr][nc] == Cell.EMPTY and
                (nr, nc) not in self.state.ai_targets):
                self.state.ai_targets.append((nr, nc))

    def _ai_advanced_shot(self) -> None:
        """
        Hard mode: random until hit, then destroy by following ship orientation.
        """
        if self.ai_mode == 'search':
            # Initial random shot
            while True:
                rr, cc = randint(0, Config.GRID_SIZE-1), randint(0, Config.GRID_SIZE-1)
                cell = self.state.player_board[rr][cc]
                if cell in (Cell.EMPTY, Cell.SHIP):
                    now = pygame.time.get_ticks()
                    self.state.ai_shots += 1
                    self.state.ai_shot_times.append(now)

                    hit = (cell == Cell.SHIP)
                    if hit:
                        self.state.ai_hits += 1
                    self._apply_shot_result(rr, cc, hit, seed_next=True)

                    if hit:
                        self.ai_mode            = 'destroy'
                        self.destroy_origin     = (rr, cc)
                        self.destroy_directions = [(-1,0),(1,0),(0,-1),(0,1)]
                        self.current_direction  = None
                    if hit and self.state.player_ships == 0:
                        self.state.winner     = "AI"
                        self.state.game_state = "stats"
                    break
        else:
            # Destroy mode
            if self.current_direction is None:
                # Probe each direction once
                while self.destroy_directions:
                    dr, dc = self.destroy_directions.pop(0)
                    r0, c0 = self.destroy_origin
                    nr, nc = r0 + dr, c0 + dc
                    if self._valid_target(nr, nc):
                        now = pygame.time.get_ticks()
                        self.state.ai_shots += 1
                        self.state.ai_shot_times.append(now)

                        hit = (self.state.player_board[nr][nc] == Cell.SHIP)
                        if hit:
                            self.state.ai_hits += 1
                        self._apply_shot_result(nr, nc, hit, seed_next=False)

                        if hit:
                            self.current_direction = (dr, dc)
                        if hit and self.state.player_ships == 0:
                            self.state.winner     = "AI"
                            self.state.game_state = "stats"
                        return
                # No valid probes -> back to search
                self._reset_destroy_mode()
                self._ai_shot_random(seed_next=True)
                return

            # Follow locked direction
            dr, dc = self.current_direction
            lr, lc = self.state.last_player_hit
            nr, nc = lr + dr, lc + dc
            if self._valid_target(nr, nc):
                now = pygame.time.get_ticks()
                self.state.ai_shots += 1
                self.state.ai_shot_times.append(now)

                hit = (self.state.player_board[nr][nc] == Cell.SHIP)
                if hit:
                    self.state.ai_hits += 1
                self._apply_shot_result(nr, nc, hit, seed_next=False)

                if hit:
                    if self.state.player_ships == 0:
                        self.state.winner     = "AI"
                        self.state.game_state = "stats"
                    return

                # Reverse direction
                odr, odc = -dr, -dc
                self.current_direction     = (odr, odc)
                self.state.last_player_hit = self.destroy_origin
                rr, rc = self.destroy_origin[0] + odr, self.destroy_origin[1] + odc
                if self._valid_target(rr, rc):
                    now = pygame.time.get_ticks()
                    self.state.ai_shots += 1
                    self.state.ai_shot_times.append(now)

                    hit = (self.state.player_board[rr][rc] == Cell.SHIP)
                    if hit:
                        self.state.ai_hits += 1
                    self._apply_shot_result(rr, rc, hit, seed_next=False)
                    if hit and self.state.player_ships == 0:
                        self.state.winner     = "AI"
                        self.state.game_state = "stats"

            # Clean up and resume search
            self._reset_destroy_mode()
            self._ai_shot_random(seed_next=True)

    def _valid_target(self, r: int, c: int) -> bool:
        """
        True if cell at (r,c) is in bounds and unshot.
        """
        size = Config.GRID_SIZE
        return (0 <= r < size and 0 <= c < size
                and self.state.player_board[r][c] in (Cell.EMPTY, Cell.SHIP))

    def _reset_destroy_mode(self) -> None:
        """Reset from destroy mode back to pure search."""
        self.ai_mode            = 'search'
        self.destroy_origin     = None
        self.destroy_directions = []
        self.current_direction  = None
