import heapq
import os
import random
import math
from copy import deepcopy

import tifffile

from city import City
from culture import Culture
from state import State
from utils.definitions import Grid, Point
from utils.log import Logger, LogCityCollapse


SETTLERSTEPCOUNT = 48

ROAD_K = 0.04

FRIENDLY_CITY_DENSITY = 32
HOSTILE_CITY_DENSITY = 64
ROOT2 = math.sqrt(0.5)

RAMP = [
    (-90.0,  ( ROOT2,  ROOT2)),   # Polar Easterlies
    (-60.0,  ( 0.0,    0.0   )),  # Subpolar Low
    (-45.0,  (-ROOT2, -ROOT2)),   # Westerlies
    (-30.0,  ( 0.0,    0.0   )),  # Subtropical High
    (-15.0,  ( ROOT2,  ROOT2)),   # SE Trade
    (  0.0,  ( 1.0,    0.0   )),  # ITCZ
    ( 15.0,  ( ROOT2, -ROOT2)),   # NE Trade
    ( 30.0,  ( 0.0,    0.0   )),  # Subtropical High
    ( 45.0,  (-ROOT2,  ROOT2)),   # Westerlies
    ( 60.0,  ( 0.0,    0.0   )),  # Subpolar Low
    ( 90.0,  ( ROOT2, -ROOT2)),   # Polar Easterlies
]

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_vec2(v1, v2, t):
    return (
        lerp(v1[0], v2[0], t),
        lerp(v1[1], v2[1], t)
    )

STATIC_RANGE = 10
INFLUENCE_THRESHOLD = 15.0
POPULATION_PREMIUM = 2.0

CARDINAL = [(1,0), (-1,0), (0,1), (0,-1)]
DIAGONAL = [(1,1), (1,-1), (-1,1), (-1,-1)]
EIGHT = CARDINAL + DIAGONAL
EIGHT_COSTS = [1.0] * 4 + [1.41] * 4


class World:
    def __init__(self) -> None:
        self.mining_resources: list[object] = []
        self.wood_resources: list[object] = []
        self.fertility: object = None
        self.rivers: Grid[float] = []
        self.state_names: dict[str, str] = {}
        self.avaiable_states: list[str] = []
        self.turn: int = 0
        self.layers = {}
        self.compatibility(self.load_new_map8("maps/m_isles.tiff"))
        self.path_cache = {}
        self.path_cache_start = {}
        self.sailing_cache = {}
        self.sailing_cache_start = {}
        self.load_state_names()
        self.ter_scale = 2
        self.influence_grid = [[0.0 for _ in range(self.width//self.ter_scale)] for _ in range(self.height//self.ter_scale)]
        self.territory_map = [
            [None for _ in range(self.width//self.ter_scale)] for _ in range(self.height//self.ter_scale)
        ]

        # TODO: zamienić to na państwa po skończeniu dema
        self.cities: list[City] = []
        self.states: dict[str, State] = {}
        self.roads: Grid[float] = [[0.0] * self.width for _ in range(self.height)]
        self.logger = Logger("log")

        self.cities_pos()

    def action(self):
        pass

    def compatibility(self, layers):
        self.heightmap = layers["height_map"]
        self.temperature = layers["temp_map"]
        self.humidity = layers["humidity_map"]
        self.rivers = layers["river_map"]
        self.water = layers["water_map"]
        self.silver = layers["silver_map"]

    def load_new_map8(self, filename):
        MAX = 255

        with tifffile.TiffFile(filename) as tif:
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
        with open(filename, "rb") as f:
            f.seek(-2, 2)  # move 2 bytes before the end (2 = end of file)
            last_two = f.read(2)
            self.top_latitude = int(last_two[0])
            self.bot_latitude = int(last_two[1])
        return self.layers

    def build_road(self, path: list[Point]):
        for x, y in path:
            old_road = self.roads[x][y]
            self.roads[x][y] = old_road + ROAD_K * (1 - old_road)

    def next_turn(self):
        for s in self.states.values():
            s.turn()
        if self.turn % 150 == 0:
            self.road_decay()
        if self.turn % 10 == 0:
            self.update_territories_cel()

        dead_cities = [city for city in self.cities if city.citizens == 0]
        for dead_city in dead_cities:
            self.cities.remove(dead_city)

            if dead_city in dead_city.state.cities:
                dead_city.state.cities.remove(dead_city)

            self.logger.save_logs([
                LogCityCollapse(
                    turn=self.turn,
                    location=dead_city.name,
                    description=f"Ostatni mieszkańcy opuścili {dead_city.name}. Miasto pochłonęła dzicz, pozostawiając jedynie zgliszcza dawnej świetności."
                )
            ])
        self.turn += 1

    def manhattan(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def spawn_states(
        self, count: int, no_citizens: int, cultures: list[Culture] | None = None
    ):
        assert cultures is None or len(cultures) == count
        # print(no_citizens)
        for i in range(count):
            state_name = self.avaiable_states.pop()
            filename = self.state_names[state_name]
            with open(filename, encoding="utf-8") as f:
                content = f.read().split("\n")
                self.states[state_name] = State(
                    self, state_name, i * 360 / count, content
                )
            new_city = self.spawn_settler_rand(
                self.states[state_name].city_names.pop(),
                no_citizens,
                cultures[i] if cultures is not None else None,
            )
            self.states[state_name].add_city(new_city)
            new_city._randomize_initial_recources()
            new_city.state = self.states[state_name]
            new_city.state.update_tarrif()

    def spawn_settler_rand(
        self, name, no_citizens, culture: Culture | None = None, goal="fertility_map"
    ):
        NEIGHBOR_OFFSETS = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        while True:
            contflag = 1
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

                fertility = self.layers[goal][nx][ny]
                water = self.layers["water_map"][nx][ny]

                if water == 0:
                    continue

                score = fertility - water

                if score > best_score:
                    best_score = score
                    best_pos = (nx, ny)

            # Move to the best neighbor
            x_curr, y_curr = best_pos
        new_city = City(x_curr, y_curr, name, self, culture)
        new_city.citizens += no_citizens

        new_city.create_trader()
        new_city.calculate_use_rate()
        self.cities.append(new_city)
        return new_city

    def settle(self, state: State, no_citizens, x, y):
        owner = self.territory_map[x//self.ter_scale][y//self.ter_scale]
        if owner is not None and owner != state.name:
            return None

        for c in self.cities:
            if c.state == state:
                if self.manhattan(x, y, c.x, c.y) < FRIENDLY_CITY_DENSITY:
                    return None
            else:
                if self.manhattan(x, y, c.x, c.y) < HOSTILE_CITY_DENSITY:
                    return None
        if len(state.city_names) == 0:
            return None
        new_city = City(x, y, state.city_names.pop(), self, deepcopy(state.culture))
        new_city.citizens = no_citizens

        new_city.create_trader()
        new_city.calculate_use_rate()
        self.cities.append(new_city)
        state.add_city(new_city)
        new_city.state = state

        self.cities_pos()
        return new_city

    def spawn_settlers(self, names: list[str], no_citizens: int):
        for n in names:
            new_city = self.spawn_settler_rand(n, no_citizens)
            self.cities.append(new_city)
        self.cities_pos()

    def find_ocean(self, pos: Point):
        RADIUS = 5
        for x in range(-RADIUS, RADIUS + 1):
            for y in range(-RADIUS, RADIUS + 1):
                if abs(x) < RADIUS and abs(y) < RADIUS:
                    continue
                cur_pos = (pos[0] + x, pos[1] + y)
                if (
                    cur_pos[0] < 0
                    or cur_pos[0] >= self.width
                    or cur_pos[1] < 0
                    or cur_pos[1] >= self.height
                ):
                    continue
                if self.heightmap[cur_pos[0]][cur_pos[1]] == 0.0:
                    return self.layers["id_map"][cur_pos[0]][cur_pos[1]], cur_pos
        return None, None
    
    def check_path_cache(self, line):
        if line not in self.path_cache:
            return False
        cache_value_age = self.turn - self.path_cache[line][2]
        cache_age = self.turn - self.path_cache_start[line]
        return cache_value_age < 0.5 * cache_age

    def write_path_cache(self, line, value):
        if line not in self.path_cache:
            self.path_cache_start[line] = self.turn
        self.path_cache[line] = value


    def check_sailing_cache(self, line):
        return line in self.sailing_cache

    def write_sailing_path_cache(self, line, value):
        if line not in self.sailing_cache:
            self.sailing_cache_start[line] = self.turn
        self.sailing_cache[line] = value
        

    def update_prices(self):
        self.prices = {}
        for city in self.cities:
            for resource, price in city.resources.items():
                if resource not in self.prices:
                    self.prices[resource] = price[1]
                else:
                    self.prices[resource] += price[1]
        for resource in self.prices:
            self.prices[resource] /= len(self.cities)

    def load_state_names(self):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        names_dir = root_dir + "/names/"
        print(names_dir)
        for file in os.listdir(names_dir):
            filename = os.fsdecode(file)
            name = filename.split(".")[0]
            self.state_names[name] = names_dir + filename
            self.avaiable_states.append(name)
        print(self.state_names)

    def road_decay(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.roads[x][y] > 0:
                    if self.roads[x][y] < ROAD_K:
                        self.roads[x][y] = 0
                    else:
                        self.roads[x][y] -= ROAD_K / 2

    def cities_pos(self):
        self.cities_map = [(c.x, c.y) for c in self.cities]

    def get_wind(self, pos: Point):
        x, y = pos
        if not (0 <= x < self.width and 0 <= y < self.height):
            return (0.0, 0.0)

        lat_delta = self.top_latitude - self.bot_latitude
        latitude = self.top_latitude - (lat_delta * (y / self.height))

        if latitude <= RAMP[0][0]:
            return RAMP[0][1]
        if latitude >= RAMP[-1][0]:
            return RAMP[-1][1]

        for i in range(len(RAMP) - 1):
            lat0, v0 = RAMP[i]
            lat1, v1 = RAMP[i + 1]
            if lat0 <= latitude <= lat1:
                t = (latitude - lat0) / (lat1 - lat0)
                return lerp_vec2(v0, v1, t)
        return (0.0, 0.0)
    

    def update_territories_cel(self):
        map_scale = self.ter_scale

        for state_name, state in self.states.items():
            total_population = sum(city.citizens for city in state.cities)
            is_true_state = len(state.cities) >= 3 and total_population >= 50
            for city in state.cities:
                if is_true_state:
                    base_influence = 30.0 + (city.citizens * POPULATION_PREMIUM)
                else:
                    base_influence = 30.0 + (city.citizens / POPULATION_PREMIUM)
                if base_influence <= 0:
                    continue
                cx = int(city.x/map_scale)
                cy = int(city.y/map_scale)
                self.influence_grid[cx][cy] = base_influence
                self.territory_map[cx][cy] = state_name

        for x in range(0, self.width//map_scale):
            for y in range(0, self.height//map_scale):
                if self.layers["height_map"][x*map_scale][y*map_scale] == 0:
                    continue

                terrain_cost = 3.0 + (self.layers["height_map"][x*map_scale][y*map_scale] * 10.0)
                road_level = self.roads[x*map_scale][y*map_scale]
                next_influence = {}
                for (dx, dy), base_cost in zip(EIGHT, EIGHT_COSTS):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < self.width/map_scale and 0 <= ny < self.height/map_scale:
                        if self.territory_map[nx][ny] is not None:
                            owner = self.territory_map[nx][ny]
                            step_cost = terrain_cost * (1.0 - (road_level * 0.5)) * base_cost * self.ter_scale
                            if owner not in next_influence:
                                next_influence[owner] = self.influence_grid[nx][ny] - step_cost
                            else:
                                next_influence[owner] = max(next_influence[owner], self.influence_grid[nx][ny] - step_cost)

                for owner, inf in next_influence.items():
                    if inf > INFLUENCE_THRESHOLD and self.influence_grid[x][y] < inf:
                        self.influence_grid[x][y] = inf
                        self.territory_map[x][y] = owner

        for x in reversed(range(0, self.width//map_scale)):
            for y in reversed(range(0, self.height//map_scale)):
                if self.layers["height_map"][x*map_scale][y*map_scale] == 0:
                    continue

                terrain_cost = 3.0 + (self.layers["height_map"][x*map_scale][y*map_scale] * 10.0)
                road_level = self.roads[x*map_scale][y*map_scale]
                next_influence = {}
                for (dx, dy), base_cost in zip(EIGHT, EIGHT_COSTS):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < self.width/map_scale and 0 <= ny < self.height/map_scale:
                        if self.territory_map[nx][ny] is not None:
                            owner = self.territory_map[nx][ny]
                            step_cost = terrain_cost * (1.0 - (road_level * 0.5)) * base_cost * self.ter_scale
                            if owner not in next_influence:
                                next_influence[owner] = self.influence_grid[nx][ny] - step_cost
                            else:
                                next_influence[owner] = max(next_influence[owner], self.influence_grid[nx][ny] - step_cost)

                for owner, inf in next_influence.items():
                    if inf > INFLUENCE_THRESHOLD and self.influence_grid[x][y] < inf:
                        self.influence_grid[x][y] = inf
                        self.territory_map[x][y] = owner