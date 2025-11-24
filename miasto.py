from obywatel import Obywatel

# from panstwo import Panstwo


class Miasto:

    def __init__(self, x: int, y: int, nazwa: str) -> None:
        self.x: int = x
        self.y: int = y
        self.nazwa: str = nazwa
        # self.panstwo: Panstwo | None = None
        self.obywatele: list[Obywatel] = []
        self.tablica_wag: list[object] = []
        self.wartosc_religijna: object = None

        print(f"Miasto {self.nazwa} zostało założone")

    def add_obywatel(self, obywatel) -> None:
        obywatel.miasto = self
        self.obywatele.append(obywatel)

    def create_obywatel(self):
        obywatel = Obywatel()
        self.add_obywatel(obywatel)
        return obywatel

    def rozbudowa(self):
        pass

    def podatek(self):
        pass

    def tworz_obywateli(self):
        pass

    def akcja(self):
        print(f"    Akcje w mieście: {self.nazwa}")
        for o in self.obywatele:
            o.akcja()
