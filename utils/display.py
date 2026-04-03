from world import World
import pygame
import numpy as np

COLOR_PATH = [120, 120, 120]
COLOR_GROUND = [0, 250, 0]
COLOR_WATER = [0, 0, 250]
COLOR_BLACK = [0, 0, 0]


class Display:
    def __init__(self, world: "World"):
        self.world = world
        self.camera_scale = 1.0
        self.camera_offset = pygame.Vector2(0, 0)
        self.zoom_speed = 0.1
        self.pan_speed = 20

    def pygame_init(self):
        pygame.init()
        pygame.font.init()
        win_size = (self.world.width, self.world.height)
        self.screen = pygame.display.set_mode(win_size)

        heightmap = self.world.layers["height_map"]
        rivermap = self.world.layers["river_map"]

        terrain_array = np.zeros(
            (self.world.width, self.world.height, 3), dtype=np.uint8
        )
        terrain_array[:] = COLOR_GROUND
        water_mask = heightmap == 0
        river_mask = rivermap != 0
        terrain_array[water_mask] = COLOR_WATER
        terrain_array[river_mask] = COLOR_WATER

        shademap = self.world.layers["shade_map"]

        alpha = 0.5
        shade_factor = 1.0 - shademap * alpha

        terrain_array = terrain_array.astype(np.float32)
        terrain_array *= shade_factor[..., None]
        terrain_array = np.clip(terrain_array, 0, 255).astype(np.uint8)
        self.terrain_surface = pygame.surfarray.make_surface(terrain_array)
        self.ter_scale = self.world.ter_scale
        self.territory_surface = pygame.Surface((self.world.width//self.ter_scale, self.world.height//self.ter_scale), pygame.SRCALPHA)

        self.font = pygame.font.SysFont('Verdana', 16)
        self.text_surface = self.font.render('Some Text', False, (128, 128, 128))

    def pygame_sync(self):
        road_array = np.array(self.world.roads, dtype=np.float32)
        road_intensity = np.clip(road_array * 255, 0, 255).astype(np.uint8)
        road_rgb = np.stack([road_intensity] * 3, axis=-1)
        alpha = np.where(road_intensity == 0, 0, 255).astype(np.uint8)
        road_rgba = np.dstack([road_rgb, alpha])
        h, w = road_rgba.shape[:2]
        self.roads_surface = pygame.image.frombuffer(
            road_rgba.transpose((1, 0, 2)).copy(), (w, h), "RGBA"
        ).convert_alpha()

        territory_rgba = np.zeros((self.world.width, self.world.height, 4), dtype=np.uint8)

        # Słownik do szybkiego wyszukiwania koloru państwa
        color_map = {}
        for state_name, state in self.world.states.items():
            c = pygame.Color(0)
            c.hsva = (state.hue % 360, 70, 90,
                      100)  # Saturacja 70, Value 90. Ostatnia wartość w hsva nie kontroluje alphy bezpośrednio
            # Tworzymy krotkę RGBA (z alphą ustawioną na 100/255 -> półprzezroczystość)
            color_map[state_name] = (c.r, c.g, c.b, 100)

            # Sprawdzamy, czy world ma już territory_map (dla bezpieczeństwa pierwszych tur)
        if hasattr(self.world, 'territory_map'):
            for x in range(self.world.width//self.ter_scale):
                for y in range(self.world.height//self.ter_scale):
                    owner = self.world.territory_map[x][y]
                    if owner is not None and owner in color_map:
                        territory_rgba[x, y] = color_map[owner]

        # Konwersja na pygame Surface w ten sam sposób co drogi
        h_t, w_t = territory_rgba.shape[:2]
        self.territory_surface = pygame.image.frombuffer(
            territory_rgba.transpose((1, 0, 2)).copy(), (w_t, h_t), "RGBA"
        ).convert_alpha()

        self.text_surface = self.font.render(str(self.world.turn), False, (128, 128, 128))

    def pygame_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            # --- Mouse wheel zoom ---
            if event.type == pygame.MOUSEWHEEL:
                old_scale = self.camera_scale
                self.camera_scale *= 1 + self.zoom_speed * event.y
                self.camera_scale = max(0.1, min(5.0, self.camera_scale))
                mx, my = pygame.mouse.get_pos()
                mouse = pygame.Vector2(mx, my)
                self.camera_offset = mouse - (mouse - self.camera_offset) * (
                    self.camera_scale / old_scale
                )

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

        # --- Apply camera transform ---
        terrain_scaled = pygame.transform.scale(
            self.terrain_surface,
            (
                int(self.world.width * self.camera_scale),
                int(self.world.height * self.camera_scale),
            ),
        )

        roads_scaled = pygame.transform.scale(
            self.roads_surface,
            (
                int(self.world.width * self.camera_scale),
                int(self.world.height * self.camera_scale),
            ),
        )

        territory_scaled = pygame.transform.smoothscale (
            self.territory_surface,
            (
                int(self.world.width * self.camera_scale * self.ter_scale),
                int(self.world.height * self.camera_scale * self.ter_scale),
            ),
        )

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw terrain + roads with offset
        self.screen.blit(terrain_scaled, self.camera_offset)
        self.screen.blit(territory_scaled, self.camera_offset)
        self.screen.blit(roads_scaled, self.camera_offset)

        # Draw cities (scaled + offset)
        state_color = pygame.Color(0)
        for st in self.world.states.values():
            state_color.hsva = (st.hue, 100, 100, 100)
            for index, city in enumerate(st.cities):
                pos = pygame.Vector2(city.x, city.y) * \
                self.camera_scale + self.camera_offset

                if index == 0:
                    pygame.draw.circle(self.screen, COLOR_BLACK, pos, 5)
                else:
                    pygame.draw.circle(self.screen, COLOR_BLACK, pos, 4)
                if len(city.citizens) > 0:
                    pygame.draw.circle(self.screen, state_color, pos, 3)

        self.screen.blit(self.text_surface, (0,0))
        pygame.display.flip()
        # pygame.time.wait(8) #should be 16 for 60fps but simulation is bottleneck here
        return True

    def save(self):
        pygame.image.save(self.screen, "visualization/simulation_snapshot.png")