import os
import struct
import random
import tifffile

from city import City
from utils.definitions import Grid, Point
from utils.log import Logger
SETTLERSTEPCOUNT = 32


class World:

    def __init__(self) -> None:
        self.mining_resources: list[object] = []
        self.wood_resources: list[object] = []
        self.fertility: object = None
        self.rivers: Grid[float] = []
        self.turn = 0
        self.layers = {}
        self.compatibility(self.load_new_map8("m_temperate8.tiff"))

        # TODO: zamienić to na państwa po skończeniu dema
        self.cities: list[City] = []
        self.roads: Grid[float] = [[0.0] * self.width for _ in range(self.height)]
        self.logger = Logger("log")

    def action(self):
        pass

    def compatibility(self, layers):
        self.heightmap = layers["height_map"]
        self.temperature = layers["temp_map"]
        self.humidity = layers["humidity_map"]
        self.rivers = layers["river_map"]
        self.water = layers["water_map"]

    def load_new_map8(self, name):
        MAX = 255
        with tifffile.TiffFile(name) as tif:
            for i, page in enumerate(tif.pages):

                page_name = page.tags.get("PageName")
                if page_name is not None:
                    page_name = page_name.value
                else:
                    page_name = f"page_{i}"

                data = page.asarray()

                normalized = data / MAX
                self.layers[page_name] = normalized
        for name, arr in self.layers.items():
            print(f"Layer '{name}' has shape {arr.shape}")
            self.width, self.height = arr.shape
        return self.layers
    
    
    def build_road(self, path: list[Point], value=0.05):
        for x, y in path:
            self.roads[x][y] += value

    def next_turn(self):
        for city in self.cities:
            accumulation_rate = {name: 0 for name in city.resources.keys()}
            for citizen in city.citizens:
                res, ammount = citizen.gather_resources(
                    self.temperature[city.x][city.y],
                    self.heightmap[city.x][city.y],
                    self.humidity[city.x][city.y],
                )
                resources, price = city.resources[res]
                # TODO przeliczanie ceny po każdej iteracji
                city.resources[res] = (resources + ammount, price)
                accumulation_rate[res] += ammount
            city.accumulation_rate = accumulation_rate
            city.turn()
            if self.turn % 10 == 0:
                city.recalculate_goods_prices()
            for trader in city.traders:
                trader.trader_action()
        self.turn += 1

    def manhattan(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)


    def spawn_settlers(self, names, no_citizens, seed=10):
        NEIGHBOR_OFFSETS = [ (0, -1), (-1, 0), (1, 0), (0, 1)]
        random.seed(seed)       
        for n in names:
            contflag = 1
            while True:
                x_curr = int(random.uniform(0, self.width))
                y_curr = int(random.uniform(0, self.height))
                if self.water[x_curr][y_curr] == 0:
                    continue
                if len(self.cities) == 0:
                    break
                for c in self.cities:
                    dist = self.manhattan(x_curr, y_curr, c.x, c.y)
                    if dist < SETTLERSTEPCOUNT * 2:
                        contflag = 0
                        break
                if contflag == 1:
                    break

            for _ in range(SETTLERSTEPCOUNT):

                best_score = float("-inf")
                best_pos = (x_curr, y_curr)

                for dx, dy in NEIGHBOR_OFFSETS:
                    nx = x_curr + dx
                    ny = y_curr + dy

                    # bounds check
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue

                    fertility = self.layers['fertility_map'][nx][ny]
                    water     = self.layers['water_map'][nx][ny]

                    if water == 0:
                        continue
                    
                    score = fertility - water

                    if score > best_score:
                        best_score = score
                        best_pos = (nx, ny)

                # Move to the best neighbor
                x_curr, y_curr = best_pos
            new_city = City(x_curr, y_curr, n, self)
            for _ in range(no_citizens):
                new_city.create_citizen()
            self.cities.append(new_city)
            
    def find_ocean(self, pos:Point):
        RADIUS = 5
        for x in range(-RADIUS, RADIUS+1):
            for y in range(-RADIUS, RADIUS+1):
                if (abs(x)<RADIUS and abs(y)<RADIUS):
                    continue
                cur_pos = (pos[0]+x, pos[1]+y)
                if (cur_pos[0]<0 or cur_pos[0]>=self.width or cur_pos[1]<0 or cur_pos[1]>=self.height):
                    continue
                if self.heightmap[cur_pos[0]][cur_pos[1]] == 0.0:
                    return self.layers["id_map"][cur_pos[0]][cur_pos[1]]
        return None
