from typing import List
from obywatel import Obywatel


class Miasto:

    def __init__(self, nazwa: str) -> None:
        self.nazwa: str = nazwa
        self.panstwo: "Panstwo | None" = None
        self.obywatele: List[Obywatel] = []

    def add_obywatel(self, obywatel) -> None:
        obywatel.miasto = self
        self.obywatele.append(obywatel)

    def create_obywatel(self):
        obywatel = Obywatel()
        self.add_obywatel(obywatel)
        return obywatel

    def akcja(self):
        print(f"    Akcje w mieście: {self.nazwa}")
        for o in self.obywatele:
            o.akcja()