import sys

import numpy as np
import pygame

from settler import Settler
from utils.pathfinder import find_path
from world import World

MAX_LAND_HEIGHT = 120

BLUE = np.array([0, 105, 150])  # Water
GREEN = np.array([100, 220, 100])  # Land low
BROWN = np.array([120, 70, 20])  # Land high
RED = np.array([250, 0, 0])  # City
PUPRLE = np.array([80, 0, 130])  # Path

gradient = np.linspace(GREEN, BROWN, MAX_LAND_HEIGHT).astype(np.int8)

land_palette = np.zeros((256, 3), dtype=np.uint8)
land_palette[0:MAX_LAND_HEIGHT] = gradient
land_palette[MAX_LAND_HEIGHT:] = BROWN


def float_to_int_arr(float_grid):
    arr = np.array(float_grid)
    arr = arr * 255
    return arr.astype(np.uint8)


def main():
    # State initialization
    world = World()
    WIN_SIZE = (world.width, world.height)
    initial_settlers = [
        Settler(10, 10, 1, world),
        Settler(20, 50, 1, world),
        Settler(200, 600, 1, world),
        Settler(100, 100, 1, world),
        Settler(600, 200, 1, world),
    ]
    city_names = ["C1", "C2", "C3", "C4", "C5"]

    for o, n in zip(initial_settlers, city_names):
        world.cities.append(o.settle(n))
    cities = world.cities

    # Map preparation
    height_map = float_to_int_arr(world.heightmap)
    water_arr = np.array(world.water)
    river_arr = np.array(world.rivers)

    rgb_arr = land_palette[height_map]
    is_water = water_arr == 0
    is_river = river_arr > 0
    rgb_arr[is_water | is_river] = BLUE

    cities_pos = [(c.x, c.y) for c in cities]
    for i in range(len(cities_pos)):
        for j in range(i + 1, len(cities_pos)):
            c1 = cities_pos[i]
            c2 = cities_pos[j]
            path, cost = find_path(world, c1, c2)
            print(f"Droga z {c1} do {c2}: koszt {round(cost, 4)}; {len(path)} kroków")
            for x, y in path:
                rgb_arr[x, y] = PUPRLE

    r = 2
    for x, y in cities_pos:
        x_min, x_max = max(0, x - r), min(world.width, x + r)
        y_min, y_max = max(0, y - r), min(world.height, y + r)
        rgb_arr[x_min:x_max, y_min:y_max] = RED

    rgb_arr = np.swapaxes(rgb_arr, 0, 1)

    # Pygame initialization
    pygame.init()
    screen = pygame.display.set_mode(WIN_SIZE)
    pygame.display.set_caption("Pathfinder test")
    terrain_surface = pygame.surfarray.make_surface(rgb_arr)

    # Main loop
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
