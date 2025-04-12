import pygame
from DraggableShip import DraggableShip
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box
from config import Config
from game_state import GameState
from util import get_grid_pos


class PlacingScreen:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state
        self.orientation = 'h'
        self.draggable_ships = [DraggableShip(
            size, 100 + Config.GRID_WIDTH, 100 + i * 60) for i, size in enumerate(Config.SHIP_SIZES)]
        self.placed_ships = []
    def toggle_orientation(self):
        self.orientation = 'v' if self.orientation == 'h' else 'h'

    def undo_last_ship(self):
        if len (self.placed_ships)>0:
            ship = self.placed_ships.pop()
            for row, col in ship:
                self.state.player_board[row][col] = 'O'
            self.draggable_ships.append(DraggableShip(len(ship), 200, 200)) #TODO store original ship in placed ships
            
    def checkLastship(self,state:GameState):
        if len(self.draggable_ships) == 0:
            state.game_state = "playing"
            state.player_ships = state.count_ships(state.player_board)

    def placeShip(self, row, col, ship, state: GameState):
        if row is not None and len(self.draggable_ships) > 0:
            size = ship.size
            coords = []
            fits = True
            if self.orientation == 'h':
                if col + size > Config.GRID_SIZE:
                    fits = False
                else:
                    for i in range(size):
                        if state.player_board[row][col + i] != 'O':
                            fits = False
                            break
                    if fits:
                        for i in range(size):
                            state.player_board[row][col + i] = 'S'
                            coords.append((row, col + i))
            else:
                if row + size > Config.GRID_SIZE:
                    fits = False
                else:
                    for i in range(size):
                        if state.player_board[row + i][col] != 'O':
                            fits = False
                            break
                    if fits:
                        for i in range(size):
                            state.player_board[row + i][col] = 'S'
                            coords.append((row + i, col))
            if fits:
                self.placed_ships.append(coords)
                self.draggable_ships.remove(ship)
                self.checkLastship(state)
        return

    def draw_preview(self,cells, screen, valid):
        for row, col in cells:
            x = Config.BOARD_OFFSET_X + col * Config.CELL_SIZE
            y = Config.BOARD_OFFSET_Y + row * Config.CELL_SIZE
            s = pygame.Surface((Config.CELL_SIZE,Config.CELL_SIZE), pygame.SRCALPHA)
            s.fill(Config.PREVIEW_GREEN if valid else Config.PREVIEW_RED)
            screen.blit(s, (x, y))

    def tryStartDragging(self, event: pygame.event, state: GameState):
        for ship in self.draggable_ships:
            if ship.rect.collidepoint(event.pos) and not ship.dragging:
                ship.dragging = True
        return

    def handleEvent(self, event: pygame.event, state: GameState):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            row, col = get_grid_pos(
                event.pos, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row != None and col != None:
                self.placeShip(row, col, self.draggable_ships[0], state)
            else:
                self.tryStartDragging(event, state)
        elif event.type == pygame.MOUSEMOTION:
            for ship in self.draggable_ships:
                if ship.dragging:
                    ship.update_position(*event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for ship in self.draggable_ships:
                if ship.dragging:
                    ship.dragging = False
                    preview_cells = ship.get_preview_cells(Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
                    if preview_cells:
                        valid = all(state.player_board[r][c] == 'O' for r, c in preview_cells)
                        if valid:
                            (row, col) = preview_cells[0]
                            self.placeShip(row, col,ship,state)
                            break
            

        return

    def draw(self, screen, state: GameState):

        draw_grid(screen, state.player_board, Config.BOARD_OFFSET_X,
                  Config.BOARD_OFFSET_Y, show_ships=True)
        if len(self.draggable_ships) > 0:
            draw_text_center(
            screen, f"Place ship of length {self.draggable_ships[0].size} ({'H' if self.orientation == 'h' else 'V'})", Config.WIDTH // 2, 50)
        draw_button(screen, "Toggle H/V", Config.WIDTH - 160, 50, 140,
                    40, Config.GRAY, Config.DARK_GRAY, self.toggle_orientation)
        draw_button(screen, "Undo Last Ship", Config.WIDTH - 160, 100,
                    140, 40, Config.GRAY, Config.DARK_GRAY, self.undo_last_ship)
        for ship in self.draggable_ships:
            if ship.dragging:
                cells = ship.get_preview_cells(Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
                if cells:
                    valid = all(state.player_board[r][c] == 'O' for r, c in cells)
                    self.draw_preview(cells, screen, valid)
            ship.draw(screen)


        return
