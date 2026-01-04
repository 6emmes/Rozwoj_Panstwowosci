import os
import struct

import tifffile

from city import City
from utils.definitions import Grid, Point


class World:

    def __init__(self) -> None:
        self.mining_resources: list[object] = []
        self.wood_resources: list[object] = []
        self.fertility: object = None
        self.rivers: Grid[float] = []
        self.turn = 0
        self.compatibility(self.load_new_map8("NowaMapa8.tiff"))

        # TODO: zamienić to na państwa po skończeniu dema
        self.cities: list[City] = []
        self.roads: Grid[float] = [[0.0] * self.width for _ in range(self.height)]

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

        layers = {}

        with tifffile.TiffFile(name) as tif:
            for i, page in enumerate(tif.pages):

                page_name = page.tags.get("PageName")
                if page_name is not None:
                    page_name = page_name.value
                else:
                    page_name = f"page_{i}"

                data = page.asarray()

                normalized = data / MAX
                layers[page_name] = normalized
        for name, arr in layers.items():
            print(f"Layer '{name}' has shape {arr.shape}")
            self.width, self.height = arr.shape
        return layers


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
