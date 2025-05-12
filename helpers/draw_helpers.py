import pygame
from core.config import Config
from game.board_helpers import Cell

# ─── Load Ship Images ─────────────────────────────────────────────────────────
ship_images = {
    5: pygame.image.load("resources/images/ShipBattleshipHull.png"),
    4: pygame.image.load("resources/images/ShipSubMarineHull.png"),
    3: pygame.image.load("resources/images/ShipDestroyerHull.png")
}

# Resize images to fit grid
for size in ship_images:
    ship_images[size] = pygame.transform.scale(
        ship_images[size],
        (Config.CELL_SIZE, Config.CELL_SIZE * size)
    )

def draw_text_center(screen, text, x, y, size, color=Config.WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_button(screen, label, x, y, w, h, color, hover_color, on_click_fn):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    button_rect = pygame.Rect(x, y, w, h)
    is_hovered = button_rect.collidepoint(mouse)

    pygame.draw.rect(screen, hover_color if is_hovered else color, button_rect)
    pygame.draw.rect(screen, Config.BLACK, button_rect, 2)

    draw_text_center(screen, label, x + w // 2, y + h // 2, 24)

    if is_hovered and click[0]:
        on_click_fn()

def draw_grid(screen, board, offset_x, offset_y, show_ships=False):
    placed_ships = set()

    for row in range(Config.GRID_SIZE):
        for col in range(Config.GRID_SIZE):
            x = offset_x + col * Config.CELL_SIZE
            y = offset_y + row * Config.CELL_SIZE
            rect = pygame.Rect(x, y, Config.CELL_SIZE, Config.CELL_SIZE)
            cell_value = board[row][col]

            # Draw grid outline first
            pygame.draw.rect(screen, Config.WHITE, rect, 1)

            # Draw ship if it's part of a new unprocessed one
            if show_ships and cell_value in (Cell.SHIP, Cell.HIT) and (row, col) not in placed_ships:
                length = detect_ship_length(board, row, col)
                if length in ship_images:
                    image = ship_images[length]
                    screen.blit(image, (x, y))
                    # Mark the whole ship so it's only drawn once
                    for i in range(length):
                        placed_ships.add((row + i, col))

            # Draw hit (on top of ship)
            if cell_value == Cell.HIT:
                pygame.draw.line(screen, Config.RED, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, Config.RED, rect.topright, rect.bottomleft, 2)

            # Draw miss
            elif cell_value == Cell.MISS:
                pygame.draw.circle(screen, Config.BLUE, rect.center, 5)

def detect_ship_length(board, row, col):
    length = 1
    for i in range(1, Config.GRID_SIZE - row):
        if board[row + i][col] == Cell.SHIP or board[row + i][col] == Cell.HIT:
            length += 1
        else:
            break
    return length

def draw_top_bar(screen, state):
    draw_text_center(screen, "Admiral", 100, 30, 28)
    draw_text_center(screen, "Audio: On" if state.audio_enabled else "Audio: Off", Config.WIDTH - 130, 30, 24)
    draw_button(screen, "Restart", 20, 10, 100, 40, Config.GREEN, Config.DARK_GREEN, lambda: setattr(state, "show_restart_modal", True))
    draw_button(screen, "Close", Config.WIDTH - 120, 10, 100, 40, Config.RED, Config.DARK_RED, lambda: setattr(state, "show_quit_modal", True))

def draw_modal(screen, title, subtitle, on_yes, on_no, yes_text="Yes", no_text="No"):
    modal_rect = pygame.Rect(Config.WIDTH // 2 - 150, Config.HEIGHT // 2 - 100, 300, 200)
    pygame.draw.rect(screen, Config.DARK_GRAY, modal_rect)
    pygame.draw.rect(screen, Config.WHITE, modal_rect, 2)

    draw_text_center(screen, title, Config.WIDTH // 2, Config.HEIGHT // 2 - 60, 28)
    draw_text_center(screen, subtitle, Config.WIDTH // 2, Config.HEIGHT // 2 - 30, 20)

    draw_button(screen, yes_text, Config.WIDTH // 2 - 120, Config.HEIGHT // 2 + 40, 80, 40, Config.GRAY, Config.DARK_GRAY, on_yes)
    draw_button(screen, no_text,  Config.WIDTH // 2 + 40, Config.HEIGHT // 2 + 40, 80, 40, Config.GRAY, Config.DARK_GRAY, on_no)
