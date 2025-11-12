from typing import List
from miasto import Miasto


class Panstwo:
    def __init__(self, nazwa: str) -> None:
        self.nazwa: str = nazwa
        self.miasta: List[Miasto] = []
        self.armie: List["Armia | None"] = []
        self.cele: List[object] = []
        self.wladca: object = None
        self.tablicaDyplomacji: List[object] = []

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

    def wypowiedzWojne(self):
        pass

    def homogenizujKulture(self):
        pass
