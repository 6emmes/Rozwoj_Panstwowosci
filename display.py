from world import World
import pygame
import numpy as np

COLOR_CITY = [250, 0, 0]
COLOR_PATH = [120, 120, 120]
COLOR_GROUND = [0, 250, 0]
COLOR_WATER = [0, 0, 250]

class Display:

    def __init__(self, world: "World"):
        self.world = world
        self.camera_scale = 1.0
        self.camera_offset = pygame.Vector2(0, 0)
        self.zoom_speed = 0.1
        self.pan_speed = 20

    def pygame_init(self):
        pygame.init()
        win_size = (self.world.width, self.world.height)
        self.screen = pygame.display.set_mode(win_size)

        heightmap = self.world.layers["height_map"]
        terrain_array = np.zeros((self.world.width, self.world.height, 3), dtype=np.uint8)
        terrain_array[:] = COLOR_GROUND
        water_mask = heightmap == 0
        terrain_array[water_mask] = COLOR_WATER
        self.terrain_surface = pygame.surfarray.make_surface(terrain_array)

    def pygame_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            # --- Mouse wheel zoom ---
            if event.type == pygame.MOUSEWHEEL:
                old_scale = self.camera_scale
                self.camera_scale *= (1 + self.zoom_speed * event.y)
                self.camera_scale = max(0.1, min(5.0, self.camera_scale))
                mx, my = pygame.mouse.get_pos()
                mouse = pygame.Vector2(mx, my)
                self.camera_offset = mouse - (mouse - self.camera_offset) * (self.camera_scale / old_scale)

            # --- Arrow key panning ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.camera_offset.x += self.pan_speed
                if event.key == pygame.K_RIGHT:
                    self.camera_offset.x -= self.pan_speed
                if event.key == pygame.K_UP:
                    self.camera_offset.y += self.pan_speed
                if event.key == pygame.K_DOWN:
                    self.camera_offset.y -= self.pan_speed

        # --- Build roads surface ---
        road_array = np.array(self.world.roads, dtype=np.float32)
        road_intensity = np.clip(road_array * 255, 0, 255).astype(np.uint8)
        road_rgb = np.stack([road_intensity] * 3, axis=-1)
        alpha = np.where(road_intensity == 0, 0, 255).astype(np.uint8)
        road_rgba = np.dstack([road_rgb, alpha])
        h, w = road_rgba.shape[:2]
        roads_surface = pygame.image.frombuffer(
            road_rgba.transpose((1,0,2)).copy(), (w, h), "RGBA"
        ).convert_alpha()

        # --- Apply camera transform ---
        terrain_scaled = pygame.transform.scale(
            self.terrain_surface,
            (int(self.terrain_surface.get_width() * self.camera_scale),
            int(self.terrain_surface.get_height() * self.camera_scale))
        )

        roads_scaled = pygame.transform.scale(
            roads_surface,
            (int(w * self.camera_scale), int(h * self.camera_scale))
        )

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw terrain + roads with offset
        self.screen.blit(terrain_scaled, self.camera_offset)
        self.screen.blit(roads_scaled, self.camera_offset)

        # Draw cities (scaled + offset)
        for city in self.world.cities:
            pos = pygame.Vector2(city.x, city.y) * self.camera_scale + self.camera_offset
            pygame.draw.circle(self.screen, COLOR_CITY, pos, int(3 * self.camera_scale))

        pygame.display.flip()
        #pygame.time.wait(16) #should be 16 for 60fps but simulation is bottleneck here
        return True

