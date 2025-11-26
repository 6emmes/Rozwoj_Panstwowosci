from miasto import Miasto
from swiat import Swiat


class Osadnik:
    def __init__(self, x: int, y: int, l_obywateli: int, swiat: Swiat) -> None:
        self.x = x
        self.y = y
        self.l_obywateli = l_obywateli
        # na potrzeby linka
        self.swiat: Swiat = swiat

    def zaloz_miasto(self, nazwa_miasta: str):
        # TODO: dodać sprawdzanie czy miasto nie jest za blisko innego miasta
        city = Miasto(self.x, self.y, nazwa_miasta, self.swiat)
        for _ in range(self.l_obywateli):
            city.create_obywatel()
        return city
