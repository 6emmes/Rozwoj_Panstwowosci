import sys

import numpy as np
import pygame

from world import World

MAX_LAND_HEIGHT = 120

BLUE = np.array([0, 105, 150])
GREEN = np.array([100, 220, 100])
BROWN = np.array([120, 70, 20])

gradient = np.linspace(GREEN, BROWN, MAX_LAND_HEIGHT).astype(np.int8)

land_palette = np.zeros((256, 3), dtype=np.uint8)
land_palette[0:MAX_LAND_HEIGHT] = gradient
land_palette[MAX_LAND_HEIGHT:] = BROWN


def process_data(float_grid):
    arr = np.array(float_grid)
    arr = arr * 255
    return arr.astype(np.uint8)


def main():
    world = World()
    WIN_SIZE = (world.width, world.height)

    height_map = process_data(world.heightmap)
    water_arr = np.array(world.water)

    rgb_arr = land_palette[height_map]
    is_water = water_arr == 0
    rgb_arr[is_water] = BLUE
    rgb_array = np.swapaxes(rgb_arr, 0, 1)
    terrain_surface = pygame.surfarray.make_surface(rgb_arr)

    pygame.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    pygame.display.set_caption("Pathfinder test")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(terrain_surface, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
