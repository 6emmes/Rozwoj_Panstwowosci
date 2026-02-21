import os
import random
import struct

import tifffile

from city import City
from state import State
from utils.definitions import Grid, Point

SETTLERSTEPCOUNT = 32
ANNEALING_START = 50
ANNEALING_END = 250
ANNEALING_COOLING_TIME = 1000


class World:
    def __init__(self) -> None:
        self.mining_resources: list[object] = []
        self.wood_resources: list[object] = []
        self.fertility: object = None
        self.rivers: Grid[float] = []
        self.state_names: dict[str, str] = {}
        self.avaiable_states: list[str] = []
        self.turn = 0
        self.layers = {}
        self.compatibility(self.load_new_map8("maps/m_continent.tiff"))
        self.path_cache = {}
        self.path_cache_timeout = ANNEALING_START
        self.load_state_names()

        # TODO: zamienić to na państwa po skończeniu dema
        self.cities: list[City] = []
        self.states: dict[str, State] = {}
        self.roads: Grid[float] = [[0.0] * self.width for _ in range(self.height)]

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

    def build_road(self, path: list[Point], value=0.05):
        for x, y in path:
            self.roads[x][y] += value

    def next_turn(self):
        for s in self.states.values():
            s.turn()
        self.pathfinder_annealing()
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

    def spawn_settler_rand(self, name, no_citizens, goal = "fertility_map"):
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
        new_city.calcualate_use_rate()
        self.cities.append(new_city)
        return new_city
    
    def settle(self, state: State, no_citizens, x, y):
        new_city = City(x, y, state.city_names.pop(), self)
        for _ in range(no_citizens):
            new_city.create_citizen()

        new_city.create_trader()
        new_city.calcualate_use_rate()
        self.cities.append(new_city)
        state.add_city(new_city)
        new_city.state = state
        return new_city


    def spawn_settlers(self, names: list[str], no_citizens: int, seed=10):
        random.seed(seed)
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

    def pathfinder_annealing(self):
        if self.turn > ANNEALING_COOLING_TIME:
            self.path_cache_timeout = ANNEALING_END
        else:
            self.path_cache_timeout = int(
                ANNEALING_START
                + (ANNEALING_END - ANNEALING_START) * self.turn / ANNEALING_COOLING_TIME
            )

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
