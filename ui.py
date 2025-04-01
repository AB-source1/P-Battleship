import pygame
from config import Config

def draw_grid(screen, board, offset_x, offset_y, show_ships=False):
    for row in range(Config.GRID_SIZE):
        for col in range(Config.GRID_SIZE):
            x = offset_x + col * Config.CELL_SIZE
            y = offset_y + row * Config.CELL_SIZE
            rect = pygame.Rect(x, y, Config.CELL_SIZE, Config.CELL_SIZE)
            pygame.draw.rect(screen, Config.WHITE, rect, 1)

            cell = board[row][col]
            if cell == 'M':
                pygame.draw.circle(screen, Config.BLUE, rect.center, Config.CELL_SIZE // 6)
            elif cell == 'X':
                pygame.draw.line(screen, Config.RED, rect.topleft, rect.bottomright, 2)
                pygame.draw.line(screen, Config.RED, rect.topright, rect.bottomleft, 2)
            elif show_ships and cell == 'S':
                pygame.draw.rect(screen, Config.BLUE, rect.inflate(-4, -4))

def draw_text_center(screen, text, x, y, font_size=30):
    font = pygame.font.SysFont(None, font_size)
    surface = font.render(text, True, Config.WHITE)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

def draw_button(screen, text, x, y, w, h, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, hover_color if rect.collidepoint(mouse) else color, rect)
    font = pygame.font.SysFont(None, 30)
    text_surf = font.render(text, True, Config.WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    if rect.collidepoint(mouse) and click[0] == 1 and action:
        action()

def draw_text_input_box(screen, user_text):
    font = pygame.font.SysFont(None, 36)
    prompt = font.render("Enter your name:", True, Config.WHITE)
    screen.blit(prompt, (Config.WIDTH // 2 - 150, Config.HEIGHT // 2 - 60))
    input_box = pygame.Rect(Config.WIDTH // 2 - 150, Config.HEIGHT // 2, 300, 40)
    pygame.draw.rect(screen, Config.WHITE, input_box, 2)
    name_surface = font.render(user_text, True, Config.WHITE)
    screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))
