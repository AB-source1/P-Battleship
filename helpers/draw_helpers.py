import sys
import pygame
from core.config import Config
from game.board_helpers import Cell

button_states = {}
hit_explosions = {}  # {(row, col): timestamp}


def draw_top_bar(screen, state):
    bar_rect = pygame.Rect(0, 0, Config.WIDTH, Config.TOP_BAR_HEIGHT)
    pygame.draw.rect(screen, Config.GRAY, bar_rect)

    y = 5  # Vertical offset inside the top bar

    draw_button(screen, "Restart", 10, y, 110, 30, Config.GREEN, Config.DARK_GREEN,
                lambda: setattr(state, 'show_restart_modal', True))

    audio_label = "Audio: On" if state.audio_enabled else "Audio: Off"
    draw_button(screen, audio_label, Config.WIDTH - 220, y, 120, 30,
                Config.GRAY, Config.DARK_GRAY,
                lambda: toggle_audio(state))

    draw_button(screen, "Close", Config.WIDTH - 100, y, 90, 30,
                Config.RED, Config.DARK_GRAY,
                lambda: setattr(state, 'show_quit_modal', True))


def toggle_audio(state):
    state.audio_enabled = not state.audio_enabled
    pygame.mixer.music.set_volume(1 if state.audio_enabled else 0)


def draw_button(screen, text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)

    pygame.draw.rect(screen, hover_color if rect.collidepoint(mouse) else color, rect)
    pygame.draw.rect(screen, (0, 31, 63), rect, 3)

    font = pygame.font.SysFont(None, 30)
    text_surf = font.render(text, True, Config.WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    key = f"{text}-{x}-{y}"
    if key not in button_states:
        button_states[key] = False

    if rect.collidepoint(mouse):
        if click[0] == 1 and not button_states[key]:
            button_states[key] = True
            if action:
                action()
        elif click[0] == 0:
            button_states[key] = False
    else:
        button_states[key] = False


def _cell_color(cell: Cell, show_ships: bool):
    if cell == Cell.HIT:
        return Config.RED
    elif cell == Cell.MISS:
        return Config.BLUE
    elif cell == Cell.SHIP and show_ships:
        return Config.BLUE
    return None


def draw_grid(screen, board, offset_x, offset_y, show_ships=False):
    # Load ocean and explosion images (after display is initialized)
    ocean_img = pygame.image.load("resources/Ocean.png").convert()
    ocean_bg = pygame.transform.scale(
        ocean_img,
        (Config.CELL_SIZE * Config.GRID_SIZE, Config.CELL_SIZE * Config.GRID_SIZE)
    )

    explosion_img = pygame.image.load("resources/images/explosion.png").convert_alpha()
    explosion_img = pygame.transform.scale(explosion_img, (Config.CELL_SIZE, Config.CELL_SIZE))

    # Draw ocean background under the board
    screen.blit(ocean_bg, (offset_x, offset_y))

    now = pygame.time.get_ticks()

    for row in range(Config.GRID_SIZE):
        for col in range(Config.GRID_SIZE):
            x = offset_x + col * Config.CELL_SIZE
            y = offset_y + row * Config.CELL_SIZE
            rect = pygame.Rect(x, y, Config.CELL_SIZE, Config.CELL_SIZE)
            pygame.draw.rect(screen, Config.WHITE, rect, 1)

            cell = board[row][col]

            if cell == Cell.HIT:
                key = (row, col)
                if key not in hit_explosions:
                    hit_explosions[key] = now

                if now - hit_explosions[key] <= 1000:
                    screen.blit(explosion_img, (x, y))
                else:
                    pygame.draw.line(screen, Config.RED, rect.topleft, rect.bottomright, 2)
                    pygame.draw.line(screen, Config.RED, rect.topright, rect.bottomleft, 2)

            elif cell == Cell.MISS:
                pygame.draw.circle(screen, Config.BLUE, rect.center, Config.CELL_SIZE // 6)

            elif cell == Cell.SHIP and show_ships:
                pygame.draw.rect(screen, Config.BLUE, rect.inflate(-4, -4))


def draw_text_center(screen, text, x, y, font_size=30):
    font = pygame.font.SysFont(None, font_size)
    surface = font.render(text, True, Config.WHITE)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def draw_modal(screen, title, subtitle, on_yes, on_no):
    overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    box_w, box_h = 400, 180
    box_rect = pygame.Rect((Config.WIDTH - box_w) // 2, (Config.HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(screen, Config.DARK_GRAY, box_rect)
    pygame.draw.rect(screen, Config.WHITE, box_rect, 2)

    draw_text_center(screen, title, box_rect.centerx, box_rect.y + 40, 36)
    draw_text_center(screen, subtitle, box_rect.centerx, box_rect.y + 80, 24)

    draw_button(screen, "Yes", box_rect.x + 60, box_rect.y + 120, 100, 40, Config.GREEN, Config.DARK_GREEN, on_yes)
    draw_button(screen, "No", box_rect.right - 160, box_rect.y + 120, 100, 40, Config.RED, Config.DARK_GRAY, on_no)


def draw_text_input_box(screen, user_text):
    font = pygame.font.SysFont(None, 36)
    prompt = font.render("Enter your name:", True, Config.WHITE)
    screen.blit(prompt, (Config.WIDTH // 2 - 150, Config.HEIGHT // 2 - 60))
    input_box = pygame.Rect(Config.WIDTH // 2 - 150, Config.HEIGHT // 2, 300, 40)
    pygame.draw.rect(screen, Config.WHITE, input_box, 2)
    name_surface = font.render(user_text, True, Config.WHITE)
    screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))


def draw_x(screen, x, y, cell_size):
    half = cell_size // 2
    color = Config.RED
    pygame.draw.line(screen, color, (x - half, y - half), (x + half, y + half), 2)
    pygame.draw.line(screen, color, (x + half, y - half), (x - half, y + half), 2)
