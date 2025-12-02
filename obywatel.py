# from miasto import Miasto
import random
from typing import TYPE_CHECKING

import zasoby

if TYPE_CHECKING:
    from miasto import City


class Citizen:

    def __init__(self) -> None:
        self.city: City | None = None
        # placeholder attribute
        self.culture: object = None

    def debug_print(self) -> None:
        city_name = self.city.name if self.city else None
        print(f"        Obywatel, miasto: {city_name}")

    def gather_resources(
        self, sqr_temperature: int, sqr_height: int, sqr_humidity: int
    ) -> tuple[str, float]:
        resource = random.choice([zasoby.WOOD, zasoby.FOOD, zasoby.STONE])
        return (
            resource,
            round(
                10
                * zasoby.height_efficiency(resource, sqr_height)
                * zasoby.temp_efficiency(resource, sqr_temperature)
                * zasoby.humidity_efficiency(resource, sqr_humidity),
                2,
            ),
        )

    def action(self):
        self.debug_print()

    def migrate(self):
        pass

    def go_for_pilgrimage(self):
        pass
