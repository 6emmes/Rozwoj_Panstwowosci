from typing import List
from obywatel import Obywatel
from handlarz import Handlarz
import random

class Miasto:

    def __init__(self, nazwa: str, x: int, y: int) -> None:
        self.nazwa: str = nazwa
        self.x: int = x
        self.y: int = y
        self.panstwo: "Panstwo | None" = None
        self.obywatele: list[Obywatel] = []
        self.tablica_wag: list[object] = []
        self.wartosc_religijna: object = None
        self.zasoby: dict = {} # nie jestem przekonany do trzymania tego w dictcie ale na razie nie wiem jak to dobrze załatwić klasą
        self._losuj_zasoby_startowe() #Do celów testowych

    def _losuj_zasoby_startowe(self):
        mozliwe_zasoby = ['jedzenie', 'drewno', 'kamien']
        max_zasobu = 100
        zasoby = {}
        for zasob in mozliwe_zasoby:
            # format zasoby[zasob] = (ilosc, cena)
            self.zasoby[zasob] = (random.randint(0, max_zasobu), random.uniform(1.0, 10.0))


    def add_obywatel(self, obywatel) -> None:
        obywatel.miasto = self
        self.obywatele.append(obywatel)

    def create_obywatel(self):
        obywatel = Obywatel()
        self.add_obywatel(obywatel)
        return obywatel

    def create_handlarz(self):
        try:
            self.obywatele.pop()
        except IndexError:
            raise IndexError("Brak obywateli do przekształcenia w handlarza")
        handlarz = Handlarz()
        self.add_obywatel(handlarz)
        return handlarz

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

    def __repr__(self):
        return f"Miasto({self.nazwa})"