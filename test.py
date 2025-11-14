import pygame
import sys

# -----------------------------
# Config
# -----------------------------
WIDTH = 64
HEIGHT = 32
PIXEL_SIZE = 10          # Scale factor for visibility
WINDOW_WIDTH = WIDTH * PIXEL_SIZE
WINDOW_HEIGHT = HEIGHT * PIXEL_SIZE

# -----------------------------
# Initialize Pygame
# -----------------------------
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("64x32 Pixel Screen")

clock = pygame.time.Clock()

# 2D pixel buffer (0 or 1)
buffer = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

# -----------------------------
# Main Functions
# -----------------------------
def draw_buffer():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = (255, 255, 255) if buffer[y][x] else (0, 0, 0)
            pygame.draw.rect(
                screen,
                color,
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            )

def example_pattern():
    """Draws something onto the buffer."""
    for x in range(WIDTH):
        buffer[10][x] = 1
    for y in range(HEIGHT):
        buffer[y][20] = 1


# -----------------------------------
# MAIN LOOP
# -----------------------------------
example_pattern()  # remove or change as needed

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))
    draw_buffer()

    pygame.display.flip()
    clock.tick(60)  # limit to 60fps