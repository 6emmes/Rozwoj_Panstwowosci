class Obywatel:

    def __init__(self) -> None:
        self.miasto: "Miasto | None" = None

    def debug_print(self) -> None:
        city_name = self.miasto.nazwa if self.miasto else None
        print(
            f"        Obywatel, miasto: {city_name}"
        )

    def akcja(self):
        self.debug_print()