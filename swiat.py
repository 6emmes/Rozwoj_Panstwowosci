from typing import List
import os
import struct


class Swiat:

    def __init__(self) -> None:
        self.tablica_drog: List[object] = []
        self.heightmap: object = None
        self.zasoby_kopalne: List[object] = []
        self.zasoby_drzewa: List[object] = []
        self.zyznosc: object = None
        self.rzeki: List[object] = []
        self.load_stara_map(path="StaraMapa_s.bmp")
        

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

        if bi_bit_count == 32:
            depth = 4
        elif bi_bit_count == 24:
            depth = 3

        width = bi_width
        height = bi_height

        row_padded = (width * depth + 3) & ~3


        red = [[0] * width for _ in range(height)]
        green = [[0] * width for _ in range(height)]
        blue = [[0] * width for _ in range(height)]

        for row in range(height):
            src_row = height - 1 - row
            start = bf_off_bits + src_row * row_padded
            for col in range(width):
                offset = start + col * depth
                
                blue[row][col] = data[offset]
                green[row][col] = data[offset + 1]
                red[row][col] = data[offset + 2]

        self.temperature = red
        self.heightmap = green
        self.humidity = blue
