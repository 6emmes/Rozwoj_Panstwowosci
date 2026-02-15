# from miasto import Miasto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from city import City


class Citizen:
    def __init__(self) -> None:
        self.city: City | None = None
        # placeholder attribute
        self.culture: object = None

    def debug_print(self) -> None:
        city_name = self.city.name if self.city else None
        print(f"        Obywatel, miasto: {city_name}")

    def action(self):
        self.debug_print()

    def migrate(self):
        pass

    def go_for_pilgrimage(self):
        pass

    def __repr__(self) -> str:
        return self.__class__.__name__
