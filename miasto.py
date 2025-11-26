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
        self.zasoby: dict = {}
        self.wartosc_religijna: object = None

        self._inicjuj_zasoby()

        print(f"Miasto {self.nazwa} zostało założone")

    def _inicjuj_zasoby(self):
        self.zasoby = {"drewno": 0, "kamien": 0, "jedzenie": 0}

    def add_obywatel(self, obywatel) -> None:
        obywatel.miasto = self
        self.obywatele.append(obywatel)

    def debug_zasoby(self):
        rounded_resources = {
            key: round(value, 2) if isinstance(value, (int, float)) else value
            for key, value in self.zasoby.items()
        }
        print(f"{self.nazwa}: {rounded_resources}")

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
