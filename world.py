import os
import struct

import tifffile

from city import City

type Point = tuple[int, int]
type Grid[T] = list[list[T]]


class World:

    def __init__(self) -> None:
        self.mining_resources: list[object] = []
        self.wood_resources: list[object] = []
        self.fertility: object = None
        self.rivers: Grid[int] = []
        self.compatibility(self.load_new_map("NowaMapa.tiff"))

        # TODO: zamienić to na państwa po skończeniu dema
        self.cities: list[City] = []
        self.roads: Grid[float] = [[0.0] * self.width for _ in range(self.height)]

    def action(self):
        pass

    def compatibility(self, layers):
        self.heightmap = layers["heightMap"]
        self.temperature = layers["tempMap"]
        self.humidity = layers["humidityMap"]
        self.rivers = layers["riverMap"]
        self.water = layers["waterMap"]

    def load_new_map(self, name):

        MAX = 2**31 - 1

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

    def load_old_map(self, path) -> None:
        script_dir = os.path.dirname(__file__)
        total_path = os.path.join(script_dir, path)
        with open(total_path, "rb") as f:
            data = f.read()

        bf_type, bf_size, bf_reserved1, bf_reserved2, bf_off_bits = struct.unpack_from(
            "<2sIHHI", data, 0
        )
        if bf_type != b"BM":
            raise ValueError("File is not a BMP image")

        bi_size, bi_width, bi_height, bi_planes, bi_bit_count = struct.unpack_from(
            "<IiiHH", data, 14
        )

        depth = 0
        if bi_bit_count == 32:
            depth = 4
        elif bi_bit_count == 24:
            depth = 3
        assert depth == 3 or depth == 4

        self.width = bi_width
        self.height = bi_height

        row_padded = (self.width * depth + 3) & ~3

        red = [[0] * self.width for _ in range(self.height)]
        green = [[0] * self.width for _ in range(self.height)]
        blue = [[0] * self.width for _ in range(self.height)]

        for row in range(self.height):
            src_row = self.height - 1 - row
            start = bf_off_bits + src_row * row_padded
            for col in range(self.width):
                offset = start + col * depth

                blue[row][col] = data[offset]
                green[row][col] = data[offset + 1]
                red[row][col] = data[offset + 2]

        self.temperature = red
        self.heightmap = green
        self.humidity = blue

        print(f"Wczytano mapę {self.width} x {self.height}")

    def build_road(self, path: list[Point], value=0.05):
        for x, y in path:
            self.roads[x][y] += value

    def next_turn(self):
        for city in self.cities:
            for citizen in city.citizens:
                res, ammount = citizen.gather_resources(
                    self.temperature[city.x][city.y],
                    self.heightmap[city.x][city.y],
                    self.humidity[city.x][city.y],
                )
                resources, price = city.resources[res]
                # TODO przeliczanie ceny po każdej iteracji
                city.resources[res] = (resources + ammount, price)
