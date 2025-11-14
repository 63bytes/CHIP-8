import chip8

c = chip8.CHIP_8("Dump.hex")
for x in range(50):
    c.Cycle()
c.DumpRam()

"""
import pygame

WIDTH = 64
HEIGHT = 32
PIXEL_SIZE = 10          
WINDOW_WIDTH = WIDTH * PIXEL_SIZE
WINDOW_HEIGHT = HEIGHT * PIXEL_SIZE

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("64x32 Pixel Screen")
clock = pygame.time.Clock()

buffer = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def draw_buffer():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = (255, 255, 255) if buffer[y][x] else (0, 0, 0)
            pygame.draw.rect(
                screen,
                color,
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE)
            )

count= 0
while True:
    pygame.event.get()
    draw_buffer()
    print(1)
    pygame.display.flip()
    clock.tick(5)
    count+=1"""