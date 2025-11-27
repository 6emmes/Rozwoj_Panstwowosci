import os
import struct

from miasto import Miasto


class Swiat:

    def __init__(self) -> None:
        self.tablica_drog: list[object] = []
        self.heightmap: object = None
        self.zasoby_kopalne: list[object] = []
        self.zasoby_drzewa: list[object] = []
        self.zyznosc: object = None
        self.rzeki: list[object] = []
        self.load_stara_map(path="StaraMapa_s.bmp")

        # TODO: zamienić to na państwa po skończeniu dema
        self.miasta: list[Miasto] = []

    def akcja(self):
        pass

    def load_stara_map(self, path) -> None:
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
        # print(f"min: {min(self.temperature)}, max: {max(self.temperature)}")
        self.heightmap = green
        # print(f"min: {min(self.heightmap)}, max: {max(self.heightmap)}")
        self.humidity = blue
        # print(f"min: {min(self.humidity)}, max: {max(self.humidity)}")

        print(f"Wczytano mapę {self.width} x {self.height}")

    def next_turn(self):
        for miasto in self.miasta:
            for obywatel in miasto.obywatele:
                res, ammount = obywatel.zbierz_zasoby(
                    self.temperature[miasto.x][miasto.y],
                    self.heightmap[miasto.x][miasto.y],
                    self.humidity[miasto.x][miasto.y],
                )
                zasoby, cena = miasto.zasoby[res]
                # TODO przeliczanie ceny po każdej iteracji
                miasto.zasoby[res] = (zasoby + ammount, cena)
