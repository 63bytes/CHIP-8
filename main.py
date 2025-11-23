import chip8
from time import sleep
import tkinter as tk

HOLD = True
WINDOW_OUT = False
def hex(i):
    return f"{i:02X}"

#Output window
if WINDOW_OUT:
    Window = tk.Tk()
    decOut = tk.Text(Window)
    decOut.pack()
    readOut = tk.Text(Window)
    readOut.pack()

def output(action, d={}):
    if action=="DECODE":
        decOut.insert("end", f"[DECODE]: 0x{hex(d["val"])} - {d["ins"]}" + "\n")
        decOut.see("end")
    elif action=="READ":
        readOut.insert("end", f"[READ]: 0x{hex(d["ad"])} - 0x{hex(d["val"])}" + "\n")
        readOut.see("end")
if WINDOW_OUT:
    chip8.output = output
c = chip8.CHIP_8("Dump.hex", "Programs/Testing.hex")

while c.stop==False:
    c.Cycle()
    if WINDOW_OUT:
        Window.update()
    sleep(0.1)
    print(c.Cycles)
c.DumpRam()

if HOLD:
    while True:
        c.Display.Update()

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