# from miasto import Miasto
import random

import zasoby


class Obywatel:

    def __init__(self) -> None:
        self.miasto: "Miasto | None" = None
        # placeholder attribute
        self.kultura: object = None

    def debug_print(self) -> None:
        city_name = self.miasto.nazwa if self.miasto else None
        print(f"        Obywatel, miasto: {city_name}")

    def zbierz_zasoby(
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

    def akcja(self):
        self.debug_print()

    def migruj(self):
        pass

    def pielgrzymkuj(self):
        pass
