from miasto import Miasto
from obywatel import Obywatel


class Osadnik:
    def __init__(self, x: int, y: int, l_obywateli: int) -> None:
        self.x = x
        self.y = y
        self.l_obywateli = l_obywateli

    def zaloz_miasto(self, nazwa_miasta: str):
        # TODO: dodać sprawdzanie czy miasto nie jest za blisko innego miasta
        miasto = Miasto(self.x, self.y, nazwa_miasta)
        for _ in range(self.l_obywateli):
            miasto.add_obywatel(Obywatel())
        return miasto
