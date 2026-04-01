import heapq
import os
import random
from copy import deepcopy

import tifffile

from city import City
from culture import Culture
from state import State
from utils.definitions import Grid, Point
from utils.log import Logger

SETTLERSTEPCOUNT = 32

ROAD_K = 0.04

FRIENDLY_CITY_DENSITY = 32
HOSTILE_CITY_DENSITY = 64

STATIC_RANGE = 10
INFLUENCE_THRESHOLD = 15.0
POPULATION_PREMIUM = 2.0


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
        self.compatibility(self.load_new_map8("maps/m_continent.tiff"))
        self.path_cache = {}
        self.path_cache_start = {}
        self.load_state_names()
        self.territory_map = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        # TODO: zamienić to na państwa po skończeniu dema
        self.cities: list[City] = []
        self.states: dict[str, State] = {}
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
        self.silver = layers["silver_map"]

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
            self.update_territories()
        self.turn += 1

    def manhattan(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def spawn_states(self, count: int, no_citizens: int, seed=10):
        random.seed(seed)
        print(no_citizens)
        for i in range(count):
            state_name = self.avaiable_states.pop()
            filename = self.state_names[state_name]
            with open(filename, encoding="utf-8") as f:
                content = f.read().split("\n")
                self.states[state_name] = State(
                    self, state_name, i * 360 / count, content
                )
            new_city = self.spawn_settler_rand(
                self.states[state_name].city_names.pop(), no_citizens
            )
            self.states[state_name].add_city(new_city)
            new_city._randomize_initial_recources()
            new_city.state = self.states[state_name]
            new_city.state.update_tarrif()

    def spawn_settler_rand(self, name, no_citizens, goal="fertility_map"):
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
        new_city = City(x_curr, y_curr, name, self)
        for _ in range(no_citizens):
            new_city.create_citizen()

        new_city.create_trader()
        new_city.calculate_use_rate()
        self.cities.append(new_city)
        return new_city

    def settle(self, state: State, no_citizens, x, y):
        owner = self.territory_map[x][y]
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
        for _ in range(no_citizens):
            new_city.create_citizen()

        new_city.create_trader()
        new_city.calculate_use_rate()
        self.cities.append(new_city)
        state.add_city(new_city)
        new_city.state = state
        return new_city

    def spawn_settlers(self, names: list[str], no_citizens: int):
        for n in names:
            new_city = self.spawn_settler_rand(n, no_citizens)
            self.cities.append(new_city)

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
                    return self.layers["id_map"][cur_pos[0]][cur_pos[1]]
        return None

    def check_path_cache(self, line):
        if line not in self.path_cache:
            return False
        cache_value_age = self.turn - self.path_cache[line][2]
        cache_age = self.turn - self.path_cache_start[line]
        if cache_value_age < 0.5 * cache_age:
            return True
        return False

    def write_path_cache(self, line, value):
        if line not in self.path_cache:
            self.path_cache_start[line] = self.turn
        self.path_cache[line] = value

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

    def update_territories(self):
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        influence_grid = {
            state_name: [[0.0 for _ in range(self.width)] for _ in range(self.height)]
            for state_name in self.states.keys()
        }

        for state_name, state in self.states.items():
            total_population = sum(len(city.citizens) for city in state.cities)
            is_true_state = len(state.cities) >= 3 and total_population >= 50

            for city in state.cities:
                if is_true_state:
                    base_influence = 30.0 + (len(city.citizens) * POPULATION_PREMIUM)
                else:
                    base_influence = 30.0

                if base_influence <= 0:
                    continue

                queue = [(-base_influence, city.x, city.y)]
                visited = set()

                while queue:
                    current_influence_neg, cx, cy = heapq.heappop(queue)
                    current_influence = -current_influence_neg

                    if (cx, cy) in visited:
                        continue
                    visited.add((cx, cy))

                    influence_grid[state_name][cx][cy] += current_influence

                    for dx, dy in directions:
                        nx, ny = cx + dx, cy + dy

                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if (nx, ny) not in visited:
                                if self.layers["water_map"][nx][ny] == 0.0:
                                    continue

                                height = self.layers["height_map"][nx][ny]
                                terrain_cost = 3.0 + (height * 10.0)
                                road_level = self.roads[nx][ny]

                                step_cost = terrain_cost * (1.0 - (road_level * 0.5))

                                if dx != 0 and dy != 0:
                                    step_cost *= 1.414

                                next_influence = current_influence - step_cost

                                if next_influence > 0.1:
                                    heapq.heappush(queue, (-next_influence, nx, ny))

        for state_name, state in self.states.items():
            for city in state.cities:
                for dx in range(-STATIC_RANGE, STATIC_RANGE + 1):
                    for dy in range(-STATIC_RANGE, STATIC_RANGE + 1):
                        if dx**2 + dy**2 <= pow(STATIC_RANGE, 2):
                            nx, ny = city.x + dx, city.y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if self.layers["water_map"][nx][ny] != 0.0:
                                    influence_grid[state_name][nx][ny] = float("inf")

        for x in range(0, self.width, 2):
            for y in range(0, self.height, 2):
                best_state = None
                max_inf = INFLUENCE_THRESHOLD
                for state_name, grid in influence_grid.items():
                    if grid[x][y] > max_inf:
                        max_inf = grid[x][y]
                        best_state = state_name
                self.territory_map[x][y] = best_state
