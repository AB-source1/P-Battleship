import pygame
import random
import sys
import time

pygame.init()

# === CONFIG ===
WIDTH, HEIGHT = 1000, 600
GRID_SIZE = 10
SHIP_SIZES = [5, 4, 3]
CELL_SIZE = 40
GRID_WIDTH = GRID_SIZE * CELL_SIZE

# Centering and layout
space_between = 100
board_offset_x = (WIDTH - (2 * GRID_WIDTH + space_between)) // 2
enemy_offset_x = board_offset_x + GRID_WIDTH + space_between
board_offset_y = (HEIGHT - GRID_WIDTH) // 2

# === Pygame Setup ===
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship")
background = pygame.image.load("image.jpeg")
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

# === Colors ===
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 180, 0)
GRAY = (70, 70, 70)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

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
def create_board():
    return [['O' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

player_board = create_board()
computer_board = create_board()
player_attacks = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def place_ship_randomly(board, size):
    while True:
        orientation = random.choice(['h', 'v'])
        if orientation == 'h':
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - size)
            if all(board[row][col + i] == 'O' for i in range(size)):
                for i in range(size):
                    board[row][col + i] = 'S'
                break
        else:
            row = random.randint(0, GRID_SIZE - size)
            col = random.randint(0, GRID_SIZE - 1)
            if all(board[row + i][col] == 'O' for i in range(size)):
                for i in range(size):
                    board[row + i][col] = 'S'
                break

for size in SHIP_SIZES:
    place_ship_randomly(computer_board, size)

# === Drawing ===
def draw_grid(board, offset_x, offset_y, show_ships=False):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = offset_x + col * CELL_SIZE
            y = offset_y + row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

            cell = board[row][col]
            if cell == 'M':
                pygame.draw.circle(screen, BLUE, rect.center, CELL_SIZE // 6)
            elif cell == 'X':
                pygame.draw.line(screen, RED, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, RED, rect.topright, rect.bottomleft, 2)
            elif show_ships and cell == 'S':
                pygame.draw.rect(screen, BLUE, rect.inflate(-4, -4))

def draw_text_center(text, x, y, font_size=30):
    font = pygame.font.SysFont(None, font_size)
    surface = font.render(text, True, WHITE)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

def draw_button(text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, hover_color if rect.collidepoint(mouse) else color, rect)
    font = pygame.font.SysFont(None, 30)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    if rect.collidepoint(mouse) and click[0] == 1 and action:
        action()

def draw_text_input_box():
    font = pygame.font.SysFont(None, 36)
    prompt = font.render("Enter your name:", True, WHITE)
    screen.blit(prompt, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
    input_box = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 40)
    pygame.draw.rect(screen, WHITE, input_box, 2)
    name_surface = font.render(user_text, True, WHITE)
    screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))

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
    player_attacks = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    ship_index = 0
    placed_ships.clear()
    orientation = 'h'
    ai_turn_pending = False
    for size in SHIP_SIZES:
        place_ship_randomly(computer_board, size)
    player_ships = 0
    computer_ships = sum(row.count('S') for row in computer_board)

def get_grid_pos(pos, offset_x, offset_y):
    mx, my = pos
    col = (mx - offset_x) // CELL_SIZE
    row = (my - offset_y) // CELL_SIZE
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
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
            row, col = get_grid_pos(event.pos, board_offset_x, board_offset_y)
            if row is not None and ship_index < len(SHIP_SIZES):
                size = SHIP_SIZES[ship_index]
                coords = []
                fits = True
                if orientation == 'h':
                    if col + size > GRID_SIZE:
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
                    if row + size > GRID_SIZE:
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
                    if ship_index == len(SHIP_SIZES):
                        game_state = "playing"
                        player_ships = sum(row.count('S') for row in player_board)

        elif game_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not ai_turn_pending:
            row, col = get_grid_pos(event.pos, enemy_offset_x, board_offset_y)
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

    # === Drawing Phase ===
    if game_state == "menu":
        draw_button("Play", WIDTH // 2 - 75, HEIGHT // 2 - 50, 150, 50, GREEN, DARK_GREEN, start_game)
        draw_button("Settings", WIDTH // 2 - 75, HEIGHT // 2 + 20, 150, 50, GRAY, DARK_GRAY, show_settings)

    elif game_state == "settings":
        draw_text_input_box()

    elif game_state == "placing":
        draw_grid(player_board, board_offset_x, board_offset_y, show_ships=True)
        draw_text_center(f"Place ship of length {SHIP_SIZES[ship_index]} ({'H' if orientation == 'h' else 'V'})", WIDTH // 2, 50)
        draw_button("Toggle H/V", WIDTH - 160, 50, 140, 40, GRAY, DARK_GRAY, toggle_orientation)
        draw_button("Undo Last Ship", WIDTH - 160, 100, 140, 40, GRAY, DARK_GRAY, undo_last_ship)

    elif game_state == "playing":
        draw_text_center("Your Fleet", board_offset_x + GRID_WIDTH // 2, board_offset_y - 30)
        draw_text_center("Enemy Waters", enemy_offset_x + GRID_WIDTH // 2, board_offset_y - 30)
        draw_grid(player_board, board_offset_x, board_offset_y, show_ships=True)
        draw_grid(player_attacks, enemy_offset_x, board_offset_y)
        draw_text_center(f"Admiral {player_name}", 100, 20)
        if computer_ships == 0:
            draw_text_center(f"{player_name or 'You'} win! Click Restart", WIDTH // 2, HEIGHT // 2 - 50)
            draw_button("Restart", WIDTH // 2 - 75, HEIGHT // 2, 150, 50, GREEN, DARK_GREEN, restart_game)
        elif player_ships == 0:
            draw_text_center(f"{player_name or 'You'} lost! Click Restart", WIDTH // 2, HEIGHT // 2 - 50)
            draw_button("Restart", WIDTH // 2 - 75, HEIGHT // 2, 150, 50, GREEN, DARK_GREEN, restart_game)

    pygame.display.flip()

pygame.quit()
sys.exit()