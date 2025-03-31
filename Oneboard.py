import pygame
import random
import sys
import time
from config import Config
from board import create_board, place_ship_randomly
from ui import draw_grid, draw_text_center, draw_button, draw_text_input_box

pygame.init()

# === Pygame Setup ===
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Battleship")
background = pygame.image.load("image.jpeg")
background = pygame.transform.smoothscale(background, (Config.WIDTH, Config.HEIGHT))

# === Game State ===
game_state = "menu"
user_text = ""
player_name = ""
ship_index = 0
orientation = 'h'
placed_ships = []
ai_turn_pending = False
ai_turn_start_time = 0

# === Boards ===
player_board = create_board()
computer_board = create_board()
player_attacks = [['' for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]

for size in Config.SHIP_SIZES:
    place_ship_randomly(computer_board, size)

# === Button Actions ===
def start_game():
    global game_state
    game_state = "placing"

def show_settings():
    global game_state
    game_state = "settings"

def toggle_orientation():
    global orientation
    orientation = 'v' if orientation == 'h' else 'h'

def undo_last_ship():
    global ship_index
    if placed_ships:
        ship = placed_ships.pop()
        for row, col in ship:
            player_board[row][col] = 'O'
        ship_index -= 1

def restart_game():
    global game_state, player_board, computer_board, player_attacks, ship_index, placed_ships
    global player_ships, computer_ships, orientation, ai_turn_pending
    game_state = "menu"
    player_board = create_board()
    computer_board = create_board()
    player_attacks = [['' for _ in range(Config.GRID_SIZE)] for _ in range(Config.GRID_SIZE)]
    ship_index = 0
    placed_ships.clear()
    orientation = 'h'
    ai_turn_pending = False
    for size in Config.SHIP_SIZES:
        place_ship_randomly(computer_board, size)
    player_ships = 0
    computer_ships = sum(row.count('S') for row in computer_board)

def get_grid_pos(pos, offset_x, offset_y):
    mx, my = pos
    col = (mx - offset_x) // Config.CELL_SIZE
    row = (my - offset_y) // Config.CELL_SIZE
    if 0 <= row < Config.GRID_SIZE and 0 <= col < Config.GRID_SIZE:
        return row, col
    return None, None

# === Main Loop ===
running = True
player_ships = 0
computer_ships = sum(row.count('S') for row in computer_board)

while running:
    screen.blit(background, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "settings":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and user_text.strip():
                    player_name = user_text.strip()
                    user_text = ""
                    game_state = "placing"
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    if len(user_text) < 15:
                        user_text += event.unicode

        elif game_state == "placing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            row, col = get_grid_pos(event.pos, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row is not None and ship_index < len(Config.SHIP_SIZES):
                size = Config.SHIP_SIZES[ship_index]
                coords = []
                fits = True
                if orientation == 'h':
                    if col + size > Config.GRID_SIZE:
                        fits = False
                    else:
                        for i in range(size):
                            if player_board[row][col + i] != 'O':
                                fits = False
                                break
                        if fits:
                            for i in range(size):
                                player_board[row][col + i] = 'S'
                                coords.append((row, col + i))
                else:
                    if row + size > Config.GRID_SIZE:
                        fits = False
                    else:
                        for i in range(size):
                            if player_board[row + i][col] != 'O':
                                fits = False
                                break
                        if fits:
                            for i in range(size):
                                player_board[row + i][col] = 'S'
                                coords.append((row + i, col))
                if fits:
                    placed_ships.append(coords)
                    ship_index += 1
                    if ship_index == len(Config.SHIP_SIZES):
                        game_state = "playing"
                        player_ships = sum(row.count('S') for row in player_board)

        elif game_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not ai_turn_pending:
            row, col = get_grid_pos(event.pos, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y)
            if row is not None and player_attacks[row][col] == '':
                if computer_board[row][col] == 'S':
                    player_attacks[row][col] = 'X'
                    computer_board[row][col] = 'X'
                    computer_ships -= 1
                else:
                    player_attacks[row][col] = 'M'
                ai_turn_pending = True
                ai_turn_start_time = current_time

    if ai_turn_pending and current_time - ai_turn_start_time >= 1000:
        while True:
            r, c = random.randint(0, 9), random.randint(0, 9)
            if player_board[r][c] in ['O', 'S']:
                if player_board[r][c] == 'S':
                    player_board[r][c] = 'X'
                    player_ships -= 1
                else:
                    player_board[r][c] = 'M'
                break
        ai_turn_pending = False

    if game_state == "menu":
        draw_button(screen, "Play", Config.WIDTH // 2 - 75, Config.HEIGHT // 2 - 50, 150, 50, Config.GREEN, Config.DARK_GREEN, start_game)
        draw_button(screen, "Settings", Config.WIDTH // 2 - 75, Config.HEIGHT // 2 + 20, 150, 50, Config.GRAY, Config.DARK_GRAY, show_settings)

    elif game_state == "settings":
        draw_text_input_box(screen, user_text)

    elif game_state == "placing":
        draw_grid(screen, player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y, show_ships=True)
        draw_text_center(screen, f"Place ship of length {Config.SHIP_SIZES[ship_index]} ({'H' if orientation == 'h' else 'V'})", Config.WIDTH // 2, 50)
        draw_button(screen, "Toggle H/V", Config.WIDTH - 160, 50, 140, 40, Config.GRAY, Config.DARK_GRAY, toggle_orientation)
        draw_button(screen, "Undo Last Ship", Config.WIDTH - 160, 100, 140, 40, Config.GRAY, Config.DARK_GRAY, undo_last_ship)

    elif game_state == "playing":
        draw_text_center(screen, "Your Fleet", Config.BOARD_OFFSET_X + Config.GRID_WIDTH // 2, Config.BOARD_OFFSET_Y - 30)
        draw_text_center(screen, "Enemy Waters", Config.ENEMY_OFFSET_X + Config.GRID_WIDTH // 2, Config.BOARD_OFFSET_Y - 30)
        draw_grid(screen, player_board, Config.BOARD_OFFSET_X, Config.BOARD_OFFSET_Y, show_ships=True)
        draw_grid(screen, player_attacks, Config.ENEMY_OFFSET_X, Config.BOARD_OFFSET_Y)
        draw_text_center(screen, f"Admiral {player_name}", 100, 20)
        if computer_ships == 0:
            draw_text_center(screen, f"{player_name or 'You'} win! Click Restart", Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart", Config.WIDTH // 2 - 75, Config.HEIGHT // 2, 150, 50, Config.GREEN, Config.DARK_GREEN, restart_game)
        elif player_ships == 0:
            draw_text_center(screen, f"{player_name or 'You'} lost! Click Restart", Config.WIDTH // 2, Config.HEIGHT // 2 - 50)
            draw_button(screen, "Restart", Config.WIDTH // 2 - 75, Config.HEIGHT // 2, 150, 50, Config.GREEN, Config.DARK_GREEN, restart_game)

    pygame.display.flip()

pygame.quit()
sys.exit()
