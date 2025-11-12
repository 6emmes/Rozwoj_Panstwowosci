from typing import List


class Panstwo:
    def __init__(self, nazwa: str) -> None:
        self.nazwa: str = nazwa
        self.miasta: List[Miasto] = []

    def add_miasto(self, miasto) -> None:
        miasto.panstwo = self
        self.miasta.append(miasto)

    def akcja(self):
        print(f"Akcje w państwie: {self.nazwa}")
        for m in self.miasta:
            m.akcja()
