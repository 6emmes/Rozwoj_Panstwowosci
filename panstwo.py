from armia import Armia
from miasto import Miasto


class Panstwo:
    def __init__(self, nazwa: str) -> None:
        self.nazwa: str = nazwa
        self.miasta: list[Miasto] = []
        self.armie: list[Armia] = []
        self.cele: list[object] = []
        self.wladca: object = None
        self.tablica_dyplomacji: list[object] = []

    def add_miasto(self, miasto) -> None:
        miasto.panstwo = self
        self.miasta.append(miasto)

    def add_armia(self, armia) -> None:
        self.armie.append(armia)

    def akcja(self):
        print(f"Akcje w państwie: {self.nazwa}")
        for m in self.miasta:
            m.akcja()

    def podatek(self):
        pass

    def wypowiedz_wojne(self):
        pass

    def homogenizuj_kulture(self):
        pass
