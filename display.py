from world import World
import pygame
import numpy as np

COLOR_CITY = [250, 0, 0]
COLOR_PATH = [120, 120, 120]
COLOR_GROUND = [0, 250, 0]
COLOR_WATER = [0, 0, 250]


def pygame_init(world: 'World'):
    pygame.init()
    win_size = (world.width, world.height)
    screen = pygame.display.set_mode(win_size)

    heightmap = world.layers["height_map"]

    terrain_array = np.zeros((world.width, world.height, 3), dtype=np.uint8)
    terrain_array[:] = COLOR_GROUND
    water_mask = heightmap == 0
    terrain_array[water_mask] = COLOR_WATER
    terrain_surface = pygame.surfarray.make_surface(terrain_array)
    return screen, terrain_surface


def pygame_loop(screen: pygame.Surface, world: 'World', terrain_surface: pygame.Surface):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

    # Update roads
    road_array = np.array(world.roads, dtype=np.float32)
    road_intensity = np.clip(road_array * 255, 0, 255).astype(np.uint8)
    road_rgb = np.stack([road_intensity] * 3, axis=-1)
    alpha = np.where(road_intensity == 0, 0, 255).astype(np.uint8)
    road_rgba = np.dstack([road_rgb, alpha])
    h, w = road_rgba.shape[:2]
    roads_surface = pygame.image.frombuffer(
        road_rgba.copy(), (w, h), "RGBA").convert_alpha()

    screen.blit(terrain_surface, (0, 0))
    screen.blit(roads_surface, (0, 0))

    # Draw cities
    for city in world.cities:
        pygame.draw.circle(screen, COLOR_CITY, (city.x, city.y), 3)
    pygame.display.flip()
    pygame.time.wait(20)
    return True
